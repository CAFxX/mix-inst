"""Bit-exact Python model for t6_xc4c (batch 25)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
XC_SCHED4C = [(2, 3, 17, 11), (9, 10, 25, 5), (4, 6, 41, 17), (15, 16, 33, 29)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _xc(x, k, sched):
    t_prev = np.uint64(0)
    if not np.ndim(x) == 0:
        t_prev = np.zeros_like(x)
    for j, s in enumerate(sched):
        a, b, c, rot = s
        t = _rotl64(x, a) & _rotl64(x, b)
        x = (x ^ t ^ _rotl64(x, c) ^ _rk(k, j) ^ _rotl64(t_prev, rot)) & M64
        t_prev = t
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64

def t6_xc4c(v, k):
    """4-stage cross-coupled, close AND pairs, alternative schedule."""
    x = (v ^ k) & M64
    return _xc(x, k, XC_SCHED4C)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_xc4c(np.uint64(v), np.uint64(k)))
    return t6_xc4c(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_xc4c(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4-stage cross-coupled, close AND pairs, alt schedule'}
