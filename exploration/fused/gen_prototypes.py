#!/usr/bin/env python3
"""Generate 3 fused nonlinear-diffusive prototypes for Track 8.

Prototype 1 (f8_maj5): Majority-5 cascade. Each output bit = maj5 of 5 rotated
inputs. Fan-in 5 vs chi's 3. Depth ~2 gates (same as chi) but much wider.
Hypothesis: 3-4 stages suffice for full diffusion (log_5(64)~2.6).

Prototype 2 (f8_nlcarry): Nonlinear carry. Single 64-bit add (carry = maj,
already nonlinear) + XOR with rotated sum. Lower-triangular from add,
upper-triangular from rotate-XOR. Full diffusion in ONE add + XOR.
Hypothesis: ~11-16u total, smashes 19.8u floor if quality holds.

Prototype 3 (f8_sbox8): 8-bit S-box layer. Each output byte = SBOX(input byte)
with low-depth boolean circuit, then cross-byte mixing. Higher fan-in (8)
per stage than 4-bit S-boxes.
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x

def _maj5(a, b, c, d, e):
    """5-bit majority: 1 iff >=3 inputs are 1. Computed via threshold."""
    # Sum bits; maj5 = (s >= 3). Use: maj5 = (a&b&(c|d|e)) | (c&d&(a|b|e)) | ...
    # Simpler: pairwise ANDs then OR of 3-combos via adder trick
    # Direct: count = a+b+c+d+e (as integers per bit, vectorized)
    # For numpy vectorization, compute sum across the 5 values
    s = (a.astype(np.uint64) + b.astype(np.uint64) + c.astype(np.uint64)
         + d.astype(np.uint64) + e.astype(np.uint64))
    # This doesn't work bitwise! Need per-bit majority.
    # Per-bit: maj5 bit i = 1 iff at least 3 of {a[i],b[i],c[i],d[i],e[i]} are 1
    # Boolean formula: OR over all C(5,3)=10 triples of AND3
    t = ((a & b & c) | (a & b & d) | (a & b & e) |
         (a & c & d) | (a & c & e) | (a & d & e) |
         (b & c & d) | (b & c & e) | (b & d & e) |
         (c & d & e))
    return t & M64

# --- Prototype 1: maj5 cascade ---
# 4 stages of maj5 on rotated copies. Rotations chosen for spread.
MAJ5_STAGES = [
    (1, 7, 23, 37, 53),
    (3, 11, 29, 41, 59),
    (5, 13, 31, 43, 61),
    (2, 17, 33, 47, 57),
]
RC1 = [0x9e3779b97f4a7c15, 0x3c6ef372fe94f82a, 0xdaa66d2c7ddf743f, 0x78dde6e5fd29f054]

def mix_f8_maj5_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    for i, (a, b, c, d, e) in enumerate(MAJ5_STAGES):
        t = _maj5(_rotl(x, a), _rotl(x, b), _rotl(x, c), _rotl(x, d), _rotl(x, e))
        t = (t ^ _rotl(x, (a + 32) % 64) ^ np.uint64(RC1[i])) & M64
        x = t
    x = (x ^ _rotl(k, 13)) & M64
    return x & M64

def mix_f8_maj5(v, k):
    return int(mix_f8_maj5_np(np.uint64(v), np.uint64(k)))

# --- Prototype 2: nonlinear carry ---
# x1 = x + k (carry chain = nonlinear maj, lower-triangular diffusion)
# x2 = x1 ^ rotl(x1, 32) ^ rotl(x1, 17) (upper-triangular fill)
# x3 = x2 + k2 (second carry, now full diffusion)
# Then final whitening.
def mix_f8_nlcarry_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    x = (x + np.uint64(0x9e3779b97f4a7c15)) & M64       # add 1: nonlinear carry
    x = (x ^ _rotl(x, 32) ^ _rotl(x, 17)) & M64          # cross-mix
    x = (x + np.uint64(0x3c6ef372fe94f82a)) & M64       # add 2: full diffusion
    x = (x ^ _rotl(x, 29) ^ _rotl(k, 11)) & M64         # final whiten
    return x & M64

def mix_f8_nlcarry(v, k):
    return int(mix_f8_nlcarry_np(np.uint64(v), np.uint64(k)))

# --- Prototype 3: 8-bit S-box ---
# Simple low-depth 8-bit S-box: x -> x ^ ((x rol 3) & (x rol 5)) ^ ((x rol 1) | (x rol 7))
# applied per byte, then bytes permuted + XORed across.
def _sbox8_byte(b):
    # b is 0..255; operate within byte
    r1 = ((b << 3) | (b >> 5)) & 0xFF
    r3 = ((b << 5) | (b >> 3)) & 0xFF
    r5 = ((b << 1) | (b >> 7)) & 0xFF
    r7 = ((b << 7) | (b >> 1)) & 0xFF
    return (b ^ (r1 & r3) ^ (r5 | r7)) & 0xFF

_SBOX8 = bytes(_sbox8_byte(b) for b in range(256))

def _sbox8_layer(x_int):
    out = 0
    for i in range(8):
        byte = (x_int >> (i * 8)) & 0xFF
        out |= _SBOX8[byte] << (i * 8)
    return out

def _byteshuffle(x_int):
    # Permute bytes: [0,1,2,3,4,5,6,7] -> [3,0,5,1,6,2,7,4] (spread)
    perm = [3, 0, 5, 1, 6, 2, 7, 4]
    out = 0
    for new_pos, old_pos in enumerate(perm):
        byte = (x_int >> (old_pos * 8)) & 0xFF
        out |= byte << (new_pos * 8)
    return out

def mix_f8_sbox8_np(V, K):
    # Vectorized via Python loop (slow but correct for model)
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    res = np.empty_like(x)
    for idx in range(x.shape[0]):
        xi = int(x[idx])
        for r in range(3):
            xi = _sbox8_layer(xi)
            xi = _byteshuffle(xi)
            xi ^= (0x9e3779b97f4a7c15 >> (r * 11)) & 0xFFFFFFFFFFFFFFFF
            xi ^= ((xi << 13) | (xi >> 51)) & 0xFFFFFFFFFFFFFFFF  # rotl 13
            xi &= 0xFFFFFFFFFFFFFFFF
        res[idx] = np.uint64(xi)
    res = (res ^ _rotl(k, 13)) & M64
    return res & M64

def mix_f8_sbox8(v, k):
    return int(mix_f8_sbox8_np(np.array([v], dtype=np.uint64), np.array([k], dtype=np.uint64))[0])

if __name__ == "__main__":
    # Quick smoke test
    for name, fn in [("f8_maj5", mix_f8_maj5), ("f8_nlcarry", mix_f8_nlcarry), ("f8_sbox8", mix_f8_sbox8)]:
        o1 = fn(0x0, 0x123456789ABCDEF0)
        o2 = fn(0x123456789ABCDEF0, 0x0)
        o3 = fn(0x1, 0x123456789ABCDEF0)  # avalanche check: 1-bit input diff
        diff = bin(o1 ^ o3).count("1")
        print(f"{name}: {o1:016x} {o2:016x} avalanche_bits={diff}/64")
