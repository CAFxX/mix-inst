"""Wave-35 two-state: AND-cascade + Midori-Sb0 S-box layer (template F)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SB0 = np.array([12, 10, 13, 3, 14, 11, 15, 7, 8, 9, 1, 5, 0, 2, 4, 6], dtype=np.uint64)
AND_SCHED = [(27, 25, 37), (42, 26, 32), (2, 23, 38), (8, 62, 31), (20, 3, 27)]
INTER_ROT = 0
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _splayer64(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SB0[((x >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)] << np.uint64(4*i)
    return y & M64
_PBOX = [(9*i) % 64 for i in range(64)]
def _splayer(x):
    x = np.asarray(x, dtype=np.uint64)
    xs = _splayer64(x)
    y = np.zeros_like(xs)
    for i in range(64):
        y |= ((xs >> np.uint64(i)) & np.uint64(1)) << np.uint64(_PBOX[i])
    return y & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    ai = iter(AND_SCHED)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = _splayer(x)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
