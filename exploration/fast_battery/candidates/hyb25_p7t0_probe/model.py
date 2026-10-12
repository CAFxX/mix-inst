"""hyb25_p7t0_probe: batch-25 PNL 7-stage partial-nonlinear-layer cascade (triage-exact DIFF z=2.92)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
STAGES = [(7, 49, 3, 34), (6, 15, 7, 16), (38, 42, 57, 12), (23, 13, 57, 29), (59, 48, 24, 23), (23, 42, 50, 34), (15, 63, 48, 37)]
MASKS = [np.uint64(0xffffffff), np.uint64(0xf0f0f0f0f0f0f0f), np.uint64(0x5555555555555555), np.uint64(0xaaaaaaaaaaaaaaaa), np.uint64(0xffff0000ffff0000), np.uint64(0xffffffff), np.uint64(0xcccccccccccccccc)]
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for (a, b, c, d), mk in zip(STAGES, MASKS):
        x = (x ^ (((_rotl(x, a) & _rotl(x, b)) & mk) ^ _rotl(x, c) ^ _rotl(x, d))) & M64
    return ((x ^ _rotl(k, 13))) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
