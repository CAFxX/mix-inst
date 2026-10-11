"""Track 6, batch 19: parallel dual-cascade + AND-combine (new axis).

Batch 18 proved S-box+P-box needs ~10 rounds at 4u/round (40u) — dead.
New idea: TWO INDEPENDENT 5-stage AND-cascades in PARALLEL, then combined
with a nonlinear combine. Total AND-depths = 5 (per cascade) + 1 (combine)
= 6, but SEQUENTIAL stages = 5 + combine.

  a = rs1; 5x [a ^= (ra&rb)^rc^rkA]   (keyed by rs2)
  b = rs2; 5x [b ^= (ra&rb)^rc^rkB]   (keyed by rs1)   [parallel with a]
  out = a ^ b ^ (a & b) ^ rkC

Latency: max(5-stage, 5-stage) + combine = ~16.75u + ~2u = ~18.75u < 20.1u.
A differential trail through input rs1 sees 5 sequential ANDs (cascade A)
then the combine AND = 6 AND-depths sequentially. LIN-safety from per-stage
rc terms in both cascades.

Candidates:
  t6_par5a: as above, schedule A.
  t6_par5b: alt schedules.

rkA_j = rotl64(rs2,13*(j+1)) ^ RC[j%8]; rkB_j = rotl64(rs1,13*(j+1)) ^ RC[j%8];
rkC = rotl64(rs1^rs2, 77) ^ RC[7].
Post-whiten out ^= rotl64(rs1^rs2,13) >> 32.
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _cascade(x, key, sched):
    for j, (a, b, c) in enumerate(sched):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c) ^
             _rk(key, j)) & M64
    return x


SCHED_A = [(3, 11, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59), (13, 37, 53)]
SCHED_B = [(5, 13, 29), (19, 31, 43), (11, 23, 47), (29, 41, 61), (7, 17, 53)]


def _par5(v, k, sched):
    # v=rs1, k=rs2; a keyed by rs2, b keyed by rs1 (cross-keyed)
    a = _cascade(v, k, sched)
    b = _cascade(k, v, sched)
    rkC = (_rotl64(v ^ k, 77) ^ RC64[7]) & M64
    out = (a ^ b ^ (a & b) ^ rkC) & M64
    return (out ^ (_rotl64(v ^ k, 13) >> np.uint64(32))) & M64


def t6_par5a(v, k):
    """Parallel dual 5-stage cascade + AND-combine, schedule A."""
    return _par5(v, k, SCHED_A)


def t6_par5b(v, k):
    """Parallel dual 5-stage cascade + AND-combine, schedule B."""
    return _par5(v, k, SCHED_B)


CANDIDATES_B19 = {
    "t6_par5a": (t6_par5a, "parallel dual 5-stage cascade + AND-combine, A"),
    "t6_par5b": (t6_par5b, "parallel dual 5-stage cascade + AND-combine, B"),
}
