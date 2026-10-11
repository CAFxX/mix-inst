"""Round 15 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round15/gen_r15.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening
(unless noted), affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).
All r15 designs are Feistel-based, so fixed-key bijectivity holds regardless
of F (whitening is an XOR with a fixed-key constant -> bijection).

Round 15 exploits the r13 heterogeneity breakthrough further:
  F1: alt rotation-heterogeneity (6r) -
      alt_s713_c311: odd rounds S1-F (7,13), even rounds chi-F (3,11)
      alt_s311_c713: odd rounds S1-F (3,11), even rounds chi-F (7,13)
      alt_2rot: S1/chi alt; rotmix pair alternates every two rounds:
                {1,2} (3,11), {3,4} (7,13), {5,6} (3,11)
                (the task's "(c)" collapsed to (b) under the natural reading,
                so (c) is this genuinely distinct rotation-block variant)
  F2: alt + input whitening (6r) -
      alt_wh: W = val ^ key, then the r13 alt structure (odd S1 / even chi,
              (3,11)). Whitening was pure cost on single-S1 6r (r8/r10);
              re-tested on the heterogeneous structure.
  F3: mixed single/double-F rounds -
      mix5_db3: 5r, round 3 double-F (S1->lin->S1->lin, 2 keys); singles
                [s1, chi, chi, s1] on rounds 1,2,4,5
      mix6_db4: 6r, round 4 double-F; singles [s1, chi, s1, s1, chi]
      mix5_db24: 5r, double-F on rounds 2 and 4; singles [s1, chi, s1]
      mix6_db34: 6r, double-F on rounds 3 and 4; singles [s1, chi, s1, chi]
      Key indices (1-based C sense): mix5_db3 [1],[2],[3,4],[5],[6];
      mix6_db4 [1],[2],[3],[4,5],[6],[7]; mix5_db24 [1],[2,3],[4],[5,6],[7];
      mix6_db34 [1],[2],[3,4],[5,6],[7],[8].
  F4: parallel-split F (6r) -
      parsplit: t[15:0] = S1(R[15:0]) (4 nibbles), t[31:16] = chi16(R[31:16])
                (b_i = a_i ^ (~a_{i+1} & a_{i+2}) mod 16);
                F = lin(3,11)(t) ^ rk.
  F5: key-diffusion variants on the r13 alt structure (6r) -
      alt_rkdiff: rk' = RK32(key,i) ^ rotl32(RK32(key,i+1),8)
      alt_rksbox: rk = sbox_layer32(RK32(key,i)) (key through one S-box layer)
  F6: alt with chi offsets (2,3) (6r) -
      alt_chioff023: odd rounds S1-F (3,11), even rounds chi-F with
                b_i = a_i ^ (~a_{i+2} & a_{i+3}) (the "offsets (0,2,3)"
                probe: taps at base+2 and base+3).
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)  # THF/Blink (r7-r15)

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


def _sbox_layer32_np(x):
    """Eight 4-bit S1 S-boxes over the 32-bit word."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1, nib) << np.uint64(4 * i)
    return out & MASK32


def _sbox_layer16_np(x):
    """Four 4-bit S1 S-boxes over the low 16 bits."""
    out = np.zeros_like(x)
    xv = x & MASK16
    for i in range(4):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1, nib) << np.uint64(4 * i)
    return out & MASK16


def _chi32_np(x):
    """b_i = a_i ^ (~a_{i+1} & a_{i+2}). Even width -> not a permutation;
    fine, a Feistel F need not be invertible."""
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 1)) & _rotr32_np(x, 2))) & MASK32


def _chi32_off23_np(x):
    """Chi with offsets (2,3): b_i = a_i ^ (~a_{i+2} & a_{i+3})."""
    x = x & MASK32
    return (x ^ ((~_rotr32_np(x, 2)) & _rotr32_np(x, 3))) & MASK32


