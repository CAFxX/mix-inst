"""hyb28_mu5_266a: batch-28 MU5 MUX-gate 5-stage cascade (triage-exact DIFF z=2.66, LIN proxy D=27)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(24, 19, 61, 46), (20, 12, 30, 22), (4, 45, 56, 31), (53, 48, 18, 32), (46, 3, 37, 49)]
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
