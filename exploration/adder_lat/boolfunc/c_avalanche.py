#!/usr/bin/env python3
"""Design C: quick avalanche proxy to pick the best F offset set.

Metric (mirrors d2_sweep.avalanche): n_x random 64-bit inputs, all 64
single-bit flips, mean fraction of output bits flipped (and mean count).
"""
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/boolfunc")

import numpy as np

from c_model import feistel_vec

OFFSET_SETS = [(1, 3, 5, 7), (1, 5, 9, 13), (3, 7, 11, 15)]


def popcnt(a):
    b = np.asarray(a, dtype=np.uint64).view(np.uint8).reshape(-1, 8)
    return np.unpackbits(b, axis=1).sum(axis=1)


def avalanche(ab, n_x=1024, seed=0xA7A1):
    rng = np.random.default_rng(seed)
    X = rng.integers(0, 2**64, size=n_x, dtype=np.uint64)
    base = feistel_vec(X, *ab)
    tot = 0
    for k in range(64):
        d = np.uint64(1) << np.uint64(k)
        tot += int(popcnt(feistel_vec(X ^ d, *ab) ^ base).sum())
    frac = tot / (64 * n_x)
    return frac, frac * 64


def main():
    print("Design C avalanche proxy (n_x=1024, all 64 single-bit flips):")
    best, bestv = None, -1.0
    for ab in OFFSET_SETS:
        frac, cnt = avalanche(ab)
        print(f"  offsets {ab}: mean frac={frac:.4f} mean count={cnt:.2f}/64")
        if cnt > bestv:
            best, bestv = ab, cnt
    print(f"BEST: {best} ({bestv:.2f}/64)")


if __name__ == "__main__":
    main()
