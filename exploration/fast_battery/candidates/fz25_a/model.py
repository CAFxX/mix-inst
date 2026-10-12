"""Fused wave-25 fz25_a: 5-stage shared-lin-diff: p=rotl(x0,13)^rotl(x0,29) (gen_fused25.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    p = (_rotl(x, 13) ^ _rotl(x, 29)) & M64
    x = (x ^ (_rotl(x,1) & _rotl(x,7)) ^ _rotl(p,0)) & M64
    x = (x ^ (_rotl(x,3) & _rotl(x,11)) ^ _rotl(p,13)) & M64
    x = (x ^ (_rotl(x,5) & _rotl(x,15)) ^ _rotl(p,29)) & M64
    x = (x ^ (_rotl(x,9) & _rotl(x,21)) ^ _rotl(p,7)) & M64
    x = (x ^ (_rotl(x,13) & _rotl(x,25)) ^ _rotl(p,31)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
