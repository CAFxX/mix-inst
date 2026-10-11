"""Round 16 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round16/gen_r16.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Round 16 = verdict-scope re-tests (VERDICT_SCOPE.md) + parsplit variants:
  F1 (re-test O1, HIGH): crypto S-boxes in HETEROGENEOUS rounds — odd rounds
      XBOX-F = lin(3,11)(XBOX_layer32(R))^rk, even rounds chi-F. r11 tested
      crypto S-boxes only in the homogeneous single-S-box-F slot; here only
      3/6 rounds pay S-box cost (different economics).
      XBOX in {GIFT, PRESENT, SKINNY-4 (corrected table)}.
  F2 (re-test O2, MEDIUM): 3-rotation linear in chi-F rounds — odd S1-F(3,11),
      even chi-F with lin3(a,b,c) = x^rotl(x,a)^rotl(x,b)^rotl(x,c),
      (3,7,11) and (7,13,19). r12 tested 3-rot lin only with S1-F.
  F3: parsplit variants (r15's parsplit: t[31:16]=chi16(R[31:16]),
      t[15:0]=S1(R[15:0]), F=lin(3,11)(t)^rk):
      rev (S1 high / chi16 low), 713 (lin(7,13)), chioff23 (chi16 offsets
      (2,3)), w24 (S1 on 24 bits + chi8 on 8 bits), giftsplit (GIFT low /
      chi16 high).
  F4: (S1-F, parsplit-F) alternation — odd rounds r13 S1-F, even rounds r15
      parsplit-F.
  F5 (re-test O5, LOW): mid-key on the alt structure — odd rounds
      F=lin(3,11)(S1(R)^rk), even rounds F=lin(3,11)(chi32(R)^rk). r13 tested
      mid-key only on the r9 (homogeneous) structure.
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)
GIFT = np.array([1, 10, 4, 12, 6, 15, 3, 9, 2, 13, 11, 7, 5, 0, 8, 14],
                dtype=np.uint64)
PRESENT = np.array([12, 5, 6, 11, 9, 0, 10, 13, 3, 14, 15, 8, 4, 7, 1, 2],
                   dtype=np.uint64)
SKINNY4 = np.array([12, 6, 9, 0, 1, 10, 2, 11, 3, 8, 5, 13, 4, 14, 7, 15],
                   dtype=np.uint64)  # corrected per r11 (primary SKINNY spec)

MASK8 = np.uint64(0xFF)
MASK16 = np.uint64(0xFFFF)
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


def _rotl16_np(x, r):
    r %= 16
    if r == 0:
        return x & MASK16
    return ((x << np.uint64(r)) | (x >> np.uint64(16 - r))) & MASK16


def _rotr16_np(x, r):
    return _rotl16_np(x, (-r) % 16)


def _rotl8_np(x, r):
    r %= 8
    if r == 0:
        return x & MASK8
    return ((x << np.uint64(r)) | (x >> np.uint64(8 - r))) & MASK8


def _rotr8_np(x, r):
    return _rotl8_np(x, (-r) % 8)


def _rotl64_np(x, r):
    r %= 64
    if r == 0:
        return x & MASK64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64


def _sbox_layer32_np(x, tab):
    """Eight 4-bit S-boxes over the 32-bit word, table `tab`."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK32


def _sbox_layer24_np(x, tab):
    """Six 4-bit S-boxes over the low 24 bits."""
    out = np.zeros_like(x)
    xv = x & np.uint64(0xFFFFFF)
    for i in range(6):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & np.uint64(0xFFFFFF)


def _sbox_layer16_np(x, tab):
    """Four 4-bit S-boxes over the low 16 bits."""
    out = np.zeros_like(x)
    xv = x & MASK16
    for i in range(4):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK16


def _chi32_np(x):
    """b_i = a_i ^ (~a_{i+1} & a_{i+2}). Even width -> not a permutation;
    fine, a Feistel F need not be invertible."""
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 1)) & _rotr32_np(x, 2))) & MASK32


def _chi16_np(x, o1=1, o2=2):
    """16-bit chi: b_i = a_i ^ (~a_{i+o1} & a_{i+o2}) mod 16."""
    x = x & MASK16
    return (x ^ ((~_rotr16_np(x, o1)) & _rotr16_np(x, o2))) & MASK16


def _chi8_np(x, o1=1, o2=2):
    """8-bit chi: b_i = a_i ^ (~a_{i+o1} & a_{i+o2}) mod 8."""
    x = x & MASK8
    return (x ^ ((~_rotr8_np(x, o1)) & _rotr8_np(x, o2))) & MASK8


def _lin_ab_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _lin3_np(x, a, b, c):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b) ^ _rotl32_np(x, c)) & MASK32


