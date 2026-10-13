"""Bit-exact Python model for t6_par5a (batch 19)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
SCHED_A = [(3, 11, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59), (13, 37, 53)]
SCHED_B = [(5, 13, 29), (19, 31, 43), (11, 23, 47), (29, 41, 61), (7, 17, 53)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _cascade(x, key, sched):
    for j, (a, b, c) in enumerate(sched):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rotl64(x, c) ^
             _rk(key, j)) & M64
    return x

def _par5(v, k, sched):
    # v=rs1, k=rs2; a keyed by rs2, b keyed by rs1 (cross-keyed)
    a = _cascade(v, k, sched)
    b = _cascade(k, v, sched)
    rkC = (_rotl64(v ^ k, 77) ^ RC64[7]) & M64
    out = (a ^ b ^ (a & b) ^ rkC) & M64
    return (out ^ (_rotl64(v ^ k, 13) >> np.uint64(32))) & M64

def t6_par5a(v, k):
    """Parallel dual 5-stage cascade + AND-combine, schedule A."""
    return _par5(v, k, SCHED_A)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_par5a(np.uint64(v), np.uint64(k)))
    return t6_par5a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_par5a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': 'parallel dual 5-stage cascade + AND-combine, A'}
