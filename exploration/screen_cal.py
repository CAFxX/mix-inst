"""Calibrated screening for round 2 of the mix design-space exploration.

Runs the IDENTICAL protocol/scenario catalog as screen_lib.screen (same keys,
same N, same strided-config dedup, same reductions on SEQ and PTR-j8), but
records the full 64-vector of per-bit z-scores per (scenario, key) cell and
applies the round-2 calibrated flagging rule:

  per-bit family: per cell, Fisher-combine the 64 two-sided normal p-values
                  (chi2 df=128); Holm-Bonferroni across ALL cells, alpha=0.01.
  reduction family: per (SEQ|PTR-j8, key) cell, Fisher-combine the 9 reduction
                  p-values (chi2 df=18); Holm-Bonferroni, alpha=0.01.

Verdict CAL_PASS iff no cell rejects in either family.

The round-1 raw bars (worst per-bit |z| >= 4.0, worst reduction |z| >= 4.5)
are ALSO reported for continuity, but they do not drive the verdict.

Caveat (stated, not hidden): the 64 per-bit tests inside one cell are computed
from the same N outputs and are therefore NOT independent. Fisher's method
assumes independence, so as an exact test it is liberal under dependence; it is
used here as the prescribed calibrated screening heuristic. A secondary
Bonferroni-on-max|z| check (valid under arbitrary dependence) is reported
alongside for context.

Does NOT modify screen_lib.py; imports its constants and null-distribution
helpers.
"""
import math
import numpy as np
from scipy.stats import chi2 as chi2_dist, norm as norm_dist

import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (
    KEYS, N, POW2_KS, LEMURE_XS, MASK_MS, MOD_YS,
    PTR_JS, MPOW2_CS, MPOW2_KS, HIGH_ONLY_I, HIGH_ONLY_J, DESC_JS,
    FIB_I, FIB_J, KEYSWEEP_NINPUTS, KEYSWEEP_NKEYS, KEYSWEEP_KEYS,
    strided_distinct, lemire_z, mask_z, mask32_z, mod_z,
    check_model_equiv, bijectivity_spotcheck,
)

M64 = (1 << 64) - 1
U64 = np.uint64
ALPHA = 0.01


def perbit_zarray(S):
    """All 64 per-bit monobit |z| values for the output array S."""
    S = np.asarray(S, dtype=np.uint64)
    n = S.shape[0]
    denom = math.sqrt(n / 4.0)
    zs = np.empty(64)
    for b in range(64):
        c = int((((S >> U64(b)) & U64(1)).sum()))
        zs[b] = abs((c - n / 2.0) / denom)
    return zs


def logp_twosided_normal(z):
    """log of the two-sided standard-normal p-value for |z| = z.
    Numerically stable for extreme z via the Mills-ratio asymptote."""
    az = abs(float(z))
    if az <= 8.0:
        return math.log(2.0) + float(norm_dist.logsf(az))
    # ln(2 * Phi(-az)) ~ ln2 - az^2/2 - ln(az) - 0.5*ln(2*pi)
    return math.log(2.0) - 0.5 * az * az - math.log(az) - 0.5 * math.log(2 * math.pi)


def fisher_logp(logps):
    """Fisher combined log-p for a list of independent log-p-values."""
    x2 = -2.0 * sum(logps)
    df = 2 * len(logps)
    return float(chi2_dist.logsf(x2, df))


def holm_reject(logp_cells, alpha=ALPHA):
    """Holm-Bonferroni step-down on [(cell_id, logp), ...] (log-p ascending =
    most significant first). Returns the list of rejected cell_ids."""
    ordered = sorted(logp_cells, key=lambda t: t[1])
    M = len(ordered)
    ln_alpha = math.log(alpha)
    rejected = []
    for k, (cid, lp) in enumerate(ordered, start=1):
        thresh = ln_alpha - math.log(M - k + 1)
        if lp <= thresh:
            rejected.append(cid)
        else:
            break
    return rejected


