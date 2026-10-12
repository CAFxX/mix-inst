#!/usr/bin/env python3
"""Direction 4 models: 3-stage MUX2 + diffusion stage variants.

Option A: 3x MUX2 (base stages 0-2) + 3-term rotl-XOR diffusion:
    d[i] = m[i] ^ m[(i-r1)%64] ^ m[(i-r2)%64]
Option C: 3x MUX2 + bit-Feistel diffusion:
    d[i] = m[i] ^ (m[(i-a)%64] & m[(i-b)%64])
Battery convention: x = V^K in, S = out ^ rotl(K,13).
"""
import sys
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
BASE3 = [(0, 7, 29), (13, 31, 53), (5, 19, 43)]  # first 3 stages of O148 base

def rotl(x, r):
    r %= 64
    if r == 0:
        return x & M64
    r = np.uint64(r)
    return (((x << r) | (x >> (np.uint64(64) - r))) & M64)

def mux2_layer(x, s, p1, p2):
    sel = rotl(x, s); a = rotl(x, p1); b = rotl(x, p2)
    return ((sel & a) | ((~sel) & b)) & M64

def diff_xor3(x, r1, r2):
    return (x ^ rotl(x, r1) ^ rotl(x, r2)) & M64

def diff_feistel(x, a, b):
    return (x ^ (rotl(x, a) & rotl(x, b))) & M64

def apply_A(x, r1, r2, stages=BASE3):
    x = np.asarray(x, dtype=np.uint64) & M64
    for (s, p1, p2) in stages:
        x = mux2_layer(x, s, p1, p2)
    return diff_xor3(x, r1, r2)

def apply_C(x, a, b, stages=BASE3):
    x = np.asarray(x, dtype=np.uint64) & M64
    for (s, p1, p2) in stages:
        x = mux2_layer(x, s, p1, p2)
    return diff_feistel(x, a, b)

def gen_seq(fn, keys, n):
    seq = {}
    V = np.arange(n, dtype=np.uint64)
    for key in keys:
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        x = fn((V ^ K) & M64)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return seq

def avalanche(fn, key, nxs=4096, seed=0x5EED):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=nxs, dtype=np.uint64)
    K = np.uint64(key)
    base = fn((xs ^ K) & M64)
    flips = []
    for j in range(64):
        dj = np.uint64(1) << np.uint64(j)
        out = fn(((xs ^ K) ^ dj) & M64)
        d = out ^ base
        flips.append(float(np.mean([bin(int(v)).count("1") for v in d])))
    return sum(flips)/64, min(flips), max(flips)
