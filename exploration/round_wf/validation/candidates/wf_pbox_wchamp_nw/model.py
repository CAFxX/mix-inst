"""Python model wrapper for wf_pbox_wchamp_nw (round_wf validation).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`. Bit-exact vs impl.c."""
import numpy as np
_PTAB = np.array([12, 0, 8, 4, 13, 3, 5, 10, 7, 1, 9, 16, 11, 15, 6, 17, 14, 19, 2, 21, 18, 22, 29, 25, 23, 28, 24, 33, 27, 30, 37, 32, 26, 34, 41, 31, 35, 36, 20, 40, 38, 42, 44, 48, 43, 39, 52, 46, 47, 50, 61, 56, 51, 58, 53, 63, 54, 49, 57, 60, 55, 59, 45, 62], dtype=np.int64)
_S1 = np.array([0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10], dtype=np.int64)
_GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)
_MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl64(x, r):
    r &= 63
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & _MASK64 if r else x & _MASK64
def _rk(k, i):
    with np.errstate(over="ignore"):
        return (_rotl64(k, 13 * (i + 1)) ^ (np.uint64(i + 1) * _GOLDEN64)) & _MASK64
def _sbox16(x):
    out = np.zeros_like(x); xv = x & _MASK64
    for i in range(16):
        nib = ((xv >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(_S1, nib).astype(np.uint64) << np.uint64(4*i)
    return out & _MASK64
def _pbox(x):
    out = np.zeros_like(x); xv = x & _MASK64
    for i, d in enumerate(_PTAB):
        out |= ((xv >> np.uint64(i)) & np.uint64(1)) << np.uint64(int(d))
    return out & _MASK64
def _lin(x):
    return (x ^ _rotl64(x, 3) ^ _rotl64(x, 11)) & _MASK64
def mix_np(v, k):
    x = np.asarray(v, dtype=np.uint64) & _MASK64
    kk = np.asarray(k, dtype=np.uint64) & _MASK64
    for i in range(4):
        x = _lin(_pbox(_sbox16(x ^ _rk(kk, i))))
    return x & _MASK64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
