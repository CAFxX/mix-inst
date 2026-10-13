"""6-stage AND-rotation cascade, batch-33 proxy-guided schedule (triage z=3.4)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(38, 34, 15), (47, 35, 33), (47, 2, 23), (16, 11, 60), (19, 5, 44), (18, 42, 41)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for a, b, c in STAGES:
        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
