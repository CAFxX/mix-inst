"""Bit-exact Python model for t6_sand5b (batch 32)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SAND5B = [(5, (3, 4), 13), (17, (7, 8), 31), (29, (11, 12), 5), (41, (15, 16), 43), (9, (19, 20), 27)]

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

def t6_sand5b(v, k):
    return (_sandwich((v ^ k) & M64, SAND5B) ^ _rotl64(k, 13)) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_sand5b(np.uint64(v), np.uint64(k)))
    return t6_sand5b(np.asanyarray(v, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

def mix_np(V, K):
    return t6_sand5b(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '5-stage AND-sandwich x^=ra^(rb&rc)^rd, sched B'}
