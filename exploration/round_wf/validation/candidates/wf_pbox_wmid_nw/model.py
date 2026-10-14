"""Python model wrapper for wf_pbox_wmid_nw (round_wf validation).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`. Bit-exact vs impl.c."""
import numpy as np
_PTAB = np.array([16, 53, 0, 4, 1, 8, 24, 12, 7, 3, 13, 21, 6, 11, 28, 36, 14, 10, 20, 32, 19, 5, 37, 41, 15, 23, 45, 29, 25, 17, 33, 38, 27, 9, 44, 62, 26, 30, 40, 57, 35, 39, 52, 49, 2, 42, 48, 56, 34, 31, 58, 61, 22, 50, 47, 60, 55, 51, 43, 63, 59, 54, 46, 18], dtype=np.int64)
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
