"""Fused wave-22 fz22_cs6b: 6-stage carry-save, alt schedule (gen_fused22.py)."""
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
    ra = _rotl(s, 3); rb = _rotl(c, 13)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 9); rb = _rotl(c, 23)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 15); rb = _rotl(c, 33)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 21); rb = _rotl(c, 41)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 27); rb = _rotl(c, 49)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 35); rb = _rotl(c, 53)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra ^ rb) & M64
    c = _rotl(m, 1)
    sc = (s ^ c) & M64
    return (sc ^ _rotl(sc, 17)) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
