"""Round 8 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round8/gen_r8.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Common: S1 S-box, rk schedule = rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN).
"""
import numpy as np

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]
assert len(set(S1)) == 16
MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)
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


def _rk_np(k, i):
    """Round key for 1-indexed round i (matches impl.c rk())."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK64


def _sbox_layer32_np(x):
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(_S1A, nib) << np.uint64(4 * i)
    return out & MASK32


def _lin713_np(x):
    return (x ^ _rotl32_np(x, 7) ^ _rotl32_np(x, 13)) & MASK32


def _lin311_np(x):
    return (x ^ _rotl32_np(x, 3) ^ _rotl32_np(x, 11)) & MASK32


def _lin517_np(x):
    return (x ^ _rotl32_np(x, 5) ^ _rotl32_np(x, 17)) & MASK32


def _midori_mc_np(x):
    """Midori64 MixColumn adapted to 8 nibbles as two 4-nibble columns.
    M = [[0,1,1,1],[1,0,1,1],[1,1,0,1],[1,1,1,0]] per column."""
    x = x & MASK32
    out = np.zeros_like(x)
    for col in range(2):
        n = [((x >> np.uint64(16 * col + 4 * j)) & np.uint64(0xF)) for j in range(4)]
        m = [n[1] ^ n[2] ^ n[3], n[0] ^ n[2] ^ n[3],
             n[0] ^ n[1] ^ n[3], n[0] ^ n[1] ^ n[2]]
        for j in range(4):
            out |= (m[j] & np.uint64(0xF)) << np.uint64(16 * col + 4 * j)
    return out & MASK32


# P32 bit permutation (from gen_feistel_rtl.py Batch C): [(8*i)%31]*31 + [31]
_P32 = [(8 * i) % 31 for i in range(31)] + [31]
assert len(set(_P32)) == 32


def _p32_np(x):
    x = x & MASK32
    out = np.zeros_like(x)
    for i in range(32):
        bit = ((x >> np.uint64(_P32[i])) & np.uint64(1))
        out |= bit << np.uint64(i)
    return out & MASK32


# ---- F-functions (32 -> 32) ----
def _F_s1_1sbox(R, rk64):
    t = _sbox_layer32_np(R)
    t = _lin713_np(t)
    return (t ^ (rk64 & MASK32)) & MASK32


def _F_r311(R, rk64):
    t = _sbox_layer32_np(R)
    t = _lin311_np(t)
    t = _sbox_layer32_np(t)
    return (t ^ (rk64 & MASK32)) & MASK32


def _F_r517(R, rk64):
    t = _sbox_layer32_np(R)
    t = _lin517_np(t)
    t = _sbox_layer32_np(t)
    return (t ^ (rk64 & MASK32)) & MASK32


def _F_midori(R, rk64):
    t = _sbox_layer32_np(R)
    t = _midori_mc_np(t)
    return (t ^ (rk64 & MASK32)) & MASK32


def _F_s1_3sbox(R, rk64):
    t = _sbox_layer32_np(R)
    t = _lin713_np(t)
    t = _sbox_layer32_np(t)
    t = _lin713_np(t)
    t = _sbox_layer32_np(t)
    return (t ^ (rk64 & MASK32)) & MASK32


def _feistel_np(x, k, rounds, F, white=True, pbox=False):
    """Balanced Feistel, 32-bit halves, {R,L} output (no final swap)."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    if white:
        L = (L ^ ((k >> np.uint64(32)) & MASK32)) & MASK32
        R = (R ^ (k & MASK32)) & MASK32
    for i in range(1, rounds + 1):
        rkv = _rk_np(k, i)
        nR = (L ^ F(R, rkv)) & MASK32
        if pbox:
            nR = _p32_np(nR)
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


# ---- Round 8 candidates ----
def r8_feist6_s1_1sbox(val, key):
    return _feistel_np(val, key, 6, _F_s1_1sbox, white=True)


def r8_feist7_s1_1sbox(val, key):
    return _feistel_np(val, key, 7, _F_s1_1sbox, white=True)


def r8_feist6_s1_1sbox_nw(val, key):
    return _feistel_np(val, key, 6, _F_s1_1sbox, white=False)


def r8_feist7_s1_1sbox_nw(val, key):
    return _feistel_np(val, key, 7, _F_s1_1sbox, white=False)


def r8_feist8_s1_1sbox_nw(val, key):
    return _feistel_np(val, key, 8, _F_s1_1sbox, white=False)


def r8_feist6_r311(val, key):
    return _feistel_np(val, key, 6, _F_r311, white=True)


def r8_feist6_r517(val, key):
    return _feistel_np(val, key, 6, _F_r517, white=True)


def r8_feist8_midori(val, key):
    return _feistel_np(val, key, 8, _F_midori, white=True)


def r8_feist6_midori(val, key):
    return _feistel_np(val, key, 6, _F_midori, white=True)


