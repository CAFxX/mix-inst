"""Round 9 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round9/gen_r9.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base: 6-round Feistel of r8_feist6_s1_1sbox_nw (F = S1 layer -> lin(a,b) ->
^rk32). Round 9 attacks it from all sides:
  F1: 5-round probe (with/without whitening)
  F2: rotation-pair sweep in the F linear layer at 6r-nw
  F3: key-schedule ablation at 6r
  F4: 7r-nw repair (stronger F)
  F5: heterogeneous (alternating rotation pairs per round; byte-aligned rots)
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
    """Affine schedule (r7/r8): rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK64


def _rk32_std_np(k, i):
    return _rk_std_np(k, i) & MASK32


def _rk32_alt_np(k, i):
    """Alternating key halves + 32-bit round constant (ablation)."""
    i = np.asarray(i)
    hi = (k >> np.uint64(32)) & MASK32
    lo = k & MASK32
    half = np.where(i % 2 == 1, hi, lo)
    return (half ^ (np.uint64(i + 1) * GOLDEN32)) & MASK32


def _rk32_rot_np(k, i):
    """Cheap schedule: rotl64(k, 8*i), low 32 bits (ablation)."""
    return _rotl64_np(k, (8 * i) % 64) & MASK32


def _rk32_none_np(k, i):
    return np.zeros_like(np.asarray(k, dtype=np.uint64)) & MASK32


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


# F1: 5-round probe (defined explicitly below for clarity)
def r9_feist5_s1_1sbox_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 5,
                       lambda R, i: _F_s1_rot(R, _rk32_std_np(k, i), 7, 13),
                       white=False)


def r9_feist5_s1_1sbox(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 5,
                       lambda R, i: _F_s1_rot(R, _rk32_std_np(k, i), 7, 13),
                       white=True)


# F2: rotation-pair sweep at 6r-nw
def _rot_sweep(name, a, b):
    def fn(val, key):
        k = np.asarray(key, dtype=np.uint64)
        return _feistel_np(val, key, 6,
                           lambda R, i: _F_s1_rot(R, _rk32_std_np(k, i), a, b),
                           white=False)
    fn.__name__ = name
    return fn


r9_feist6_rot311_nw = _rot_sweep("r9_feist6_rot311_nw", 3, 11)
r9_feist6_rot517_nw = _rot_sweep("r9_feist6_rot517_nw", 5, 17)
r9_feist6_rot1119_nw = _rot_sweep("r9_feist6_rot1119_nw", 11, 19)
r9_feist6_rot0925_nw = _rot_sweep("r9_feist6_rot0925_nw", 9, 25)
r9_feist6_rot0719_nw = _rot_sweep("r9_feist6_rot0719_nw", 7, 19)
r9_feist6_rot0824_nw = _rot_sweep("r9_feist6_rot0824_nw", 8, 24)


# F3: key-schedule ablation at 6r
def r9_feist6_ksalt_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 6,
                       lambda R, i: _F_s1_rot(R, _rk32_alt_np(k, i), 7, 13),
                       white=False)


def r9_feist6_ksrot_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 6,
                       lambda R, i: _F_s1_rot(R, _rk32_rot_np(k, i), 7, 13),
                       white=False)


def r9_feist6_nork(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 6,
                       lambda R, i: _F_s1_rot(R, _rk32_none_np(k, i), 7, 13),
                       white=True)


# F4: 7r-nw repair (stronger F)
def r9_feist7_s1_lin2_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 7,
                       lambda R, i: _F_s1_lin2(R, _rk32_std_np(k, i)),
                       white=False)


def r9_feist7_rot517_nw(val, key):
    k = np.asarray(key, dtype=np.uint64)
    return _feistel_np(val, key, 7,
                       lambda R, i: _F_s1_rot(R, _rk32_std_np(k, i), 5, 17),
                       white=False)


# F5: heterogeneous
def r9_feist6_altrot_nw(val, key):
    """Alternating rotation pairs per round: odd rounds (7,13), even (5,17)."""
    k = np.asarray(key, dtype=np.uint64)

    def F(R, i):
        i = np.asarray(i)
        a = np.where(i % 2 == 1, np.uint64(7), np.uint64(5))
        b = np.where(i % 2 == 1, np.uint64(13), np.uint64(17))
        t = _sbox_layer32_np(R)
        # lin with per-element (a,b): rotl amounts are scalars per element
        # only in the vectorized path; here i is scalar in the loop.
        ai, bi = int(a), int(b)
        t = _lin_np(t, ai, bi)
        return (t ^ _rk32_std_np(k, i)) & MASK32

    return _feistel_np(val, key, 6, F, white=False)


CANDIDATES_R9 = [
    ("r9_feist5_s1_1sbox_nw", r9_feist5_s1_1sbox_nw, "5r Feistel, F=S1x1+lin713, NO whitening"),
    ("r9_feist5_s1_1sbox", r9_feist5_s1_1sbox, "5r Feistel, F=S1x1+lin713, whitening"),
    ("r9_feist6_rot311_nw", r9_feist6_rot311_nw, "6r Feistel, F=S1+lin(3,11), NO whitening"),
    ("r9_feist6_rot517_nw", r9_feist6_rot517_nw, "6r Feistel, F=S1+lin(5,17), NO whitening"),
    ("r9_feist6_rot1119_nw", r9_feist6_rot1119_nw, "6r Feistel, F=S1+lin(11,19), NO whitening"),
    ("r9_feist6_rot0925_nw", r9_feist6_rot0925_nw, "6r Feistel, F=S1+lin(9,25), NO whitening"),
    ("r9_feist6_rot0719_nw", r9_feist6_rot0719_nw, "6r Feistel, F=S1+lin(7,19), NO whitening"),
    ("r9_feist6_rot0824_nw", r9_feist6_rot0824_nw, "6r Feistel, F=S1+lin(8,24) byte-aligned, NO whitening"),
    ("r9_feist6_ksalt_nw", r9_feist6_ksalt_nw, "6r Feistel, F=S1x1+lin713, alternating key halves, NO whitening"),
    ("r9_feist6_ksrot_nw", r9_feist6_ksrot_nw, "6r Feistel, F=S1x1+lin713, rk=rotl64(k,8i), NO whitening"),
    ("r9_feist6_nork", r9_feist6_nork, "6r Feistel, F=S1x1+lin713 no round key, whitening only"),
    ("r9_feist7_s1_lin2_nw", r9_feist7_s1_lin2_nw, "7r Feistel, F=S1+lin713+lin713, NO whitening"),
    ("r9_feist7_rot517_nw", r9_feist7_rot517_nw, "7r Feistel, F=S1+lin(5,17), NO whitening"),
    ("r9_feist6_altrot_nw", r9_feist6_altrot_nw, "6r Feistel, F=S1+lin alternating (7,13)/(5,17) per round, NO whitening"),
]
