"""Bit-exact Python model for t6_lane4a (batch 32)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
LANE4A_A = [((1, 2), 7), ((5, 6), 23), ((9, 10), 41), ((13, 14), 29)]
LANE4A_B = [((17, 18), 11), ((21, 22), 37), ((25, 26), 3), ((29, 30), 19)]
LANE4A_S = [3, 17, 31, 43]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _lanes(x0, b0, sa, sb, feed):
    a = x0
    b = b0
    for j, (((pa, qa), da), ((pb, qb), db), s) in enumerate(zip(sa, sb, feed)):
        an = (a ^ (_rotl64(a, pa) & _rotl64(a, qa)) ^ _rotl64(a, da)) & M64
        bn = (b ^ (_rotl64(b, pb) & _rotl64(b, qb)) ^ _rotl64(b, db)
              ^ _rotl64(a, s)) & M64
        a, b = an, bn
    return a, b

def t6_lane4a(v, k):
    a, b = _lanes((v ^ k) & M64, _rotl64(k, 29), LANE4A_A, LANE4A_B, LANE4A_S)
    return (a ^ b ^ _rotl64(k, 13)) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_lane4a(np.uint64(v), np.uint64(k)))
    return t6_lane4a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

def mix_np(V, K):
    return t6_lane4a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4+4 cross-fed dual-lane cascade, sched A'}
