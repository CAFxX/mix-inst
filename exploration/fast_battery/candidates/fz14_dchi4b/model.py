"""Fused wave-14 fz14_dchi4b: 4-stage dual-AND chi (alt rotations) (gen_fused14.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    x = (x ^ (_rotl(x,2) & _rotl(x,9)) ^ (_rotl(x,17) & _rotl(x,35)) ^ _rotl(x,7)) & M64
    x = (x ^ (_rotl(x,7) & _rotl(x,15)) ^ (_rotl(x,27) & _rotl(x,45)) ^ _rotl(x,13)) & M64
    x = (x ^ (_rotl(x,13) & _rotl(x,25)) ^ (_rotl(x,37) & _rotl(x,55)) ^ _rotl(x,19)) & M64
    x = (x ^ (_rotl(x,19) & _rotl(x,33)) ^ (_rotl(x,47) & _rotl(x,61)) ^ _rotl(x,27)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
