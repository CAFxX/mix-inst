"""Bit-exact Python model for t6_wand3_5c (batch 30)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _u64(hi, lo):
    return (np.uint64(hi) << np.uint64(32)) | np.uint64(lo)
WAND3_5A = [((1, 2, 3), 13), ((11, 12, 13), 5), ((5, 6, 7), 29), ((17, 18, 19), 7), ((25, 26, 27), 37)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _wide(x, k, sched):
    for j, (ops, d) in enumerate(sched):
        t = _rotl64(x, ops[0])
        for a in ops[1:]:
            t = t & _rotl64(x, a)
        x = (x ^ t ^ _rotl64(x, d)) & M64
    return (x ^ _rotl64(k, 13)) & M64

def t6_wand3_5c(v, k):
    """5-stage AND3+spread, al key schedule, sched A."""
    return _wide((v ^ k) & M64, k, WAND3_5A)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_wand3_5c(np.uint64(v), np.uint64(k)))
    return t6_wand3_5c(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_wand3_5c(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '5-stage AND3+spread, al key schedule, sched A'}
