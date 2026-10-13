"""Bit-exact Python model for t6_and4_6a (batch 22)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
AND3_SCHED6 = [(3, 11, 23, 41), (17, 29, 41, 7), (7, 31, 47, 23), (23, 43, 59, 11), (11, 37, 53, 5), (5, 19, 61, 29)]
AND3_SCHED5 = [(3, 11, 23, 41), (17, 29, 41, 7), (7, 31, 47, 23), (23, 43, 59, 11), (11, 37, 53, 5)]
AND4_SCHED6 = [(3, 11, 23, 41, 53), (17, 29, 41, 7, 19), (7, 31, 47, 23, 5), (23, 43, 59, 11, 37), (11, 37, 53, 5, 61), (5, 19, 61, 29, 43)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def t6_and4_6a(v, k):
    """6-stage quad-AND: x ^= (ra&rb&rc&rd)^re^rk."""
    x = (v ^ k) & M64
    for j in range(6):
        a, b, c, d, e = AND4_SCHED6[j]
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b) & _rotl64(x, c) & _rotl64(x, d))
             ^ _rotl64(x, e) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_and4_6a(np.uint64(v), np.uint64(k)))
    return t6_and4_6a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_and4_6a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '6-stage quad-AND (quartic)'}
