"""hyb15_3and4_C: 4x3AND schedule C: aggressive spread, varied d. Self-contained bit-exact model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

SCHED = [(7, 25, 49, 13), (5, 23, 47, 19), (11, 27, 51, 17), (3, 21, 43, 9)]

def _mix_core(x, k):
    for (a, b, c, d) in SCHED:
        ra, rb, rc, rd = _rotl(x, a), _rotl(x, b), _rotl(x, c), _rotl(x, d)
        x = (x ^ (ra & rb & rc) ^ rd) & M64
    return (x ^ _rotl(k, 13)) & M64

def mix_hash(val, key):
    return int(_mix_core(np.uint64(val) ^ np.uint64(key), np.uint64(key)))

def mix_np(V, K):
    V = np.asarray(V, dtype=np.uint64)
    K = np.asarray(K, dtype=np.uint64)
    return _mix_core(V ^ K, K)

def mix(v, k):
    return mix_hash(v, k)

