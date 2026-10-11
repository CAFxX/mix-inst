"""Round-2 lane2_il_e: bit-interleaved 2x32-bit lanes.

Pipeline (fixed key):
  x = val ^ key
  y = INTERLEAVE2(x): bit i of x -> bit (i%2)*32 + (i//2) of y.
    Lane 0 holds even bits {0,2,...,62}, lane 1 holds odd bits {1,3,...,63}.
    Small inputs drive both lanes (D3 dead-lane fix).
  per 32-bit lane l: w[l] = y[l] * C[l]   (C odd => bijection mod 2^32)
  bijective downmix: w[l] ^= w[l]>>16; w[l] ^= w[l]>>8  (high->low)
  Feistel cross on (w0,w1), two rounds with rotations (11,17) and (7,19):
    sequential half-steps, bijective for any F.
  z = DEINTERLEAVE2(w)  (inverse bit-permutation)
  out = z ^ ROTL64(key, 7)

Bijectivity (fixed key): INTERLEAVE2/DEINTERLEAVE2 are bit-permutations;
x*=C with C odd is a bijection mod 2^32; Feistel sequential half-steps are
bijective for ANY F; final key-xor is a bijection. Composition => permutation.
Constants 0x9E3779B9, 0x85EBCA77: both asserted ODD at import time.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import check_model_equiv, bijectivity_spotcheck, rotl64_np

M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
U64 = np.uint64
CONSTS = (0x9E3779B9, 0x85EBCA77)
for _c in CONSTS:
    assert _c & 1, f"lane mult constant 0x{_c:08X} is EVEN - mult is not bijective!"


def _interleave2_scalar(x):
    y = 0
    for i in range(64):
        if (x >> i) & 1:
            y |= 1 << (((i % 2) * 32) + (i // 2))
    return y


def _deinterleave2_scalar(w):
    z = 0
    for i in range(64):
        if (w >> i) & 1:
            l, j = divmod(i, 32)
            z |= 1 << (l + 2 * j)
    return z


def _interleave2_np(x):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for j in range(32):
        bit0 = (x >> U64(2 * j)) & U64(1)
        bit1 = (x >> U64(2 * j + 1)) & U64(1)
        y |= bit0 << U64(j)
        y |= bit1 << U64(32 + j)
    return y


def _deinterleave2_np(w):
    w = np.asarray(w, dtype=np.uint64)
    z = np.zeros_like(w)
    for l in range(2):
        lane = (w >> U64(32 * l)) & U64(M32)
        for j in range(32):
            z |= ((lane >> U64(j)) & U64(1)) << U64(2 * j + l)
    return z


def _downmix32_scalar(w):
    w ^= w >> 16
    w ^= w >> 8
    return w & M32


def _downmix32_np(w):
    w = np.asarray(w, dtype=np.uint64)
    w = w ^ (w >> U64(16))
    w = w ^ (w >> U64(8))
    return w & U64(M32)


def _rotl32_scalar(x, r):
    r %= 32
    return (((x << r) | (x >> (32 - r))) & M32) if r else x


def _rotl32_np(v, r):
    v = np.asarray(v, dtype=np.uint64) & U64(M32)
    r = int(r) & 31
    if r == 0:
        return v
    return ((v << U64(r)) | (v >> U64(32 - r))) & U64(M32)


def _cross32_scalar(p, q, r1, r2):
    t = p ^ _rotl32_scalar(q, r1)
    q = q ^ _rotl32_scalar(t, r2)
    p = t
    return p, q


def _cross32_np(p, q, r1, r2):
    t = p ^ _rotl32_np(q, r1)
    q = q ^ _rotl32_np(t, r2)
    p = t
    return p, q


def mix_lane2_il_e_scalar(val, key):
    val &= M64
    key &= M64
    y = _interleave2_scalar(val ^ key)
    a = _downmix32_scalar((((y & M32) * CONSTS[0]) & M32))
    b = _downmix32_scalar(((((y >> 32) & M32) * CONSTS[1]) & M32))
    a, b = _cross32_scalar(a, b, 11, 17)
    a, b = _cross32_scalar(a, b, 7, 19)
    w = (b << 32) | a
    z = _deinterleave2_scalar(w)
    return z ^ (((key << 7) | (key >> 57)) & M64)


def mix_lane2_il_e_np(val, key):
    k = np.asarray(key, dtype=np.uint64)
    x = np.asarray(val, dtype=np.uint64) ^ k
    y = _interleave2_np(x)
    a = _downmix32_np((((y & U64(M32)) * U64(CONSTS[0])) & U64(M32)))
    b = _downmix32_np(((((y >> U64(32)) & U64(M32)) * U64(CONSTS[1])) & U64(M32)))
    a, b = _cross32_np(a, b, 11, 17)
    a, b = _cross32_np(a, b, 7, 19)
    w = (b << U64(32)) | a
    z = _deinterleave2_np(w)
    return z ^ rotl64_np(k, 7)


if __name__ == "__main__":
    check_model_equiv(mix_lane2_il_e_scalar, mix_lane2_il_e_np, "lane2_il_e")
    bijectivity_spotcheck(mix_lane2_il_e_np, "lane2_il_e")
