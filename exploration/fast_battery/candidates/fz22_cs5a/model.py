"""Fused wave-22 fz22_cs5a: 5-stage carry-save (gen_fused22.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _maj(a, b, c):
    return (a & b) | (a & c) | (b & c)
def mix_np(V, K):
    s = np.asarray(V, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)
    c = _rotl(np.asarray(K, dtype=np.uint64), 13)
    ra = _rotl(s, 1); rb = _rotl(c, 11)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 7); rb = _rotl(c, 19)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 13); rb = _rotl(c, 29)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 17); rb = _rotl(c, 37)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 23); rb = _rotl(c, 43)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    sc = (s ^ c) & M64
    return (sc ^ _rotl(sc, 17)) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
