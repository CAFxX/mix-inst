"""STATISTICAL PROBE ONLY (not a candidate): arx3_full_probe.

The plan's original 3-round shape, verbatim: 3 rounds of (add-key + 3
sequential xorshifts) + xor whitening. Delay would be ~3*25.5 = 76.5 > 44.3
(OUT by construction). This probe answers ONLY the statistical question:
does the planned 3-round depth fix the diffusion failure seen at 2 rounds?
If YES -> the family needs ~76 units and is delay-excluded. If NO -> deeper
multiply-free ARX is statistically broken at any affordable depth.

x  = val
3x { x += rk[i]; x ^= x>>29; x ^= x<<17; x ^= x>>43 }
out = x ^ rk[3]
rk[i] = ROTL64(key, 17*(i+1)) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15
Bijective per stage; no RTL (not a candidate).
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_GOLDEN = 0x9E3779B97F4A7C15
_S1, _S2, _S3 = 29, 17, 43


def _rk_np(k, i):
    return rotl64_np(k, U64((17 * (i + 1)) % 64)) ^ U64(((i + 1) * _GOLDEN) & M64)


def _rk_scalar(key, i):
    r = (17 * (i + 1)) % 64
    rot = (((key << r) | (key >> (64 - r))) & M64) if r else (key & M64)
    return (rot ^ (((i + 1) * _GOLDEN) & M64)) & M64


def mix_arx3_full_probe_scalar(val, key):
    val &= M64
    key &= M64
    x = val
    for i in range(3):
        x = (x + _rk_scalar(key, i)) & M64
        x ^= x >> _S1
        x ^= (x << _S2) & M64
        x ^= x >> _S3
    x ^= _rk_scalar(key, 3)
    return x & M64


def mix_arx3_full_probe_np(val, key):
    x = np.asarray(val, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(3):
        x = x + _rk_np(k, i)
        x ^= x >> U64(_S1)
        x ^= x << U64(_S2)
        x ^= x >> U64(_S3)
    x ^= _rk_np(k, 3)
    return x


if __name__ == "__main__":
    check_model_equiv(mix_arx3_full_probe_scalar, mix_arx3_full_probe_np,
                      "arx3_full_probe")
    bijectivity_spotcheck(mix_arx3_full_probe_np, "arx3_full_probe")
