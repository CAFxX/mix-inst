"""hyb28_mu5_234: batch-28 MU5 MUX-gate 5-stage cascade (triage-exact DIFF z=2.34, LIN proxy D=20)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(48, 8, 49, 10), (42, 41, 48, 55), (5, 45, 43, 14), (49, 12, 1, 63), (31, 2, 16, 39)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _mux(s, a, b):
    return ((s & a) | ((~s) & b)) & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for (s, a, b, d) in STAGES:
        x = (x ^ _mux(_rotl(x, s), _rotl(x, a), _rotl(x, b)) ^ _rotl(x, d)) & M64
    return ((x ^ _rotl(k, 13))) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
