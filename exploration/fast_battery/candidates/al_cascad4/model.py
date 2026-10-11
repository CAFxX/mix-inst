"""4-stage cascaded dual-AND. Adder-latency probe.
4 stages: x ^= (ra&rb) ^ (rc&rd) ^ re
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [
    (1,8,3,11,2),
    (7,19,5,17,13),
    (2,9,13,29,4),
    (11,23,19,37,7),
]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for (a,b,c,d,e) in STAGES:
        x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ (_rotl(x,c) & _rotl(x,d)) ^ _rotl(x,e)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
