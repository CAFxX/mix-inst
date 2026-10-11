"""Round-2 deeper ARX candidate arx2_xs_a.

Adapted from the planned 3-round shape: the delay probe measured one round
(add + 3 xorshifts) at 25.5 units, so 3 rounds (~76) cannot fit the 44.3 bar.
This is the densest 2-add shape that fits: 2 modular adds + 3 sequential
xorshift steps + xor whitening, no initial val^key (key enters via add-key,
saves ~1 unit on the critical path).

x  = val
x += rk[0]
x ^= x >> 30
x ^= x << 27
x += rk[1]
x ^= x >> 31
out = x ^ rk[2]
rk[i] = ROTL64(key, 17*(i+1)) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15

Bijectivity (fixed key): x+=rk is bijective (mod 2^64); each x^=x>>s /
x^=x<<s is bijective (triangular xor with 1s on the diagonal); x^=rk is
bijective. Composition of bijections => permutation.
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


def mix_arx2_xs_a_scalar(val, key):
    val &= M64
    key &= M64
    x = (val + _rk_scalar(key, 0)) & M64
    x ^= x >> _S1
    x ^= (x << _S2) & M64
    x = (x + _rk_scalar(key, 1)) & M64
    x ^= x >> _S3
    x ^= _rk_scalar(key, 2)
    return x & M64


def mix_arx2_xs_a_np(val, key):
    x = np.asarray(val, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    x = x + _rk_np(k, 0)                      # uint64 wraps mod 2^64
    x ^= x >> U64(_S1)
    x ^= x << U64(_S2)
    x = x + _rk_np(k, 1)
    x ^= x >> U64(_S3)
    x ^= _rk_np(k, 2)
    return x


if __name__ == "__main__":
    check_model_equiv(mix_arx2_xs_a_scalar, mix_arx2_xs_a_np, "arx2_xs_a")
    bijectivity_spotcheck(mix_arx2_xs_a_np, "arx2_xs_a")
