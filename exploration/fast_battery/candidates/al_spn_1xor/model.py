"""4-round SPN with single-XOR linear. Adder-latency probe.
Round: x = L(P(S(x ^ rk))), L(z) = z ^ rotl(z,7) [1 XOR level]
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SBOX = np.array([0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14], dtype=np.uint64)
PBOX = np.array([(19 * i + 1) % 64 for i in range(64)], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054], dtype=np.uint64)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _sbox64(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SBOX[((x >> np.uint64(4*i)) & np.uint64(0xF))] << np.uint64(4*i)
    return y & M64
def _pbox64(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << PBOX[i]
    return y & M64
def _lin(z):
    return (z ^ _rotl(z, 7)) & M64  # SINGLE XOR
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    for i in range(4):
        rk = _rotl(k, 13*(i+1)) ^ RC[i]
        x = _lin(_pbox64(_sbox64(x ^ rk)))
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
