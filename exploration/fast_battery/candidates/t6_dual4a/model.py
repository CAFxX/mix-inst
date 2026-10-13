"""Bit-exact Python model for t6_dual4a (batch 27)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _u64(hi, lo):
    return (np.uint64(hi) << np.uint64(32)) | np.uint64(lo)
RC64 = [_u64(0x9E3779B9, 0x7F4A7C15), _u64(0x3C6EF372, 0xFE94F82A),
        _u64(0xDAA66D2C, 0x7DDF743F), _u64(0x78DDE6E5, 0xFD29F054),
        _u64(0x2545F491, 0x4F6CDD1D),
        _u64(0x9E3779B9, 0x7F4A7C15) ^ np.uint64(0xDEADBEEF),
        _u64(0x3C6EF372, 0xFE94F82A) ^ np.uint64(0x12345678),
        _u64(0xDAA66D2C, 0xDD6129B3E)]
DUAL4_SCHED = [(1, 2, 9, 10), (13, 14, 21, 22), (5, 6, 29, 30), (17, 18, 37, 38)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _dual(x, k, sched):
    for j, (a, b, c, d) in enumerate(sched):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b))
             ^ (_rotl64(x, c) & _rotl64(x, d)) ^ _rk(k, j)) & M64
    return (x ^ _rotl64(k, 13)) & M64

def t6_dual4a(v, k):
    """4-stage dual-AND (4-stage wall test with 2x density)."""
    return _dual((v ^ k) & M64, k, DUAL4_SCHED)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_dual4a(np.uint64(v), np.uint64(k)))
    return t6_dual4a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_dual4a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4-stage dual-AND (density vs 4-stage wall)'}
