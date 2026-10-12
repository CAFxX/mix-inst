"""hyb20_dm4a: batch-20 fused maj+chi [dm4]: dm(47,26,63,62,7,8) -> dm(63,47,4,59,25,45) -> dm(45,43,18,11,49,62) -> dm(47,11,53,34,10,23) (hill-climbed proxy z=6.6, est=18.80u)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [('dm', 47, 26, 63, 62, 7, 8), ('dm', 63, 47, 4, 59, 25, 45), ('dm', 45, 43, 18, 11, 49, 62), ('dm', 47, 11, 53, 34, 10, 23)]

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _maj(a,b,c): return (a & b) | (b & c) | (a & c)

def _stage(x, st):
    kind, a, b, c, d, e, f = st
    ra, rb, rc = _rotl(x,a), _rotl(x,b), _rotl(x,c)
    rd, re, rf = _rotl(x,d), _rotl(x,e), _rotl(x,f)
    m1 = _maj(x,ra,rb)
    if kind == 'fm':
        return (x ^ m1 ^ rc ^ ((~rd) & re) ^ rf) & M64
    if kind == 'dm':
        return (x ^ m1 ^ rc ^ _maj(x,rd,re) ^ rf) & M64
    return (m1 ^ ((~rd) & re) ^ rf) & M64

def _mix_core(x):
    for st in STAGES:
        x = _stage(x, st)
    return x & M64

def mix_hash(val, key):
    return int(_mix_core(np.uint64(val) ^ np.uint64(key)))

def mix_np(V, K):
    V = np.asarray(V, dtype=np.uint64)
    K = np.asarray(K, dtype=np.uint64)
    return _mix_core(V ^ K)

def mix(v, k):
    return mix_hash(v, k)
