""" fz31_s2: wave31 axis C (S-box layer probe) """
import numpy as np
M64 = 0xFFFFFFFFFFFFFFFF
PSBOX = np.array([0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2], dtype=np.uint64)
def _rotl(x, r):
    r &= 63
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & np.uint64(M64) if r else x & np.uint64(M64)
def _psbox(x):
    y = np.zeros_like(x)
    for n in range(16):
        y |= PSBOX[(x >> np.uint64(4*n)) & np.uint64(0xF)] << np.uint64(4*n)
    return y & np.uint64(M64)
def mix_np(v, k):
    x = (np.uint64(v) ^ np.uint64(k))
    x = (x ^ _psbox(x) ^ _rotl(x, 13)) & np.uint64(M64)
    x = (x ^ (_rotl(x,1) & _rotl(x,7)) ^ _rotl(x,13) ^ _rotl(x,29)) & np.uint64(M64)
    x = (x ^ (_rotl(x,5) & _rotl(x,15)) ^ _rotl(x,21)) & np.uint64(M64)
    x = (x ^ _rotl(np.uint64(k), 13)) & np.uint64(M64)
    return x
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
