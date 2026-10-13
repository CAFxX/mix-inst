"""Bit-exact Python model for t6_quad3a (batch 15)."""
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

def _rotl16(x, r):
    r %= 16
    x = x & M16
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(16 - r))) & M16

QUAD_BASE = [[(3, 9, 13), (7, 2, 11)], [(11, 5, 1), (13, 8, 4)], [(6, 12, 2), (9, 4, 14)]]
QUAD_CROSS = [(3, 7), (5, 11), (9, 13)]
def t6_quad3a(v, k):
    """3 super-stages: 4 parallel 16-bit 2-stage cascades + full cross."""
    x = v ^ k
    for s in range(3):
        lanes = [(x >> np.uint64(16 * i)) & M16 for i in range(4)]
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = QUAD_BASE[s][t]
            new = []
            for i in range(4):
                p1, p2, p3 = (b1 + 5 * i) % 16, (b2 + 5 * i) % 16, (b3 + 5 * i) % 16
                li = lanes[i]
                li = (li ^ (_rotl16(li, p1) & _rotl16(li, p2)) ^
                      _rotl16(li, p3) ^ (_rk(k, j) & M16)) & M16
                new.append(li)
            lanes = new
        c1, c2 = QUAD_CROSS[s]
        out = []
        for i in range(4):
            ni = (lanes[i] ^ _rotl16(lanes[(i + 1) % 4], c1) ^
                  _rotl16(lanes[(i + 2) % 4], c2) ^
                  (_rk(k, 6 + 2 * s + i) & M16)) & M16
            out.append(ni)
        x = (out[0] | (out[1] << np.uint64(16)) |
             (out[2] << np.uint64(32)) | (out[3] << np.uint64(48))) & M64
    return _postwhite(x, k)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_quad3a(np.uint64(v), np.uint64(k)))
    return t6_quad3a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_quad3a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '3 super-stages, 4 parallel 16-bit cascades + cross'}
