"""Bit-exact Python model for t6_sboxrot6 (batch 15)."""
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

def _sbox_nibbles(x, sbox):
    y = np.zeros_like(x)
    for i in range(16):
        y |= sbox[((x >> np.uint64(4 * i)) & np.uint64(0xF))] << np.uint64(4 * i)
    return y & M64

SBOX_ROTS = [7, 23, 41, 11, 29, 53]
def t6_sboxrot6(v, k):
    """6 rounds: key xor, Midori-Sb0 nibble layer, rotation. No linear layer."""
    x = v ^ k
    for j in range(6):
        x = (x ^ _rk(k, j)) & M64
        x = _sbox_nibbles(x, SBOX_MIDORI0)
        x = _rotl64(x, SBOX_ROTS[j])
    return _postwhite(x, k)


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_sboxrot6(np.uint64(v), np.uint64(k)))
    return t6_sboxrot6(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_sboxrot6(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '6 rounds Midori-Sb0 + rotation, no linear layer'}
