"""LIN + DIFF Holm families for the amended calibrated screen.

Peer-review methodology deliverable (round4/peer_review_h_xorspn3.md, section 3):
the old screen (PB + RD, 468 cells) is blind by construction to joint 64-bit
and consecutive-output structure. Two new families, SEQ x 10 keys:

- LIN (linear bound): per cell, 4096 matrices of 64x64 (rows = 64 consecutive
  outputs); D = #{rank <= 61}; null D ~ Binomial(4096, 0.005285) exact;
  per-cell p = upper tail. Bound: no detectable GF(2)-linear dependency at N=2^18.
- DIFF (differential bound): per cell, 18 weight-1 deltas 2^0..2^17, deduped
  2^17 pairs each; low-8-bit chi2 -> two-sided normal p; Fisher-combine the 18
  p-values per cell, Bonferroni-on-max as dependence-robust secondary.
  Bound: no detectable truncated-differential structure at N=2^18.

Verdict: CAL_PASS iff zero Holm rejections across all four families
(PB, RD, LIN, DIFF). Honest FWER <= 0.04.

Both families reuse the already-computed SEQ outputs -- no extra hashing.
"""

import math
import numpy as np
from scipy.stats import binom as binom_dist, chi2 as chi2_dist

import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_cal import logp_twosided_normal, fisher_logp, holm_reject, ALPHA

# Exact null P(rank <= 61) for a random 64x64 binary matrix (from the
# peer-review prototype; verified against the rank distribution).
P_RANK_DEFICIENT = 0.005285
N_MATRICES = 4096  # 2^18 / 64
LIN_DF = None  # not needed; binomial exact


def gf2_rank64(rows):
    """Rank over GF(2) of a 64x64 binary matrix given as 64 Python ints
    (row i = 64-bit bitmask). Gaussian elimination with bitset rows."""
    # copy to list for mutation
    m = list(rows)
    rank = 0
    for col in range(64):
        bit = 1 << (63 - col)
        # find pivot
        piv = -1
        for r in range(rank, 64):
            if m[r] & bit:
                piv = r
                break
        if piv < 0:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        # eliminate below (above not needed for rank)
        mr = m[rank]
        for r in range(rank + 1, 64):
            if m[r] & bit:
                m[r] ^= mr
        rank += 1
        if rank == 64:
            break
    return rank


def lin_cell_logp(S):
    """LIN cell: 4096 64x64 matrices from 64 consecutive outputs each.
    Returns (logp_upper_tail, D_deficient)."""
    S = np.asarray(S, dtype=np.uint64)
    assert S.shape[0] >= N_MATRICES * 64
    D = 0
    for i in range(N_MATRICES):
        rows = [int(S[i * 64 + r]) for r in range(64)]
        if gf2_rank64(rows) <= 61:
            D += 1
    # upper-tail p of Binomial(4096, 0.005285) >= D
    p = float(binom_dist.sf(D - 1, N_MATRICES, P_RANK_DEFICIENT)) if D > 0 else 1.0
    # guard against p == 0.0 (underflow) -> use logsf directly
    if p <= 0.0:
        logp = float(binom_dist.logsf(D - 1, N_MATRICES, P_RANK_DEFICIENT))
    else:
        logp = math.log(p)
    return logp, D


def _chi2_twosided_logp(chi2_val, df=255):
    """Two-sided normal p-value (log) for a chi2 statistic via Wilson-Hilferty."""
    # Wilson-Hilferty: z = ((x/df)^(1/3) - (1 - 2/(9df))) / sqrt(2/(9df))
    x = float(chi2_val)
    t = (x / df) ** (1.0 / 3.0)
    mu = 1.0 - 2.0 / (9.0 * df)
    sd = math.sqrt(2.0 / (9.0 * df))
    z = (t - mu) / sd
    return logp_twosided_normal(z)


def diff_cell_logp(S):
    """DIFF cell: 18 weight-1 deltas, low-8-bit chi2 each, Fisher-combined.
    Returns (fisher_logp, worst_chi2_z, worst_delta)."""
    S = np.asarray(S, dtype=np.uint64)
    n = S.shape[0]
    assert n >= 1 << 18
    logps = []
    worst_z = 0.0
    worst_d = None
    # expected count per bin: 2^17 pairs / 256 bins = 512
    exp = (1 << 17) / 256.0
    for k in range(18):
        delta = np.uint64(1) << np.uint64(k)
        # deduped pairs: v in [0, 2^18) with bit k clear -> 2^17 pairs
        V = np.arange(1 << 18, dtype=np.uint64)
        V = V[(V & delta) == 0]
        diffs = (S[V] ^ S[V ^ delta]) & np.uint64(0xFF)
        counts = np.bincount(diffs.astype(np.int64), minlength=256).astype(np.float64)
        chi2v = float(((counts - exp) ** 2 / exp).sum())
        lp = _chi2_twosided_logp(chi2v, 255)
        logps.append(lp)
        # track worst |z| for reporting (invert logp approx via normal)
        # use Wilson-Hilferty z directly
        t = (chi2v / 255) ** (1.0 / 3.0)
        z = abs((t - (1.0 - 2.0 / (9.0 * 255))) / math.sqrt(2.0 / (9.0 * 255)))
        if z > worst_z:
            worst_z, worst_d = z, k
    return fisher_logp(logps), worst_z, worst_d


def screen_lindiff(S_cache, name, verbose=True):
    """Run LIN + DIFF families on cached SEQ outputs.

    S_cache: dict (scen, key) -> S array, must contain ("SEQ", key) for the
    screen's KEYS. Returns dict with Holm verdicts.
    """
    from screen_lib import KEYS
    lin_logps = []   # (cell_id, logp)
    diff_logps = []  # (cell_id, logp)
    lin_D = {}
    diff_worst = {}
    for key in KEYS:
        S = S_cache[("SEQ", key)]
        lp_lin, D = lin_cell_logp(S)
        lin_logps.append(((f"LIN-SEQ", key), lp_lin))
        lin_D[key] = D
        lp_diff, wz, wd = diff_cell_logp(S)
        diff_logps.append(((f"DIFF-SEQ", key), lp_diff))
        diff_worst[key] = (wz, wd)
    rej_lin = holm_reject(lin_logps, alpha=ALPHA)
    rej_diff = holm_reject(diff_logps, alpha=ALPHA)
    verdict = "CAL_PASS" if not rej_lin and not rej_diff else "CAL_FLAG"
    if verbose:
        print(f"[{name}] LIN: max D={max(lin_D.values())}/4096 "
              f"(null exp {N_MATRICES*P_RANK_DEFICIENT:.1f}), rej={len(rej_lin)}")
        print(f"[{name}] DIFF: worst chi2|z|={max(w for w, _ in diff_worst.values()):.1f}, "
              f"rej={len(rej_diff)} -> {verdict}")
    return dict(
        name=name,
        lin_verdict="CAL_PASS" if not rej_lin else "CAL_FLAG",
        diff_verdict="CAL_PASS" if not rej_diff else "CAL_FLAG",
        verdict=verdict,
        rej_lin=[(c[0], f"{c[1]:#018x}") for c in rej_lin],
        rej_diff=[(c[0], f"{c[1]:#018x}") for c in rej_diff],
        lin_D=lin_D,
        diff_worst=diff_worst,
        n_lin_cells=len(lin_logps),
        n_diff_cells=len(diff_logps),
    )
