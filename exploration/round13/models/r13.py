"""Round 13 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round13/gen_r13.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Round 13 attacks genuinely new F diffusion/topologies (S-box swap, rotation
pairs, 5r, 3-rot linear, partial-S-box, whitening all exhausted in r8-r12):
  F1: 4r Feistel, DOUBLE-STRENGTH F = lin(S1(lin(S1(R^rkA))^rkB)), 2 keys/round
      (rkA=RK32(key,2i-1), rkB=RK32(key,2i)), (3,11) and (7,13).
      Hypothesis: stronger F crosses the 4r barrier inside ~41u.
  F2: chi32 nonlinear layer: b_i = a_i ^ (~a_{i+1} & a_{i+2}) (degree 2,
      ~3-gate boolean depth, much cheaper than the S1 DNF layer),
      F = lin(3,11)(chi32(R)) ^ rk at 5/6/8 rounds.
  F3: chi->S1 hybrid F = lin(3,11)(S1(chi32(R))) ^ rk, 6r.
  F4: heterogeneous rounds: alt (odd rounds S1-F, even rounds chi-F) and
      s1x3/chix3 (first 3 rounds S1-F, last 3 chi-F), 6r.
  F5: Lai-Massey with orthomorphism sigma(L,R) = (R, L^R):
      t = lin(3,11)(S1(L^R))^rk; L' = R^t; R' = L^R. Bijective for fixed key.
      4r and 6r. (The naive form L'=R^t, R'=L^t leaves D = L^R invariant and
      degenerates to a single F layer -- caught by S0 in r13.)
  F6: key-schedule variants on the r9 structure:
        midk: F = lin(3,11)(S1(R) ^ rk)  (key between S-box and linear);
        rkhi: F = lin(3,11)(S1(R)) ^ rk with rk = high32(RK64) on odd rounds,
              low32(RK64) on even rounds (rotating key-half selection).
  F7: sandwich F = lin(3,11)(S1(lin(3,11)(R))) ^ rk, 6r (diffusion before
      AND after the S-box).
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)  # THF/Blink (r7-r13)

MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)


def _rotl32_np(x, r):
    r %= 32
    if r == 0:
        return x & MASK32
    return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & MASK32


def _rotr32_np(x, r):
    return _rotl32_np(x, (-r) % 32)


def _rotl64_np(x, r):
    r %= 64
    if r == 0:
        return x & MASK64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64


def _sbox_layer32_np(x):
    """Eight 4-bit S1 S-boxes over the 32-bit word."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1, nib) << np.uint64(4 * i)
    return out & MASK32


def _chi32_np(x):
    """32-bit Keccak-style chi: b_i = a_i ^ (~a_{i+1} & a_{i+2}).
    NOTE: chi over an EVEN word size is not a permutation (Daemen: invertible
    iff width odd). That is fine here -- a Feistel F need not be invertible;
    statistical quality is judged by the battery, not by F bijectivity."""
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 1)) & _rotr32_np(x, 2))) & MASK32


