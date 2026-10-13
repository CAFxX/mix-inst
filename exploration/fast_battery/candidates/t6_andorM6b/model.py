"""t6_andorM6b: batch-44 andorM6 cascade (triage z=9.13)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(3, 30, 58, 5), (62, 35, 52, 23), (13, 20, 44, 43), (13, 51, 41, 25), (35, 47, 63, 34), (30, 19, 12, 59)]
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
