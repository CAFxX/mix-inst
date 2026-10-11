"""LIN and DIFF families for the amended S1 screen (fast staged battery).

Implements the round-5 screen amendment from round4/peer_review_h_xorspn3.md:
- Family LIN (linear bound): per cell (SEQ x 10 keys), 4096 matrices of 64x64
  (rows = 64 consecutive outputs); D = #{rank <= 61}; null D ~ Binomial(4096,
  0.005285) exact; per-cell p = upper tail. Holm-Bonferroni across cells, a=0.01.
  Bound: no detectable GF(2)-linear dependency at N=2^18.
- Family DIFF (differential bound): per cell, 18 weight-1 deltas 2^0..2^17,
  deduped 2^17 pairs each; low-8-bit chi2 -> two-sided normal p; Fisher-combine
  the 18 p-values per cell (Bonferroni-on-max reported as dependence-robust
  secondary). Holm-Bonferroni across cells, a=0.01.
  Bound: no detectable truncated-differential structure at N=2^18.

Both reuse already-computed SEQ outputs (passed in as dict key -> uint64 array).
"""
import math
import numpy as np
from scipy.stats import binom as binom_dist, chi2 as chi2_dist, norm as norm_dist

ALPHA = 0.01
N_MATRICES = 4096
RANK_CUTOFF = 61
NULL_P_RANKDEF = 0.005285  # exact P(rank <= 61) for 64x64 binary matrix
N_DIFF_PAIRS = 1 << 17
DIFF_KS = list(range(18))  # deltas 2^0 .. 2^17


def gf2_rank64(rows):
    """Rank over GF(2) of a 64x64 binary matrix given as 64 uint64 row bitmasks."""
    r = [int(x) for x in rows]
    rank = 0
    for col in range(63, -1, -1):
        piv = -1
        for i in range(rank, 64):
            if (r[i] >> col) & 1:
                piv = i
                break
        if piv < 0:
            continue
        r[rank], r[piv] = r[piv], r[rank]
        for i in range(rank + 1, 64):
            if (r[i] >> col) & 1:
                r[i] ^= r[rank]
        rank += 1
    return rank


def lin_cell_logp(S):
    """D = #{64x64 matrices with rank <= 61} over 4096 non-overlapping blocks
    of 64 consecutive outputs. Returns (D, upper-tail log-p)."""
    S = np.asarray(S, dtype=np.uint64)
    assert S.shape[0] >= N_MATRICES * 64
    d = 0
    for m in range(N_MATRICES):
        block = S[m * 64:(m + 1) * 64]
        if gf2_rank64(block) <= RANK_CUTOFF:
            d += 1
    # upper-tail: P(Bin(n,p) >= d); d==0 -> logp = 0 (no evidence)
    logp = float(binom_dist.logsf(d - 1, N_MATRICES, NULL_P_RANKDEF)) if d > 0 else 0.0
    return d, logp


def logp_twosided_chi2(obs, df):
    """Two-sided p-value for a chi2 statistic via normal approximation."""
    z = (obs - df) / math.sqrt(2.0 * df)
    az = abs(z)
    # log of 2*Phi(-|z|), Mills asymptote for |z| > 8
    if az <= 8.0:
        return math.log(2.0) + float(norm_dist.logsf(az))
    return math.log(2.0) - 0.5 * az * az - math.log(az) - 0.5 * math.log(2 * math.pi)


def diff_cell_logps(S, key):
    """18 weight-1 deltas 2^0..2^17 on sequential inputs: for delta 2^k, pairs
    (x, x^2^k) for x in [0, 2^17) canonical-deduped. Low-8-bit chi2 of the
    output differences -> two-sided normal log-p per delta.
    Returns (list of 18 logps, worst |z|, fisher combined logp)."""
    S = np.asarray(S, dtype=np.uint64)
    n = N_DIFF_PAIRS
    logps = []
    worst_z = 0.0
    for k in DIFF_KS:
        dl = np.uint64(1) << np.uint64(k)
        xs = np.arange(n, dtype=np.uint64)
        ys = xs ^ dl
        keep = xs < ys  # canonical unordered dedupe
        dx = (S[xs[keep]] ^ S[ys[keep]]).astype(np.uint64)
        npairs = int(keep.sum())
        h8 = np.bincount((dx & np.uint64(0xFF)).astype(np.int64), minlength=256).astype(float)
        exp = npairs / 256.0
        chi2 = float((((h8 - exp) ** 2) / exp).sum())
        df = 255
        logps.append(logp_twosided_chi2(chi2, df))
        z = abs(chi2 - df) / math.sqrt(2.0 * df)
        worst_z = max(worst_z, z)
    # Fisher combine (heuristic under dependence; Bonferroni-on-max is the
    # dependence-robust secondary, reported alongside)
    x2 = -2.0 * sum(logps)
    fisher_logp = float(chi2_dist.logsf(x2, 2 * len(logps)))
    bonf_logp = min(logps) + math.log(len(logps))  # log(min p * 18), capped later
    return logps, worst_z, fisher_logp, bonf_logp


def holm_reject(logp_cells, alpha=ALPHA):
    """Holm-Bonferroni step-down on [(cell_id, logp)]. Returns rejected ids."""
    ordered = sorted(logp_cells, key=lambda t: t[1])
    m = len(ordered)
    rej = []
    for i, (cid, lp) in enumerate(ordered):
        if lp < math.log(alpha / (m - i)):
            rej.append(cid)
        else:
            break
    return rej


def screen_lin_diff(seq_outputs, verbose=True):
    """seq_outputs: dict key -> uint64 array (N >= 2^18 sequential outputs).
    Returns dict with per-family verdicts and rejected cells."""
    lin_cells, diff_cells = [], []
    detail = {}
    for key, S in seq_outputs.items():
        d, lp = lin_cell_logp(S)
        lin_cells.append((("LIN", key), lp))
        detail[("LIN", key)] = {"D": d, "logp": lp}
        _, wz, flp, blp = diff_cell_logps(S, key)
        diff_cells.append((("DIFF", key), flp))
        detail[("DIFF", key)] = {"worst_z": wz, "fisher_logp": flp,
                                 "bonf_logp": blp}
    lin_rej = holm_reject(lin_cells)
    diff_rej = holm_reject(diff_cells)
    res = {
        "lin_rejected": lin_rej, "diff_rejected": diff_rej,
        "lin_detail": {str(k): v for k, v in detail.items() if k[0] == "LIN"},
        "diff_detail": {str(k): v for k, v in detail.items() if k[0] == "DIFF"},
        "lin_verdict": "PASS" if not lin_rej else "FLAG",
        "diff_verdict": "PASS" if not diff_rej else "FLAG",
    }
    if verbose:
        for (fam, key), lp in lin_cells:
            dd = detail[(fam, key)]
            print(f"  [LIN] key={key:#x} D={dd['D']}/4096 logp={lp:.2f}")
        for (fam, key), lp in diff_cells:
            dd = detail[(fam, key)]
            print(f"  [DIFF] key={key:#x} worst|z|={dd['worst_z']:.1f} "
                  f"fisher_logp={lp:.2f} bonf_logp={dd['bonf_logp']:.2f}")
        print(f"  LIN: {res['lin_verdict']} (rej={len(lin_rej)})  "
              f"DIFF: {res['diff_verdict']} (rej={len(diff_rej)})")
    return res
