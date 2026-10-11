"""Round 10 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round10/gen_r10.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base: 6-round Feistel attacking the round-9 winner r9_feist6_rot311_nw
(F = S1 layer -> lin(3,11) -> ^rk32, no whitening, 41.0u):
  F1: fine rotation sweep around (3,11) at 6r-nw: (2,11),(3,13),(3,17),
      (4,11),(3,7),(5,11)
  F2: (3,11) + input whitening
  F3: 5-round phase-transition crossing: (a) 5r + lin713 doubled,
      (b) 5r + 2-S-box F (S1->lin311->S1), (c) 5r + whitening + (3,11)
  F4: key-schedule x (3,11): alternating halves, rotl64(k,8i)
  F5: heterogeneous: alternating (3,11)/(7,13) per round at 6r-nw
"""
import numpy as np

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]
assert len(set(S1)) == 16
MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)
GOLDEN32 = np.uint64(0x9E3779B9)
_S1A = np.array(S1, dtype=np.uint64)


def _rotl32_np(x, r):
    r %= 32
    if r == 0:
        return x & MASK32
    return (((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & MASK32)


def _rotl64_np(x, r):
    r %= 64
    if r == 0:
        return x & MASK64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64


def _sbox_layer32_np(x):
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(_S1A, nib) << np.uint64(4 * i)
    return out & MASK32


def _lin_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


# ---- key schedules (1-indexed round i) ----
def _rk_std_np(k, i):
    """Affine schedule (r7/r8/r9): rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK64


def _rk32_std_np(k, i):
    return _rk_std_np(k, i) & MASK32


def _rk32_alt_np(k, i):
    """Alternating key halves + 32-bit round constant."""
    i = np.asarray(i)
    hi = (k >> np.uint64(32)) & MASK32
    lo = k & MASK32
    half = np.where(i % 2 == 1, hi, lo)
    return (half ^ (np.uint64(i + 1) * GOLDEN32)) & MASK32


def _rk32_rot_np(k, i):
    """Cheap schedule: rotl64(k, 8*i), low 32 bits."""
    return _rotl64_np(k, (8 * i) % 64) & MASK32


# ---- F-functions (32 -> 32), parameterized ----
def _F_s1_rot(R, rk32, a, b):
    t = _sbox_layer32_np(R)
    t = _lin_np(t, a, b)
    return (t ^ rk32) & MASK32


def _F_s1_lin2(R, rk32):
    """Doubled linear layer: S1 -> lin713 -> lin713 -> ^rk32."""
    t = _sbox_layer32_np(R)
    t = _lin_np(t, 7, 13)
    t = _lin_np(t, 7, 13)
    return (t ^ rk32) & MASK32


def _F_s1_2sbox(R, rk32, a, b):
    """Two S-box layers: S1 -> lin(a,b) -> S1 -> ^rk32."""
    t = _sbox_layer32_np(R)
    t = _lin_np(t, a, b)
    t = _sbox_layer32_np(t)
    return (t ^ rk32) & MASK32


def _feistel_np(x, k, rounds, F, white=True):
    """Balanced Feistel, 32-bit halves, {R,L} output (no final swap)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    if white:
        L = (L ^ ((k >> np.uint64(32)) & MASK32)) & MASK32
        R = (R ^ (k & MASK32)) & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ F(R, i)) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _mk_rot(name, rounds, a, b, ks, white):
    rk = {"std": _rk32_std_np, "alt": _rk32_alt_np, "rot": _rk32_rot_np}[ks]

    def fn(val, key):
        k = np.asarray(key, dtype=np.uint64)
        return _feistel_np(val, key, rounds,
                           lambda R, i: _F_s1_rot(R, rk(k, i), a, b),
                           white=white)
    fn.__name__ = name
    return fn


# ---- F1: fine rotation sweep around (3,11), 6r-nw, std ks ----
r10_feist6_rot0211_nw = _mk_rot("r10_feist6_rot0211_nw", 6, 2, 11, "std", False)
r10_feist6_rot0313_nw = _mk_rot("r10_feist6_rot0313_nw", 6, 3, 13, "std", False)
r10_feist6_rot0317_nw = _mk_rot("r10_feist6_rot0317_nw", 6, 3, 17, "std", False)
r10_feist6_rot0411_nw = _mk_rot("r10_feist6_rot0411_nw", 6, 4, 11, "std", False)
r10_feist6_rot0307_nw = _mk_rot("r10_feist6_rot0307_nw", 6, 3, 7, "std", False)
r10_feist6_rot0511_nw = _mk_rot("r10_feist6_rot0511_nw", 6, 5, 11, "std", False)

# ---- F2: (3,11) + whitening ----
r10_feist6_rot311 = _mk_rot("r10_feist6_rot311", 6, 3, 11, "std", True)


# ---- F3: 5-round phase-transition crossing ----
def r10_feist5_s1_lin2_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 5,
                       lambda R, i: _F_s1_lin2(R, _rk32_std_np(k, i)),
                       white=False)


