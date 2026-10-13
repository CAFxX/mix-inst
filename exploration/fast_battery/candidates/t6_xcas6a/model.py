"""Bit-exact Python model for t6_xcas6a (batch 17)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
SCHED_XA = [((3, 11, 7), (13, 5, 19)), ((17, 23, 9), (29, 15, 25)), ((7, 27, 13), (5, 21, 11)), ((23, 9, 17), (15, 29, 3)), ((11, 19, 23), (27, 7, 13)), ((29, 3, 27), (9, 17, 21))]
SCHED_XB = [((5, 13, 11), (19, 7, 23)), ((23, 3, 17), (11, 27, 5)), ((13, 29, 7), (3, 15, 29)), ((9, 21, 25), (17, 11, 7)), ((27, 7, 3), (23, 19, 15)), ((15, 25, 19), (7, 3, 27))]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rotl32(x, r):
    r %= 32
    x = x & M32
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _postwhite(x, k):
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64

def _xcas(v, k, sched):
    x = v ^ k
    for j, ((a, b, e), (c, d, f)) in enumerate(sched):
        lo = x & M32
        hi = (x >> np.uint64(32)) & M32
        rkj = _rk(k, j)
        rk_lo, rk_hi = rkj & M32, (rkj >> np.uint64(32)) & M32
        nlo = (lo ^ (_rotl32(lo, a) & _rotl32(hi, b)) ^
               _rotl32(lo, e) ^ rk_lo) & M32
        nhi = (hi ^ (_rotl32(hi, c) & _rotl32(lo, d)) ^
               _rotl32(hi, f) ^ rk_hi) & M32
        x = (nlo | (nhi << np.uint64(32))) & M64
    return _postwhite(x, k)

def t6_xcas6a(v, k):
    """6-stage cross-cascade, schedule A."""
    return _xcas(v, k, SCHED_XA)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_xcas6a(np.uint64(v), np.uint64(k)))
    return t6_xcas6a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_xcas6a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '6-stage cross-cascade (cross-AND halves), sched A'}
