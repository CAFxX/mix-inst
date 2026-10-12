"""al_linchi3: 3 rounds of (lin + chi). Prototype for breaking 19.8u floor.
lin: x ^= rotl(x,a) ^ rotl(x,b)  (~1u/stage)
chi: x ^= ((~ra) & rb) ^ rc     (~3.3u/stage)
Expected: ~3*(1+3.3) = ~13u.
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F], dtype=np.uint64)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
LIN_ROTS = [(5, 13), (11, 29), (7, 23)]
CHI_ROTS = [(1, 2, 13), (7, 19, 5), (3, 11, 29)]
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64)
    k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for i in range(3):
        a, b = LIN_ROTS[i]
        x = (x ^ _rotl(x, a) ^ _rotl(x, b)) & M64
        c, d, e = CHI_ROTS[i]
        x = (x ^ ((~_rotl(x, c) & M64) & _rotl(x, d)) ^ _rotl(x, e)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
