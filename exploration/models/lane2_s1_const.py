"""D2 lane2_s1_const: single stage, two 32-bit lanes.

a *= 0x9E3779B1; b *= 0x85EBCA77 (parallel constant mults);
Feistel cross #1: t = a ^ ROTL32(b,11); b ^= ROTL32(t,17); a = t;
Feistel cross #2: t = a ^ ROTL32(b,7);  b ^= ROTL32(t,19); a = t;
whitening a ^= 0x9E3779B1; b ^= 0x85EBCA77; out = {b, a}.

Bijectivity (fixed key): odd constant mults are bijections; each Feistel
half-step (L,R)->(L^F(R),R) and (L,R)->(L,R^F(L)) is bijective for ANY F;
xor whitening is a bijection. Composition of bijections => 2^64 permutation.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import check_model_equiv

M32 = 0xFFFFFFFF
U64 = np.uint64
CA = 0x9E3779B1
CB = 0x85EBCA77
assert CA & 1 and CB & 1, "lane mult constants must be odd"


def _rotl32_scalar(x, r):
    r &= 31
    return (((x << r) | (x >> (32 - r))) & M32) if r else x


def _rotl32_np(v, r):
    v = np.asarray(v, dtype=np.uint64) & U64(M32)
    r = int(r) & 31
    if r == 0:
        return v
    return ((v << U64(r)) | (v >> U64(32 - r))) & U64(M32)


def mix_lane2_s1_const_scalar(val, key):
    val &= (1 << 64) - 1
    key &= (1 << 64) - 1
    x = val ^ key
    a, b = x & M32, (x >> 32) & M32
    a = (a * CA) & M32
    b = (b * CB) & M32
    for r1, r2 in ((11, 17), (7, 19)):
        t = a ^ _rotl32_scalar(b, r1)
        b = b ^ _rotl32_scalar(t, r2)
        a = t
    a ^= CA
    b ^= CB
    return (b << 32) | a


def mix_lane2_s1_const_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    a, b = x & U64(M32), (x >> U64(32)) & U64(M32)
    a = (a * U64(CA)) & U64(M32)
    b = (b * U64(CB)) & U64(M32)
    for r1, r2 in ((11, 17), (7, 19)):
        t = a ^ _rotl32_np(b, r1)
        b = b ^ _rotl32_np(t, r2)
        a = t
    a = a ^ U64(CA)
    b = b ^ U64(CB)
    return ((b << U64(32)) | a) & np.uint64(0xFFFFFFFFFFFFFFFF)


if __name__ == "__main__":
    check_model_equiv(mix_lane2_s1_const_scalar, mix_lane2_s1_const_np,
                      "lane2_s1_const")
