"""Fused wave-25 fz25_b: 5-stage shared-lin-diff: p=rotl(x0,7)^rotl(x0,41) (gen_fused25.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    p = (_rotl(x, 7) ^ _rotl(x, 41)) & M64
    x = (x ^ (_rotl(x,2) & _rotl(x,9)) ^ _rotl(p,0)) & M64
    x = (x ^ (_rotl(x,4) & _rotl(x,13)) ^ _rotl(p,17)) & M64
    x = (x ^ (_rotl(x,6) & _rotl(x,17)) ^ _rotl(p,33)) & M64
    x = (x ^ (_rotl(x,11) & _rotl(x,23)) ^ _rotl(p,11)) & M64
    x = (x ^ (_rotl(x,15) & _rotl(x,27)) ^ _rotl(p,47)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