def _scenario_vectors():
    """(scenario_name, input_vector_fn) list, mirroring screen_lib.screen."""
    scens = [("SEQ", lambda: np.arange(N, dtype=np.uint64))]
    scens.append(("PTR-j8", lambda: strided_distinct(0, PTR_JS[0], N)))
    scens.append(("PTR-j16", lambda: strided_distinct(0, PTR_JS[1], N)))
    for c in MPOW2_CS:
        for kk in MPOW2_KS:
            scens.append((f"MPOW2-{c}x2^{kk}",
                          lambda c=c, kk=kk: strided_distinct(0, c * (1 << kk), N)))
    scens.append(("HIGH-ONLY", lambda: strided_distinct(HIGH_ONLY_I, HIGH_ONLY_J, N)))
    for j in DESC_JS:
        scens.append((f"DESC-j={(j & M64):#x}",
                      lambda j=j: strided_distinct(0, j, N)))
    for kk in POW2_KS:
        scens.append((f"POW2-2^{kk}",
                      lambda kk=kk: strided_distinct(0, 1 << kk, N)))
    scens.append(("STRIDE-3", lambda: strided_distinct(0, 3, N)))
    scens.append(("STRIDE-FIB", lambda: strided_distinct(FIB_I, FIB_J, N)))
    scens.append(("SINGLE-BIT", lambda: (U64(1) << np.arange(64, dtype=np.uint64))))
    return scens


