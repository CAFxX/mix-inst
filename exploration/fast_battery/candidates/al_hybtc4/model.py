"""Hybrid: 2x trichi (fan-in 7) + 2x chi (fan-in 3). Est: 2*5u + 2*3.3u = 16.6u."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054]
def _rotl(x, r):
    r = np.uint64(r % 64)
    return ((x << r) | (x >> (np.uint64(64) - r))) & M64 if r else x & M64
# Stage 0,1: trichi (7 rotations each)
TRI_STAGES = [(1,2,4,8,16,32,7),(3,9,13,19,29,5,11)]
# Stage 2,3: chi (3 rotations each)
CHI_STAGES = [(11,23,37),(19,41,23)]
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for i,(a,b,c,d,e,f,g) in enumerate(TRI_STAGES):
        ra,rb,rc,rd,re,rf,rg = _rotl(x,a),_rotl(x,b),_rotl(x,c),_rotl(x,d),_rotl(x,e),_rotl(x,f),_rotl(x,g)
        t = (x ^ ((~ra) & rb) ^ ((~rc) & rd) ^ ((~re) & rf) ^ rg) & M64
        x = t
    for i,(a,b,c) in enumerate(CHI_STAGES):
        ra,rb,rc = _rotl(x,a),_rotl(x,b),_rotl(x,c)
        t = (x ^ ((~ra) & rb) ^ rc) & M64
        x = t
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