def _F_alt(R, rk64, rnd):
    # odd rounds: cheap 1sbox F; even rounds: stronger 2sbox F
    if rnd % 2 == 1:
        return _F_s1_1sbox(R, rk64)
    t = _sbox_layer32_np(R)
    t = _lin713_np(t)
    t = _sbox_layer32_np(t)
    return (t ^ (rk64 & MASK32)) & MASK32


def r8_feist6_s1_alt(val, key):
    x = np.asarray(val, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    L = ((x >> np.uint64(32)) & MASK32) ^ ((k >> np.uint64(32)) & MASK32)
    R = (x & MASK32) ^ (k & MASK32)
    L, R = L & MASK32, R & MASK32
    for i in range(1, 7):
        rkv = _rk_np(k, i)
        nR = (L ^ _F_alt(R, rkv, i)) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def r8_feist4_s1_3sbox(val, key):
    return _feistel_np(val, key, 4, _F_s1_3sbox, white=True)


def r8_feist6_pbox(val, key):
    return _feistel_np(val, key, 6, _F_s1_1sbox, white=True, pbox=True)


# ---- Unbalanced Feistel 16/48 repair probe ----
def _rotl16_np(x, r):
    r %= 16
    if r == 0:
        return x & np.uint64(0xFFFF)
    return (((x << np.uint64(r)) | (x >> np.uint64(16 - r))) & np.uint64(0xFFFF))


def _F_ufeist_f2(R48, rk64):
    # 48->16: S1 on 12 nibbles -> xor-fold to 16 -> lin16(3,7) -> S1 on 4 nibbles -> ^rk16
    R48 = R48 & np.uint64(0xFFFFFFFFFFFF)
    s = np.zeros_like(R48)
    for j in range(12):
        nib = ((R48 >> np.uint64(4 * j)) & np.uint64(0xF)).astype(np.int64)
        s |= np.take(_S1A, nib) << np.uint64(4 * j)
    f = ((s >> np.uint64(32)) ^ (s >> np.uint64(16)) ^ s) & np.uint64(0xFFFF)
    f = (f ^ _rotl16_np(f, 3) ^ _rotl16_np(f, 7)) & np.uint64(0xFFFF)
    f2 = np.zeros_like(f)
    for j in range(4):
        nib = ((f >> np.uint64(4 * j)) & np.uint64(0xF)).astype(np.int64)
        f2 |= np.take(_S1A, nib) << np.uint64(4 * j)
    return (f2 ^ (rk64 & np.uint64(0xFFFF))) & np.uint64(0xFFFF)


def r8_ufeist16_48_f2(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    L = (x >> np.uint64(48)) & np.uint64(0xFFFF)
    R = x & np.uint64(0xFFFFFFFFFFFF)
    for i in range(1, 9):
        F = _F_ufeist_f2(R, _rk_np(np.asarray(key, dtype=np.uint64), i))
        nL = (R >> np.uint64(32)) & np.uint64(0xFFFF)
        nR = ((((R & np.uint64(0xFFFFFFFF)) << np.uint64(16)) |
               ((L ^ F) & np.uint64(0xFFFF))) & np.uint64(0xFFFFFFFFFFFF))
        L, R = nL, nR
    return ((L << np.uint64(48)) | R) & MASK64


CANDIDATES_R8 = [
    ("r8_feist6_s1_1sbox", r8_feist6_s1_1sbox, "6r Feistel, F=S1x1+lin713, whitening"),
    ("r8_feist7_s1_1sbox", r8_feist7_s1_1sbox, "7r Feistel, F=S1x1+lin713, whitening"),
    ("r8_feist6_s1_1sbox_nw", r8_feist6_s1_1sbox_nw, "6r Feistel, F=S1x1+lin713, NO whitening"),
    ("r8_feist7_s1_1sbox_nw", r8_feist7_s1_1sbox_nw, "7r Feistel, F=S1x1+lin713, NO whitening"),
    ("r8_feist8_s1_1sbox_nw", r8_feist8_s1_1sbox_nw, "8r Feistel, F=S1x1+lin713, NO whitening"),
    ("r8_feist6_r311", r8_feist6_r311, "6r Feistel, F=S1+lin311+S1, whitening"),
    ("r8_feist6_r517", r8_feist6_r517, "6r Feistel, F=S1+lin517+S1, whitening"),
    ("r8_feist8_midori", r8_feist8_midori, "8r Feistel, F=S1+MidoriMC(2col), whitening"),
    ("r8_feist6_midori", r8_feist6_midori, "6r Feistel, F=S1+MidoriMC(2col), whitening"),
    ("r8_feist6_s1_alt", r8_feist6_s1_alt, "6r Feistel, alternating F (1sbox/2sbox), whitening"),
    ("r8_feist4_s1_3sbox", r8_feist4_s1_3sbox, "4r Feistel, F=S1+lin+S1+lin+S1, whitening"),
    ("r8_feist6_pbox", r8_feist6_pbox, "6r Feistel, F=S1x1+lin713 + P32 on new R, whitening"),
    ("r8_ufeist16_48_f2", r8_ufeist16_48_f2, "8r uFeistel 16/48, F=S1+fold+lin16+S1, whitening"),
]
