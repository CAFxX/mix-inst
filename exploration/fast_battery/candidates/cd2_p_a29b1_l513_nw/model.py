"""Self-contained numpy model for cd2_p_a29b1_l513_nw (hybrid).

Hybrid Batch 4 front 1: rasC2_0 S-box + affine P(i)=(29*i+1)%64 co-designed FOR lin(5,13) (lin-trail min-top tier).
"""
import numpy as np

SBOX = np.array([0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14], dtype=np.uint64)
PBOX = np.array([1, 30, 59, 24, 53, 18, 47, 12, 41, 6, 35, 0, 29, 58, 23, 52, 17, 46, 11, 40, 5, 34, 63, 28, 57, 22, 51, 16, 45, 10, 39, 4, 33, 62, 27, 56, 21, 50, 15, 44, 9, 38, 3, 32, 61, 26, 55, 20, 49, 14, 43, 8, 37, 2, 31, 60, 25, 54, 19, 48, 13, 42, 7, 36], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
               0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054], dtype=np.uint64)
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
ROUNDS = 4
ROTA = 5
ROTB = 13


def _rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _sbox64(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SBOX[((x >> np.uint64(4 * i)) & np.uint64(0xF))] \
            << np.uint64(4 * i)
    return y & M64


def _pbox64(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << PBOX[i]
    return y & M64


def _lin(x):
    return (x ^ _rotl(x, ROTA) ^ _rotl(x, ROTB)) & M64


def _round(x, key, i):
    rk = _rotl(key, 13 * (i + 1)) ^ RC[i]
    return _lin(_pbox64(_sbox64(x ^ rk)))


def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64)
    k = np.asarray(K, dtype=np.uint64)
    for i in range(ROUNDS):
        x = _round(x, k, i)
    return x & M64


def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
