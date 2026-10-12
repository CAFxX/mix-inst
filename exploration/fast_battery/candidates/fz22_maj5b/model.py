"""Fused wave-22c fz22_maj5b: 5-stage x^=maj(ra,rb,rc), no lin term."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _maj(a, b, c):
    return (a & b) | (a & c) | (b & c)
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)
    kk = np.asarray(K, dtype=np.uint64)
    x = (x ^ _maj(_rotl(x,1),_rotl(x,7),_rotl(x,13))) & M64
    x = (x ^ _maj(_rotl(x,3),_rotl(x,11),_rotl(x,19))) & M64
    x = (x ^ _maj(_rotl(x,5),_rotl(x,15),_rotl(x,25))) & M64
    x = (x ^ _maj(_rotl(x,9),_rotl(x,21),_rotl(x,31))) & M64
    x = (x ^ _maj(_rotl(x,13),_rotl(x,27),_rotl(x,37))) & M64
    x = (x ^ _rotl(kk, 13)) & M64
    return x
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