def _chi16_np(x):
    """16-bit chi: b_i = a_i ^ (~a_{i+1} & a_{i+2}) mod 16."""
    x = x & MASK16
    return (x ^ ((~_rotr16_np(x, 1)) & _rotr16_np(x, 2))) & MASK16


def _lin_ab_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _rk64_std_np(k, i):
    """Full 64-bit affine schedule value (1-based i)."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK64


def _rk32_std_np(k, i):
    """Affine schedule (r7/r8/r9): low32 of _rk64_std_np."""
    return _rk64_std_np(k, i) & MASK32


# ---------------- F functions ----------------
def _F_s1(R, rk32, a, b):
    return (_lin_ab_np(_sbox_layer32_np(R), a, b) ^ rk32) & MASK32


def _F_chi(R, rk32, a, b):
    return (_lin_ab_np(_chi32_np(R), a, b) ^ rk32) & MASK32


def _F_chi713(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 7, 13) ^ rk32) & MASK32


def _F_chi_off23(R, rk32):
    return (_lin_ab_np(_chi32_off23_np(R), 3, 11) ^ rk32) & MASK32


def _F_s1x2_311(R, rkA, rkB):
    t = _sbox_layer32_np(R ^ rkA)
    t = _lin_ab_np(t, 3, 11) ^ rkB
    t = _sbox_layer32_np(t)
    return _lin_ab_np(t, 3, 11) & MASK32


def _F_parsplit(R, rk32):
    t = ((_chi16_np((R >> np.uint64(16)) & MASK16) << np.uint64(16)) |
         _sbox_layer16_np(R & MASK16))
    return (_lin_ab_np(t, 3, 11) ^ rk32) & MASK32


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


def _feistel_mixed_np(x, k, rounds, fsched, kidx):
    """Mixed single/double-F rounds. fsched[r] in {"s1","chi","s1x2"} for
    round r (1-based, list index r-1); kidx[r] = list of 1-based key
    indices for round r."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        f = fsched[i - 1]
        ks = kidx[i - 1]
        if f == "s1":
            nR = (L ^ _F_s1(R, _rk32_std_np(k, ks[0]), 3, 11)) & MASK32
        elif f == "chi":
            nR = (L ^ _F_chi(R, _rk32_std_np(k, ks[0]), 3, 11)) & MASK32
        elif f == "s1x2":
            nR = (L ^ _F_s1x2_311(R, _rk32_std_np(k, ks[0]),
                                  _rk32_std_np(k, ks[1]))) & MASK32
        else:
            raise ValueError(f)
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_alt_wh_np(x, k, rounds):
    """r13 alt structure (odd S1 / even chi, (3,11)) with input whitening
    W = val ^ key before round 1."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    w = (x ^ k) & MASK64
    L = (w >> np.uint64(32)) & MASK32
    R = w & MASK32
    for i in range(1, rounds + 1):
        F = _F_s1_311 if (i & 1) else _F_chi_311
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_alt_rkdiff_np(x, k, rounds):
    """r13 alt structure with rk' = RK32(key,i) ^ rotl32(RK32(key,i+1),8)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        rk = (_rk32_std_np(k, i) ^ _rotl32_np(_rk32_std_np(k, i + 1), 8))
        rk &= MASK32
        F = _F_s1_311 if (i & 1) else _F_chi_311
        nR = (L ^ F(R, rk)) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_alt_rksbox_np(x, k, rounds):
    """r13 alt structure with rk = sbox_layer32(RK32(key,i))."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        rk = _sbox_layer32_np(_rk32_std_np(k, i))
        F = _F_s1_311 if (i & 1) else _F_chi_311
        nR = (L ^ F(R, rk)) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_alt_2rot_np(x, k, rounds):
    """r13 alt structure (odd S1 / even chi); rotmix pair alternates every
    two rounds: {1,2} (3,11), {3,4} (7,13), {5,6} (3,11)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        a, b = (3, 11) if ((i - 1) // 2) % 2 == 0 else (7, 13)
        rk = _rk32_std_np(k, i)
        if (i & 1):
            nR = (L ^ _F_s1(R, rk, a, b)) & MASK32
        else:
            nR = (L ^ _F_chi(R, rk, a, b)) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _F_s1_311(R, rk32):
    return _F_s1(R, rk32, 3, 11)


def _F_s1_713(R, rk32):
    return _F_s1(R, rk32, 7, 13)


def _F_chi_311(R, rk32):
    return _F_chi(R, rk32, 3, 11)


def _mk(name, fn):
    fn.__name__ = name
    return fn


# F1: alt rotation-heterogeneity, 6r
r15_feist6_alt_s713_c311_nw = _mk(
    "r15_feist6_alt_s713_c311_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_s1_713, _F_chi_311))
r15_feist6_alt_s311_c713_nw = _mk(
    "r15_feist6_alt_s311_c713_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_s1_311, _F_chi713))
r15_feist6_alt_2rot_nw = _mk(
    "r15_feist6_alt_2rot_nw",
    lambda v, k: _feistel_alt_2rot_np(v, k, 6))

# F2: alt + input whitening, 6r
r15_feist6_alt_wh_nw = _mk(
    "r15_feist6_alt_wh_nw",
    lambda v, k: _feistel_alt_wh_np(v, k, 6))

# F3: mixed single/double-F rounds
r15_feist5_db3_nw = _mk(
    "r15_feist5_db3_nw",
    lambda v, k: _feistel_mixed_np(
        v, k, 5, ["s1", "chi", "s1x2", "chi", "s1"],
        [[1], [2], [3, 4], [5], [6]]))
r15_feist6_db4_nw = _mk(
    "r15_feist6_db4_nw",
    lambda v, k: _feistel_mixed_np(
        v, k, 6, ["s1", "chi", "s1", "s1x2", "s1", "chi"],
        [[1], [2], [3], [4, 5], [6], [7]]))
r15_feist5_db24_nw = _mk(
    "r15_feist5_db24_nw",
    lambda v, k: _feistel_mixed_np(
        v, k, 5, ["s1", "s1x2", "chi", "s1x2", "s1"],
        [[1], [2, 3], [4], [5, 6], [7]]))
r15_feist6_db34_nw = _mk(
    "r15_feist6_db34_nw",
    lambda v, k: _feistel_mixed_np(
        v, k, 6, ["s1", "chi", "s1x2", "s1x2", "s1", "chi"],
        [[1], [2], [3, 4], [5, 6], [7], [8]]))

# F4: parallel-split F, 6r
r15_feist6_parsplit_nw = _mk(
    "r15_feist6_parsplit_nw",
    lambda v, k: _feistel_nw_np(v, k, 6, _F_parsplit))

# F5: key-diffusion variants on the r13 alt structure, 6r
r15_feist6_alt_rkdiff_nw = _mk(
    "r15_feist6_alt_rkdiff_nw",
    lambda v, k: _feistel_alt_rkdiff_np(v, k, 6))
r15_feist6_alt_rksbox_nw = _mk(
    "r15_feist6_alt_rksbox_nw",
    lambda v, k: _feistel_alt_rksbox_np(v, k, 6))

# F6: alt with chi offsets (2,3), 6r
r15_feist6_alt_chioff023_nw = _mk(
    "r15_feist6_alt_chioff023_nw",
    lambda v, k: _feistel_alt_np(v, k, 6, _F_s1_311, _F_chi_off23))

ALL = [
    r15_feist6_alt_s713_c311_nw, r15_feist6_alt_s311_c713_nw,
    r15_feist6_alt_2rot_nw, r15_feist6_alt_wh_nw,
    r15_feist5_db3_nw, r15_feist6_db4_nw, r15_feist5_db24_nw,
    r15_feist6_db34_nw, r15_feist6_parsplit_nw,
    r15_feist6_alt_rkdiff_nw, r15_feist6_alt_rksbox_nw,
    r15_feist6_alt_chioff023_nw,
]
