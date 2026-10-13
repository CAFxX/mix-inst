"""6-stage AND-rotation cascade, batch-33 proxy-guided schedule (triage z=6.9)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(25, 44, 8), (27, 40, 37), (63, 5, 39), (11, 22, 6), (29, 7, 21), (12, 3, 44)]
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
