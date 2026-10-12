"""hyb25_x6_245: batch-25 X6 XOR-fed-chain 6-stage cascade (triage-exact DIFF z=2.45)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(15, 16, 28, 51, 59), (57, 40, 55, 1, 38), (11, 47, 52, 26, 57), (50, 10, 12, 18, 29), (16, 10, 7, 44, 52), (19, 18, 14, 6, 8)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    a, b, s, e, c = STAGES[0]
    u = (_rotl(x, a) & _rotl(x, b)) & M64
    x = (x ^ u ^ _rotl(x, c)) & M64
    for (a, b, s, e, c) in STAGES[1:]:
        u = (_rotl(x, a) & ((_rotl(u, s) ^ _rotl(x, e)) & M64)) & M64
        x = (x ^ u ^ _rotl(x, c)) & M64
    return ((x ^ _rotl(k, 13))) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
