"""t6_chiS4a: batch-45 chiS4 cascade (triage z=2.82)."""
M64 = 0xFFFFFFFFFFFFFFFF
STAGES = [(23, 13), (28, 7), (45, 60), (29, 59)]
def _rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64
def _chi3(x):
    m0 = 0x9249249249249249 & 0x7FFFFFFFFFFFFFFF
    m1 = 0x2492492492492492
    m2 = 0x4924924924924924
    y0 = (x & m0) ^ ((~(x >> 1) & m0) & ((x >> 2) & m0))
    y1 = (x & m1) ^ ((~(x >> 1) & m1) & ((x << 1) & m1))
    y2 = (x & m2) ^ ((~(x << 2) & m2) & ((x << 1) & m2))
    return (y0 | y1 | y2 | (x & 0x8000000000000000)) & M64
def mix_np(V, K):
    import numpy as np
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & np.uint64(M64)
    for a, b in STAGES:
        y = np.array([_chi3(int(v)) for v in x], dtype=np.uint64)
        ra = ((y << np.uint64(a)) | (y >> np.uint64(64-a)))
        rb = ((y << np.uint64(b)) | (y >> np.uint64(64-b)))
        x = (y ^ ra ^ rb) & np.uint64(M64)
    x = (x ^ ((k << np.uint64(13)) | (k >> np.uint64(51)))) & np.uint64(M64)
    return x
def mix(v, k):
    x = (v ^ k) & M64
    for a, b in STAGES:
        y = _chi3(x)
        x = (y ^ _rotl(y, a) ^ _rotl(y, b)) & M64
    return (x ^ _rotl(k, 13)) & M64
