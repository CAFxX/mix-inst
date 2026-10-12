"""hyb12_asb5a: 5xAND (al_and6a triplets 1-5) + rasC2_0 S-box layer + L(5,13): does S-box fix 5-stage DIFF death?. Self-contained bit-exact model."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SBOX = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]

def _rotl(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _sbox64(x):
    # vectorized: works for scalar np.uint64 AND ndarrays (mix_np path).
    # A scalar-only version (int(...) per nibble) raises TypeError on the
    # S1 vector path -- see hyb12-s1s2-20261010 INFRA_FAIL (2026-10-10).
    x = np.asarray(x, dtype=np.uint64)
    S = np.asarray(SBOX, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(16):
        y |= S[((x >> np.uint64(4*i)) & np.uint64(0xF))] << np.uint64(4*i)
    return y & M64

def _lin(x):
    return (x ^ _rotl(x, 5) ^ _rotl(x, 13)) & M64

AND6A = [(1, 2, 13), (7, 19, 5), (3, 11, 29), (17, 31, 7), (11, 23, 37), (19, 41, 23)]

def _mix_core(x, k):
    for (a, b, c) in AND6A[:5]:
        ra, rb, rc = _rotl(x, a), _rotl(x, b), _rotl(x, c)
        x = (x ^ (ra & rb) ^ rc) & M64
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
