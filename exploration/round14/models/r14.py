"""Round 14 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round14/gen_r14.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).
All r14 designs are Feistel-based, so fixed-key bijectivity holds regardless
of F (invertible final diffusion in F5 verified separately).

Round 14 exploits the r13 heterogeneity breakthrough (alt S1/chi = new speed
point 40.1u):
  F1: alt variants (6r) -
      alt_rev: round order reversed (odd rounds chi-F, even rounds S1-F)
      alt713: alt with (7,13) rotmix on both S1 and chi rounds
      alt_chinolin: alt, but chi-F = chi32(R) ^ rk (NO rotmix on chi rounds)
      alt_chioff: alt with chi offsets (i+2,i+3):
                  b_i = a_i ^ (~a_{i+2} & a_{i+3})
      alt_rkhi: alt; S1 rounds (odd) use standard rk, chi rounds (even) use
                the rotating key-half (high32 RK64 on even rounds, low32 odd)
  F2: 4r lighter-strong-F probes -
      chis1l4: F = lin(3,11)(chi32(S1(R ^ rk))) (single key), 4r
      pars1chi: F = lin(3,11)(S1(R ^ rk)) ^ lin(3,11)(chi32(R))
                (parallel S1+chi paths XORed), 4r
  F3: 5r double-strength-F: F = lin(S1(lin(S1(R^rkA))^rkB)), 2 keys/round,
      (3,11), 5 rounds. Closes the round-strength question; S1 verdict first,
      full battery only if not dominated.
  F4: 6r heterogeneous placement -
      chi25: chi-F on rounds {2,5}, S1-F elsewhere
      chi16: chi-F on rounds {1,6}, S1-F elsewhere
  F5: r9 structure + cheap invertible 64-bit final diffusion:
      out = W ^ rotl64(W,a) ^ rotl64(W,b), W = {R,L}.
      Linear operator p(t) = 1 + t^a + t^b with p(1) = 1+1+1 = 1 (mod 2);
      coprime with (t+1)^64 = t^64+1, hence a permutation of GF(2)^64.
      (Note: a SINGLE-term out ^= rotl64(out,r) is NOT bijective -- kernel =
      r-periodic vectors -- so single-term output diffusion is excluded.)
  F6: s1chi: 6r, F = lin(3,11)(chi32(S1(R))) ^ rk (reverse of r13 chi->S1).
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)  # THF/Blink (r7-r14)

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
    """b_i = a_i ^ (~a_{i+1} & a_{i+2}). Even width -> not a permutation;
    fine, a Feistel F need not be invertible."""
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 1)) & _rotr32_np(x, 2))) & MASK32


def _chi32_off_np(x):
    """Chi with offsets (i+2,i+3): b_i = a_i ^ (~a_{i+2} & a_{i+3})."""
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 2)) & _rotr32_np(x, 3))) & MASK32


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


def _F_chi_713(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 7, 13) ^ rk32) & MASK32


def _F_chi_nolin(R, rk32):
    return (_chi32_np(R) ^ rk32) & MASK32


def _F_chi_off_311(R, rk32):
    return (_lin_ab_np(_chi32_off_np(R), 3, 11) ^ rk32) & MASK32


def _F_chis1l(R, rk32):
    return (_lin_ab_np(_chi32_np(_sbox_layer32_np(R ^ rk32)), 3, 11)
            ) & MASK32


def _F_s1chi_311(R, rk32):
    return (_lin_ab_np(_chi32_np(_sbox_layer32_np(R)), 3, 11) ^ rk32) & MASK32


def _F_pars1chi(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R ^ rk32), 3, 11) ^
            _lin_ab_np(_chi32_np(R), 3, 11)) & MASK32


def _F_s1x2_311(R, rkA, rkB):
    t = _sbox_layer32_np(R ^ rkA)
    t = _lin_ab_np(t, 3, 11) ^ rkB
    t = _sbox_layer32_np(t)
    return _lin_ab_np(t, 3, 11) & MASK32


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
    """Feistel with two round keys per round (F3)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ F(R, _rk32_std_np(k, 2 * i - 1),
                    _rk32_std_np(k, 2 * i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_alt_rev_np(x, k, rounds):
    """Heterogeneous reversed: odd rounds chi-F, even rounds S1-F."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = _F_chi_311 if (i & 1) else _F_s1_311
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_alt713_np(x, k, rounds):
    """Heterogeneous: odd rounds S1-F, even rounds chi-F, (7,13) rotmix."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = _F_s1_713 if (i & 1) else _F_chi_713
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_alt_chinolin_np(x, k, rounds):
    """Heterogeneous: odd rounds S1-F(lin 3,11); even rounds chi-F = chi ^ rk
    (no rotmix on chi rounds)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = _F_s1_311 if (i & 1) else _F_chi_nolin
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_alt_chioff_np(x, k, rounds):
    """Heterogeneous: odd rounds S1-F, even rounds chi-off-F (i+2,i+3)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = _F_s1_311 if (i & 1) else _F_chi_off_311
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_alt_rkhi_np(x, k, rounds):
    """Heterogeneous: odd rounds S1-F with standard rk; even rounds chi-F
    with the rotating key-half (high32 odd / low32 even, i.e. low32 on the
    even rounds used here)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        if i & 1:
            nR = (L ^ _F_s1_311(R, _rk32_std_np(k, i))) & MASK32
        else:
            nR = (L ^ _F_chi_311(R, _rk32_hi_lo_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_chiset_np(x, k, rounds, chiset):
    """Heterogeneous: chi-F on rounds in chiset (1-based), S1-F elsewhere."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = _F_chi_311 if i in chiset else _F_s1_311
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_nw_r9out_np(x, k, rounds, a, b):
    """r9 structure (6r S1-F lin(3,11), no whitening) + invertible 64-bit
    final diffusion out = W ^ rotl64(W,a) ^ rotl64(W,b)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ _F_s1_311(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    W = ((R << np.uint64(32)) | L) & MASK64
    return (W ^ _rotl64_np(W, a) ^ _rotl64_np(W, b)) & MASK64


def _mk(name, fn):
    fn.__name__ = name
    return fn


# F1: alt variants, 6r
r14_feist6_chi_s1alt_nw = _mk(
    "r14_feist6_chi_s1alt_nw",
    lambda v, k: _feistel_nw_alt_rev_np(v, k, 6))
r14_feist6_alt713_nw = _mk(
    "r14_feist6_alt713_nw",
    lambda v, k: _feistel_nw_alt713_np(v, k, 6))
r14_feist6_alt_chinolin_nw = _mk(
    "r14_feist6_alt_chinolin_nw",
    lambda v, k: _feistel_nw_alt_chinolin_np(v, k, 6))
r14_feist6_alt_chioff_nw = _mk(
    "r14_feist6_alt_chioff_nw",
    lambda v, k: _feistel_nw_alt_chioff_np(v, k, 6))
r14_feist6_alt_rkhi_nw = _mk(
    "r14_feist6_alt_rkhi_nw",
    lambda v, k: _feistel_nw_alt_rkhi_np(v, k, 6))

# F2: 4r lighter-strong-F probes
r14_feist4_chis1l_nw = _mk(
    "r14_feist4_chis1l_nw",
    lambda v, k: _feistel_nw_np(v, k, 4, _F_chis1l))
r14_feist4_pars1chi_nw = _mk(
    "r14_feist4_pars1chi_nw",
    lambda v, k: _feistel_nw_np(v, k, 4, _F_pars1chi))

# F3: 5r double-strength-F
r14_feist5_s1x2_311_nw = _mk(
    "r14_feist5_s1x2_311_nw",
    lambda v, k: _feistel_nw_2k_np(v, k, 5, _F_s1x2_311))

# F4: heterogeneous placement, 6r
r14_feist6_chi25_nw = _mk(
    "r14_feist6_chi25_nw",
    lambda v, k: _feistel_nw_chiset_np(v, k, 6, {2, 5}))
r14_feist6_chi16_nw = _mk(
    "r14_feist6_chi16_nw",
    lambda v, k: _feistel_nw_chiset_np(v, k, 6, {1, 6}))

# F5: r9 + invertible 64-bit final diffusion
r14_feist6_r9_outdiff_nw = _mk(
    "r14_feist6_r9_outdiff_nw",
    lambda v, k: _feistel_nw_r9out_np(v, k, 6, 13, 37))
r14_feist6_r9_outdiff2_nw = _mk(
    "r14_feist6_r9_outdiff2_nw",
    lambda v, k: _feistel_nw_r9out_np(v, k, 6, 7, 29))

# F6: S1->chi->lin single pass, 6r
r14_feist6_s1chi_311_nw = _mk(
    "r14_feist6_s1chi_311_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_s1chi_311))

ALL = [
    r14_feist6_chi_s1alt_nw, r14_feist6_alt713_nw,
    r14_feist6_alt_chinolin_nw, r14_feist6_alt_chioff_nw,
    r14_feist6_alt_rkhi_nw,
    r14_feist4_chis1l_nw, r14_feist4_pars1chi_nw,
    r14_feist5_s1x2_311_nw,
    r14_feist6_chi25_nw, r14_feist6_chi16_nw,
    r14_feist6_r9_outdiff_nw, r14_feist6_r9_outdiff2_nw,
    r14_feist6_s1chi_311_nw,
]
