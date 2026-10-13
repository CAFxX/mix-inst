"""Bit-exact Python model for t6_het5a (batch 8)."""
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

def _fchi(x, ra, rb):
    return (x ^ (ra & (~rb & M64))) & M64

def _fand(x, ra, rb):
    return ((x & ra) ^ rb) & M64

def _fxorand(x, ra, rb, rc):
    return ((x & ra) ^ (x & rb) ^ rc) & M64

def _maj(a, b, c):
    return ((a & b) | (a & c) | (b & c)) & M64

SEQ_HET5 = ['maj', 'andor', 'chi', 'majxor', 'xor3and']
SCHED_HET5 = [(11, 23, 37, 5, 17, 29), (7, 19, 31, 43, 13, 25), (3, 15, 27, 39, 51, 9), (21, 33, 45, 1, 35, 47), (5, 29, 53, 17, 41, 11)]
OP_NROTS_B6 = {'maj': 4, 'andor': 5, 'chi': 3, 'majxor': 5, 'xor3and': 6}
def _hetero5_cascade(v, k):
    # 5-stage hetero from b6 ops (same _apply_op semantics as t6_models_b6)
    x = np.uint64(v) ^ np.uint64(k)
    for i, op in enumerate(SEQ_HET5):
        nrots = OP_NROTS_B6[op]
        rots = SCHED_HET5[i][:nrots]
        r = [_rotl64(x, t) for t in rots]
        if op == "maj":
            nl = (_maj(r[0], r[1], r[2]) ^ r[3]) & M64
        elif op == "andor":
            nl = (((r[0] & r[1]) | (r[2] & r[3])) ^ r[4]) & M64
        elif op == "chi":
            nl = (r[0] ^ (r[1] & (~r[2] & M64))) & M64
        elif op == "majxor":
            nl = (_maj(r[0], r[1], r[2]) ^ (r[3] & r[4])) & M64
        elif op == "xor3and":
            nl = (r[0] ^ r[1] ^ r[2] ^ (r[3] & r[4] & r[5])) & M64
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


def _scalar(v, k):
    return _hetero5_cascade(v, k)

_mix_np = _vec(_scalar)

def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _scalar(int(v), int(k))
    return _mix_np(v, k)

def mix_np(V, K):
    return _mix_np(V, K)

meta = {'desc': 'heterogeneous 5-stage: maj/andor/chi/majxor/xor3and'}
