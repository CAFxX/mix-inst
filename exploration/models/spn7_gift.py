"""spn7_gift: 7-round SPN, GIFT 4-bit S-box + PRESENT pLayer.

x = val ^ key
rk[i] = ROTL64(key,13*(i+1)) ^ RC[i]
round: x = pLayer(SBOX16(x ^ rk[i]))
out = x ^ rk[7]

Bijectivity (fixed key): xor round key (bijection), 16x bijective 4-bit
S-box (16 distinct outputs asserted), PRESENT pLayer bit-permutation
(bijection), final xor whitening (bijection); composition of bijections =>
permutation of 2^64. The S-box TABLE is borrowed only, applied to contiguous
nibbles -- NOT the full cipher; published security bounds do not transfer.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, rotl64_np, sbox16_np, present_perm_np,
                        check_model_equiv, bijectivity_spotcheck)

M64 = (1 << 64) - 1
_SBOX = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9, 0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]
assert len(set(_SBOX)) == 16, "S-box table must be a permutation"
_SBOX_NP = np.array(_SBOX, dtype=np.uint64)
_ROUNDS = 7


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _rotl64_scalar(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_scalar(key, i):
    return _rotl64_scalar(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)


def mix_spn7_gift_scalar(val, key):
    val &= M64
    key &= M64
    P = [(16 * b) % 63 for b in range(63)] + [63]
    x = val ^ key
    for i in range(_ROUNDS):
        x ^= _rk_scalar(key, i)
        y = 0
        for s in range(16):
            y |= _SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
        z = 0
        for b in range(64):
            if (y >> b) & 1:
                z |= 1 << P[b]
        x = z
    return (x ^ _rk_scalar(key, _ROUNDS)) & M64


def mix_spn7_gift_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(_ROUNDS):
        x = present_perm_np(sbox16_np(x ^ _rk_np(k, i), _SBOX_NP))
    return x ^ _rk_np(k, _ROUNDS)


if __name__ == "__main__":
    check_model_equiv(mix_spn7_gift_scalar, mix_spn7_gift_np, "spn7_gift")
    bijectivity_spotcheck(mix_spn7_gift_np, "spn7_gift")
