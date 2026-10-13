"""Bit-exact Python model for t6_sb8spn3a (batch 21)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A), np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054), np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B9A1E7C2FA), np.uint64(0x3C6EF372ECA0AE52), np.uint64(0xDAA66D2CD6129B3E)]
SB8_AES = np.array([99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22], dtype=np.uint64)
PBOX = [0, 8, 16, 24, 32, 40, 48, 56, 9, 17, 25, 33, 41, 49, 57, 1, 18, 26, 34, 42, 50, 58, 2, 10, 27, 35, 43, 51, 59, 3, 11, 19, 36, 44, 52, 60, 4, 12, 20, 28, 45, 53, 61, 5, 13, 21, 29, 37, 54, 62, 6, 14, 22, 30, 38, 46, 63, 7, 15, 23, 31, 39, 47, 55]
SHF_SCHED = [(5, 13, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59), (11, 37, 53), (3, 19, 61)]
OR_SCHED = [(3, 11, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59), (11, 37, 53), (5, 19, 61)]

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64

def _sb8(x):
    y = np.zeros_like(x)
    for i in range(8):
        y |= SB8_AES[((x >> np.uint64(8 * i)) & np.uint64(0xFF))] << np.uint64(8 * i)
    return y & M64

def _pbox(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << np.uint64(PBOX[i])
    return y & M64

def _shl64(x, s):
    return (x << np.uint64(s)) & M64 if s < 64 else np.zeros_like(x)

def _shr64(x, s):
    return (x >> np.uint64(s)) if s < 64 else np.zeros_like(x)

def t6_sb8spn3a(v, k):
    """3-round SPN, 8-bit AES S-box, per-round key."""
    x = (v ^ k) & M64
    for j in range(3):
        x = (_sb8(x ^ _rk(k, j))) & M64
        x = _pbox(x)
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return int(t6_sb8spn3a(np.uint64(v), np.uint64(k)))
    return t6_sb8spn3a(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))

def mix_np(V, K):
    return t6_sb8spn3a(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))

meta = {'desc': '3-round SPN, 8-bit AES S-box'}
