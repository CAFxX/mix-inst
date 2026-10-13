"""Bit-exact Python model for t6_skip5a (batch 32)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SKIP5A = [((1, 2), 7, 13), ((5, 6), 23, 29), ((9, 10), 41, 3), ((13, 14), 29, 47), ((17, 18), 11, 59)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _skipcascade(x0, sched):
    xm1 = np.zeros_like(np.asanyarray(x0, dtype=np.uint64))
    x = np.asanyarray(x0, dtype=np.uint64)
    for (a, b), d, s in sched:
        xn = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, d)
              ^ _rotl64(xm1, s)) & M64
        xm1, x = x, xn
    return x

def t6_skip5a(v, k):
    return (_skipcascade((v ^ k) & M64, SKIP5A) ^ _rotl64(k, 13)) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_skip5a(np.uint64(v), np.uint64(k)))
    return t6_skip5a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

def mix_np(V, K):
    return t6_skip5a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '5-stage skip-coupled cascade (x-state residual)'}
