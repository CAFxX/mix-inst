"""Batch B candidate B1: add2r_a -- 2-round ARX with 3-term xor-linear layer.

x = val ^ key
2 rounds:  t = x + rk[i];  x = t ^ ROTL64(t,13) ^ ROTL64(t,41)
out = x ^ rk[2];  rk[i] = ROTL64(key, 17*(i+1)) ^ RC[i]

Bijectivity (fixed key): modular add is bijective; the 3-term xor-linear
L(t) = t ^ ROTL64(t,13) ^ ROTL64(t,41) is bijective for distinct nonzero
13,41 (proven in CANDIDATE_BRIEF.md: 1+x^r+x^s coprime to (x+1)^64); the
final xor-whitening is bijective. Composition of bijections => permutation.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_GOLDEN = 0x9E3779B97F4A7C15
_R, _S = 13, 41
assert _R != 0 and _S != 0 and _R != _S, "3-term L needs distinct nonzero rotations"


def _rc_np(i):
    return np.uint64(((i + 1) * _GOLDEN) & M64)


def _rotl_scalar(v, r):
    r &= 63
    return ((v << r) | (v >> (64 - r))) & M64 if r else v & M64


def mix_add2r_a_scalar(val, key):
    val &= M64
    key &= M64
    x = val ^ key
    for i in range(2):
        rk = _rotl_scalar(key, (17 * (i + 1)) % 64) ^ (((i + 1) * _GOLDEN) & M64)
        t = (x + rk) & M64
        x = t ^ _rotl_scalar(t, _R) ^ _rotl_scalar(t, _S)
    rk = _rotl_scalar(key, (17 * 3) % 64) ^ ((3 * _GOLDEN) & M64)
    return (x ^ rk) & M64


def mix_add2r_a_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(2):
        rk = rotl64_np(k, U64((17 * (i + 1)) % 64)) ^ _rc_np(i)
        t = (x + rk) & MASK64
        x = t ^ rotl64_np(t, U64(_R)) ^ rotl64_np(t, U64(_S))
    x ^= rotl64_np(k, U64((17 * 3) % 64)) ^ _rc_np(2)
    return x


if __name__ == "__main__":
    check_model_equiv(mix_add2r_a_scalar, mix_add2r_a_np, "add2r_a")
    bijectivity_spotcheck(mix_add2r_a_np, "add2r_a")
