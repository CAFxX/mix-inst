"""Round 19 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round19/gen_r19.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Frontier entering round 19: r18_feist6_alt_notr_nw (37.9u / 4,119 / 11,621),
6r alt with round 6's linear dropped (F_6 = chi32(R)^rk). Documented blemish:
Q1 bic_maxcorr=0.172 vs family norm ~0.008.

Round 19 (per coordinator brief), all 6r:
  A. BIC-fix probes (notr + cheap final mixing on round 6's F output):
    fm03: F_6 = (chi32(R)^rk) ^ rotl32(chi32(R)^rk, 3)
    fm07: same with rotl 7
    fm11: same with rotl 11
    fm311: F_6 = rotl32(chi32(R),3) ^ rotl32(chi32(R),11) ^ rk
  B. truncation axis:
    notr5: r13 alt with round 5's linear ALSO dropped (F_5 = S1(R)^rk)
    ps_notr: parsplit-F with round 6's linear dropped
    r9_notr: r9 structure with round 6's linear dropped (F_6 = S1(R)^rk)
    chioff13: notr + chi offsets (1,3) on rounds 2,4 (round 6 unchanged)
    notr_517: notr with (5,17) rotmix on the 5 surviving linears

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


def _sbox_layer16_np(x, tab):
    out = np.zeros_like(x)
    xv = x & MASK16
    for i in range(4):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK16


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


def _chi16_np(x, o1=1, o2=2):
    x = x & MASK16
    r1 = ((x >> np.uint64(o1)) | (x << np.uint64(16 - o1))) & MASK16
    r2 = ((x >> np.uint64(o2)) | (x << np.uint64(16 - o2))) & MASK16
    return (x ^ ((~r1) & r2)) & MASK16


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


def _F_chi_notr(R, rk32):
    return (_chi32_np(R) ^ rk32) & MASK32


def _F_s1_notr(R, rk32):
    return (_sbox_layer32_np(R, S1) ^ rk32) & MASK32


def _F_chi_fm(R, rk32, m):
    # cheap final mixing: y = chi32(R)^rk; F = y ^ rotl32(y, m)
    y = (_chi32_np(R) ^ rk32) & MASK32
    return (y ^ _rotl32_np(y, m)) & MASK32


def _F_chi_fm311(R, rk32):
    # F = rotl32(chi32(R),3) ^ rotl32(chi32(R),11) ^ rk
    c = _chi32_np(R)
    return (_rotl32_np(c, 3) ^ _rotl32_np(c, 11) ^ rk32) & MASK32


def _F_ps_311(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_ps_notr(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (t ^ rk32) & MASK32


def _F_s1_517(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R, S1), 5, 17) ^ rk32) & MASK32


def _F_chi_517(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 5, 17) ^ rk32) & MASK32


# ---------------- main loop ----------------
def _feistel_r19_np(x, k, Fsel):
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


_ALT = {1: _F_s1_311, 2: _F_chi_311, 3: _F_s1_311, 4: _F_chi_311,
        5: _F_s1_311}

r19_feist6_alt_notr_fm03_nw = _mk(
    "r19_feist6_alt_notr_fm03_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {**_ALT, 6: lambda R, rk: _F_chi_fm(R, rk, 3)}))

r19_feist6_alt_notr_fm07_nw = _mk(
    "r19_feist6_alt_notr_fm07_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {**_ALT, 6: lambda R, rk: _F_chi_fm(R, rk, 7)}))

r19_feist6_alt_notr_fm11_nw = _mk(
    "r19_feist6_alt_notr_fm11_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {**_ALT, 6: lambda R, rk: _F_chi_fm(R, rk, 11)}))

r19_feist6_alt_notr_fm311_nw = _mk(
    "r19_feist6_alt_notr_fm311_nw",
    lambda v, k: _feistel_r19_np(v, k, {**_ALT, 6: _F_chi_fm311}))

r19_feist6_alt_notr5_nw = _mk(
    "r19_feist6_alt_notr5_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {1: _F_s1_311, 2: _F_chi_311, 3: _F_s1_311, 4: _F_chi_311,
               5: _F_s1_notr, 6: _F_chi_notr}))

r19_feist6_ps_notr_nw = _mk(
    "r19_feist6_ps_notr_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {1: _F_ps_311, 2: _F_ps_311, 3: _F_ps_311, 4: _F_ps_311,
               5: _F_ps_311, 6: _F_ps_notr}))

r19_feist6_r9_notr_nw = _mk(
    "r19_feist6_r9_notr_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {1: _F_s1_311, 2: _F_s1_311, 3: _F_s1_311, 4: _F_s1_311,
               5: _F_s1_311, 6: _F_s1_notr}))

r19_feist6_alt_notr_chioff13_nw = _mk(
    "r19_feist6_alt_notr_chioff13_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {1: _F_s1_311, 2: _F_chi32v_311, 3: _F_s1_311,
               4: _F_chi32v_311, 5: _F_s1_311, 6: _F_chi_notr}))

r19_feist6_alt_notr_517_nw = _mk(
    "r19_feist6_alt_notr_517_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {1: _F_s1_517, 2: _F_chi_517, 3: _F_s1_517, 4: _F_chi_517,
               5: _F_s1_517, 6: _F_chi_notr}))

r19_feist6_alt_notr_chioff13_fm03_nw = _mk(
    "r19_feist6_alt_notr_chioff13_fm03_nw",
    lambda v, k: _feistel_r19_np(
        v, k, {1: _F_s1_311, 2: _F_chi32v_311, 3: _F_s1_311,
               4: _F_chi32v_311, 5: _F_s1_311,
               6: lambda R, rk: _F_chi_fm(R, rk, 3)}))

ALL = [
    r19_feist6_alt_notr_fm03_nw, r19_feist6_alt_notr_fm07_nw,
    r19_feist6_alt_notr_fm11_nw, r19_feist6_alt_notr_fm311_nw,
    r19_feist6_alt_notr5_nw, r19_feist6_ps_notr_nw,
    r19_feist6_r9_notr_nw, r19_feist6_alt_notr_chioff13_nw,
    r19_feist6_alt_notr_517_nw, r19_feist6_alt_notr_chioff13_fm03_nw,
]
