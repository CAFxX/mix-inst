"""Round 18 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round18/gen_r18.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Round 18 (per coordinator brief), all 6r unless noted:
  1. parsplit chi16 offsets (1,3) mod 16 (incumbent (1,2); (0,1) died DIFF
     r17, (2,3) dominated r16).
  2. parsplit chi16 offsets (0,2) mod 16.
  3. parsplit S1-8/chi-24: S1 on R[7:0] (2 nibbles), chi24 on R[31:8] with
     offsets (1,2) mod 24.
  4. truncation probe: r13 alt structure, but round 6's F drops the linear
     layer (F = chi32(R)^rk on the even/chi round 6).
  5. palindromic key on r13 alt: rk_i = RK32(key,i) ^ RK32(key,7-i).
  6. asymmetric: odd rounds full S1-F; even rounds
     F = lin(3,11)((R[31:16]<<16) | chi16(R[15:0]))^rk
     (chi on low half, passthrough high half).
  7. parsplit with (5,17) rotmix.
  8. F = lin(3,11)(S1(R) ^ chi32(R))^rk — XOR of nonlinear outputs BEFORE a
     single shared linear layer (r17's parmix had separate linears and died).
  9. chi variant in alt structure: even rounds
     b_i = a_i ^ (~a_{i+1} & a_{i+3}).

Structural note (premix lesson): all are plain balanced Feistel with an
arbitrary round function F — bijectivity in val for fixed key holds
regardless of F, and every round's F sees a changing input by construction.
No novel topology here, so no invertibility round-trip beyond the standard
fixed-key bijection self-test.
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)

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


def _rotl64_np(x, r):
    r %= 64
    if r == 0:
        return x & MASK64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64


def _rotrN_np(x, r, n):
    r %= n
    if r == 0:
        return x & (np.uint64((1 << n) - 1) if n < 64 else MASK64)
    m = np.uint64((1 << n) - 1) if n < 64 else MASK64
    return ((x >> np.uint64(r)) | (x << np.uint64(n - r))) & m


def _sbox_layer32_np(x, tab):
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK32


def _sbox_layer16_np(x, tab):
    out = np.zeros_like(x)
    xv = x & MASK16
    for i in range(4):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK16


def _sbox_layer8_np(x, tab):
    out = np.zeros_like(x)
    xv = x & np.uint64(0xFF)
    for i in range(2):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & np.uint64(0xFF)


def _chi32_np(x):
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 1)) & _rotr32_np(x, 2))) & MASK32


def _chi32v_np(x):
    # variant: b_i = a_i ^ (~a_{i+1} & a_{i+3})
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 1)) & _rotr32_np(x, 3))) & MASK32


def _chi16_np(x, o1=1, o2=2):
    x = x & MASK16
    return (x ^ ((~_rotrN_np(x, o1, 16)) & _rotrN_np(x, o2, 16))) & MASK16


def _chi24_np(x, o1=1, o2=2):
    x = x & np.uint64(0xFFFFFF)
    return (x ^ ((~_rotrN_np(x, o1, 24)) & _rotrN_np(x, o2, 24))) & np.uint64(
        0xFFFFFF)


def _lin_ab_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _rk32_std_np(k, i):
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32


# ---------------- F functions ----------------
def _F_s1_311(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R, S1), 3, 11) ^ rk32) & MASK32


def _F_chi_311(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 3, 11) ^ rk32) & MASK32


def _F_chi32v_311(R, rk32):
    return (_lin_ab_np(_chi32v_np(R), 3, 11) ^ rk32) & MASK32


def _F_parsplit_chioff(R, rk32, o1, o2):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16, o1, o2)
          << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_parsplit_517(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 5, 17) ^ rk32) & MASK32


def _F_parsplit_s18_chi24(R, rk32):
    t = ((_chi24_np((R >> np.uint64(8)) & np.uint64(0xFFFFFF))
          << np.uint64(8)) |
         _sbox_layer8_np(R & np.uint64(0xFF), S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_chi_notr(R, rk32):
    # truncation probe: nonlinear output only, no linear layer
    return (_chi32_np(R) ^ rk32) & MASK32


def _F_asym_even(R, rk32):
    t = (((R >> np.uint64(16)) & MASK16) << np.uint64(16)) | \
        _chi16_np(R & MASK16)
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_s1xorchi(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R, S1) ^ _chi32_np(R), 3, 11) ^
            rk32) & MASK32


# ---------------- main loops ----------------
def _feistel_nw_np(x, k, rounds, F):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_alt_np(x, k, rounds, F_odd, F_even):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        F = F_odd if (i & 1) else F_even
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_alt_notr_np(x, k):
    # r13 alt, but round 6 (even/chi) drops the linear layer
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 7):
        if i == 6:
            F = _F_chi_notr
        else:
            F = _F_s1_311 if (i & 1) else _F_chi_311
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_alt_palk_np(x, k):
    # r13 alt with palindromic round keys: rk_i = RK32(k,i) ^ RK32(k,7-i)
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 7):
        rk = (_rk32_std_np(k, i) ^ _rk32_std_np(k, 7 - i)) & MASK32
        F = _F_s1_311 if (i & 1) else _F_chi_311
        nR = (L ^ F(R, rk)) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


# ---------------- candidates ----------------
def _mk(name, fn):
    fn.__name__ = name
    return fn


r18_feist6_ps_chioff13_nw = _mk(
    "r18_feist6_ps_chioff13_nw",
    lambda v, k: _feistel_nw_np(
        v, k, 6, lambda R, rk: _F_parsplit_chioff(R, rk, 1, 3)))

r18_feist6_ps_chioff02_nw = _mk(
    "r18_feist6_ps_chioff02_nw",
    lambda v, k: _feistel_nw_np(
        v, k, 6, lambda R, rk: _F_parsplit_chioff(R, rk, 0, 2)))

r18_feist6_ps_s18_chi24_nw = _mk(
    "r18_feist6_ps_s18_chi24_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit_s18_chi24))

r18_feist6_alt_notr_nw = _mk(
    "r18_feist6_alt_notr_nw",
    lambda v, k: _feistel_alt_notr_np(v, k))

r18_feist6_alt_palk_nw = _mk(
    "r18_feist6_alt_palk_nw",
    lambda v, k: _feistel_alt_palk_np(v, k))

r18_feist6_alt_asym_nw = _mk(
    "r18_feist6_alt_asym_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_s1_311, _F_asym_even))

r18_feist6_ps_517_nw = _mk(
    "r18_feist6_ps_517_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit_517))

r18_feist6_s1xorchi_nw = _mk(
    "r18_feist6_s1xorchi_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_s1xorchi))

r18_feist6_alt_chioff13_nw = _mk(
    "r18_feist6_alt_chioff13_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_s1_311, _F_chi32v_311))

ALL = [
    r18_feist6_ps_chioff13_nw, r18_feist6_ps_chioff02_nw,
    r18_feist6_ps_s18_chi24_nw, r18_feist6_alt_notr_nw,
    r18_feist6_alt_palk_nw, r18_feist6_alt_asym_nw,
    r18_feist6_ps_517_nw, r18_feist6_s1xorchi_nw,
    r18_feist6_alt_chioff13_nw,
]
