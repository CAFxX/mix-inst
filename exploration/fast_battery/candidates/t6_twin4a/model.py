"""Bit-exact Python model for t6_twin4a (batch 26)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]

TWIN4_SCHED = [(1, 2, 5, 6, 19), (9, 10, 13, 14, 33), (3, 4, 17, 18, 45), (7, 8, 21, 22, 55)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def t6_twin4a(v, k):
    """4-stage twin-AND: x ^= (ra&rb)^(rc&rd)^re^rk."""
    x = (v ^ k) & M64
    for j, (a, b, c, d, e) in enumerate(TWIN4_SCHED):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b))
             ^ (_rotl64(x, c) & _rotl64(x, d))
             ^ _rotl64(x, e) ^ _rk(k, j)) & M64
    return (x ^ _rotl64(k, 13)) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_twin4a(np.uint64(v), np.uint64(k)))
    return t6_twin4a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_twin4a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4-stage twin-AND (density hypothesis)'}
