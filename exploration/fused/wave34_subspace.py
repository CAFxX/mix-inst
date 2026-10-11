#!/usr/bin/env python3
"""Validate the subspace-collapse theory for wave-34 deterministic bits.

Compares always-1 counts under (a) sequential inputs xs=arange(2^16)
(the S1-DIFF methodology used by the wave-34 gate) vs (b) random 64-bit
inputs. If always-1 bits collapse under random inputs, they are an
artifact of the sequential subspace (AND controlling bits constant),
not true full-space deterministic differentials.
"""
import sys
import random
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
from wave34_probe import make_stages, make_mix

LOGN = 16
KEY = np.uint64(0x123456789ABCDEF0)


def always1(mix_fn, xs, logN=LOGN):
    N = 1 << logN
    K = np.full(N, KEY)
    total = 0
    for k in range(64):
        d0 = np.uint64(1) << np.uint64(k)
        y0 = mix_fn(xs, K)
        y1 = mix_fn(xs ^ d0, K)
        d = y0 ^ y1
        bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :])) & np.uint64(1)).astype(np.float64)
        mm = bitmat.mean(axis=0)
        total += int(np.sum(mm == 1.0))
    return total


if __name__ == "__main__":
    rng_np = np.random.default_rng(0x5EED)
    for variant, nstages, vs in [("V0", 3, 0xA0), ("V1", 3, 0xB1)]:
        rng = random.Random(0x34 ^ vs)
        stages = make_stages(variant, nstages, rng)  # try-1
        mix_fn = make_mix(variant, stages)
        xs_seq = np.arange(1 << LOGN, dtype=np.uint64)
        xs_rnd = rng_np.integers(0, 2**64, size=1 << LOGN, dtype=np.uint64)
        # deltas must stay within the sampled set for the random case;
        # use independent random base points (pairs, not a permutation)
        a_seq = always1(mix_fn, xs_seq)
        a_rnd = always1(mix_fn, xs_rnd)
        print(f"{variant} try-1: always-1 sequential={a_seq} random64={a_rnd}", flush=True)
    print("SUBSPACE CHECK DONE", flush=True)
