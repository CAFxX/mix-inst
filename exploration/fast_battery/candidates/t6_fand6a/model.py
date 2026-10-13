"""Bit-exact Python model for t6_fand6a (batch 8)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _fchi(x, ra, rb):
    return (x ^ (ra & (~rb & M64))) & M64

def _fand(x, ra, rb):
    return ((x & ra) ^ rb) & M64

def _fxorand(x, ra, rb, rc):
    return ((x & ra) ^ (x & rb) ^ rc) & M64

def _fused_cascade(v, k, fn, sched, nrots):
    x = np.uint64(v) ^ np.uint64(k)
    for i in range(6):
        rots = sched[i][:nrots]
        r = [_rotl64(x, t) for t in rots]
        rk = _rotl64(np.uint64(k), 13 * (i + 1)) ^ RC64[i % 8]
        x = (fn(x, *r) ^ rk) & M64
    x = (x ^ (_rotl64(np.uint64(k), 13) >> np.uint64(32))) & M64
    return x

def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f

SCHED = [(11, 29), (23, 41), (7, 37), (19, 53), (5, 31), (13, 47)]
_FN = _fand
_NROTS = 2

def _scalar(v, k):
    return _fused_cascade(v, k, _FN, SCHED, _NROTS)

_mix_np = _vec(_scalar)

def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _scalar(int(v), int(k))
    return _mix_np(v, k)

def mix_np(V, K):
    return _mix_np(V, K)

meta = {'desc': 'fused 6-stage: x=(x&ra)^rb'}
