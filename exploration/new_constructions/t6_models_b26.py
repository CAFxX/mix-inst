"""Track 6, batch 26: three genuinely new axes (cross-coupling dead after batch 25).

Prong B: t6_andchi5a — 4x AND-cascade stages + chi substitution layer.
          New PRIMITIVE COMBO: algebraic nonlinearity (Keccak chi, no tables)
          instead of table S-box. Tests whether chi fixes the 5-stage wall
          like the S-box did for hyb12_asb5a.
Prong C: t6_split6a — split parallel 32-bit AND-cascade (3+3 stages) with
          bijective cross. New TOPOLOGY: parallelism + cross coupling
          instead of a single 64-bit cascade.
Prong D: t6_twin4a — 4-stage twin-AND `x ^= (ra&rb)^(rc&rd)^re^rk`.
          Tests the DENSITY hypothesis: is the 4-stage wall about stage
          count or total AND count? 8 ANDs in 4 stages, ~17u target.

KILLED IN TRIAGE (not promoted to S0):
  2-round Feistel (F=3-stage 32-bit AND): avg 24.1, dev 8.85 — 2 rounds
    cannot saturate diffusion; a strong-enough F makes 2 rounds too slow.
    Structural tension, scoped kill.
  2-round 4-bit SPN (Midori Sb0): avg 1.9 (nibble P-box) / 2.8 (bit P-box)
    — 2 rounds structurally incapable of avalanche (max ~8 bits flip).
    Scoped kill: 2-round 4-bit SPN.

Bijectivity:
  B: AND stages are `x ^= N(x)^c` (track convention); chi layer is
     `x = chi(rot(x))^rk` with chi a permutation -> bijective.
  C: 32-bit stages `x ^= N(x)^c`; cross (hi,lo)->(hi^lo,lo^rot(hi,7))
     is bijective (each step invertible). Empirically verified (200k, 0 coll).
  D: `x ^= N(x)^c` (track convention).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
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


def _rotl32(x, r):
    r %= 32
    if r == 0:
        return x & M32
    return (((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32)


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


# --- Prong A: 2-round Feistel ---------------------------------------------
# F32: 3-stage 32-bit AND-cascade. Close pairs (|a-b|<=2), 32-bit rotations.
F32_SCHED = [(1, 2, 9), (5, 6, 17), (3, 4, 25)]


def _f32(y, k, jbase):
    x = y & M32
    for j, (a, b, c) in enumerate(F32_SCHED):
        rkj = np.uint64(_rk(k, jbase + j) & M32)
        x = (x ^ (_rotl32(x, a) & _rotl32(x, b)) ^ _rotl32(x, c) ^ rkj) & M32
    return x


def t6_feist2a(v, k):
    """2-round Feistel, 32-bit halves, F=3-stage 32-bit AND-cascade."""
    x = (v ^ k) & M64
    hi = (x >> np.uint64(32)) & M32
    lo = x & M32
    hi = (hi ^ _f32(lo, k, 0)) & M32
    lo = (lo ^ _f32(hi, k, 3)) & M32
    x = ((hi << np.uint64(32)) | lo) & M64
    return (x ^ _rotl64(k, 13)) & M64


# --- Prong B: AND-cascade + chi layer --------------------------------------
# 4 AND stages (close pairs), then chi substitution layer.
AND4_SCHED = [(1, 2, 11), (7, 8, 23), (3, 4, 37), (13, 14, 51)]
CHI_ROTS = (0, 11, 23)


def _chi_layer(x, k, j):
    a, b, c = CHI_ROTS
    p = _rotl64(x, a)
    q = _rotl64(x, b)
    r = _rotl64(x, c)
    # chi(p,q,r)[i] = p[i] ^ ((~q[i]) & r[i]); chi is a permutation
    return ((p ^ ((~q) & r)) & M64 ^ _rk(k, j)) & M64


def t6_andchi5a(v, k):
    """4x AND-cascade + chi substitution layer."""
    x = (v ^ k) & M64
    for j, (a, b, c) in enumerate(AND4_SCHED):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c)
             ^ _rk(k, j)) & M64
    x = _chi_layer(x, k, 4)
    return (x ^ _rotl64(k, 13)) & M64


# --- Prong C: split parallel 32-bit cascade with bijective cross ------------
# Two independent 32-bit AND-cascades (3 stages each), coupled by a
# bijective cross step. New TOPOLOGY: parallelism + cross instead of
# a single 64-bit cascade.
# Bijectivity: 32-bit stages are `x ^= N(x)^c` (track convention);
# cross is (hi,lo)->(hi^lo,lo)->(hi,lo^rot(hi,7)), each step bijective.
SPLIT32_SCHED = [(1, 2, 9), (5, 6, 17), (3, 4, 25)]


def _casc32(x, k, jbase):
    for j, (a, b, c) in enumerate(SPLIT32_SCHED):
        rkj = np.uint64(_rk(k, jbase + j) & M32)
        x = (x ^ (_rotl32(x, a) & _rotl32(x, b)) ^ _rotl32(x, c) ^ rkj) & M32
    return x


def t6_split6a(v, k):
    """Split 32-bit parallel AND-cascade (3+3 stages) with bijective cross."""
    x = (v ^ k) & M64
    hi = (x >> np.uint64(32)) & M32
    lo = x & M32
    hi = _casc32(hi, k, 0)
    lo = _casc32(lo, k, 3)
    # bijective cross: (hi,lo) -> (hi^lo, lo) -> (hi, lo^rot(hi,7))
    hi = (hi ^ lo) & M32
    lo = (lo ^ _rotl32(hi, 7)) & M32
    hi = _casc32(hi, k, 6)
    lo = _casc32(lo, k, 9)
    x = ((hi << np.uint64(32)) | lo) & M64
    return (x ^ _rotl64(k, 13)) & M64


# --- Prong D: 4-stage twin-AND ----------------------------------------------
# (a,b) and (c,d) close pairs; e is the linear term.
TWIN4_SCHED = [(1, 2, 5, 6, 19), (9, 10, 13, 14, 33),
               (3, 4, 17, 18, 45), (7, 8, 21, 22, 55)]


def t6_twin4a(v, k):
    """4-stage twin-AND: x ^= (ra&rb)^(rc&rd)^re^rk."""
    x = (v ^ k) & M64
    for j, (a, b, c, d, e) in enumerate(TWIN4_SCHED):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b))
             ^ (_rotl64(x, c) & _rotl64(x, d))
             ^ _rotl64(x, e) ^ _rk(k, j)) & M64
    return (x ^ _rotl64(k, 13)) & M64


CANDIDATES_B26 = {
    "t6_andchi5a": (t6_andchi5a, "4x AND-cascade + chi substitution layer"),
    "t6_split6a": (t6_split6a, "Split 32-bit parallel cascade (3+3) + bijective cross"),
    "t6_twin4a": (t6_twin4a, "4-stage twin-AND (density hypothesis)"),
}
