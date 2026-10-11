"""Round 4, family S: SPEEDY 6-bit S-box SPN probe (survey-driven).

Uses the SPEEDY 6-bit S-box (eprint 2021/960, Table 3; cross-checked against
the paper's DNF on all 64 inputs -- they agree). 64 is not a multiple of 6,
so the S-box layer is 10x S6 on bits [59:0] plus the S1 4-bit S-box on bits
[63:60] (all bits nonlinear every round), followed by ROTL64(.,17) which
moves bits between S-box groups across rounds (17 coprime to 64).

Round: x ^= rk[i]; x = sbox_layer(x); x = ROTL64(x,17); + final whitening.
rk[i] = ROTL64(key,13*(i+1)) ^ (i+1)*0x9E3779B97F4A7C15.

Candidates: speedy3, speedy4.

Bijectivity (fixed key): S6 and S1 are permutations (asserted) applied to
disjoint bit groups + rotation + key xors => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
# SPEEDY 6-bit S-box, eprint 2021/960 Table 3 (x0 MSB; index = 6-bit value)
_S6 = [0x08, 0x00, 0x09, 0x03, 0x38, 0x10, 0x29, 0x13,
       0x0c, 0x0d, 0x04, 0x07, 0x30, 0x01, 0x20, 0x23,
       0x1a, 0x12, 0x18, 0x32, 0x3e, 0x16, 0x2c, 0x36,
       0x1c, 0x1d, 0x14, 0x37, 0x34, 0x05, 0x24, 0x27,
       0x02, 0x06, 0x0b, 0x0f, 0x33, 0x17, 0x21, 0x15,
       0x0a, 0x1b, 0x0e, 0x1f, 0x31, 0x11, 0x25, 0x35,
       0x22, 0x26, 0x2a, 0x2e, 0x3a, 0x1e, 0x28, 0x3c,
       0x2b, 0x3b, 0x2f, 0x3f, 0x39, 0x19, 0x2d, 0x3d]
assert len(set(_S6)) == 64 and max(_S6) < 64
_S1 = [0x0, 0x1, 0x2, 0x4, 0x3, 0x8, 0xF, 0xC,
       0x9, 0x5, 0xB, 0x6, 0x7, 0xE, 0xD, 0xA]
assert len(set(_S1)) == 16
_S6_NP = np.array(_S6, dtype=np.uint64)
_S1_NP = np.array(_S1, dtype=np.uint64)


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _sbox_layer_np(x):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for g in range(10):
        y |= _S6_NP[(x >> np.uint64(6 * g)) & np.uint64(0x3F)] << np.uint64(6 * g)
    y |= _S1_NP[(x >> np.uint64(60)) & np.uint64(0xF)] << np.uint64(60)
    return y


def _speedy_np(val, key, rounds):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(rounds):
        x = rotl64_np(_sbox_layer_np(x ^ _rk_np(k, i)), U64(17))
    return (x ^ _rk_np(k, rounds)) & MASK64


def mix_speedy3_np(val, key): return _speedy_np(val, key, 3)
def mix_speedy4_np(val, key): return _speedy_np(val, key, 4)


# ---- scalar ----
def _rotl64_s(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_s(key, i):
    return (_rotl64_s(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)) & M64


def _speedy_s(v, k, rounds):
    x = (v ^ k) & M64
    for i in range(rounds):
        x ^= _rk_s(k, i)
        y = 0
        for g in range(10):
            y |= _S6[(x >> (6 * g)) & 0x3F] << (6 * g)
        y |= _S1[(x >> 60) & 0xF] << 60
        x = _rotl64_s(y, 17)
    return (x ^ _rk_s(k, rounds)) & M64


def mix_speedy3_s(v, k): return _speedy_s(v, k, 3)
def mix_speedy4_s(v, k): return _speedy_s(v, k, 4)


if __name__ == "__main__":
    for s, n in [(mix_speedy3_s, mix_speedy3_np), (mix_speedy4_s, mix_speedy4_np)]:
        check_model_equiv(s, n, n.__name__)
        bijectivity_spotcheck(n, n.__name__)
