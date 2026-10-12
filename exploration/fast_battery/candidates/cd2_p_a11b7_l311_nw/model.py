"""Self-contained numpy model for cd2_p_a11b7_l311_nw (hybrid).

Hybrid Batch 4 front 2: rasC2_0 S-box + affine P(i)=(11*i+7)%64 co-designed FOR lin(3,11) (lin-trail min-top tier).
"""
import numpy as np

SBOX = np.array([0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14], dtype=np.uint64)
PBOX = np.array([7, 18, 29, 40, 51, 62, 9, 20, 31, 42, 53, 0, 11, 22, 33, 44, 55, 2, 13, 24, 35, 46, 57, 4, 15, 26, 37, 48, 59, 6, 17, 28, 39, 50, 61, 8, 19, 30, 41, 52, 63, 10, 21, 32, 43, 54, 1, 12, 23, 34, 45, 56, 3, 14, 25, 36, 47, 58, 5, 16, 27, 38, 49, 60], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
               0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054], dtype=np.uint64)
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
ROUNDS = 4
ROTA = 3
ROTB = 11


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
