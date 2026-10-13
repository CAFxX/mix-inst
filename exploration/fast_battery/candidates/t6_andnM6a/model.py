"""t6_andnM6a: batch-39 andnM6 cascade (triage z=2.2)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(21, 17, 43), (5, 37, 27), (32, 3, 56), (32, 43, 18), (49, 31, 44), (28, 19, 7)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for a, b, c in STAGES:
        x = (x ^ (_rotl(x, a) & ~_rotl(x, b)) ^ _rotl(x, c)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
