"""Fused wave-16 fz16_d: 5-stage 3-term-linear, small Yosys-friendly rotations (speed) (gen_fused16.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    x = (x ^ ((_rotl(x,1) & _rotl(x,5)) ^ _rotl(x,9) ^ _rotl(x,13))) & M64
    x = (x ^ ((_rotl(x,2) & _rotl(x,6)) ^ _rotl(x,11) ^ _rotl(x,17))) & M64
    x = (x ^ ((_rotl(x,3) & _rotl(x,8)) ^ _rotl(x,14) ^ _rotl(x,19))) & M64
    x = (x ^ ((_rotl(x,5) & _rotl(x,11)) ^ _rotl(x,18) ^ _rotl(x,23))) & M64
    x = (x ^ ((_rotl(x,7) & _rotl(x,13)) ^ _rotl(x,21) ^ _rotl(x,27))) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
