"""hyb25_x6_269: batch-25 X6 XOR-fed-chain 6-stage cascade (triage-exact DIFF z=2.69)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(38, 12, 29, 17, 22), (15, 60, 4, 56, 33), (41, 10, 54, 47, 21), (62, 10, 39, 56, 32), (1, 42, 26, 9, 38), (23, 13, 43, 36, 3)]
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
