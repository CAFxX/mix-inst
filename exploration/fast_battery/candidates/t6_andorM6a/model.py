"""t6_andorM6a: batch-44 andorM6 cascade (triage z=3.31)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(31, 12, 58, 39), (54, 57, 4, 32), (6, 4, 33, 42), (54, 10, 8, 59), (38, 45, 41, 27), (9, 43, 53, 44)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for a, b, c, d in STAGES:
        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ (_rotl(x, c) | _rotl(x, d))) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