def _reduction_logps(S):
    """Log-p-values for the 9 reduction tests on output array S."""
    lps = []
    for X in LEMURE_XS:
        lps.append(logp_twosided_normal(lemire_z(S, X)))
    for m in MASK_MS:
        if m == 32:
            _t, zs = mask32_z(S)
            # mask32_z returns the worst (label, z); recover the three
            # sub-stats individually for a proper Fisher sum:
            n = S.shape[0]
            w = (np.asarray(S, dtype=np.uint64) & U64(0xFFFFFFFF)).astype(np.int64)
            lo = w & 0xFFFF
            hi = (w >> 16) & 0xFFFF
            from screen_lib import chi2_z
            lps.append(logp_twosided_normal(
                chi2_z(np.bincount(lo, minlength=1 << 16).astype(float), n)))
            lps.append(logp_twosided_normal(
                chi2_z(np.bincount(hi, minlength=1 << 16).astype(float), n)))
            _, counts = np.unique(w, return_counts=True)
            coll = int(((counts * (counts - 1)) // 2).sum())
            exp_coll = (n * (n - 1) / 2) / (1 << 32)
            lps.append(logp_twosided_normal((coll - exp_coll) / math.sqrt(exp_coll)))
        else:
            lps.append(logp_twosided_normal(mask_z(S, m)))
    for y in MOD_YS:
        lps.append(logp_twosided_normal(mod_z(S, y)))
    return lps


def screen_marginal(fn, name, verbose=True):
    """Standalone marginal PB/RD screen (S1b of screen_calibrated).

    Runs the 468-cell marginal screen: per-bit (PB) + reduction (RD) families
    over all scenarios x KEYS, Fisher-combine + Holm-Bonferroni, alpha=0.01.
    Deterministic given fn (fixed scenario vectors, no RNG).

    Triage-upgrade gate (O143, 2026-10-12): run this at triage on the Python
    model and REJECT if n_pb_reject >= 1 or n_rd_reject >= 1. Sound: S0a
    XCHECK (10000/10000 C==Python) guarantees the C bundle matches, so the
    triage verdict == the S1 verdict for every candidate that reaches S1
    (43/43 historical marginal kills; 0/6 battery-passers rejected).

    Returns dict with verdict ("MARGINAL_PASS"/"MARGINAL_FLAG"), rej lists,
    counts, and raw worst|z| values.
    """
    scens = _scenario_vectors()
    K = np.uint64

    perbit_cells = []      # (cell_id, [64 logps])
    red_cells = []         # (cell_id, [9 logps])
    raw_pb = {}            # scen -> [worst|z|, loc]
    raw_rd = {}            # scen -> [worst|z|, loc]

    for key in KEYS:
        kb = np.full(N, K(key), dtype=np.uint64)
        for scen, vfn in scens:
            V = vfn()
            n = V.shape[0]
            S = np.asarray(fn(V, np.full(n, K(key), dtype=np.uint64)),
                           dtype=np.uint64)
            zarr = perbit_zarray(S)
            perbit_cells.append(((scen, key), [logp_twosided_normal(z) for z in zarr]))
            mz = float(zarr.max())
            r = raw_pb.setdefault(scen, [0.0, None])
            if mz > r[0]:
                r[0] = mz
                r[1] = (key, int(zarr.argmax()))
            if scen in ("SEQ", "PTR-j8"):
                lps = _reduction_logps(S)
                red_cells.append(((scen, key), lps))
                # raw reduction worst |z| for continuity
                rz = 0.0
                rloc = None
                for X in LEMURE_XS:
                    z = abs(float(lemire_z(S, X)))
                    if z > rz:
                        rz, rloc = z, f"lemire-X={X}"
                for m in MASK_MS:
                    if m == 32:
                        t, z = mask32_z(S)
                        z = abs(float(z))
                    else:
                        t, z = f"mask-m={m}", abs(float(mask_z(S, m)))
                    if z > rz:
                        rz, rloc = z, t
                for y in MOD_YS:
                    z = abs(float(mod_z(S, y)))
                    if z > rz:
                        rz, rloc = z, f"mod-{y}"
                rr = raw_rd.setdefault(scen, [0.0, None])
                if rz > rr[0]:
                    rr[0] = rz
                    rr[1] = (key, rloc)

    # KEY-SWEEP: 128 fixed inputs x 64 keys, per-bit over the key axis.
    Vin = np.arange(KEYSWEEP_NINPUTS, dtype=np.uint64)
    Sf = np.asarray(fn(np.tile(Vin, KEYSWEEP_NKEYS),
                       np.repeat(KEYSWEEP_KEYS, KEYSWEEP_NINPUTS)),
                    dtype=np.uint64).reshape(KEYSWEEP_NKEYS, KEYSWEEP_NINPUTS)
    for j in range(KEYSWEEP_NINPUTS):
        zarr = perbit_zarray(Sf[:, j])
        perbit_cells.append((("KEY-SWEEP", int(Vin[j])), [logp_twosided_normal(z) for z in zarr]))
        mz = float(zarr.max())
        r = raw_pb.setdefault("KEY-SWEEP", [0.0, None])
        if mz > r[0]:
            r[0] = mz
            r[1] = (int(Vin[j]), int(zarr.argmax()))

    # ---- calibration ----
    pb_logps = [(cid, fisher_logp(lps)) for cid, lps in perbit_cells]
    rd_logps = [(cid, fisher_logp(lps)) for cid, lps in red_cells]
    rej_pb = holm_reject(pb_logps)
    rej_rd = holm_reject(rd_logps)

    verdict = "MARGINAL_PASS" if not rej_pb and not rej_rd else "MARGINAL_FLAG"
    gw_pb = max(raw_pb.items(), key=lambda kv: kv[1][0])
    gw_rd = max(raw_rd.items(), key=lambda kv: kv[1][0])
    res = dict(
        name=name,
        verdict=verdict,
        n_pb_reject=len(rej_pb),
        n_rd_reject=len(rej_rd),
        rejected_perbit=[(f"{c[0]}", f"{c[1]:#018x}" if isinstance(c[1], int) and c[0] != "KEY-SWEEP" else c[1]) for c in rej_pb],
        rejected_red=[(f"{c[0]}", f"{c[1]:#018x}") for c in rej_rd],
        raw_worst_perbit_z=gw_pb[1][0],
        raw_worst_red_z=gw_rd[1][0],
        n_perbit_cells=len(pb_logps),
        n_red_cells=len(rd_logps),
        # full intermediate state for screen_calibrated's report fields
        _rej_pb=rej_pb,
        _rej_rd=rej_rd,
        _pb_logps=pb_logps,
        _rd_logps=rd_logps,
        _raw_pb=raw_pb,
        _raw_rd=raw_rd,
    )
    if verbose:
        print(f"[{name}] marginal: PB rej={len(rej_pb)} RD rej={len(rej_rd)} "
              f"(raw max|z| pb={gw_pb[1][0]:.2f} rd={gw_rd[1][0]:.2f}) -> {verdict}")
    return res


def screen_calibrated(fn, name, verbose=True):
    """Full calibrated screen. Returns a result dict with raw and calibrated
    verdicts. See module docstring for the method.

    S1 order (amended): LIN/DIFF run FIRST on SEQ outputs; the 468-cell
    marginal (PB/RD) screen is skipped on a LIN/DIFF kill (early exit).
    """
    scens = _scenario_vectors()
    K = np.uint64

    # ---- S1a: LIN/DIFF first (binding constraint; fast kill) ----
    from screen_lindiff import screen_lindiff
    S_seq = {}
    for key in KEYS:
        V = np.arange(N, dtype=np.uint64)  # SEQ scenario
        S = np.asarray(fn(V, np.full(N, K(key), dtype=np.uint64)),
                       dtype=np.uint64)
        S_seq[("SEQ", key)] = S
    ld_res = screen_lindiff(S_seq, name, verbose=verbose)
    if ld_res["verdict"] == "CAL_FLAG":
        # Early kill: skip the marginal screen entirely.
        if verbose:
            print(f"[{name}] S1 LIN/DIFF KILL -> CAL_FLAG (marginal screen skipped)")
        return dict(
            name=name,
            cal_verdict="CAL_FLAG",
            lin_verdict=ld_res["lin_verdict"],
            diff_verdict=ld_res["diff_verdict"],
            cal_rejected_lin=ld_res["rej_lin"],
            cal_rejected_diff=ld_res["rej_diff"],
            lin_D=ld_res["lin_D"],
            diff_worst=ld_res["diff_worst"],
            n_lin_cells=ld_res["n_lin_cells"],
            n_diff_cells=ld_res["n_diff_cells"],
            s1_kill=True,
            # PB/RD not run
            cal_rejected_perbit=[], cal_rejected_red=[],
            n_perbit_cells=0, n_red_cells=0,
        )

    # ---- S1b: marginal screen (PB/RD) only if LIN/DIFF pass ----
    # (O143 triage-upgrade: standalone screen_marginal, shared with triage.)
    marg = screen_marginal(fn, name, verbose=False)
    rej_pb = marg["_rej_pb"]
    rej_rd = marg["_rej_rd"]
    pb_logps = marg["_pb_logps"]
    rd_logps = marg["_rd_logps"]
    raw_pb = marg["_raw_pb"]
    raw_rd = marg["_raw_rd"]

    # secondary Bonferroni-on-max|z| check (valid under dependence):
    # scenario-level Bonferroni on the raw worst|z| (conservative, informational).
    bonf_scen = {}
    for scen, (mz, _loc) in raw_pb.items():
        # cells in this scenario: 10 keys (or 128 inputs for KEY-SWEEP)
        ncells = KEYSWEEP_NINPUTS if scen == "KEY-SWEEP" else len(KEYS)
        p_bonf = ncells * 64 * math.exp(logp_twosided_normal(mz))
        bonf_scen[scen] = p_bonf

    # ---- LIN + DIFF families (amended screen, peer-review M2) ----
    # Already computed and passed in S1a above (early exit on kill);
    # reuse the same result here for the combined verdict.
    cal_verdict = ("CAL_PASS" if not rej_pb and not rej_rd else "CAL_FLAG")
    raw_flagged_pb = sorted(s for s, r in raw_pb.items() if r[0] >= 4.0)
    raw_flagged_rd = sorted(s for s, r in raw_rd.items() if r[0] >= 4.5)
    raw_verdict = "PASS" if not raw_flagged_pb and not raw_flagged_rd else "FLAG"
    gw_pb = max(raw_pb.items(), key=lambda kv: kv[1][0])
    gw_rd = max(raw_rd.items(), key=lambda kv: kv[1][0])

    # most significant calibrated cells for the report
    pb_sorted = sorted(pb_logps, key=lambda t: t[1])[:5]
    rd_sorted = sorted(rd_logps, key=lambda t: t[1])[:5]

    res = dict(
        name=name,
        raw_verdict=raw_verdict,
        raw_worst_perbit_z=gw_pb[1][0], raw_perbit_loc=(gw_pb[0], gw_pb[1][0], gw_pb[1][1]),
        raw_worst_red_z=gw_rd[1][0], raw_red_loc=(gw_rd[0], gw_rd[1][0], gw_rd[1][1]),
        raw_flagged_pb=raw_flagged_pb, raw_flagged_red=raw_flagged_rd,
        cal_verdict=cal_verdict,
        cal_rejected_perbit=[(f"{c[0]}", f"{c[1]:#018x}" if isinstance(c[1], int) and c[0] != "KEY-SWEEP" else c[1]) for c in rej_pb],
        cal_rejected_red=[(f"{c[0]}", f"{c[1]:#018x}") for c in rej_rd],
        cal_top_perbit=[(f"{c[0]}", math.exp(lp)) for c, lp in
                        [((t[0][0], t[0][1]), t[1]) for t in pb_sorted]],
        cal_top_red=[(f"{c[0]}", math.exp(lp)) for c, lp in
                     [((t[0][0], t[0][1]), t[1]) for t in rd_sorted]],
        bonferroni_scenario_p=bonf_scen,
        n_perbit_cells=len(pb_logps), n_red_cells=len(rd_logps),
        # amended-screen LIN/DIFF families
        lin_verdict=ld_res["lin_verdict"],
        diff_verdict=ld_res["diff_verdict"],
        cal_rejected_lin=ld_res["rej_lin"],
        cal_rejected_diff=ld_res["rej_diff"],
        lin_D=ld_res["lin_D"],
        diff_worst=ld_res["diff_worst"],
        n_lin_cells=ld_res["n_lin_cells"],
        n_diff_cells=ld_res["n_diff_cells"],
    )
    if verbose:
        print(f"[{name}] raw: perbit max|z|={res['raw_worst_perbit_z']:.2f} "
              f"red max|z|={res['raw_worst_red_z']:.2f} -> {raw_verdict}")
        print(f"[{name}] calibrated (4-family): {cal_verdict} "
              f"(rej pb: {len(rej_pb)}, red: {len(rej_rd)}, "
              f"lin: {len(ld_res['rej_lin'])}, diff: {len(ld_res['rej_diff'])})")
    return res


if __name__ == "__main__":
    # self-tests of the calibration machinery (no candidate involved)
    rng = np.random.default_rng(0)
    # 1) null-like cells: 64 z ~ |N(0,1)| per cell, 500 cells -> expect no rejection
    cells = []
    for i in range(500):
        z = np.abs(rng.standard_normal(64))
        cells.append((i, [logp_twosided_normal(v) for v in z]))
    rej = holm_reject([(c, fisher_logp(l)) for c, l in cells])
    print(f"null simulation: {len(rej)}/500 cells rejected (expect 0, allow <=2)")
    assert len(rej) <= 2, rej
    # 2) one bad cell with a single z=6 bit -> Fisher should NOT reject
    #    (isolated marginal bit washes out), but z=20 must reject
    z1 = np.abs(rng.standard_normal(64)); z1[0] = 6.0
    z2 = np.abs(rng.standard_normal(64)); z2[0] = 20.0
    lp1 = fisher_logp([logp_twosided_normal(v) for v in z1])
    lp2 = fisher_logp([logp_twosided_normal(v) for v in z2])
    rej = holm_reject([(0, lp1), (1, lp2)] + [(i + 2, fisher_logp([logp_twosided_normal(v) for v in np.abs(rng.standard_normal(64))])) for i in range(446)])
    assert 1 in rej, "z=20 cell must reject"
    print(f"single-bit z=6: {'rejected' if 0 in rej else 'not rejected'} (expect not); "
          f"z=20: {'rejected' if 1 in rej else 'NOT rejected'} (expect rejected)")
    # 3) systematic: 8 bits at z=5 -> must reject
    z3 = np.abs(rng.standard_normal(64)); z3[:8] = 5.0
    lp3 = fisher_logp([logp_twosided_normal(v) for v in z3])
    rej = holm_reject([(0, lp3)] + [(i + 1, fisher_logp([logp_twosided_normal(v) for v in np.abs(rng.standard_normal(64))])) for i in range(447)])
    assert 0 in rej, "8x z=5 systematic cell must reject"
    print("systematic 8x z=5: rejected (expect rejected)")
    print("calibration self-tests: OK")
