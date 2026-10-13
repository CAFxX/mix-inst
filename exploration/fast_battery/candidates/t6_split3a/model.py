"""Bit-exact Python model for t6_split3a (batch 15)."""
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

def _rotl32(x, r):
    r %= 32
    x = x & M32
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32

SPLIT_BASE = [[(3, 11, 23), (13, 29, 7)], [(17, 5, 27), (23, 9, 15)], [(29, 13, 3), (7, 19, 25)]]
SPLIT_CROSS = [(5, 9), (11, 15), (17, 21)]
def t6_split3a(v, k):
    """3 super-stages: parallel 32-bit 2-stage cascades per half + cross."""
    x = v ^ k
    for s in range(3):
        lo = x & M32
        hi = (x >> np.uint64(32)) & M32
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = SPLIT_BASE[s][t]
            # lo uses base triple, hi uses base triple offset by +7 (mod 32)
            p = ((b1) % 32, (b2) % 32, (b3) % 32)
            q = ((b1 + 7) % 32, (b2 + 7) % 32, (b3 + 7) % 32)
            lo = (lo ^ (_rotl32(lo, p[0]) & _rotl32(lo, p[1])) ^
                  _rotl32(lo, p[2]) ^ (_rk(k, j) & M32)) & M32
            hi = (hi ^ (_rotl32(hi, q[0]) & _rotl32(hi, q[1])) ^
                  _rotl32(hi, q[2]) ^ (_rk(k, j) & M32)) & M32
            hi = hi & M32
        r1, r2 = SPLIT_CROSS[s]
        nlo = (lo ^ _rotl32(hi, r1) ^ (_rk(k, 6 + 2 * s) & M32)) & M32
        nhi = (hi ^ _rotl32(lo, r2) ^ (_rk(k, 7 + 2 * s) & M32)) & M32
        x = (nlo | (nhi << np.uint64(32))) & M64
    return _postwhite(x, k)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_split3a(np.uint64(v), np.uint64(k)))
    return t6_split3a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_split3a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '3 super-stages, parallel 32-bit cascades + cross'}
