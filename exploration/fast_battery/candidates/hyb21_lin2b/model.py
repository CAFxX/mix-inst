"""5-stage 1-AND+2-linear cascade, batch-21d proxy-guided schedule (triage z=2.48)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(29, 54, 38, 39), (10, 4, 46, 6), (37, 5, 57, 49), (10, 29, 35, 33), (30, 17, 44, 50)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for a, b, c, d in STAGES:
        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c) ^ _rotl(x, d)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
