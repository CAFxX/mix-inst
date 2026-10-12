"""5-stage fat-AND cascade, batch-21b proxy-guided schedule (triage z=2.42)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(11, 6, 25, 13, 30), (16, 7, 24, 23, 31), (22, 18, 3, 14, 38), (7, 28, 14, 15, 10), (11, 34, 19, 38, 5)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for a, b, c, d, e in STAGES:
        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ (_rotl(x, c) & _rotl(x, d)) ^ _rotl(x, e)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
