"""spn4_xorlin_719: 4 rounds of (xor rk, 16x PRESENT 4-bit S-box, bijective 3-term xor-linear L(x)=x^ROTL(x,7)^ROTL(x,19) applied to the state) + whitening; key schedule rk[i] = ROTL64(key,13*(i+1)) ^ RC[i]

Bijectivity (fixed key): xor round key (bijection), 16x bijective 4-bit
S-box (16 distinct outputs asserted), bijective 3-term xor-linear layer
L(x) = x ^ ROTL(x,7) ^ ROTL(x,19) -- over GF(2), L <-> 1+x^7+x^19;
(1+x^7+x^19)(1) = 1 != 0 mod 2 so x+1 does not divide it, and
x^64+1 = (x+1)^64 has no other factor ==> L is a permutation of 2^64 --
final xor whitening (bijection); composition of bijections => permutation of
2^64. The S-box TABLE is borrowed only, applied to contiguous nibbles --
NOT the full cipher; published security bounds do not transfer.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, rotl64_np, sbox16_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
assert len(set(_SBOX)) == 16, "S-box table must be a permutation"
_SBOX_NP = np.array(_SBOX, dtype=np.uint64)
_ROUNDS = 4


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _rotl64_scalar(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_scalar(key, i):
    return _rotl64_scalar(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)


def mix_spn4_xorlin_719_scalar(val, key):
    val &= M64
    key &= M64
    x = val ^ key
    for i in range(_ROUNDS):
        x ^= _rk_scalar(key, i)
        y = 0
        for s in range(16):
            y |= _SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
        x = (y ^ _rotl64_scalar(y, 7) ^ _rotl64_scalar(y, 19)) & M64
    return (x ^ _rk_scalar(key, _ROUNDS)) & M64


def _L64_np(x):
    return x ^ rotl64_np(x, U64(7)) ^ rotl64_np(x, U64(19))


def mix_spn4_xorlin_719_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(_ROUNDS):
        x = _L64_np(sbox16_np(x ^ _rk_np(k, i), _SBOX_NP))
    return x ^ _rk_np(k, _ROUNDS)


if __name__ == "__main__":
    check_model_equiv(mix_spn4_xorlin_719_scalar, mix_spn4_xorlin_719_np, "spn4_xorlin_719")
    bijectivity_spotcheck(mix_spn4_xorlin_719_np, "spn4_xorlin_719")
