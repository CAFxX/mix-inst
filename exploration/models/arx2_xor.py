"""Round-2 deeper ARX candidate arx2_xor (xor-key fallback form).

Add-key forms (arx2_xs_a/b) failed with the saturated diffusion signature, so
per plan we test the xor-key injection mode. Same 2-add delay budget
(one round = 25.5 units measured; 3 rounds ~76 > 44.3, impossible), mirrored
structure to arx2_xs_a for comparability:

x  = val ^ rk[0]
x ^= x >> 30
x ^= x << 27
x += rk[1]
x ^= x >> 31
x += rk[2]          # add-whitening (bijective)
out = x
rk[i] = ROTL64(key, 17*(i+1)) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15

Bijectivity (fixed key): x^=rk bijective; x^=x>>s / x^=x<<s bijective
(unitriangular over GF(2)); x+=rk bijective (mod 2^64). Composition => perm.
No multiplies; no 2-term x^ROTL.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_GOLDEN = 0x9E3779B97F4A7C15
_S1, _S2, _S3 = 30, 27, 31


def _rk_np(k, i):
    return rotl64_np(k, U64((17 * (i + 1)) % 64)) ^ U64(((i + 1) * _GOLDEN) & M64)


def _rotl_scalar(v, r):
    r &= 63
    return (((v << r) | (v >> (64 - r))) & M64) if r else (v & M64)


def _rk_scalar(key, i):
    return (_rotl_scalar(key, (17 * (i + 1)) % 64)
            ^ (((i + 1) * _GOLDEN) & M64)) & M64


def mix_arx2_xor_scalar(val, key):
    val &= M64
    key &= M64
    x = (val ^ _rk_scalar(key, 0)) & M64
    x ^= x >> _S1
    x ^= (x << _S2) & M64
    x = (x + _rk_scalar(key, 1)) & M64
    x ^= x >> _S3
    x = (x + _rk_scalar(key, 2)) & M64
    return x


def mix_arx2_xor_np(val, key):
    # NOTE: .copy() is required: np.asarray does not copy a uint64 ndarray,
    # and the in-place ^= below would otherwise mutate the caller's buffer.
    x = np.asarray(val, dtype=np.uint64).copy()
    k = np.asarray(key, dtype=np.uint64)
    x ^= _rk_np(k, 0)
    x ^= x >> U64(_S1)
    x ^= x << U64(_S2)
    x = x + _rk_np(k, 1)
    x ^= x >> U64(_S3)
    x = x + _rk_np(k, 2)
    return x


if __name__ == "__main__":
    check_model_equiv(mix_arx2_xor_scalar, mix_arx2_xor_np, "arx2_xor")
    bijectivity_spotcheck(mix_arx2_xor_np, "arx2_xor")
