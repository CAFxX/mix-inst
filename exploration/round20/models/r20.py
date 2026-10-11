"""Round 20 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round20/gen_r20.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Frontier entering round 20: r19_feist6_alt_notr_chioff13_nw (37.4u, speed,
BIC blemish 0.142), r18_feist6_alt_notr_nw (37.9u, smaller, BIC 0.172).
Both: 6r alt, odd rounds F_S1 = lin(3,11)(S1(R))^rk, even rounds F_chi =
lin(3,11)(chi32(R))^rk, round 6 F = chi32(R)^rk (truncated, no linear).

Round 20 (per coordinator brief), all 6r Feistel, no whitening:
  1. notr_s1final: r18 notr but round 6 F = S1(R)^rk (no linear)
  2. notr_chioff13all: chioff13 with chi(1,3) also on round 6 (truncated)
  3. chioff13_517: chioff13 with (5,17) rotmix on the 5 surviving linears
  4. notr_keyin: round 6 F = chi32(R ^ rk32) (key inside chi input)
  5. notr_drop4: round 4's (chi) linear ALSO dropped (S1-gated probe)
  6. notr_713: (7,13) rotmix on the 5 surviving linears
  7. notr_fm16: F_6 = (chi32(R)^rk) ^ rotl32(chi32(R)^rk, 16)
  8. notr_chioff31: chi variant b_i = a_i ^ (~a_{i+3} & a_{i+1}) on rounds 2,4
  9. alt_chioff13: r13-full alt (WITH round-6 linear) + chi(1,3) on rounds 2,4,6

Structural note: all are plain balanced Feistel with an arbitrary round
function F — bijective in val for fixed key regardless of F, and every
round's F sees a changing input by construction. No novel topology.
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


def _rotl64_np(x, r):
    r %= 64
    if r == 0:
        return x & MASK64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64


def _sbox_layer32_np(x, tab):
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK32


def _chi32_np(x):
    x = x & MASK32
    r1 = ((x >> np.uint64(1)) | (x << np.uint64(31))) & MASK32
    r2 = ((x >> np.uint64(2)) | (x << np.uint64(30))) & MASK32
    return (x ^ ((~r1) & r2)) & MASK32


def _chi32v_np(x):
    # variant: b_i = a_i ^ (~a_{i+1} & a_{i+3})
    x = x & MASK32
    r1 = ((x >> np.uint64(1)) | (x << np.uint64(31))) & MASK32
    r3 = ((x >> np.uint64(3)) | (x << np.uint64(29))) & MASK32
    return (x ^ ((~r1) & r3)) & MASK32


def _chi32w_np(x):
    # variant: b_i = a_i ^ (~a_{i+3} & a_{i+1})  (offsets swapped vs chi32v)
    x = x & MASK32
    r3 = ((x >> np.uint64(3)) | (x << np.uint64(29))) & MASK32
    r1 = ((x >> np.uint64(1)) | (x << np.uint64(31))) & MASK32
    return (x ^ ((~r3) & r1)) & MASK32


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


def _F_chi32w_311(R, rk32):
    return (_lin_ab_np(_chi32w_np(R), 3, 11) ^ rk32) & MASK32


def _F_s1_713(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R, S1), 7, 13) ^ rk32) & MASK32


def _F_chi_713(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 7, 13) ^ rk32) & MASK32


def _F_s1_517(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R, S1), 5, 17) ^ rk32) & MASK32


def _F_chi32v_517(R, rk32):
    return (_lin_ab_np(_chi32v_np(R), 5, 17) ^ rk32) & MASK32


def _F_chi_notr(R, rk32):
    return (_chi32_np(R) ^ rk32) & MASK32


def _F_chi32v_notr(R, rk32):
    return (_chi32v_np(R) ^ rk32) & MASK32


def _F_s1_notr(R, rk32):
    return (_sbox_layer32_np(R, S1) ^ rk32) & MASK32


def _F_chi_keyin_notr(R, rk32):
    return _chi32_np((R ^ rk32) & MASK32) & MASK32


def _F_chi_fm(R, rk32, m):
    # cheap final mixing: y = chi32(R)^rk; F = y ^ rotl32(y, m)
    y = (_chi32_np(R) ^ rk32) & MASK32
    return (y ^ _rotl32_np(y, m)) & MASK32


# ---------------- main loop ----------------
def _feistel_r20_np(x, k, Fsel):
    # Fsel: dict 1-based round -> F function
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 7):
        nR = (L ^ Fsel[i](R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _mk(name, fn):
    fn.__name__ = name
    return fn


r20_feist6_alt_notr_s1final_nw = _mk(
    "r20_feist6_alt_notr_s1final_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi_311, 3: _F_s1_311, 4: _F_chi_311,
               5: _F_s1_311, 6: _F_s1_notr}))

r20_feist6_alt_notr_chioff13all_nw = _mk(
    "r20_feist6_alt_notr_chioff13all_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32v_311, 3: _F_s1_311,
               4: _F_chi32v_311, 5: _F_s1_311, 6: _F_chi32v_notr}))

r20_feist6_alt_notr_chioff13_517_nw = _mk(
    "r20_feist6_alt_notr_chioff13_517_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_517, 2: _F_chi32v_517, 3: _F_s1_517,
               4: _F_chi32v_517, 5: _F_s1_517, 6: _F_chi_notr}))

r20_feist6_alt_notr_keyin_nw = _mk(
    "r20_feist6_alt_notr_keyin_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi_311, 3: _F_s1_311, 4: _F_chi_311,
               5: _F_s1_311, 6: _F_chi_keyin_notr}))

r20_feist6_alt_notr_drop4_nw = _mk(
    "r20_feist6_alt_notr_drop4_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi_311, 3: _F_s1_311, 4: _F_chi_notr,
               5: _F_s1_311, 6: _F_chi_notr}))

r20_feist6_alt_notr_713_nw = _mk(
    "r20_feist6_alt_notr_713_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_713, 2: _F_chi_713, 3: _F_s1_713, 4: _F_chi_713,
               5: _F_s1_713, 6: _F_chi_notr}))

r20_feist6_alt_notr_fm16_nw = _mk(
    "r20_feist6_alt_notr_fm16_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi_311, 3: _F_s1_311, 4: _F_chi_311,
               5: _F_s1_311,
               6: lambda R, rk: _F_chi_fm(R, rk, 16)}))

r20_feist6_alt_notr_chioff31_nw = _mk(
    "r20_feist6_alt_notr_chioff31_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32w_311, 3: _F_s1_311,
               4: _F_chi32w_311, 5: _F_s1_311, 6: _F_chi_notr}))

r20_feist6_alt_chioff13_nw = _mk(
    "r20_feist6_alt_chioff13_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32v_311, 3: _F_s1_311,
               4: _F_chi32v_311, 5: _F_s1_311, 6: _F_chi32v_311}))

ALL = [
    r20_feist6_alt_notr_s1final_nw,
    r20_feist6_alt_notr_chioff13all_nw,
    r20_feist6_alt_notr_chioff13_517_nw,
    r20_feist6_alt_notr_keyin_nw,
    r20_feist6_alt_notr_drop4_nw,
    r20_feist6_alt_notr_713_nw,
    r20_feist6_alt_notr_fm16_nw,
    r20_feist6_alt_notr_chioff31_nw,
    r20_feist6_alt_chioff13_nw,
]
