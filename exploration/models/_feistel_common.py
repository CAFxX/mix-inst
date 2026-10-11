"""Shared helpers for Batch C (short Feistel, 32-bit halves).

Structure (identical for all Batch C candidates):
  L = val[31:0], R = val[63:32]
  L0 = L ^ key[31:0], R0 = R ^ key[63:32]
  round: (L, R) -> (R, L ^ F(R, rk[i]))
  rk[i] = ROTL32(key[31:0], 3*(i+1)) ^ ROTL32(key[63:32], 5*(i+1))
          ^ ((i+1)*0x9E3779B9 mod 2^32)
  NO final swap
  out = { Rn ^ ROTL32(key[63:32],7), Ln ^ ROTL32(key[31:0],7) }

Each candidate module supplies F (scalar + vectorized) and calls
feistel_s / feistel_np from here.
"""
import numpy as np

M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
U64 = np.uint64
_RC32 = 0x9E3779B9

# PRESENT 4-bit S-box (trusted table, also used by spn12_present baseline)
PRESENT_SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
                0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]

# GIFT 4-bit S-box, verified against the GIFT-128 spec paper
# (Banik et al.; cross-checked via IACR ToSC "Linear Cryptanalyses of Three
# AEADs with GIFT-128 as Underlying Primitives": GS = 1 A 4 C 6 F 3 9 2 D B 7 5 0 8 E)
GIFT_SBOX = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9, 0x2,
             0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]
assert len(set(GIFT_SBOX)) == 16, "GIFT S-box not a permutation!"

# P32 bit-permutation: input bit i -> output bit P32(i),
# P32(i) = 8*i mod 31 for i < 31, P32(31) = 31.
# 8 is coprime to 31 so i -> 8*i mod 31 permutes {0..30}; + fixed 31 => permutation of 32.
P32 = [(8 * i) % 31 for i in range(31)] + [31]
assert len(set(P32)) == 32, "P32 is not a permutation!"
_P32_NP = np.array(P32, dtype=np.int64)


def rotl32_s(x, r):
    r &= 31
    x &= M32
    if r == 0:
        return x
    return ((x << r) | (x >> (32 - r))) & M32


def rotl32_np(v, r):
    v = np.asarray(v, dtype=np.uint64) & U64(M32)
    r = int(r) & 31
    if r == 0:
        return v
    return (((v << np.uint64(r)) | (v >> np.uint64(32 - r))) & U64(M32))


def rk_s(key, i):
    """Round key i (0-based): rk[i] per Batch C schedule."""
    klo = key & M32
    khi = (key >> 32) & M32
    j = i + 1
    return (rotl32_s(klo, 3 * j) ^ rotl32_s(khi, 5 * j)
            ^ ((j * _RC32) & M32))


def rk_np(key, i):
    k = np.asarray(key, dtype=np.uint64)
    klo = k & U64(M32)
    khi = (k >> U64(32)) & U64(M32)
    j = i + 1
    return (rotl32_np(klo, 3 * j) ^ rotl32_np(khi, 5 * j)
            ^ U64((j * _RC32) & M32))


def p32_s(x):
    y = 0
    for i in range(32):
        if (x >> i) & 1:
            y |= 1 << P32[i]
    return y


def p32_np(x):
    xf = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(xf)
    for i in range(32):
        y |= ((xf >> U64(i)) & U64(1)) << U64(int(_P32_NP[i]))
    return y


def sbox8_s(x, table):
    y = 0
    for s in range(8):
        y |= table[(x >> (4 * s)) & 0xF] << (4 * s)
    return y


def sbox8_np(x, table):
    xf = np.asarray(x, dtype=np.uint64)
    t = np.asarray(table, dtype=np.uint64)
    y = np.zeros_like(xf)
    for s in range(8):
        idx = ((xf >> U64(4 * s)) & U64(0xF)).astype(np.int64)
        y |= t[idx] << U64(4 * s)
    return y


def feistel_s(val, key, rounds, F):
    """Scalar Batch-C Feistel. F(x, rk) is the candidate's round function."""
    val &= M64
    key &= M64
    klo = key & M32
    khi = (key >> 32) & M32
    L = (val & M32) ^ klo
    R = ((val >> 32) & M32) ^ khi
    for i in range(rounds):
        L, R = R, L ^ F(R, rk_s(key, i))
    out_hi = R ^ rotl32_s(khi, 7)
    out_lo = L ^ rotl32_s(klo, 7)
    return ((out_hi << 32) | out_lo) & M64


def feistel_np(val, key, rounds, F):
    """Vectorized Batch-C Feistel. F(x, rk) is the candidate's round function."""
    v = np.asarray(val, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    klo = k & U64(M32)
    khi = (k >> U64(32)) & U64(M32)
    L = (v & U64(M32)) ^ klo
    R = ((v >> U64(32)) & U64(M32)) ^ khi
    for i in range(rounds):
        L, R = R, L ^ F(R, rk_np(k, i))
    out_hi = R ^ rotl32_np(khi, 7)
    out_lo = L ^ rotl32_np(klo, 7)
    return ((out_hi << U64(32)) | out_lo) & U64(M64)
