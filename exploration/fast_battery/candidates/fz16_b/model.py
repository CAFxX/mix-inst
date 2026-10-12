"""Fused wave-16 fz16_b: 4-stage dual-AND 3-term-linear: x^=(ra&rb)^(rc&rd)^re^rf^rg (gen_fused16.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    x = (x ^ ((_rotl(x,1) & _rotl(x,7)) ^ (_rotl(x,13) & _rotl(x,29)) ^ _rotl(x,37) ^ _rotl(x,43) ^ _rotl(x,53))) & M64
    x = (x ^ ((_rotl(x,3) & _rotl(x,11)) ^ (_rotl(x,19) & _rotl(x,31)) ^ _rotl(x,41) ^ _rotl(x,47) ^ _rotl(x,59))) & M64
    x = (x ^ ((_rotl(x,5) & _rotl(x,15)) ^ (_rotl(x,23) & _rotl(x,37)) ^ _rotl(x,43) ^ _rotl(x,53) ^ _rotl(x,61))) & M64
    x = (x ^ ((_rotl(x,9) & _rotl(x,21)) ^ (_rotl(x,29) & _rotl(x,41)) ^ _rotl(x,49) ^ _rotl(x,57) ^ _rotl(x,7))) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
