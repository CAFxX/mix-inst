"""Round 17 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round17/gen_r17.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Round 17 (per coordinator brief):
  1. 5r parsplit-F (highest value): F = lin(3,11)(S1(R[15:0]) ||
     chi16(R[31:16])) ^ rk, 5 rounds. The 5r phase transition was established
     for the single-S1 F; parsplit-F is stronger.
  2. 5r alt (S1,chi): r13's alternating structure at 5 rounds
     (rounds 1,3,5 S1-F; rounds 2,4 chi-F).
  3. 5r alt chi-first: rounds 1,3,5 chi-F; rounds 2,4 S1-F (order probe at 5r).
  4. [re-test O4] 6r parallel S1+chi: F = lin(3,11)(S1(R^rk)) ^
     lin(3,11)(chi32(R)). r14's version died at 4r; test at 6r.
  5. [re-test O3] partial-S-box in heterogeneous context: 6r alt where odd
     (S1) rounds apply S1 to only the low 16 bits of R (high 16 pass through
     the linear layer unmodified), even chi rounds unchanged.
  6. double-S1 split: 6r parsplit geometry but S1 on R[15:0] AND S1rev on
     R[31:16], where S1rev = S1 composed with nibble bit-reversal
     (affine-equivalent S-box, different bit positions active).
  7. parsplit with chi16 offsets (0,1) mod 16, 6r (r16 tested (2,3); (1,2)
     is the incumbent).
  8. pre-mix F: F = lin(3,11)(S1(R ^ rotl32(R,16))) ^ rk, 6r.
  9. 4r parsplit-F (S1-gated probe only).
 10. 5r parsplit-F with lin(7,13) (rotation data point at 5r).
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)

# bit-reversal of a 4-bit value (a permutation of {0..15}, linear on bits)
_REV4 = np.array([((v & 1) << 3) | ((v & 2) << 1) | ((v & 4) >> 1) | ((v & 8) >> 3)
                  for v in range(16)], dtype=np.int64)
# S1rev[v] = S1[rev4(v)]: affine-equivalent to S1 (same diff/linear profile),
# different active bit positions when mixed with the linear layer.
S1REV = np.take(S1, _REV4)

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
    return (x ^ ((~_rotr32_np(x, 1)) & _rotr32_np(x, 2))) & MASK32


def _chi16_np(x, o1=1, o2=2):
    x = x & MASK16
    return (x ^ ((~_rotr16_np(x, o1)) & _rotr16_np(x, o2))) & MASK16


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


def _F_parsplit(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_parsplit_713(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 7, 13) ^ rk32) & MASK32


def _F_parsplit_chioff01(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16, 0, 1) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_pshalf(R, rk32):
    # [O3 re-test] S1 on low 16 bits only; high 16 pass through unmodified.
    t = (((R >> np.uint64(16)) & MASK16) << np.uint64(16)) | \
        _sbox_layer16_np(R & MASK16, S1)
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_parmix(R, rk32):
    # [O4 re-test] parallel S1+chi; key inside the S1 branch only.
    return (_lin_ab_np(_sbox_layer32_np(R ^ rk32, S1), 3, 11) ^
            _lin_ab_np(_chi32_np(R), 3, 11)) & MASK32


def _F_dbs1split(R, rk32):
    t = ((_sbox_layer16_np((R >> np.uint64(16)) & MASK16, S1REV)
          << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16, S1))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


def _F_premix(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R ^ _rotl32_np(R, 16), S1), 3, 11) ^
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


# ---------------- candidates ----------------
def _mk(name, fn):
    fn.__name__ = name
    return fn


r17_feist5_parsplit_nw = _mk(
    "r17_feist5_parsplit_nw",
    lambda v, k: _feistel_nw_np(v, k, 5, _F_parsplit))

r17_feist5_alt_s1chi_nw = _mk(
    "r17_feist5_alt_s1chi_nw",
    lambda v, k: _feistel_alt_np(v, k, 5, _F_s1_311, _F_chi_311))

r17_feist5_alt_chifirst_nw = _mk(
    "r17_feist5_alt_chifirst_nw",
    lambda v, k: _feistel_alt_np(v, k, 5, _F_chi_311, _F_s1_311))

r17_feist6_parmix_nw = _mk(
    "r17_feist6_parmix_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parmix))

r17_feist6_alt_pshalf_nw = _mk(
    "r17_feist6_alt_pshalf_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_pshalf, _F_chi_311))

r17_feist6_dbs1split_nw = _mk(
    "r17_feist6_dbs1split_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_dbs1split))

r17_feist6_parsplit_chioff01_nw = _mk(
    "r17_feist6_parsplit_chioff01_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit_chioff01))

r17_feist6_premix_nw = _mk(
    "r17_feist6_premix_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_premix))

r17_feist4_parsplit_nw = _mk(
    "r17_feist4_parsplit_nw",
    lambda v, k: _feistel_nw_np(v, k, 4, _F_parsplit))

r17_feist5_parsplit_713_nw = _mk(
    "r17_feist5_parsplit_713_nw",
    lambda v, k: _feistel_nw_np(v, k, 5, _F_parsplit_713))

ALL = [
    r17_feist5_parsplit_nw, r17_feist5_alt_s1chi_nw,
    r17_feist5_alt_chifirst_nw, r17_feist6_parmix_nw,
    r17_feist6_alt_pshalf_nw, r17_feist6_dbs1split_nw,
    r17_feist6_parsplit_chioff01_nw, r17_feist6_premix_nw,
    r17_feist4_parsplit_nw, r17_feist5_parsplit_713_nw,
]
