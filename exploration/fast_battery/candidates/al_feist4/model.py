"""4-round Feistel, F = 8x 4-bit S-box only (no linear). Adder-latency probe."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
SBOX = np.array([0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054], dtype=np.uint64)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _sbox32(x):
    # 8x 4-bit S-box on 32 bits
    y = np.uint64(0)
    for i in range(8):
        nib = (x >> np.uint64(4*i)) & np.uint64(0xF)
        y |= SBOX[nib] << np.uint64(4*i)
    return y & M32
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    L = (x >> np.uint64(32)) & M32
    R = x & M32
    for i in range(4):
        rk = (_rotl(k, 13*(i+1)) ^ RC[i]) & M32
        F = _sbox32(R ^ rk)  # S-box only, no linear!
        L, R = R, (L ^ F) & M32
    return ((L << np.uint64(32)) | R) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
