"""hyb14_3and4s_a: 4x3AND + SBOX + L(5,13): hybrid with stronger base. Self-contained bit-exact model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SBOX = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _sbox64(x):
    x = np.asarray(x, dtype=np.uint64)
    S = np.asarray(SBOX, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(16):
        y |= S[((x >> np.uint64(4*i)) & np.uint64(0xF))] << np.uint64(4*i)
    return y & M64

def _lin(x):
    return (x ^ _rotl(x, 5) ^ _rotl(x, 13)) & M64

AND3_SCHED = [(1, 2, 3, 13), (7, 19, 5, 29), (3, 11, 17, 7), (11, 23, 37, 19), (19, 41, 23, 31)]

def _mix_core(x, k):
    for (a, b, c, d) in AND3_SCHED[:4]:
        ra, rb, rc, rd = _rotl(x, a), _rotl(x, b), _rotl(x, c), _rotl(x, d)
        x = (x ^ (ra & rb & rc) ^ rd) & M64
    x = _sbox64(x)
    x = _lin(x)
    return (x ^ _rotl(k, 13)) & M64

def mix_hash(val, key):
    return int(_mix_core(np.uint64(val) ^ np.uint64(key), np.uint64(key)))

def mix_np(V, K):
    V = np.asarray(V, dtype=np.uint64)
    K = np.asarray(K, dtype=np.uint64)
    return _mix_core(V ^ K, K)

def mix(v, k):
    return mix_hash(v, k)

