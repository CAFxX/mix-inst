"""R25 Track C numpy model: 6r Feistel F restructures (no chi in r9)."""
import numpy as np

S1 = np.array([0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10], dtype=np.int64)
MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)


def _rotl32(x, n):
    n %= 32
    x = np.asarray(x, dtype=np.uint64)
    return ((x << np.uint64(n)) | (x >> np.uint64(32 - n))) & MASK32 if n else x & MASK32


def _rotl64(x, n):
    n %= 64
    x = np.asarray(x, dtype=np.uint64)
    return ((x << np.uint64(n)) | (x >> np.uint64(64 - n))) & MASK64 if n else x & MASK64


def _rk32(k, i):
    # Canonical r9-family affine schedule: rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64),
    # matching the C impls' RK32 (1-indexed round i). Fixed 2026-10-05: was 13*i / i.
    with np.errstate(over="ignore"):
        return (_rotl64(k, 13 * (i + 1)) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32


def _sbox32(x):
    x = np.asarray(x, dtype=np.uint64) & MASK32
    out = np.zeros_like(x)
    for i in range(8):
        nib = ((x >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1, nib).astype(np.uint64) << np.uint64(4 * i)
    return out & MASK32


def _lin32(x, a, b):
    x = np.asarray(x, dtype=np.uint64) & MASK32
    return (x ^ _rotl32(x, a) ^ _rotl32(x, b)) & MASK32


def _feistel(x, k, F):
    x = np.asarray(x, dtype=np.uint64) & MASK64
    k = np.asarray(k, dtype=np.uint64) & MASK64
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 7):
        nR = (L ^ F(R, _rk32(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def r25_feist6_linfirst_nw(v, k):
    return _feistel(v, k, lambda R, rk: (_sbox32(_lin32(R, 3, 11)) ^ rk) & MASK32)


def r25_feist6_keyin_nw(v, k):
    return _feistel(v, k, lambda R, rk: _lin32(_sbox32((R ^ rk) & MASK32), 3, 11) & MASK32)


def r25_feist6_rot13_nw(v, k):
    return _feistel(v, k, lambda R, rk: (_lin32(_sbox32(R), 1, 3) ^ rk) & MASK32)
