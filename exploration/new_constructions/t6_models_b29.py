"""Track 6, batch 29: wide-AND + spread rotation (co-designed).

Batch 28 (pure narrow-triplet AND3/AND4) triage-KILLED: avalanche 4.8-8.9.
Root cause: close AND operands (needed for SEQ-safety) LOCALIZE differences
-- a 1-bit flip perturbs only ~3 adjacent term bits per stage, and the
sparse term (1/8, 1/16) rarely converts them. The frontier's answer
(al_and6a's (a,b,c) triplets) is a co-design: CLOSE nonlinear pair +
WIDE linear rotation spreader. The rotation is a permutation -- it never
vanishes on SEQ inputs -- and it re-spreads differences every stage.

This batch: x ^= (ra&rb&rc) ^ rot(x,d) ^ rk  (AND3 + spread)
           x ^= (ra&rb&rc&rd) ^ rot(x,e) ^ rk (AND4 + spread)
4-operand XOR tree = 2 XOR2 levels, same as the frontier stage.
AND3 costs +0.2u/stage vs AND2 (1.7 vs 1.5); AND4 +0.4u (1.9 vs 1.5).

  - t6_wand3_5a: 5 stages AND3+spread. Est ~3.55u/stage -> ~17.8u.
  - t6_wand3_5b: alt schedule (robustness).
  - t6_wand3_4a: 4 stages AND3+spread -- order-3 test of the 4-stage wall.
  - t6_wand4_5a: 5 stages AND4+spread -- order-4 density probe.

SEQ-co-design: AND operands within |d|<=3 (non-vanishing term); spread
rotation d is a permutation (SEQ-immune by construction).
Bijectivity: x ^= N(x)^c (track convention).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _u64(hi, lo):
    return (np.uint64(hi) << np.uint64(32)) | np.uint64(lo)
RC64 = [_u64(0x9E3779B9, 0x7F4A7C15), _u64(0x3C6EF372, 0xFE94F82A),
        _u64(0xDAA66D2C, 0x7DDF743F), _u64(0x78DDE6E5, 0xFD29F054),
        _u64(0x2545F491, 0x4F6CDD1D),
        _u64(0x9E3779B9, 0x7F4A7C15) ^ np.uint64(0xDEADBEEF),
        _u64(0x3C6EF372, 0xFE94F82A) ^ np.uint64(0x12345678),
        _u64(0xDAA66D2C, 0xDD6129B3E)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


# entries: (and_operands_tuple, spread_rotation)
WAND3_5A = [((1, 2, 3), 13), ((11, 12, 13), 5), ((5, 6, 7), 29),
            ((17, 18, 19), 7), ((25, 26, 27), 37)]
WAND3_5B = [((3, 4, 5), 23), ((13, 14, 15), 41), ((7, 8, 9), 17),
            ((21, 22, 23), 11), ((29, 30, 31), 43)]
WAND3_4A = [((1, 2, 3), 13), ((11, 12, 13), 5), ((5, 6, 7), 29),
            ((17, 18, 19), 7)]
WAND4_5A = [((1, 2, 3, 4), 13), ((11, 12, 13, 14), 29), ((21, 22, 23, 24), 7),
            ((31, 32, 33, 34), 37), ((41, 42, 43, 44), 17)]


def _wide(x, k, sched):
    for j, (ops, d) in enumerate(sched):
        t = _rotl64(x, ops[0])
        for a in ops[1:]:
            t = t & _rotl64(x, a)
        x = (x ^ t ^ _rotl64(x, d) ^ _rk(k, j)) & M64
    return (x ^ _rotl64(k, 13)) & M64


def t6_wand3_5a(v, k):
    """5-stage AND3 + spread rotation, schedule A."""
    return _wide((v ^ k) & M64, k, WAND3_5A)


def t6_wand3_5b(v, k):
    """5-stage AND3 + spread rotation, schedule B (robustness)."""
    return _wide((v ^ k) & M64, k, WAND3_5B)


def t6_wand3_4a(v, k):
    """4-stage AND3 + spread (order-3 vs 4-stage DIFF wall)."""
    return _wide((v ^ k) & M64, k, WAND3_4A)


def t6_wand4_5a(v, k):
    """5-stage AND4 + spread (order-4 density probe)."""
    return _wide((v ^ k) & M64, k, WAND4_5A)


CANDIDATES_B29 = {
    "t6_wand3_5a": (t6_wand3_5a, "5-stage AND3+spread (ra&rb&rc)^rot(x,d)^rk, sched A"),
    "t6_wand3_5b": (t6_wand3_5b, "5-stage AND3+spread, sched B"),
    "t6_wand3_4a": (t6_wand3_4a, "4-stage AND3+spread (order-3 wall test)"),
    "t6_wand4_5a": (t6_wand4_5a, "5-stage AND4+spread (order-4 density probe)"),
}
