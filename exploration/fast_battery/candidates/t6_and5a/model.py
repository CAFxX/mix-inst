"""Bit-exact Python model for t6_and5a (batch 10)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _and5_cascade(v, k, stages):
    x = (np.uint64(v) ^ np.uint64(k)) & M64
    for (a, b, c) in stages:
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c)) & M64
    x = (x ^ _rotl64(np.uint64(k), 13)) & M64
    return x

def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f

STAGES = [(1, 2, 13), (7, 19, 5), (3, 11, 29), (17, 31, 7), (11, 23, 37)]

def _scalar(v, k):
    return _and5_cascade(v, k, STAGES)
_mix_np = _vec(_scalar)

def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _scalar(int(v), int(k))
    return _mix_np(v, k)
def mix_np(V, K):
    return _mix_np(V, K)
meta = {'desc': '5-stage AND-cascade x^=(ra&rb)^rc (al_and6a schedule, 5 stages)'}
