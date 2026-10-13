"""Bit-exact Python model for t6_wand3_4a (batch 29)."""
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
WAND3_4A = [((1, 2, 3), 13), ((11, 12, 13), 5), ((5, 6, 7), 29), ((17, 18, 19), 7)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _wide(x, k, sched):
    for j, (ops, d) in enumerate(sched):
        t = _rotl64(x, ops[0])
        for a in ops[1:]:
            t = t & _rotl64(x, a)
        x = (x ^ t ^ _rotl64(x, d) ^ _rk(k, j)) & M64
    return (x ^ _rotl64(k, 13)) & M64

def t6_wand3_4a(v, k):
    """4-stage AND3 + spread (order-3 vs 4-stage DIFF wall)."""
    return _wide((v ^ k) & M64, k, WAND3_4A)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_wand3_4a(np.uint64(v), np.uint64(k)))
    return t6_wand3_4a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_wand3_4a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4-stage AND3+spread (order-3 wall test)'}
