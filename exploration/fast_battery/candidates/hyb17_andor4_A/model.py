"""hyb17_andor4_A: 4x AND-OR hybrid schedule A. Self-contained bit-exact model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

SCHED = [(5, 19, 11, 37, 13), (7, 23, 13, 41, 17), (3, 17, 19, 43, 11), (11, 27, 7, 47, 23)]

def _mix_core(x, k):
    for (a, b, c, d, e) in SCHED:
        ra, rb = _rotl(x, a), _rotl(x, b)
        rc, rd = _rotl(x, c), _rotl(x, d)
        re = _rotl(x, e)
        x = (x ^ (ra & rb) ^ (rc | rd) ^ re) & M64
    return (x ^ _rotl(k, 13)) & M64

def mix_hash(val, key):
    return int(_mix_core(np.uint64(val) ^ np.uint64(key), np.uint64(key)))

def mix_np(V, K):
    V = np.asarray(V, dtype=np.uint64)
    K = np.asarray(K, dtype=np.uint64)
    return _mix_core(V ^ K, K)

def mix(v, k):
    return mix_hash(v, k)

