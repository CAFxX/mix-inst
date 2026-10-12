"""5-stage fat-AND cascade, batch-21b proxy-guided schedule (triage z=2.55)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(32, 43, 49, 9, 17), (7, 59, 11, 9, 30), (21, 31, 50, 37, 39), (35, 15, 41, 63, 45), (44, 23, 10, 46, 39)]
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
