"""Round 4, family G: Feistel with Goldreich-style 5-local F (generated).

F(h)[j] = h[a]^h[b]^h[c]^(h[d]&h[e]); taps fixed below (seed 0x6A09E667).
G1 = 6 rounds, G2 = 8 rounds. (L,R) -> (R, L ^ F(R ^ rk[i])).
Bijectivity: Feistel => permutation for fixed key.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, check_model_equiv, bijectivity_spotcheck)

M32 = np.uint64(0xFFFFFFFF)
_TAPS = [[1, 11, 14, 20, 21], [0, 2, 3, 7, 28], [3, 15, 16, 19, 21], [1, 7, 10, 19, 25], [6, 11, 19, 28, 31], [4, 11, 17, 19, 21], [3, 6, 20, 21, 23], [0, 7, 8, 10, 11], [2, 8, 15, 29, 30], [4, 14, 20, 21, 26], [0, 2, 9, 12, 20], [2, 3, 4, 5, 23], [2, 3, 4, 5, 23], [2, 19, 23, 27, 29], [1, 5, 6, 8, 12], [13, 16, 17, 18, 27], [1, 13, 15, 21, 25], [12, 13, 16, 19, 20], [6, 9, 18, 21, 28], [3, 6, 11, 12, 29], [0, 9, 15, 20, 24], [12, 14, 19, 25, 29], [1, 23, 27, 28, 31], [5, 12, 17, 27, 31], [4, 5, 6, 17, 20], [0, 3, 14, 21, 23], [1, 7, 11, 22, 24], [5, 6, 7, 15, 26], [0, 7, 16, 22, 30], [1, 18, 22, 29, 31], [6, 7, 16, 19, 27], [0, 4, 6, 10, 23]]
_RC_MUL = 0x9E3779B9


def _rotl32_np(v, r):
    r = int(r) & 31
    v = np.asarray(v, dtype=np.uint64) & M32
    if r == 0:
        return v
    return (((v << np.uint64(r)) | (v >> np.uint64(32 - r))) & M32)


def _F_np(h):
    h = np.asarray(h, dtype=np.uint64) & M32
    out = np.zeros(h.shape, dtype=np.uint64)
    hb = [(h >> np.uint64(i)) & np.uint64(1) for i in range(32)]
    for j, (a, b, c, d, e) in enumerate(_TAPS):
        bit = hb[a] ^ hb[b] ^ hb[c] ^ (hb[d] & hb[e])
        out = out | (bit << np.uint64(j))
    return out & M32


def _feistel_np(val, key, rounds):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    klo = np.asarray(key, dtype=np.uint64) & M32
    L = (x >> np.uint64(32)) & M32
    R = x & M32
    for i in range(rounds):
        rk = (_rotl32_np(klo, 7 * (i + 1)) ^
              np.uint64(((i + 1) * _RC_MUL) & 0xFFFFFFFF)) & M32
        nL = R
        nR = (L ^ _F_np(R ^ rk)) & M32
        L, R = nL, nR
    return ((L << np.uint64(32)) | R) & MASK64


def mix_gl5_f6_np(val, key):
    return _feistel_np(val, key, 6)


def mix_gl5_f8_np(val, key):
    return _feistel_np(val, key, 8)


def _rotl32_s(v, r):
    r &= 31
    v &= 0xFFFFFFFF
    return (((v << r) | (v >> (32 - r))) & 0xFFFFFFFF) if r else v


def _F_s(h):
    h &= 0xFFFFFFFF
    out = 0
    for j, (a, b, c, d, e) in enumerate(_TAPS):
        bit = (((h >> a) & 1) ^ ((h >> b) & 1) ^ ((h >> c) & 1) ^
               (((h >> d) & 1) & ((h >> e) & 1)))
        out |= bit << j
    return out & 0xFFFFFFFF


def _feistel_s(val, key, rounds):
    x = (val ^ key) & 0xFFFFFFFFFFFFFFFF
    klo = key & 0xFFFFFFFF
    L = (x >> 32) & 0xFFFFFFFF
    R = x & 0xFFFFFFFF
    for i in range(rounds):
        rk = (_rotl32_s(klo, 7 * (i + 1)) ^ (((i + 1) * _RC_MUL) & 0xFFFFFFFF)) & 0xFFFFFFFF
        nL = R
        nR = (L ^ _F_s(R ^ rk)) & 0xFFFFFFFF
        L, R = nL, nR
    return ((L << 32) | R) & 0xFFFFFFFFFFFFFFFF


def mix_gl5_f6_s(v, k): return _feistel_s(v, k, 6)
def mix_gl5_f8_s(v, k): return _feistel_s(v, k, 8)


if __name__ == "__main__":
    for s, n in [(mix_gl5_f6_s, mix_gl5_f6_np), (mix_gl5_f8_s, mix_gl5_f8_np)]:
        check_model_equiv(s, n, n.__name__)
        bijectivity_spotcheck(n, n.__name__)
