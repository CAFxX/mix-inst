"""fz32_a: wave32 and3"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r &= 63
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M64 if r else x & M64
def mix_np(v, k):
    x = (np.uint64(v) ^ np.uint64(k))
    x = (x ^ (_rotl(x,1) & _rotl(x,2)) ^ _rotl(x,13)) & M64
    x = (x ^ (_rotl(x,7) & _rotl(x,19)) ^ _rotl(x,5)) & M64
    x = (x ^ (_rotl(x,3) & _rotl(x,11)) ^ _rotl(x,29)) & M64
    x = (x ^ (_rotl(x,17) & _rotl(x,31)) ^ _rotl(x,7)) & M64
    x = (x ^ (_rotl(x,11) & _rotl(x,23) & _rotl(x,37)) ^ _rotl(x,19)) & M64
    x = (x ^ _rotl(np.uint64(k), 13)) & M64
    return x
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
