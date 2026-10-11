"""Batch B candidate B4: m32_1stage_b -- as B3 with C=32'h85EBCA77,
rotations (7,19), final xor of key[63:32] instead of key[31:0].

a = val[31:0] ^ key[31:0];  b = val[63:32] ^ key[63:32]
a1 = a * 32'h85EBCA77            (constant is ODD -> bijective mod 2^32)
b1 = b ^ a1
a2 = a1 ^ ROTL32(b1, 7)
b2 = b1 ^ ROTL32(a2, 19) ^ key[63:32]
out = {b2, a2}

Bijectivity (fixed key): odd-constant multiply (asserted below) + sequential
Feistel-structured xor half-steps (u,v)->(u,v^f(u)), each bijective; initial
and final xors bijective. Inverse: b1 = b2 ^ ROTL32(a2,19) ^ keyhi;
a1 = a2 ^ ROTL32(b1,7); b = b1 ^ a1; a = a1 * C^{-1} mod 2^32; xor key.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, check_model_equiv, bijectivity_spotcheck)

M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
_C = 0x85EBCA77
assert _C & 1, "constant must be odd so a -> a*C is bijective mod 2^32"


def _rotl32_np(v, r):
    r = np.asarray(r, dtype=np.uint64) & np.uint64(31)
    v = np.asarray(v, dtype=np.uint64) & np.uint64(M32)
    return np.where(r == 0, v,
                    (((v << r) | (v >> (np.uint64(32) - r)))
                     & np.uint64(M32)))


def _rotl32_scalar(v, r):
    r &= 31
    v &= M32
    return ((v << r) | (v >> (32 - r))) & M32 if r else v


def mix_m32_1stage_b_scalar(val, key):
    val &= M64
    key &= M64
    a = (val & M32) ^ (key & M32)
    b = ((val >> 32) & M32) ^ ((key >> 32) & M32)
    a1 = (a * _C) & M32
    b1 = b ^ a1
    a2 = a1 ^ _rotl32_scalar(b1, 7)
    b2 = b1 ^ _rotl32_scalar(a2, 19) ^ ((key >> 32) & M32)
    return ((b2 << 32) | a2) & M64


def mix_m32_1stage_b_np(val, key):
    v = np.asarray(val, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    a = (v & np.uint64(M32)) ^ (k & np.uint64(M32))
    b = ((v >> np.uint64(32)) & np.uint64(M32)) ^ ((k >> np.uint64(32)) & np.uint64(M32))
    a1 = (a * np.uint64(_C)) & np.uint64(M32)
    b1 = b ^ a1
    a2 = a1 ^ _rotl32_np(b1, 7)
    b2 = b1 ^ _rotl32_np(a2, 19) ^ ((k >> np.uint64(32)) & np.uint64(M32))
    return ((b2 << np.uint64(32)) | a2) & np.uint64(M64)


if __name__ == "__main__":
    check_model_equiv(mix_m32_1stage_b_scalar, mix_m32_1stage_b_np, "m32_1stage_b")
    bijectivity_spotcheck(mix_m32_1stage_b_np, "m32_1stage_b")
