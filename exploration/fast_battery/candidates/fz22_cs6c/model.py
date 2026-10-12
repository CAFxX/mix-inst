"""Fused wave-22 fz22_cs6c: 6-stage carry-save, no rb: s'=s^c^ra (XOR3), c'=maj(s,c,ra)<<<1 (gen_fused22.py)."""
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
    ra = _rotl(s, 11)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 19)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 29)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 37)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 43)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra) & M64
    c = _rotl(m, 1)
    ra = _rotl(s, 47)
    m = _maj(s, c, ra)
    s = (s ^ c ^ ra) & M64
    c = _rotl(m, 1)
    sc = (s ^ c) & M64
    return (sc ^ _rotl(sc, 17)) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
