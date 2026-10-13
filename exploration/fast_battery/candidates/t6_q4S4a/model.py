"""t6_q4S4a: batch-49 q4bS4 cascade (triage z=2.61)."""
M64 = 0xFFFFFFFFFFFFFFFF
NIBM = 0x1111111111111111
STAGES = [('Q4', 21, 37), ('Q4', 55, 60), ('Q4', 12, 19), ('Q4', 41, 15)]
def _rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64
def _q4(x):
    X0 = x & NIBM; X1 = (x >> 1) & NIBM
    X2 = (x >> 2) & NIBM; X3 = (x >> 3) & NIBM
    A01, A02, A12 = X0 & X1, X0 & X2, X1 & X2
    A03, A23 = X0 & X3, X2 & X3
    Y0 = NIBM ^ X0 ^ X2 ^ X3 ^ A01 ^ A02 ^ A12
    Y1 = NIBM ^ X0 ^ X2
    Y2 = X0 ^ X1 ^ X3 ^ A01 ^ A12 ^ A03 ^ A23
    Y3 = X1 ^ X3 ^ A01 ^ A12
    return (Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3)) & M64
def mix_np(V, K):
    import numpy as np
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & np.uint64(M64)
    for tag, a, b in STAGES:
        y = np.array([_q4(int(v)) for v in x], dtype=np.uint64)
        ra = ((y << np.uint64(a)) | (y >> np.uint64(64-a)))
        rb = ((y << np.uint64(b)) | (y >> np.uint64(64-b)))
        x = (y ^ ra ^ rb) & np.uint64(M64)
    x = (x ^ ((k << np.uint64(13)) | (k >> np.uint64(51)))) & np.uint64(M64)
    return x
def mix(v, k):
    x = (v ^ k) & M64
    for tag, a, b in STAGES:
        y = _q4(x)
        x = (y ^ _rotl(y, a) ^ _rotl(y, b)) & M64
    return (x ^ _rotl(k, 13)) & M64
