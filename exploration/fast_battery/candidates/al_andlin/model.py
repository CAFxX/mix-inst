"""4-round AND-nonlinearity + single-XOR linear. Adder-latency probe.
Round: x = L(P( N(x ^ rk) )), N(y) = y ^ (~rotl(y,1) & rotl(y,2)), L(z) = z ^ rotl(z,7)
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
PBOX = np.array([(19 * i + 1) % 64 for i in range(64)], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054], dtype=np.uint64)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _pbox64(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << PBOX[i]
    return y & M64
def _nonlin(y):
    # y ^ (~rotl(y,1) & rotl(y,2)) : depth 2 (NOT+AND, then XOR)
    return (y ^ ((~_rotl(y, 1)) & _rotl(y, 2))) & M64
def _lin(z):
    # z ^ rotl(z,7) : depth 1
    return (z ^ _rotl(z, 7)) & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    for i in range(4):
        rk = _rotl(k, 13*(i+1)) ^ RC[i]
        x = _lin(_pbox64(_nonlin(x ^ rk)))
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
