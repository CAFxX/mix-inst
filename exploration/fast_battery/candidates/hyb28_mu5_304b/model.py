"""hyb28_mu5_304b: batch-28 MU5 MUX-gate 5-stage cascade (triage-exact DIFF z=3.04, LIN proxy D=28)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(33, 48, 16, 39), (54, 60, 51, 44), (34, 37, 30, 3), (48, 19, 43, 26), (42, 33, 61, 32)]
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