def _lin_ab_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _rk64_std_np(k, i):
    """Full 64-bit affine schedule value (1-based i)."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK64


def _rk32_std_np(k, i):
    """Affine schedule (r7/r8/r9): low32 of _rk64_std_np."""
    return _rk64_std_np(k, i) & MASK32


def _rk32_hi_lo_np(k, i):
    """Rotating key-half: high32 on odd rounds, low32 on even rounds."""
    rkv = _rk64_std_np(k, i)
    if i & 1:
        return (rkv >> np.uint64(32)) & MASK32
    return rkv & MASK32


# ---------------- F functions ----------------
def _F_s1_311(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R), 3, 11) ^ rk32) & MASK32


def _F_s1_713(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R), 7, 13) ^ rk32) & MASK32


def _F_chi_311(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 3, 11) ^ rk32) & MASK32


def _F_chis1_311(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(_chi32_np(R)), 3, 11) ^ rk32) & MASK32


def _F_s1x2_311(R, rkA, rkB):
    t = _sbox_layer32_np(R ^ rkA)
    t = _lin_ab_np(t, 3, 11) ^ rkB
    t = _sbox_layer32_np(t)
    return _lin_ab_np(t, 3, 11) & MASK32


def _F_s1x2_713(R, rkA, rkB):
    t = _sbox_layer32_np(R ^ rkA)
    t = _lin_ab_np(t, 7, 13) ^ rkB
    t = _sbox_layer32_np(t)
    return _lin_ab_np(t, 7, 13) & MASK32


def _F_sandw_311(R, rk32):
    t = _lin_ab_np(R, 3, 11)
    t = _sbox_layer32_np(t)
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_midk_311(R, rk32):
    return _lin_ab_np(_sbox_layer32_np(R) ^ rk32, 3, 11) & MASK32


# ---------------- main loops ----------------
def _feistel_nw_np(x, k, rounds, F):
    """Balanced Feistel, 32-bit halves, {R,L} output, no whitening."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_2k_np(x, k, rounds, F):
    """Feistel with two round keys per round (F1)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ F(R, _rk32_std_np(k, 2 * i - 1),
                    _rk32_std_np(k, 2 * i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_alt_np(x, k, rounds):
    """Heterogeneous: odd rounds S1-F, even rounds chi-F."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = _F_s1_311 if (i & 1) else _F_chi_311
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_s1x3_np(x, k, rounds):
    """Heterogeneous: first 3 rounds S1-F, rest chi-F."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = _F_s1_311 if i <= 3 else _F_chi_311
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_rkhi_np(x, k, rounds):
    """Feistel with rotating key-half schedule."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ _F_s1_311(R, _rk32_hi_lo_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _lai_massey_np(x, k, rounds):
    """Lai-Massey with orthomorphism sigma(L,R) = (R, L^R):
    t = F(L^R)^rk; L' = R^t; R' = L^R.
    Bijective for fixed key: R' = D recovers t = F(R')^rk, then R = L'^t,
    L = R'^R. The orthomorphism is ESSENTIAL: without it (L'=R^t, R'=L^t)
    the difference D = L^R is invariant across rounds and all rounds apply F
    to the same input -- a degenerate single-F-layer design (caught in r13
    when S0 reported 5.5u/578 cells for the 4-round version)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        t = _F_s1_311(L ^ R, _rk32_std_np(k, i))
        L, R = (R ^ t) & MASK32, (L ^ R) & MASK32
    return ((R << np.uint64(32)) | L) & MASK64


def _mk(name, fn):
    fn.__name__ = name
    return fn


# F1: 4r double-strength F
r13_feist4_s1x2_311_nw = _mk(
    "r13_feist4_s1x2_311_nw",
    lambda v, k: _feistel_nw_2k_np(v, k, 4, _F_s1x2_311))
r13_feist4_s1x2_713_nw = _mk(
    "r13_feist4_s1x2_713_nw",
    lambda v, k: _feistel_nw_2k_np(v, k, 4, _F_s1x2_713))

# F2: chi F at 5/6/8 rounds
r13_feist5_chi311_nw = _mk(
    "r13_feist5_chi311_nw",
    lambda v, k: _feistel_nw_np(v, k, 5, _F_chi_311))
r13_feist6_chi311_nw = _mk(
    "r13_feist6_chi311_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_chi_311))
r13_feist8_chi311_nw = _mk(
    "r13_feist8_chi311_nw",
    lambda v, k: _feistel_nw_np(v, k, 8, _F_chi_311))

# F3: chi->S1 hybrid, 6r
r13_feist6_chis1_311_nw = _mk(
    "r13_feist6_chis1_311_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_chis1_311))

# F4: heterogeneous, 6r
r13_feist6_alt_s1chi_nw = _mk(
    "r13_feist6_alt_s1chi_nw",
    lambda v, k: _feistel_nw_alt_np(v, k, 6))
r13_feist6_s1x3_chix3_nw = _mk(
    "r13_feist6_s1x3_chix3_nw",
    lambda v, k: _feistel_nw_s1x3_np(v, k, 6))

# F5: Lai-Massey with S1 F, 4r/6r
r13_lm4_s1_311_nw = _mk(
    "r13_lm4_s1_311_nw",
    lambda v, k: _lai_massey_np(v, k, 4))
r13_lm6_s1_311_nw = _mk(
    "r13_lm6_s1_311_nw",
    lambda v, k: _lai_massey_np(v, k, 6))

# F6: key-schedule variants on the r9 structure
r13_feist6_s1_midk311_nw = _mk(
    "r13_feist6_s1_midk311_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_midk_311))
r13_feist6_s1_rkhi311_nw = _mk(
    "r13_feist6_s1_rkhi311_nw",
    lambda v, k: _feistel_nw_rkhi_np(v, k, 6))

# F7: sandwich, 6r
r13_feist6_sandw311_nw = _mk(
    "r13_feist6_sandw311_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_sandw_311))

ALL = [
    r13_feist4_s1x2_311_nw, r13_feist4_s1x2_713_nw,
    r13_feist5_chi311_nw, r13_feist6_chi311_nw, r13_feist8_chi311_nw,
    r13_feist6_chis1_311_nw,
    r13_feist6_alt_s1chi_nw, r13_feist6_s1x3_chix3_nw,
    r13_lm4_s1_311_nw, r13_lm6_s1_311_nw,
    r13_feist6_s1_midk311_nw, r13_feist6_s1_rkhi311_nw,
    r13_feist6_sandw311_nw,
]