def r10_feist5_s1_2sbox_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 5,
                       lambda R, i: _F_s1_2sbox(R, _rk32_std_np(k, i), 3, 11),
                       white=False)


r10_feist5_rot311 = _mk_rot("r10_feist5_rot311", 5, 3, 11, "std", True)

# ---- F4: key-schedule x (3,11), 6r-nw ----
r10_feist6_rot311_ksalt_nw = _mk_rot("r10_feist6_rot311_ksalt_nw", 6, 3, 11, "alt", False)
r10_feist6_rot311_ksrot_nw = _mk_rot("r10_feist6_rot311_ksrot_nw", 6, 3, 11, "rot", False)


# ---- F5: heterogeneous - alternating (3,11)/(7,13) per round, 6r-nw ----
def r10_feist6_altrot311_713_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)

    def F(R, i):
        rk32 = _rk32_std_np(k, i)
        t = _sbox_layer32_np(R)
        if i & 1:
            t = _lin_np(t, 3, 11)
        else:
            t = _lin_np(t, 7, 13)
        return (t ^ rk32) & MASK32

    return _feistel_np(val, key, 6, F, white=False)


CANDIDATES_R10 = [
    ("r10_feist6_rot0211_nw", r10_feist6_rot0211_nw,
     "6r Feistel, F=S1+lin(2,11), NO whitening"),
    ("r10_feist6_rot0313_nw", r10_feist6_rot0313_nw,
     "6r Feistel, F=S1+lin(3,13), NO whitening"),
    ("r10_feist6_rot0317_nw", r10_feist6_rot0317_nw,
     "6r Feistel, F=S1+lin(3,17), NO whitening"),
    ("r10_feist6_rot0411_nw", r10_feist6_rot0411_nw,
     "6r Feistel, F=S1+lin(4,11), NO whitening"),
    ("r10_feist6_rot0307_nw", r10_feist6_rot0307_nw,
     "6r Feistel, F=S1+lin(3,7), NO whitening"),
    ("r10_feist6_rot0511_nw", r10_feist6_rot0511_nw,
     "6r Feistel, F=S1+lin(5,11), NO whitening"),
    ("r10_feist6_rot311", r10_feist6_rot311,
     "6r Feistel, F=S1+lin(3,11), WITH whitening"),
    ("r10_feist5_s1_lin2_nw", r10_feist5_s1_lin2_nw,
     "5r Feistel, F=S1+lin713+lin713, NO whitening"),
    ("r10_feist5_s1_2sbox_nw", r10_feist5_s1_2sbox_nw,
     "5r Feistel, F=S1+lin311+S1, NO whitening"),
    ("r10_feist5_rot311", r10_feist5_rot311,
     "5r Feistel, F=S1+lin(3,11), WITH whitening"),
    ("r10_feist6_rot311_ksalt_nw", r10_feist6_rot311_ksalt_nw,
     "6r Feistel, F=S1+lin(3,11), alt key halves, NO whitening"),
    ("r10_feist6_rot311_ksrot_nw", r10_feist6_rot311_ksrot_nw,
     "6r Feistel, F=S1+lin(3,11), rk=rotl64(k,8i), NO whitening"),
    ("r10_feist6_altrot311_713_nw", r10_feist6_altrot311_713_nw,
     "6r Feistel, F=S1+lin(3,11)/(7,13) alternating, NO whitening"),
]
