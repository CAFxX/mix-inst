"""hyb7_and3_5: 5-stage 3-input AND cascade: x ^= (ra&rb&rc)^rd. Self-contained bit-exact model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _mix_core(x, k):
    ra, rb, rc, rd = _rotl(x, 1), _rotl(x, 2), _rotl(x, 13), _rotl(x, 41)
    x = (x ^ (ra & rb & rc) ^ rd) & M64
    ra, rb, rc, rd = _rotl(x, 7), _rotl(x, 19), _rotl(x, 5), _rotl(x, 37)
    x = (x ^ (ra & rb & rc) ^ rd) & M64
    ra, rb, rc, rd = _rotl(x, 3), _rotl(x, 11), _rotl(x, 29), _rotl(x, 47)
    x = (x ^ (ra & rb & rc) ^ rd) & M64
    ra, rb, rc, rd = _rotl(x, 17), _rotl(x, 31), _rotl(x, 7), _rotl(x, 43)
    x = (x ^ (ra & rb & rc) ^ rd) & M64
    ra, rb, rc, rd = _rotl(x, 11), _rotl(x, 23), _rotl(x, 37), _rotl(x, 5)
    x = (x ^ (ra & rb & rc) ^ rd) & M64
    return (x ^ _rotl(k, 13)) & M64

def mix_hash(val, key):
    return int(_mix_core(np.uint64(val) ^ np.uint64(key), np.uint64(key)))

def mix_np(V, K):
    V = np.asarray(V, dtype=np.uint64)
    K = np.asarray(K, dtype=np.uint64)
    return _mix_core(V ^ K, K)

def mix(v, k):
    return mix_hash(v, k)
