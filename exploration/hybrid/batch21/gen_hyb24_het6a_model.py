"""hyb24_het6a model: batch-24b guided heterogeneous 6-stage."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [('front', 17, 17, 26), ('front', 41, 56, 40), ('front', 55, 36, 4), ('front', 22, 4, 37), ('nolin', 52, 47, 22), ('nolin', 55, 55, 47)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for typ, a, b, c in STAGES:
        if typ == 'front':
            x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c)) & M64
        else:
            x = (x ^ (_rotl(x, a) & _rotl(x, b))) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
