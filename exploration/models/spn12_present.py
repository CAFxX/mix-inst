"""Baseline: 12-round PRESENT-style SPN (the current candidate under test).

x = val ^ key
for i in 0..11:
    rk[i] = ROTL64(key, 13*(i+1) mod 64) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15 mod 2^64
    x = pLayer(SBOX16(x ^ rk[i]))
out = x ^ rk[12]

Bijectivity (fixed key): xor with round key (bijection), 16x bijective 4-bit
PRESENT S-box (bijection), PRESENT pLayer bit-permutation (bijection), final
xor whitening (bijection). Composition of bijections => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, sbox16_np, present_perm_np,
                        present_sbox_table, check_model_equiv)

M64 = (1 << 64) - 1
_GOLDEN = np.uint64(0x9E3779B97F4A7C15)
_SBOX = present_sbox_table()


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def mix_spn12_present_scalar(val, key):
    # scalar reference (bit-exact vs rtl/mix_spn12.v golden vectors)
    SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
    P = [(16 * i) % 63 for i in range(63)] + [63]
    val &= M64; key &= M64
    x = val ^ key
    for i in range(12):
        r = (13 * (i + 1)) & 63
        rk = (((key << r) | (key >> (64 - r))) & M64 if r else key) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)
        x ^= rk
        y = 0
        for s in range(16):
            y |= SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
        z = 0
        for b in range(64):
            if (y >> b) & 1:
                z |= 1 << P[b]
        x = z
    r = (13 * 13) & 63
    rk = (((key << r) | (key >> (64 - r))) & M64 if r else key) ^ ((13 * 0x9E3779B97F4A7C15) & M64)
    return (x ^ rk) & M64


def mix_spn12_present_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(12):
        rk = rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)
        x = present_perm_np(sbox16_np(x ^ rk, _SBOX))
    x ^= rotl64_np(k, U64(13 * 13)) ^ _rc(12)
    return x


if __name__ == "__main__":
    check_model_equiv(mix_spn12_present_scalar, mix_spn12_present_np, "spn12-present")
    # golden vectors from ~/workspace/mix/rtl/golden_vectors.txt (12 rounds)
    golden = [
        (0x0000000000000000, 0x0000000000000000, 0x024cbda01257a07a),
        (0x0000000000000000, 0xFFFFFFFFFFFFFFFF, 0x41ce82eae7b9487d),
        (0xFFFFFFFFFFFFFFFF, 0x0000000000000000, 0x9e9a78aa35d41d14),
        (0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF, 0x73f6f6d08caed0da),
        (0x0123456789ABCDEF, 0xFEDCBA9876543210, 0xda73e6ab744e5547),
        (0x0000000000000001, 0x9E3779B97F4A7C15, 0xb5694e7be81babec),
        (0x8000000000000000, 0x0000000000000001, 0xf6fd3592929acc2b),
        (0xDEADBEEFCAFEBABE, 0x123456789ABCDEF0, 0xff99021f1b965f21),
    ]
    for v, kk, e in golden:
        g = mix_spn12_present_scalar(v, kk)
        assert g == e, (hex(v), hex(kk), hex(g), hex(e))
    print("golden vectors (12-round, from rtl/golden_vectors.txt): 8/8 match")
