"""Track 6, batch 28: wide-AND cascade (AND3/AND4 single-cell stages).

Batch-23's lemma ("you cannot buy more nonlinearity per gate-level than one
2-input AND") was about CASCADED products: (p1&~p2) is a SECOND AND level.
But the S0 genlib has AND3 (delay 1.7) and AND4 (delay 1.9) as SINGLE cells:
a 3-input product is one gate level with 2 AND-bits of nonlinearity, one
4-input product is one gate level with 3 AND-bits. Batch 23 never tested
wide cells -- this axis exploits them.

Hypothesis: the 4-stage DIFF wall is about NONLINEAR ORDER per stage, not
AND-bit count. dual4a failed with 8 AND-bits of order 2. A 4-stage AND3 has
8 AND-bits of order 3; a 4-stage AND4 has 12 AND-bits of order 4.
  - t6_and3_5a: 5 stages x AND3 (order 3). Est ~3.55u/stage -> ~17.8u.
  - t6_and3_5b: same, alt schedule (robustness).
  - t6_and3_4a: 4 stages x AND3 -- order-3 test of the 4-stage wall.
  - t6_and4_5a: 5 stages x AND4 (order 4, density 1/16 -- probe of
    order-vs-density tradeoff).

SEQ-co-design (standing lesson): all AND operands within |d|<=3 of each
other, so the term is non-vanishing on sequential low-entropy inputs.
Stage: x ^= (ra&rb&rc) ^ rk -- same 2-level XOR combine as baseline.
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


# AND3 triplets: |d|<=2 within triplet.
AND3_5A = [(1, 2, 3), (13, 14, 15), (5, 6, 7), (17, 18, 19), (25, 26, 27)]
AND3_5B = [(3, 4, 5), (11, 12, 13), (7, 8, 9), (21, 22, 23), (29, 30, 31)]
AND3_4A = [(1, 2, 3), (13, 14, 15), (5, 6, 7), (17, 18, 19)]
# AND4 quadruples: |d|<=3 within quadruple.
AND4_5A = [(1, 2, 3, 4), (11, 12, 13, 14), (21, 22, 23, 24),
           (31, 32, 33, 34), (41, 42, 43, 44)]


def _wide(x, k, sched):
    for j, ops in enumerate(sched):
        t = _rotl64(x, ops[0])
        for a in ops[1:]:
            t = t & _rotl64(x, a)
        x = (x ^ t ^ _rk(k, j)) & M64
    return (x ^ _rotl64(k, 13)) & M64


def t6_and3_5a(v, k):
    """5-stage AND3 cascade, schedule A."""
    return _wide((v ^ k) & M64, k, AND3_5A)


def t6_and3_5b(v, k):
    """5-stage AND3 cascade, schedule B (robustness)."""
    return _wide((v ^ k) & M64, k, AND3_5B)


def t6_and3_4a(v, k):
    """4-stage AND3 cascade (order-3 vs 4-stage DIFF wall)."""
    return _wide((v ^ k) & M64, k, AND3_4A)


def t6_and4_5a(v, k):
    """5-stage AND4 cascade (order-4, density 1/16 probe)."""
    return _wide((v ^ k) & M64, k, AND4_5A)


CANDIDATES_B28 = {
    "t6_and3_5a": (t6_and3_5a, "5-stage AND3 cascade (ra&rb&rc)^rk, sched A"),
    "t6_and3_5b": (t6_and3_5b, "5-stage AND3 cascade, sched B"),
    "t6_and3_4a": (t6_and3_4a, "4-stage AND3 cascade (order-3 wall test)"),
    "t6_and4_5a": (t6_and4_5a, "5-stage AND4 cascade (order-4 density probe)"),
}
