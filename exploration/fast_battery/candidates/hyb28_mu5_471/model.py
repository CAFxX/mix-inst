"""hyb28_mu5_471: batch-28 MU5 MUX-gate 5-stage cascade (triage-exact DIFF z=4.71, LIN proxy D=22)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(45, 39, 27, 54), (41, 18, 60, 20), (56, 32, 20, 61), (62, 28, 5, 23), (44, 62, 41, 10)]
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
