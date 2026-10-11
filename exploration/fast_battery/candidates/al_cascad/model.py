"""Cascaded AND-rotation (no S-box, no rounds). Adder-latency probe.
8 stages: x ^= (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
# Different rotations per stage for diffusion
STAGES = [(1,8,2), (3,11,5), (7,19,13), (2,9,4), (5,17,11), (13,29,7), (11,23,17), (19,37,23)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for (a,b,c) in STAGES:
        x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
