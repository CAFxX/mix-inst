"""t6_qlowS4a: batch-50 qlowS4 cascade (triage z=3.13)."""
M64 = 0xFFFFFFFFFFFFFFFF
NIBM = 0x1111111111111111
STAGES = [('QLOW', 46, 55), ('QLOW', 29, 43), ('QLOW', 12, 7), ('QLOW', 10, 26)]
def _rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64
def _qlow(x):
    X = [(x >> b) & NIBM for b in range(4)]
    A01 = X[0] & X[1]
    A02 = X[0] & X[2]
    A03 = X[0] & X[3]
    Y0 = X[0]
    Y1 = NIBM ^ X[0] ^ A01 ^ X[2] ^ X[3] ^ A03
    Y2 = X[0] ^ X[1] ^ A01 ^ A02 ^ A03
    Y3 = NIBM ^ X[1] ^ A01 ^ X[3]
    return (Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3)) & M64
def mix_np(V, K):
    import numpy as np
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & np.uint64(M64)
    for tag, a, b in STAGES:
        y = np.array([_qlow(int(v)) for v in x], dtype=np.uint64)
        ra = ((y << np.uint64(a)) | (y >> np.uint64(64-a)))
        rb = ((y << np.uint64(b)) | (y >> np.uint64(64-b)))
        x = (y ^ ra ^ rb) & np.uint64(M64)
    x = (x ^ ((k << np.uint64(13)) | (k >> np.uint64(51)))) & np.uint64(M64)
    return x
def mix(v, k):
    x = (v ^ k) & M64
    for tag, a, b in STAGES:
        y = _qlow(x)
        x = (y ^ _rotl(y, a) ^ _rotl(y, b)) & M64
    return (x ^ _rotl(k, 13)) & M64
