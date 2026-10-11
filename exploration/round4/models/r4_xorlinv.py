"""Round 4, V1: SKINNY 4-bit S-box in the 4-round xorlin structure.

Same skeleton as round-2's winner-adjacent spn4_xorlin_1137
(4 rounds of xor-rk, 16x 4-bit S-box, bijective 3-term L(x)=x^ROTL(x,11)^ROTL(x,37),
final whitening) but with the SKINNY S-box instead of PRESENT:
  C 6 9 0 1 A 2 B 3 8 5 D 4 E 7 F   (published SKINNY-64 table)

Round-1 lesson 6: delay is S-box-agnostic at fixed round count; S-box choice
moves statistics. Round-2: PRESENT 0 rej, GIFT 4 rej in xorlin. SKINNY untested
in this structure.

Bijectivity (fixed key): xor-rk (bij) + 16x bijective SKINNY S-box (asserted
permutation) + bijective 3-term L (1+x^11+x^37; x=1 gives 1+1+1=1 != 0 in
GF(2), so x+1 does not divide it; x^64+1=(x+1)^64 has no other factor) +
final whitening. Composition => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, sbox16_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_SKINNY = [0xC, 0x6, 0x9, 0x0, 0x1, 0xA, 0x2, 0xB, 0x3, 0x8, 0x5, 0xD, 0x4, 0xE, 0x7, 0xF]
assert len(set(_SKINNY)) == 16, "SKINNY table must be a permutation"
_SKINNY_NP = np.array(_SKINNY, dtype=np.uint64)
_ROUNDS = 4


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _L64_np(x):
    return x ^ rotl64_np(x, U64(11)) ^ rotl64_np(x, U64(37))


def mix_skinny_xorlin_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(_ROUNDS):
        x = _L64_np(sbox16_np(x ^ _rk_np(k, i), _SKINNY_NP))
    return (x ^ _rk_np(k, _ROUNDS)) & MASK64


def _rotl64_s(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_s(key, i):
    return (_rotl64_s(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)) & M64


def mix_skinny_xorlin_s(v, k):
    x = (v ^ k) & M64
    for i in range(_ROUNDS):
        x ^= _rk_s(k, i)
        y = 0
        for s in range(16):
            y |= _SKINNY[(x >> (4 * s)) & 0xF] << (4 * s)
        x = (y ^ _rotl64_s(y, 11) ^ _rotl64_s(y, 37)) & M64
    return (x ^ _rk_s(k, _ROUNDS)) & M64


if __name__ == "__main__":
    check_model_equiv(mix_skinny_xorlin_s, mix_skinny_xorlin_np, "skinny_xorlin")
    bijectivity_spotcheck(mix_skinny_xorlin_np, "skinny_xorlin")
