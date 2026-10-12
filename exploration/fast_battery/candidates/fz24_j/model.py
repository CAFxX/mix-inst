"""Fused wave-24 fz24_j: 4-stage nibble-chi-2rot: x^=nibchi(x)^rotl(x,1)^rotl(x,61) (dead-bit fix) (gen_fused24.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
_PLANE = np.uint64(0x1111111111111111)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _maj(p, q, r):
    return ((p & q) ^ (p & r) ^ (q & r)) & M64
def _ch(p, q, r):
    return ((p & q) ^ ((~p) & r)) & M64
def _nibchi(x):
    p0 = x & _PLANE
    p1 = (x >> np.uint64(1)) & _PLANE
    p2 = (x >> np.uint64(2)) & _PLANE
    p3 = (x >> np.uint64(3)) & _PLANE
    q0 = p0 ^ ((~p1) & p2)
    q1 = p1 ^ ((~p2) & p3)
    q2 = p2 ^ ((~p3) & p0)
    q3 = p3 ^ ((~p0) & p1)
    return (q0 | (q1 << np.uint64(1)) | (q2 << np.uint64(2))
            | (q3 << np.uint64(3))) & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64

    x = (x ^ _nibchi(x) ^ _rotl(x,1) ^ _rotl(x,61)) & M64
    x = (x ^ _nibchi(x) ^ _rotl(x,1) ^ _rotl(x,61)) & M64
    x = (x ^ _nibchi(x) ^ _rotl(x,1) ^ _rotl(x,61)) & M64
    x = (x ^ _nibchi(x) ^ _rotl(x,1) ^ _rotl(x,61)) & M64
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