def _rk64_std_np(k, i):
    """Full 64-bit affine schedule value (1-based i)."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK64


def _rk32_std_np(k, i):
    """Affine schedule (r7/r8/r9): low32 of _rk64_std_np."""
    return _rk64_std_np(k, i) & MASK32


# ---------------- F functions ----------------
def _F_s1_311(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R, S1), 3, 11) ^ rk32) & MASK32


def _F_xbox_311(R, rk32, tab):
    return (_lin_ab_np(_sbox_layer32_np(R, tab), 3, 11) ^ rk32) & MASK32


def _F_chi_311(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 3, 11) ^ rk32) & MASK32


def _F_chi_lin3(R, rk32, a, b, c):
    return (_lin3_np(_chi32_np(R), a, b, c) ^ rk32) & MASK32


def _F_parsplit(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_parsplit_rev(R, rk32):
    t = ((_sbox_layer16_np((R >> np.uint64(16)) & MASK16, S1) << np.uint64(16)) |
         _chi16_np(R & MASK16))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_parsplit_713(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 7, 13) ^ rk32) & MASK32


def _F_parsplit_chioff23(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16, 2, 3) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_parsplit_w24(R, rk32):
    t = ((_chi8_np((R >> np.uint64(24)) & MASK8) << np.uint64(24)) |
         _sbox_layer24_np(R & np.uint64(0xFFFFFF), S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_giftsplit(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, GIFT))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_midk_s1(R, rk32):
    return _lin_ab_np(_sbox_layer32_np(R, S1) ^ rk32, 3, 11) & MASK32


def _F_midk_chi(R, rk32):
    return _lin_ab_np(_chi32_np(R) ^ rk32, 3, 11) & MASK32


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


def _feistel_alt_np(x, k, rounds, F_odd, F_even):
    """Alt: odd rounds F_odd, even rounds F_even (1-based), std keys."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = F_odd if (i & 1) else F_even
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


# ---------------- candidates ----------------
def _mk(name, fn):
    fn.__name__ = name
    return fn


r16_feist6_gift_het_nw = _mk(
    "r16_feist6_gift_het_nw",
    lambda v, k: _feistel_alt_np(
        v, k, 6,
        lambda R, rk: _F_xbox_311(R, rk, GIFT),
        _F_chi_311))

r16_feist6_present_het_nw = _mk(
    "r16_feist6_present_het_nw",
    lambda v, k: _feistel_alt_np(
        v, k, 6,
        lambda R, rk: _F_xbox_311(R, rk, PRESENT),
        _F_chi_311))

r16_feist6_sk4_het_nw = _mk(
    "r16_feist6_sk4_het_nw",
    lambda v, k: _feistel_alt_np(
        v, k, 6,
        lambda R, rk: _F_xbox_311(R, rk, SKINNY4),
        _F_chi_311))

r16_feist6_alt_lin3711_nw = _mk(
    "r16_feist6_alt_lin3711_nw",
    lambda v, k: _feistel_alt_np(
        v, k, 6, _F_s1_311,
        lambda R, rk: _F_chi_lin3(R, rk, 3, 7, 11)))

r16_feist6_alt_lin71319_nw = _mk(
    "r16_feist6_alt_lin71319_nw",
    lambda v, k: _feistel_alt_np(
        v, k, 6, _F_s1_311,
        lambda R, rk: _F_chi_lin3(R, rk, 7, 13, 19)))

r16_feist6_parsplit_rev_nw = _mk(
    "r16_feist6_parsplit_rev_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit_rev))

r16_feist6_parsplit_713_nw = _mk(
    "r16_feist6_parsplit_713_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit_713))

r16_feist6_parsplit_chioff23_nw = _mk(
    "r16_feist6_parsplit_chioff23_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit_chioff23))

r16_feist6_parsplit_w24_nw = _mk(
    "r16_feist6_parsplit_w24_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit_w24))

r16_feist6_giftsplit_nw = _mk(
    "r16_feist6_giftsplit_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_giftsplit))

r16_feist6_alt_s1ps_nw = _mk(
    "r16_feist6_alt_s1ps_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_s1_311, _F_parsplit))

r16_feist6_alt_midk_nw = _mk(
    "r16_feist6_alt_midk_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_midk_s1, _F_midk_chi))

ALL = [
    r16_feist6_gift_het_nw, r16_feist6_present_het_nw, r16_feist6_sk4_het_nw,
    r16_feist6_alt_lin3711_nw, r16_feist6_alt_lin71319_nw,
    r16_feist6_parsplit_rev_nw, r16_feist6_parsplit_713_nw,
    r16_feist6_parsplit_chioff23_nw, r16_feist6_parsplit_w24_nw,
    r16_feist6_giftsplit_nw, r16_feist6_alt_s1ps_nw, r16_feist6_alt_midk_nw,
]
