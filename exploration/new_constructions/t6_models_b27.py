"""Track 6, batch 27: dual-AND cascade (2 ANDs, 3-input XOR).

Batch 26's twin-AND (21.6u) was killed by the 5-input XOR tree (5.4u/stage).
This batch drops the `re` linear term: `x ^= (ra&rb)^(rc&rd)^rk` = 2 ANDs
with a 3-input XOR (2 levels, same as baseline). If Yosys holds the XOR
tree at 2 levels, this is ~3.5u/stage with 2x the ANDs.

Hypothesis: the 5-stage DIFF wall is about total AND count, not stage count.
  5 stages x 2 ANDs = 10 ANDs (vs 6 in al_and6a). Target ~17.5u.
  4 stages x 2 ANDs = 8 ANDs. Target ~14u. Tests the 4-stage wall with
  2x density.

Bijectivity: `x ^= N(x)^c` (track convention).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _u64(hi, lo):
    return (np.uint64(hi) << np.uint64(32)) | np.uint64(lo)
RC64 = [_u64(0x9E3779B9, 0x7F4A7C15), _u64(0x3C6EF372, 0xFE94F82A),
        _u64(0xDAA66D2C, 0x7DDF743F), _u64(0x78DDE6E5, 0xFD29F054),
        _u64(0x2545F491, 0x4F6CDD1D), _u64(0x9E3779B9, 0x7F4A7C15) ^ np.uint64(0xDEADBEEF),
        _u64(0x3C6EF372, 0xFE94F82A) ^ np.uint64(0x12345678),
        _u64(0xDAA66D2C, 0xDD6129B3E)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


# (a,b) and (c,d) close pairs (|.|<=2). 64-bit rotations.
DUAL5_SCHED_A = [(1, 2, 9, 10), (13, 14, 21, 22), (5, 6, 29, 30),
                 (17, 18, 37, 38), (25, 26, 45, 46)]
DUAL5_SCHED_B = [(3, 4, 11, 12), (7, 8, 33, 34), (15, 16, 41, 42),
                 (19, 20, 49, 50), (27, 28, 53, 54)]
DUAL4_SCHED = [(1, 2, 9, 10), (13, 14, 21, 22), (5, 6, 29, 30), (17, 18, 37, 38)]


def _dual(x, k, sched):
    for j, (a, b, c, d) in enumerate(sched):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b))
             ^ (_rotl64(x, c) & _rotl64(x, d)) ^ _rk(k, j)) & M64
    return (x ^ _rotl64(k, 13)) & M64


def t6_dual5a(v, k):
    """5-stage dual-AND, schedule A."""
    return _dual((v ^ k) & M64, k, DUAL5_SCHED_A)


def t6_dual5b(v, k):
    """5-stage dual-AND, schedule B (robustness)."""
    return _dual((v ^ k) & M64, k, DUAL5_SCHED_B)


def t6_dual4a(v, k):
    """4-stage dual-AND (4-stage wall test with 2x density)."""
    return _dual((v ^ k) & M64, k, DUAL4_SCHED)


CANDIDATES_B27 = {
    "t6_dual5a": (t6_dual5a, "5-stage dual-AND (ra&rb)^(rc&rd)^rk, sched A"),
    "t6_dual5b": (t6_dual5b, "5-stage dual-AND, sched B"),
    "t6_dual4a": (t6_dual4a, "4-stage dual-AND (density vs 4-stage wall)"),
}
