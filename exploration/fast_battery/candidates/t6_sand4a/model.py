"""Bit-exact Python model for t6_sand4a (batch 32)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SAND4A = [(7, (1, 2), 19), (23, (5, 6), 11), (39, (9, 10), 3), (15, (13, 14), 47)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _sandwich(x, sched):
    for a, (b, c), d in sched:
        x = (x ^ _rotl64(x, a) ^ (_rotl64(x, b) & _rotl64(x, c))
             ^ _rotl64(x, d)) & M64
    return x

def t6_sand4a(v, k):
    return (_sandwich((v ^ k) & M64, SAND4A) ^ _rotl64(k, 13)) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_sand4a(np.uint64(v), np.uint64(k)))
    return t6_sand4a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

def mix_np(V, K):
    return t6_sand4a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4-stage AND-sandwich, sched C (wall probe)'}
