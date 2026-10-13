"""Bit-exact Python model for t6_norc6a (batch 15)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)
M16 = np.uint64(0xFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
SBOX_MIDORI0 = np.array([0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6], dtype=np.uint64)

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _postwhite(x, k):
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64

def _norc_cascade(v, k, sched):
    x = v ^ k
    for j, (a, b) in enumerate(sched):
        x = (x ^ (_rotl64(x, a) & _rotl64(x, b)) ^ _rk(k, j)) & M64
    return _postwhite(x, k)

SCHED_NORC6A = [(1, 23), (5, 37), (11, 43), (17, 53), (29, 7), (41, 13)]
def t6_norc6a(v, k):
    """6-stage AND-cascade, no linear rc term."""
    return _norc_cascade(v, k, SCHED_NORC6A)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_norc6a(np.uint64(v), np.uint64(k)))
    return t6_norc6a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_norc6a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '6-stage AND-cascade, no linear rc term'}
