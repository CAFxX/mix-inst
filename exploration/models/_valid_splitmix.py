"""Validation model: keyed splitmix64 (known-good mixer) for calibrating the
round-2 calibrated screen. Not a candidate (uses a 64-bit multiply)."""
import numpy as np
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import U64

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def _splitmix64_np(z):
    z = (z + U64(0x9E3779B97F4A7C15)) & M64
    z = ((z ^ (z >> U64(30))) * U64(0xBF58476D1CE4E5B9)) & M64
    z = ((z ^ (z >> U64(27))) * U64(0x94D049BB133111EB)) & M64
    return (z ^ (z >> U64(31))) & M64


def mix_valid_splitmix_np(val, key):
    return _splitmix64_np(np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64))


def mix_valid_splitmix_scalar(val, key):
    M = (1 << 64) - 1
    z = ((val ^ key) + 0x9E3779B97F4A7C15) & M
    z = (((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M)
    z = (((z ^ (z >> 27)) * 0x94D049BB133111EB) & M)
    return ((z ^ (z >> 31)) & M)
