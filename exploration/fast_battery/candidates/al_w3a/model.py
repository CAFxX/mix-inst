"""Wave-14 W3 GF(2^64)-diffused word-AND (screen z_seq=2.52)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [[(52, 26)], [(19, 44)], [(9, 54)]]
P = 0xBF58476D1CE4E5B9
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _gf(a, C):
    res = np.zeros(a.shape, dtype=np.uint64); p = a.copy(); c = int(C)
    while c:
        if c & 1: res ^= p
        hi = (p >> np.uint64(63)) & np.uint64(1)
        p = ((p << np.uint64(1)) & M64) ^ (hi * np.uint64(0x1B))
        c >>= 1
    return res
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for ands in STAGES:
        for a, b in ands:
            x = (x ^ (_rotl(x, a) & _rotl(x, b))) & M64
        x = _gf(x, P)
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
