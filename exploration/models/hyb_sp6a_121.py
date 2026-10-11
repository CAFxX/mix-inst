"""hyb_sp6a_121: constant-multiply + PRESENT-SPN hybrid (round 2).

x = val ^ key
rk[i] = ROTL64(key,13*(i+1)) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15
ops: SPN round (rk[0]) -> x *= 0x8001fff8001fe1 -> SPN round (rk[1]); mult = (x * 0x8001fff8001fe1) mod 2^64 (Wallace CSD tree, 6 terms);
SPN round: x = pLayer(SBOX16(x ^ rk[i])), rounds numbered sequentially.
out = x ^ rk[2]

Bijectivity (fixed key): x^key (bij), each SPN round = xor-rk o
16x bijective 4-bit S-box (16 distinct outputs asserted) o PRESENT pLayer
bit-permutation (each step a bijection), const-mult by odd C (bij: gcd(C,2^64)=1),
final xor whitening (bij); composition of bijections => permutation of 2^64.
The S-box TABLE is borrowed only (contiguous nibbles) -- NOT the cipher;
published security bounds do not transfer.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, rotl64_np, sbox16_np, present_perm_np,
                        check_model_equiv, bijectivity_spotcheck)
from gen_wallace import wallace_model

M64 = (1 << 64) - 1
_SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
assert len(set(_SBOX)) == 16, "S-box table must be a permutation"
_SBOX_NP = np.array(_SBOX, dtype=np.uint64)
_C = 0x8001fff8001fe1
assert _C & 1, "constant must be odd for bijectivity"
_OPS = ['S', 'M', 'S']


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _rotl64_scalar(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_scalar(key, i):
    return _rotl64_scalar(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _spn_scalar(x, rk):
    x ^= rk
    y = 0
    for s in range(16):
        y |= _SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
    P = [(16 * b) % 63 for b in range(63)] + [63]
    z = 0
    for b in range(64):
        if (y >> b) & 1:
            z |= 1 << P[b]
    return z


def mix_hyb_sp6a_121_scalar(val, key):
    val &= M64
    key &= M64
    x = val ^ key
    si = 0
    for op in _OPS:
        if op == "S":
            x = _spn_scalar(x, _rk_scalar(key, si))
            si += 1
        else:
            x = (x * _C) & M64
    return (x ^ _rk_scalar(key, si)) & M64


def _spn_np(x, k, i):
    return present_perm_np(sbox16_np(x ^ _rk_np(k, i), _SBOX_NP))


def mix_hyb_sp6a_121_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    si = 0
    for op in _OPS:
        if op == "S":
            x = _spn_np(x, k, si)
            si += 1
        else:
            x = wallace_model(x, _C)
    return x ^ _rk_np(k, si)


if __name__ == "__main__":
    check_model_equiv(mix_hyb_sp6a_121_scalar, mix_hyb_sp6a_121_np, "hyb_sp6a_121")
    bijectivity_spotcheck(mix_hyb_sp6a_121_np, "hyb_sp6a_121")
