"""Single-addition ARX. Adder-latency probe.
x = val + key; x ^= rotl(x,13) ^ rotl(x,29); x = P(x); x ^= rotl(x,7); x ^= key
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
PBOX = np.array([(19 * i + 1) % 64 for i in range(64)], dtype=np.uint64)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _pbox64(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << PBOX[i]
    return y & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x + k) & M64                    # ADDER (nonlinear)
    x = (x ^ _rotl(x, 13) ^ _rotl(x, 29)) & M64
    x = _pbox64(x)
    x = (x ^ _rotl(x, 7)) & M64
    x = (x ^ k) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
