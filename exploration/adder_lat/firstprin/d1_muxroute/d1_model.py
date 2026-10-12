#!/usr/bin/env python3
"""Bit-exact model of d1_D (2:1 MUX, s=a&b) and d1_2stage. Mirrors gen_d1.py taps."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def bit(x, j):
    return ((np.asarray(x, dtype=np.uint64) >> np.uint64(j)) & np.uint64(1))


def stage_D(x, d0s, d1s, sa, sb):
    """y[j] = (x[(j+sa)] & x[(j+sb)]) ? x[(j+d0s)] : x[(j+d1s)]."""
    x = np.asarray(x, dtype=np.uint64) & M64
    y = np.zeros_like(x)
    for j in range(64):
        s = bit(x, (j + sa) % 64) & bit(x, (j + sb) % 64)
        d0 = bit(x, (j + d0s) % 64)
        d1 = bit(x, (j + d1s) % 64)
        y |= (np.where(s, d0, d1).astype(np.uint64) << np.uint64(j))
    return y & M64


def apply_2stage(x):
    x = stage_D(x, 5, 37, 13, 51)
    x = stage_D(x, 11, 29, 3, 43)
    return x & M64


def stage_H(x, d0s, d1s, sa, sb, sc):
    """y[j] = (~((x[(j+sa)] & x[(j+sb)]) | x[(j+sc)])) ? x[(j+d0s)] : x[(j+d1s)]."""
    x = np.asarray(x, dtype=np.uint64) & M64
    y = np.zeros_like(x)
    for j in range(64):
        s = 1 - (((bit(x, (j + sa) % 64) & bit(x, (j + sb) % 64)) |
                  bit(x, (j + sc) % 64)))
        d0 = bit(x, (j + d0s) % 64)
        d1 = bit(x, (j + d1s) % 64)
        y |= (np.where(s, d0, d1).astype(np.uint64) << np.uint64(j))
    return y & M64


def apply_2stage_H(x):
    x = stage_H(x, 5, 37, 13, 51, 29)
    x = stage_H(x, 11, 29, 3, 43, 7)
    return x & M64


def rotl(x, r):
    r %= 64
    if r == 0:
        return x & M64
    r = np.uint64(r)
    return (((x << r) | (x >> (np.uint64(64) - r))) & M64)


def gen_seq(keys, n, apply=apply_2stage):
    """v3 harness convention: x = V^K, stages, S = x ^ rotl(K,13)."""
    seq = {}
    V = np.arange(n, dtype=np.uint64)
    for key in keys:
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        x = apply(x)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return seq


def mean_avalanche(apply, n=4096):
    """Mean # output bits flipped over 64 single-bit deltas x n inputs."""
    x = np.arange(n, dtype=np.uint64) * np.uint64(0x9E3779B97F4A7C15)
    y0 = apply(x)
    tot = 0
    for b in range(64):
        y1 = apply(x ^ (np.uint64(1) << np.uint64(b)))
        tot += sum(bin(int(v)).count("1") for v in (y0 ^ y1))
    return tot / (64 * n)


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "D"
    apply = {"D": apply_2stage, "H": apply_2stage_H}[which]
    print(f"mean avalanche [{which}] (bits flipped per single-bit input delta):",
          round(mean_avalanche(apply), 3))
