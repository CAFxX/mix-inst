"""Self-contained numpy model for cd1_p_a27b1_l513_nw (hybrid).

co-design pilot: rasC2_0 + affine P(27i+1) + lin(5,13)
"""
import numpy as np

SBOX = np.array([0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14], dtype=np.uint64)
PBOX = np.array([1, 28, 55, 18, 45, 8, 35, 62, 25, 52, 15, 42, 5, 32, 59, 22, 49, 12, 39, 2, 29, 56, 19, 46, 9, 36, 63, 26, 53, 16, 43, 6, 33, 60, 23, 50, 13, 40, 3, 30, 57, 20, 47, 10, 37, 0, 27, 54, 17, 44, 7, 34, 61, 24, 51, 14, 41, 4, 31, 58, 21, 48, 11, 38], dtype=np.uint64)
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
