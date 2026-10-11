"""D1 lane2_s2_const: 2-stage, two 32-bit lanes.

Per stage: a *= 0x9E3779B1, b *= 0x85EBCA77 (parallel constant mults);
Feistel cross: t = a ^ ROTL32(b,11); b = b ^ ROTL32(t,17); a = t;
then a ^= RCa[i], b ^= RCb[i] with RCa[i]=(i+1)*0x9E3779B1 mod 2^32,
RCb[i]=(i+1)*0x85EBCA77 mod 2^32.
out = {b, a} after stage 2.

Bijectivity (fixed key): odd constant mults are bijections; each Feistel
half-step (L,R)->(L^F(R),R) and (L,R)->(L,R^F(L)) is bijective for ANY F
(inverse is the same step); xor with round constant is a bijection.
Composition of bijections => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import check_model_equiv

M32 = 0xFFFFFFFF
U64 = np.uint64
CA = 0x9E3779B1
CB = 0x85EBCA77
assert CA & 1 and CB & 1, "stage mult constants must be odd"


def _rotl32_scalar(x, r):
    r &= 31
    return (((x << r) | (x >> (32 - r))) & M32) if r else x


def _rotl32_np(v, r):
    v = np.asarray(v, dtype=np.uint64) & U64(M32)
    r = int(r) & 31
    if r == 0:
        return v
    return ((v << U64(r)) | (v >> U64(32 - r))) & U64(M32)


def _rc(i):
    return (((i + 1) * CA) & M32, ((i + 1) * CB) & M32)


def mix_lane2_s2_const_scalar(val, key):
    val &= (1 << 64) - 1
    key &= (1 << 64) - 1
    x = val ^ key
    a, b = x & M32, (x >> 32) & M32
    for i in range(2):
        a = (a * CA) & M32
        b = (b * CB) & M32
        t = a ^ _rotl32_scalar(b, 11)
        b = b ^ _rotl32_scalar(t, 17)
        a = t
        rca, rcb = _rc(i)
        a ^= rca
        b ^= rcb
    return (b << 32) | a


def mix_lane2_s2_const_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    a, b = x & U64(M32), (x >> U64(32)) & U64(M32)
    for i in range(2):
        a = (a * U64(CA)) & U64(M32)
        b = (b * U64(CB)) & U64(M32)
        t = a ^ _rotl32_np(b, 11)
        b = b ^ _rotl32_np(t, 17)
        a = t
        rca, rcb = _rc(i)
        a = a ^ U64(rca)
        b = b ^ U64(rcb)
    return ((b << U64(32)) | a) & np.uint64(0xFFFFFFFFFFFFFFFF)


if __name__ == "__main__":
    check_model_equiv(mix_lane2_s2_const_scalar, mix_lane2_s2_const_np,
                      "lane2_s2_const")
