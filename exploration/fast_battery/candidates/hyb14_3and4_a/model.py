"""hyb14_3and4_a: 4x3AND (no S-box): do 4 strong stages suffice alone?. Self-contained bit-exact model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

AND3_SCHED = [(1, 2, 3, 13), (7, 19, 5, 29), (3, 11, 17, 7), (11, 23, 37, 19), (19, 41, 23, 31)]

def _mix_core(x, k):
    for (a, b, c, d) in AND3_SCHED[:4]:
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

