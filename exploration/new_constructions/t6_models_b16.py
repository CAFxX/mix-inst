"""Track 6, batch 16: co-designed hybrid 5-stage (new axis).

Batch 15 closed the no-rc family CATASTROPHICALLY (norc5a: LIN 10/10 with
D=4096/4096 on all keys — the linear rc term is load-bearing for LIN, not
just DIFF). So every stage needs `x ^= NONLIN ^ LIN ^ rk`.

The 20.1u barrier = 6 stages x 3.35u. 5 stages always die at DIFF.
Hypothesis H16: a 5-stage construction can match 6-stage differential
strength if one stage is DUAL-AND. Differential trail probability through
4 single-AND + 1 dual-AND stages ~= p^4 * p^2 = p^6 (dual-AND kills trails
like two singles), but latency is 4*3.35 + ~4 = ~17.4u < 20.1u.

The dual stage OMITS the `re` linear term (saves an XOR level, ~4u vs 5.4u);
LIN-safety comes from the 4 single stages (which retain rc). A with-re
control (t6_hyb5d) tests whether the re-less dual stage breaks LIN.

Candidates (all x = val ^ key; rk_j = rotl64(key,13*(j+1)) ^ RC64[j%8];
post-whiten x ^= rotl64(key,13) >> 32):
  t6_hyb5a: 4x [`x ^= (ra&rb)^rc^rk`] + 1x [`x ^= (ra&rb)^(rc&rd)^rk`]
            (dual LAST, no re). Est ~17.4u.
  t6_hyb5b: 1x dual (no re) FIRST + 4x single. (Position sensitivity.)
  t6_hyb5c: 3x single + 2x dual (no re). Est ~18u. (More ANDs.)
  t6_hyb5d: 4x single + 1x dual WITH re [`^re^rk`]. Est ~18.8u.
            (LIN-safety control for the re-less dual stage.)
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


def _postwhite(x, k):
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


# Rotation schedules: singles use (a,b,c); duals use (a,b,c,d[,e]).
# All rotations within a stage distinct; well-spread across stages.
SINGLE_SCHED = [(3, 11, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59),
                (13, 37, 53), (5, 19, 61)]
DUAL_SCHED = [(3, 11, 23, 37), (17, 29, 41, 53),
              (7, 31, 47, 59), (23, 43, 5, 61)]
DUALRE_SCHED = [(3, 11, 23, 37, 53), (17, 29, 41, 53, 7)]


def _single(x, k, j, sched):
    a, b, c = sched
    return (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c) ^ _rk(k, j)) & M64


def _dual(x, k, j, sched):
    a, b, c, d = sched
    return (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^
            (_rotl64(x, c) & _rotl64(x, d)) ^ _rk(k, j)) & M64


def _dualre(x, k, j, sched):
    a, b, c, d, e = sched
    return (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^
            (_rotl64(x, c) & _rotl64(x, d)) ^ _rotl64(x, e) ^ _rk(k, j)) & M64


def t6_hyb5a(v, k):
    """4 singles + dual (no re) LAST."""
    x = v ^ k
    for j in range(4):
        x = _single(x, k, j, SINGLE_SCHED[j])
    x = _dual(x, k, 4, DUAL_SCHED[0])
    return _postwhite(x, k)


def t6_hyb5b(v, k):
    """Dual (no re) FIRST + 4 singles."""
    x = v ^ k
    x = _dual(x, k, 0, DUAL_SCHED[1])
    for j in range(4):
        x = _single(x, k, j + 1, SINGLE_SCHED[j])
    return _postwhite(x, k)


def t6_hyb5c(v, k):
    """3 singles + 2 duals (no re)."""
    x = v ^ k
    for j in range(3):
        x = _single(x, k, j, SINGLE_SCHED[j])
    x = _dual(x, k, 3, DUAL_SCHED[2])
    x = _dual(x, k, 4, DUAL_SCHED[3])
    return _postwhite(x, k)


def t6_hyb5d(v, k):
    """4 singles + dual WITH re (LIN-safety control)."""
    x = v ^ k
    for j in range(4):
        x = _single(x, k, j, SINGLE_SCHED[j])
    x = _dualre(x, k, 4, DUALRE_SCHED[0])
    return _postwhite(x, k)


CANDIDATES_B16 = {
    "t6_hyb5a": (t6_hyb5a, "4 singles + dual-AND (no re) last"),
    "t6_hyb5b": (t6_hyb5b, "dual-AND (no re) first + 4 singles"),
    "t6_hyb5c": (t6_hyb5c, "3 singles + 2 dual-AND (no re)"),
    "t6_hyb5d": (t6_hyb5d, "4 singles + dual-AND with re (control)"),
}
