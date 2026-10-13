"""Bit-exact Python model for t6_sboxp4a (batch 18)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
SBOX_MIDORI0 = np.array([0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6], dtype=np.uint64)
PBOX = [0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51, 4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55, 8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59, 12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _postwhite(x, k):
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64

def _sbox16(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SBOX_MIDORI0[((x >> np.uint64(4 * i)) & np.uint64(0xF))] << np.uint64(4 * i)
    return y & M64

def _pbox(x):
    # out[P(i)] = in[i]
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << np.uint64(PBOX[i])
    return y & M64

def _spn(v, k, nrounds):
    x = v ^ k
    for j in range(nrounds):
        x = (x ^ _rk(k, j)) & M64
        x = _sbox16(x)
        x = _pbox(x)
    return _postwhite(x, k)

def t6_sboxp4a(v, k):
    """4-round S-box+P-box SPN."""
    return _spn(v, k, 4)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_sboxp4a(np.uint64(v), np.uint64(k)))
    return t6_sboxp4a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_sboxp4a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '4-round Midori-Sb0 + PRESENT pLayer SPN'}
