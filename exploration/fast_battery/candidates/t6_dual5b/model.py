"""Bit-exact Python model for t6_dual5b (batch 27)."""
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
DUAL5_SCHED_B = [(3, 4, 11, 12), (7, 8, 33, 34), (15, 16, 41, 42), (19, 20, 49, 50), (27, 28, 53, 54)]

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

def t6_dual5b(v, k):
    """5-stage dual-AND, schedule B (robustness)."""
    return _dual((v ^ k) & M64, k, DUAL5_SCHED_B)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_dual5b(np.uint64(v), np.uint64(k)))
    return t6_dual5b(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_dual5b(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '5-stage dual-AND, sched B'}
