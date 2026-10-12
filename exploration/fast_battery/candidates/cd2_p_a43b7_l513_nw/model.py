"""Self-contained numpy model for cd2_p_a43b7_l513_nw (hybrid).

Hybrid Batch 4 front 1: rasC2_0 S-box + affine P(i)=(43*i+7)%64 co-designed FOR lin(5,13) (lin-trail min-top tier).
"""
import numpy as np

SBOX = np.array([0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14], dtype=np.uint64)
PBOX = np.array([7, 50, 29, 8, 51, 30, 9, 52, 31, 10, 53, 32, 11, 54, 33, 12, 55, 34, 13, 56, 35, 14, 57, 36, 15, 58, 37, 16, 59, 38, 17, 60, 39, 18, 61, 40, 19, 62, 41, 20, 63, 42, 21, 0, 43, 22, 1, 44, 23, 2, 45, 24, 3, 46, 25, 4, 47, 26, 5, 48, 27, 6, 49, 28], dtype=np.uint64)
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
