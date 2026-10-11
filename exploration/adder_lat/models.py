"""Python models for adder-latency research constructions."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

# rasC2_0 S-box (from the frontier)
SBOX_RASC2_0 = np.array([0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14], dtype=np.uint64)
PBOX_PBA19 = np.array([(19 * i + 1) % 64 for i in range(64)], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
               0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054], dtype=np.uint64)

def _rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _sbox64(x, sbox):
    y = np.zeros_like(x)
    for i in range(16):
        y |= sbox[((x >> np.uint64(4 * i)) & np.uint64(0xF))] << np.uint64(4 * i)
    return y & M64

def _pbox64(x, pbox):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << pbox[i]
    return y & M64

def _lin(x, a, b):
    return (x ^ _rotl(x, a) ^ _rotl(x, b)) & M64

def spn_3r(V, K, sbox=SBOX_RASC2_0, pbox=PBOX_PBA19, rots=(5,13)):
    """3-round SPN (vs 4-round frontier)."""
    x = np.asarray(V, dtype=np.uint64)
    k = np.asarray(K, dtype=np.uint64)
    a, b = rots
    for i in range(3):
        rk = _rotl(k, 13 * (i + 1)) ^ RC[i]
        x = _lin(_pbox64(_sbox64(x ^ rk, sbox), pbox), a, b)
    return x & M64

def spn_3r_mix(v, k):
    return int(spn_3r(np.uint64(v), np.uint64(k)))
