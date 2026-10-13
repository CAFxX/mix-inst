"""Bit-exact Python model for t6_hx5a (batch 9)."""
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

def _andxor(ra, rb, rc):
    return ((ra & rb) ^ rc) & M64

def _orxor(ra, rb, rc):
    return ((ra | rb) ^ rc) & M64

def _maj3(ra, rb, rc):
    return ((ra & rb) | (ra & rc) | (rb & rc)) & M64

OP_FN = {'ANDXOR': _andxor, 'ORXOR': _orxor, 'MAJ': _maj3}
def _hetero_xor_cascade(v, k, seq, sched):
    x = np.uint64(v) ^ np.uint64(k)
    n = len(seq)
    for i in range(n):
        op = seq[i]
        ra, rb, rc = [_rotl64(x, t) for t in sched[i]]
        nl = OP_FN[op](ra, rb, rc)
        rk = _rotl64(np.uint64(k), 13 * (i + 1)) ^ RC64[i % 8]
        x = (x ^ nl ^ rk) & M64
    x = (x ^ (_rotl64(np.uint64(k), 13) >> np.uint64(32))) & M64
    return x

def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f

SEQ = ['ANDXOR', 'ORXOR', 'MAJ', 'ANDXOR', 'ORXOR']
SCHED = [(11, 29, 47), (23, 41, 7), (7, 37, 19), (19, 53, 5), (5, 31, 13), (13, 47, 23)]

def _scalar(v, k):
    return _hetero_xor_cascade(v, k, SEQ, SCHED)
_mix_np = _vec(_scalar)

def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _scalar(int(v), int(k))
    return _mix_np(v, k)
def mix_np(V, K):
    return _mix_np(V, K)
meta = {'desc': 'hetero x^= 5-stage simple: ANDXOR/ORXOR/MAJ/ANDXOR/ORXOR'}
