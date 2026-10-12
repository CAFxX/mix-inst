"""2-round wide-trail SPN (128-bit state). Adder-latency probe.
Round: x(64) -> expand(128) -> S-box(32x4b) -> compress(64) -> linear
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SBOX = np.array([0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14], dtype=np.uint64)
# P-box for 128-bit (simple: interleave)
PBOX128 = np.array([ (i*37+11) % 128 for i in range(128) ], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A], dtype=np.uint64)
def _rotl(x, r, w=64):
    r %= w
    if r == 0: return x
    if w == 64:
        return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M64
    else:  # 128-bit as two uint64
        hi, lo = x
        # Simplified: just do 64-bit rotations on each half
        return ( ((hi << np.uint64(r)) | (hi >> np.uint64(64-r))) & M64,
                 ((lo << np.uint64(r)) | (lo >> np.uint64(64-r))) & M64 )
def _sbox128(hi, lo):
    # 32x 4-bit S-box: 16 on hi, 16 on lo
    yhi = np.uint64(0); ylo = np.uint64(0)
    for i in range(16):
        yhi |= SBOX[((hi >> np.uint64(4*i)) & np.uint64(0xF))] << np.uint64(4*i)
        ylo |= SBOX[((lo >> np.uint64(4*i)) & np.uint64(0xF))] << np.uint64(4*i)
    return yhi & M64, ylo & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    # Expand 64->128: (x, x ^ rotl(x, 31))
    hi = x ^ k
    lo = (x ^ _rotl(x, 31)[0] if isinstance(_rotl(x,31), tuple) else x ^ _rotl(x, 31)) & M64
    # Actually simpler: hi = x, lo = rotl(x, 31)
    hi = (x ^ k) & M64
    lo = _rotl(x, 31) & M64
    for i in range(2):
        # S-box layer (128-bit)
        hi, lo = _sbox128(hi, lo)
        # Linear: mix hi/lo, compress
        # hi' = hi ^ lo ^ rotl(hi, 13)
        # lo' = lo ^ hi ^ rotl(lo, 29)
        # Then for next round, re-expand? No, keep 128-bit.
        # For output after 2 rounds, compress: out = hi ^ lo ^ rotl(hi,7)
        nhi = (hi ^ lo ^ _rotl(hi, 13)) & M64
        nlo = (lo ^ hi ^ _rotl(lo, 29)) & M64
        hi, lo = nhi, nlo
        # Key injection
        rk = (_rotl(k, 13*(i+1)) ^ RC[i]) & M64
        hi ^= rk; lo ^= _rotl(rk, 17)
    # Compress 128->64
    out = (hi ^ lo ^ _rotl(hi, 7)) & M64
    return out & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
