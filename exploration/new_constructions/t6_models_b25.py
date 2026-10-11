"""Track 6, batch 25: cross-stage nonlinear coupling RE-TEST (incarnation F).

Batch 24's t6_xc4a (18.7u) was S1-killed, but root-cause analysis proved the
kill was a SCHEDULE bug, not an axis failure: the XC_SCHED4 AND pairs
(5,17),(11,23),(3,19),(13,27) are widely separated, so on S1's SEQ inputs
(v = 0..2^18, only low bits vary per 64-block) the AND terms are IDENTICALLY
ZERO (stage-0 t: 1 distinct value across the block). The design degraded to
nearly-linear -> catastrophic LIN (D=4096/4096) + DIFF (worst_z ~36677).

Proven fix: close AND pairs recover normal ranks (54-61 vs 35-46).

Batch 25 re-tests the axis with SEQ-co-designed schedules:
  Rule: AND pairs (a,b) must satisfy |a-b| <= 2 so both rotations overlap
  in the active low-bit region on sequential inputs.

Structure (unchanged from batch 24):
  t_j   = rot(x_j,a_j) & rot(x_j,b_j)
  x_{j+1} = x_j ^ t_j ^ rot(x_j,c_j) ^ rk_j ^ rot(t_{j-1}, s_j),  t_{-1} = 0

Candidates:
  t6_xc4b: 4-stage, close AND pairs, SAME (c,s) as killed xc4a.
           Isolates the schedule fix: only (a,b) changed.
  t6_xc4c: 4-stage, close AND pairs, ALTERNATIVE schedule (all params varied).
           Robustness: is the fix schedule-specific or general?
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

# Schedules: (a, b, c, s): t=ra&rb (|a-b|<=2 REQUIRED), linear rc,
# coupled rot(t_prev, s). t_{-1} = 0.
# xc4b: same (c,s) as killed xc4a [(5,17,29,7),(11,23,37,13),(3,19,31,19),(13,27,39,23)]
#       with (a,b) replaced by close pairs.
XC_SCHED4B = [(1, 2, 29, 7), (7, 8, 37, 13), (3, 4, 31, 19), (13, 14, 39, 23)]
# xc4c: fully alternative schedule, close pairs throughout.
XC_SCHED4C = [(2, 3, 17, 11), (9, 10, 25, 5), (4, 6, 41, 17), (15, 16, 33, 29)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _xc(x, k, sched):
    t_prev = np.uint64(0)
    if not np.ndim(x) == 0:
        t_prev = np.zeros_like(x)
    for j, s in enumerate(sched):
        a, b, c, rot = s
        t = _rotl64(x, a) & _rotl64(x, b)
        x = (x ^ t ^ _rotl64(x, c) ^ _rk(k, j) ^ _rotl64(t_prev, rot)) & M64
        t_prev = t
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_xc4b(v, k):
    """4-stage cross-coupled, close AND pairs, xc4a's (c,s). Re-test."""
    x = (v ^ k) & M64
    return _xc(x, k, XC_SCHED4B)


def t6_xc4c(v, k):
    """4-stage cross-coupled, close AND pairs, alternative schedule."""
    x = (v ^ k) & M64
    return _xc(x, k, XC_SCHED4C)


CANDIDATES_B25 = {
    "t6_xc4b": (t6_xc4b, "4-stage cross-coupled, close AND pairs (xc4a schedule fix)"),
    "t6_xc4c": (t6_xc4c, "4-stage cross-coupled, close AND pairs, alt schedule"),
}
