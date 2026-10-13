"""Bit-exact Python model for t6_hyb5a (batch 16)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
SINGLE_SCHED = [(3, 11, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59), (13, 37, 53), (5, 19, 61)]
DUAL_SCHED = [(3, 11, 23, 37), (17, 29, 41, 53), (7, 31, 47, 59), (23, 43, 5, 61)]
DUALRE_SCHED = [(3, 11, 23, 37, 53), (17, 29, 41, 53, 7)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _postwhite(x, k):
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64

def _single(x, k, j, sched):
    a, b, c = sched
    return (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c) ^ _rk(k, j)) & M64

def _dual(x, k, j, sched):
    a, b, c, d = sched
    return (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^
            (_rotl64(x, c) & _rotl64(x, d)) ^ _rk(k, j)) & M64

def _dualre(x, k, j, sched):
    a, b, c, d, e = sched
    return (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^
            (_rotl64(x, c) & _rotl64(x, d)) ^ _rotl64(x, e) ^ _rk(k, j)) & M64

def t6_hyb5a(v, k):
    """4 singles + dual (no re) LAST."""
    x = v ^ k
    for j in range(4):
        x = _single(x, k, j, SINGLE_SCHED[j])
    x = _dual(x, k, 4, DUAL_SCHED[0])
    return _postwhite(x, k)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_hyb5a(np.uint64(v), np.uint64(k)))
    return t6_hyb5a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_hyb5a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4 singles + dual-AND (no re) last'}
