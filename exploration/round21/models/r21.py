"""Round 21 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round21/gen_r21.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Frontier entering round 21 -- Frontier S:
  r20 chioff13all (37.0u speed), r19 chioff13 (37.4u), r20 chioff31 (37.5u size).
Frontier Q: r19 fm07 (38.8u), fm11 (39.3u), fm311 (39.5u), r15 parsplit (40.7u),
r9 (41.0u), r8 (42.9u).

Round 21 (per coordinator brief), all 6r Feistel, no whitening:
  1. notr_chioff31all: (3,1) chi variant on rounds 2,4 AND truncated round 6
  2. notr_chioff31final: (1,3) on rounds 2,4, (3,1) on truncated round 6
  3. notr_chioff13all_fm07: chioff13all + fm07 cure on (1,3) final chi
  4. notr_chioff31_fm07: chioff31 + fm07 cure on plain final chi
  5. notr_3rot: 3-rotation (3,7,11) linears with chi-F in notr (O2 re-test)
  6. notr_3rot_chioff13: 3-rot linears + (1,3) chi
  7. notr_keyin31: (3,1) on rounds 2,4 + key inside plain final chi
  8. notr_keyinw: (3,1) on rounds 2,4 + key inside (3,1) final chi
  9. notr_chioff21: new offset pair (2,1) b_i=a_i^(~a_{i+2}&a_{i+1}) rounds 2,4
 10. notr_chioff13all_fm311: chioff13all + fm311 cure on (1,3) final chi

Structural note: all are plain balanced Feistel with an arbitrary round
function F -- bijective in val for fixed key regardless of F, and every
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


def _chi32x_np(x):
    # variant: b_i = a_i ^ (~a_{i+2} & a_{i+1})  (offset pair (2,1))
    x = x & MASK32
    r2 = ((x >> np.uint64(2)) | (x << np.uint64(30))) & MASK32
    r1 = ((x >> np.uint64(1)) | (x << np.uint64(31))) & MASK32
    return (x ^ ((~r2) & r1)) & MASK32


def _lin_ab_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _lin_abc_np(x, a, b, c):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b) ^ _rotl32_np(x, c)) & MASK32


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


def _F_chi32w_notr(R, rk32):
    return (_chi32w_np(R) ^ rk32) & MASK32


def _F_chi32x_311(R, rk32):
    return (_lin_ab_np(_chi32x_np(R), 3, 11) ^ rk32) & MASK32


def _F_chi_fm07v(R, rk32):
    # fm07 cure on the (1,3) chi: y = chi32v(R)^rk; F = y ^ rotl32(y, 7)
    y = (_chi32v_np(R) ^ rk32) & MASK32
    return (y ^ _rotl32_np(y, 7)) & MASK32


def _F_chi_fm311v(R, rk32):
    # fm311 cure on the (1,3) chi: F = rotl(chi32v,3) ^ rotl(chi32v,11) ^ rk
    c = _chi32v_np(R)
    return (_rotl32_np(c, 3) ^ _rotl32_np(c, 11) ^ rk32) & MASK32


def _F_chi_fm311(R, rk32):
    # fm311 cure on PLAIN chi32 (r21b follow-up): F = rotl(chi32,3) ^ rotl(chi32,11) ^ rk
    c = _chi32_np(R)
    return (_rotl32_np(c, 3) ^ _rotl32_np(c, 11) ^ rk32) & MASK32


def _F_s1_3711(R, rk32):
    return (_lin_abc_np(_sbox_layer32_np(R, S1), 3, 7, 11) ^ rk32) & MASK32


def _F_chi_3711(R, rk32):
    return (_lin_abc_np(_chi32_np(R), 3, 7, 11) ^ rk32) & MASK32


def _F_chi32v_3711(R, rk32):
    return (_lin_abc_np(_chi32v_np(R), 3, 7, 11) ^ rk32) & MASK32


def _lin3ns_np(x):
    # NONSINGULAR 3-rotation layer: R3 ^ R7 ^ R11 (no identity term).
    # Odd term count -> (X+1) does not divide the polynomial -> permutation.
    # Diagnosis probe for the r21 3rot S1-LIN kill (singularity, not rotation count).
    return (_rotl32_np(x, 3) ^ _rotl32_np(x, 7) ^ _rotl32_np(x, 11)) & MASK32


def _F_s1_3ns(R, rk32):
    return (_lin3ns_np(_sbox_layer32_np(R, S1)) ^ rk32) & MASK32


def _F_chi_3ns(R, rk32):
    return (_lin3ns_np(_chi32_np(R)) ^ rk32) & MASK32


def _F_chi32w_keyin_notr(R, rk32):
    return _chi32w_np((R ^ rk32) & MASK32) & MASK32


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


def _fm(R, rk32, m):
    # plain-chi fm for round 6 of chioff31_fm07
    y = (_chi32_np(R) ^ rk32) & MASK32
    return (y ^ _rotl32_np(y, m)) & MASK32


r21_feist6_alt_notr_chioff31all_nw = _mk(
    "r21_feist6_alt_notr_chioff31all_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32w_311, 3: _F_s1_311,
               4: _F_chi32w_311, 5: _F_s1_311, 6: _F_chi32w_notr}))

r21_feist6_alt_notr_chioff31final_nw = _mk(
    "r21_feist6_alt_notr_chioff31final_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32v_311, 3: _F_s1_311,
               4: _F_chi32v_311, 5: _F_s1_311, 6: _F_chi32w_notr}))

r21_feist6_alt_notr_chioff13all_fm07_nw = _mk(
    "r21_feist6_alt_notr_chioff13all_fm07_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32v_311, 3: _F_s1_311,
               4: _F_chi32v_311, 5: _F_s1_311, 6: _F_chi_fm07v}))

r21_feist6_alt_notr_chioff31_fm07_nw = _mk(
    "r21_feist6_alt_notr_chioff31_fm07_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32w_311, 3: _F_s1_311,
               4: _F_chi32w_311, 5: _F_s1_311,
               6: lambda R, rk: _fm(R, rk, 7)}))

r21_feist6_alt_notr_3rot_nw = _mk(
    "r21_feist6_alt_notr_3rot_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_3711, 2: _F_chi_3711, 3: _F_s1_3711,
               4: _F_chi_3711, 5: _F_s1_3711, 6: _F_chi_notr}))

r21_feist6_alt_notr_3rot_chioff13_nw = _mk(
    "r21_feist6_alt_notr_3rot_chioff13_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_3711, 2: _F_chi32v_3711, 3: _F_s1_3711,
               4: _F_chi32v_3711, 5: _F_s1_3711, 6: _F_chi32v_notr}))

r21_feist6_alt_notr_keyin31_nw = _mk(
    "r21_feist6_alt_notr_keyin31_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32w_311, 3: _F_s1_311,
               4: _F_chi32w_311, 5: _F_s1_311, 6: _F_chi_keyin_notr}))

r21_feist6_alt_notr_keyinw_nw = _mk(
    "r21_feist6_alt_notr_keyinw_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32w_311, 3: _F_s1_311,
               4: _F_chi32w_311, 5: _F_s1_311, 6: _F_chi32w_keyin_notr}))

r21_feist6_alt_notr_chioff21_nw = _mk(
    "r21_feist6_alt_notr_chioff21_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32x_311, 3: _F_s1_311,
               4: _F_chi32x_311, 5: _F_s1_311, 6: _F_chi_notr}))

r21_feist6_alt_notr_chioff13all_fm311_nw = _mk(
    "r21_feist6_alt_notr_chioff13all_fm311_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_311, 2: _F_chi32v_311, 3: _F_s1_311,
               4: _F_chi32v_311, 5: _F_s1_311, 6: _F_chi_fm311v}))

r21_feist6_alt_notr_3rot_ns_nw = _mk(
    "r21_feist6_alt_notr_3rot_ns_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_3ns, 2: _F_chi_3ns, 3: _F_s1_3ns,
               4: _F_chi_3ns, 5: _F_s1_3ns, 6: _F_chi_notr}))

r21b_3rot_ns_fm311_nw = _mk(
    "r21b_3rot_ns_fm311_nw",
    lambda v, k: _feistel_r20_np(
        v, k, {1: _F_s1_3ns, 2: _F_chi_3ns, 3: _F_s1_3ns,
               4: _F_chi_3ns, 5: _F_s1_3ns, 6: _F_chi_fm311}))

ALL = [
    r21_feist6_alt_notr_chioff31all_nw,
    r21_feist6_alt_notr_chioff31final_nw,
    r21_feist6_alt_notr_chioff13all_fm07_nw,
    r21_feist6_alt_notr_chioff31_fm07_nw,
    r21_feist6_alt_notr_3rot_nw,
    r21_feist6_alt_notr_3rot_chioff13_nw,
    r21_feist6_alt_notr_keyin31_nw,
    r21_feist6_alt_notr_keyinw_nw,
    r21_feist6_alt_notr_chioff21_nw,
    r21_feist6_alt_notr_chioff13all_fm311_nw,
    r21_feist6_alt_notr_3rot_ns_nw,
    r21b_3rot_ns_fm311_nw,
]

