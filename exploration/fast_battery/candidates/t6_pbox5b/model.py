"""Bit-exact Python model for t6_pbox5b (batch 31)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
_BYTETR = [0, 8, 16, 24, 32, 40, 48, 56, 9, 17, 25, 33, 41, 49, 57, 1, 18, 26, 34, 42, 50, 58, 2, 10, 27, 35, 43, 51, 59, 3, 11, 19, 36, 44, 52, 60, 4, 12, 20, 28, 45, 53, 61, 5, 13, 21, 29, 37, 54, 62, 6, 14, 22, 30, 38, 46, 63, 7, 15, 23, 31, 39, 47, 55]
PBX5 = [((1, 2),), ((5, 6),), ((9, 10),), ((13, 14),), ((17, 18),)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _chi64(x):
    """chi64(x)_i = x_i ^ (~x_{i+1} & x_{i+2}), indices mod 64."""
    r1 = _rotl64(x, 63)   # bit i = x_{(i+1) mod 64}
    r2 = _rotl64(x, 62)   # bit i = x_{(i+2) mod 64}
    return (x ^ (~r1 & r2)) & M64

def _pbox64_vec(x, idx):
    # vectorized over arrays
    x = np.asanyarray(x, dtype=np.uint64)
    out = np.zeros_like(x)
    for i in range(64):
        out |= ((x >> np.uint64(idx[i])) & np.uint64(1)) << np.uint64(i)
    return out

def _andcascade(x, sched):
    for ops, d in sched:
        x = (x ^ (_rotl64(x, ops[0]) & _rotl64(x, ops[1])) ^ _rotl64(x, d)) & M64
    return x

def _andcascade_pbox(x, pairs, idx):
    for (ops,) in pairs:
        x = (x ^ (_rotl64(x, ops[0]) & _rotl64(x, ops[1])) ^ _pbox64_vec(x, idx)) & M64
    return x

def t6_pbox5b(v, k):
    """5-stage AND + byte-transpose diffusion."""
    x = _andcascade_pbox((v ^ k) & M64, PBX5, _BYTETR)
    return (x ^ _rotl64(k, 13)) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_pbox5b(np.uint64(v), np.uint64(k)))
    return t6_pbox5b(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_pbox5b(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '5-stage AND + byte-transpose diffusion'}
