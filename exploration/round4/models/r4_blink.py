"""Round 4, family B: Blink/Midori-style SPN (survey-driven).

Per the SOTA survey (THF/Blink, ToSC 2025): the best latency-per-round SPN
structure known is a 4-bit S-box of NAND/NOR depth 3.5 + Midori 4x4 almost-MDS
binary matrix (XOR depth 2, involutory) + free nibble permutation (wiring).

  S1: depth-3.5-class S-box, THF paper Table 6 (DU4/Lin8, full diffusion):
      x: 0 1 2 3 4 5 6 7 8 9 a b c d e f
      S1:0 1 2 4 3 8 f c 9 5 b 6 7 e d a   (a permutation; involution not
      needed -- the finalizer is one-way)
  M: Midori MixColumn, out[i] = XOR of the other three nibbles in the column
     (binary, involutory: M = J+I, M^2 = J^2+I = I over GF(2))
  shuffle: Midori ShuffleCell nibble permutation (free wiring)

Round: x ^= rk[i]; x = S1^16(x); x = M(x); x = shuffle(x).
Wrap: x = val^key; ...; out = x ^ rk[R] (whitening).
rk[i] = ROTL64(key,13*(i+1)) ^ (i+1)*0x9E3779B97F4A7C15.

Candidates: blink2 / blink3 / blink4 (S1, 2/3/4 rounds),
            midori3 (Midori Sb0, 3 rounds, control).

Bijectivity (fixed key): S-box permutation (asserted) + M invertible +
nibble permutation + key xors => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, sbox16_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_S1 = [0x0, 0x1, 0x2, 0x4, 0x3, 0x8, 0xF, 0xC,
       0x9, 0x5, 0xB, 0x6, 0x7, 0xE, 0xD, 0xA]
_MIDORI = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
           0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
assert len(set(_S1)) == 16 and len(set(_MIDORI)) == 16
_S1_NP = np.array(_S1, dtype=np.uint64)
_MIDORI_NP = np.array(_MIDORI, dtype=np.uint64)
# Midori ShuffleCell (published): out_nib[i] = in_nib[PERM[i]]
_PERM = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]
assert sorted(_PERM) == list(range(16))
_SHIFTS = np.array([4 * i for i in range(16)], dtype=np.uint64)


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _midori_M_np(x):
    shp = np.shape(x)
    xf = np.asarray(x, dtype=np.uint64).reshape(-1)
    nib = ((xf[:, None] >> _SHIFTS) & np.uint64(0xF))
    # column parity: XOR of the 4 nibbles in each column; out = parity ^ in
    out = np.empty_like(nib)
    for c in range(4):
        col = nib[:, 4 * c:4 * c + 4]
        parity = col[:, 0] ^ col[:, 1] ^ col[:, 2] ^ col[:, 3]
        out[:, 4 * c:4 * c + 4] = parity[:, None] ^ col
    y = (out << _SHIFTS).sum(axis=1)
    return y.reshape(shp)


def _shuffle_np(x):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros(x.shape, dtype=np.uint64)
    for i, p in enumerate(_PERM):
        y |= ((x >> np.uint64(4 * p)) & np.uint64(0xF)) << np.uint64(4 * i)
    return y


def _blink_np(val, key, rounds, table):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(rounds):
        x = _shuffle_np(_midori_M_np(sbox16_np(x ^ _rk_np(k, i), table)))
    return (x ^ _rk_np(k, rounds)) & MASK64


def mix_blink2_np(val, key): return _blink_np(val, key, 2, _S1_NP)
def mix_blink3_np(val, key): return _blink_np(val, key, 3, _S1_NP)
def mix_blink4_np(val, key): return _blink_np(val, key, 4, _S1_NP)
def mix_midori3_np(val, key): return _blink_np(val, key, 3, _MIDORI_NP)


# ---- scalar versions ----
def _rotl64_s(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_s(key, i):
    return (_rotl64_s(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)) & M64


def _midori_M_s(x):
    nib = [(x >> (4 * s)) & 0xF for s in range(16)]
    out = [0] * 16
    for c in range(4):
        p = nib[4 * c] ^ nib[4 * c + 1] ^ nib[4 * c + 2] ^ nib[4 * c + 3]
        for i in range(4):
            out[4 * c + i] = p ^ nib[4 * c + i]
    y = 0
    for s in range(16):
        y |= out[s] << (4 * s)
    return y


def _shuffle_s(x):
    y = 0
    for i, p in enumerate(_PERM):
        y |= ((x >> (4 * p)) & 0xF) << (4 * i)
    return y


def _blink_s(v, k, rounds, table):
    x = (v ^ k) & M64
    for i in range(rounds):
        x ^= _rk_s(k, i)
        y = 0
        for s in range(16):
            y |= table[(x >> (4 * s)) & 0xF] << (4 * s)
        x = _shuffle_s(_midori_M_s(y))
    return (x ^ _rk_s(k, rounds)) & M64


def mix_blink2_s(v, k): return _blink_s(v, k, 2, _S1)
def mix_blink3_s(v, k): return _blink_s(v, k, 3, _S1)
def mix_blink4_s(v, k): return _blink_s(v, k, 4, _S1)
def mix_midori3_s(v, k): return _blink_s(v, k, 3, _MIDORI)


if __name__ == "__main__":
    for s, n in [(mix_blink2_s, mix_blink2_np), (mix_blink3_s, mix_blink3_np),
                 (mix_blink4_s, mix_blink4_np), (mix_midori3_s, mix_midori3_np)]:
        check_model_equiv(s, n, n.__name__)
        bijectivity_spotcheck(n, n.__name__)
