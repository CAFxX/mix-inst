"""STATISTICAL PROBE ONLY (not a candidate): arx3_probe.

3-add ARX to test the diagnosed mechanism: 2 adds leave the input's 18-dim
affine-subspace image too "thin" to cross carry thresholds at high bit
positions; a third nonlinear stage should bootstrap full diffusion.
Delay est ~64 > 44.3 -> OUT on delay by construction; this probe only asks
whether 3 adds fix the STATISTICS (mapping the family's round threshold).

x  = val
x += rk[0]
x ^= x >> 30
x += rk[1]
x ^= x << 27
x += rk[2]
x ^= x >> 31
out = x ^ rk[3]
rk[i] = ROTL64(key, 17*(i+1)) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15
Bijective per stage (add / xorshift / xor); no RTL (not a candidate).
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_GOLDEN = 0x9E3779B97F4A7C15


def _rk_np(k, i):
    return rotl64_np(k, U64((17 * (i + 1)) % 64)) ^ U64(((i + 1) * _GOLDEN) & M64)


def _rotl_scalar(v, r):
    r &= 63
    return (((v << r) | (v >> (64 - r))) & M64) if r else (v & M64)


def _rk_scalar(key, i):
    return (_rotl_scalar(key, (17 * (i + 1)) % 64)
            ^ (((i + 1) * _GOLDEN) & M64)) & M64


def mix_arx3_probe_scalar(val, key):
    val &= M64
    key &= M64
    x = (val + _rk_scalar(key, 0)) & M64
    x ^= x >> 30
    x = (x + _rk_scalar(key, 1)) & M64
    x ^= (x << 27) & M64
    x = (x + _rk_scalar(key, 2)) & M64
    x ^= x >> 31
    x ^= _rk_scalar(key, 3)
    return x & M64


def mix_arx3_probe_np(val, key):
    x = np.asarray(val, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    x = x + _rk_np(k, 0)
    x ^= x >> U64(30)
    x = x + _rk_np(k, 1)
    x ^= x << U64(27)
    x = x + _rk_np(k, 2)
    x ^= x >> U64(31)
    x ^= _rk_np(k, 3)
    return x


if __name__ == "__main__":
    check_model_equiv(mix_arx3_probe_scalar, mix_arx3_probe_np, "arx3_probe")
    bijectivity_spotcheck(mix_arx3_probe_np, "arx3_probe")
