"""Bit-exact Python model for t6_pchi6b (batch 23)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
PCHI_SCHED6 = [(5, 17, 29, 41, 53), (11, 23, 37, 47, 7), (3, 19, 31, 43, 59), (13, 27, 39, 51, 9), (7, 21, 33, 45, 57), (15, 25, 35, 49, 61)]
PCHI_SCHED5 = [(5, 17, 29, 41, 53), (11, 23, 37, 47, 7), (3, 19, 31, 43, 59), (13, 27, 39, 51, 9), (7, 21, 33, 45, 57)]
PXOR_SCHED6 = [(5, 17, 29, 41, 53, 61), (11, 23, 37, 47, 7, 59), (3, 19, 31, 43, 57, 9), (13, 27, 39, 51, 21, 63), (1, 15, 25, 35, 45, 55), (9, 22, 34, 46, 58, 62)]
PCHI_SCHED6B = [(9, 25, 43, 55, 3), (19, 33, 47, 61, 13), (1, 23, 37, 53, 17), (11, 29, 41, 59, 7), (21, 35, 49, 63, 5), (15, 31, 45, 57, 27)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _pchi(x, k, sched, invert_first):
    """Shared chi-combine stage loop. invert_first=True -> (p1 & ~p2)."""
    for j, s in enumerate(sched):
        a, b, c, d, e = s
        p1 = _rotl64(x, a) & _rotl64(x, b)
        p2 = _rotl64(x, c) & _rotl64(x, d)
        if invert_first:
            comb = p1 & ~p2
        else:
            comb = ~p1 & p2
        x = (x ^ comb ^ _rotl64(x, e) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64

def t6_pchi6b(v, k):
    """6-stage parallel chi-combine: x ^= (~p1&p2)^re^rk, alt schedule."""
    x = (v ^ k) & M64
    return _pchi(x, k, PCHI_SCHED6B, False)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_pchi6b(np.uint64(v), np.uint64(k)))
    return t6_pchi6b(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_pchi6b(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '6-stage parallel chi-combine (~p1&p2), alt schedule'}
