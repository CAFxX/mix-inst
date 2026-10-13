"""6-stage AND-rotation cascade, batch-33 proxy-guided schedule (triage z=5.7)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(57, 43, 8), (41, 50, 24), (52, 3, 22), (36, 32, 21), (41, 56, 10), (54, 56, 22)]
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
