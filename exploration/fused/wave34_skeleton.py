#!/usr/bin/env python3
"""Wave-34 cross-track test of track-6's DIFF-skeleton hypothesis.

Hypothesis (track-6, 21:20): the linear cross term in two-state constructions
creates a deterministic differential skeleton D[x1]_i = d_i^d_{i-c}.
Prediction: V0 (linear cross terms rotl(y,c)/rotl(x,f)) shows deterministic
output-differential bits for single-bit input deltas; V1/V2/V3 (AND-only
cross-lane influence) do not.

Method: take the exact try-1 and try-2 candidates from the wave-34 RNG
streams (same seeds as wave34_probe.py), and for each of the 64 single-bit
input deltas count output bits with observed difference frequency exactly
1.0 or 0.0 at logN=16 (deterministic bits). Report per-variant totals.
"""
import sys
import random
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
from wave34_probe import make_stages, make_mix

LOGN = 16
KEY = np.uint64(0x123456789ABCDEF0)


def det_bits(mix_fn, logN=LOGN):
    N = 1 << logN
    K = np.full(N, KEY)
    total = 0
    detail = {}
    for k in range(64):
        d0 = np.uint64(1) << np.uint64(k)
        xs = np.arange(N, dtype=np.uint64)
        y0 = mix_fn(xs, K)
        y1 = mix_fn(xs ^ d0, K)
        d = y0 ^ y1
        bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :])) & np.uint64(1)).astype(np.float64)
        mm = bitmat.mean(axis=0)
        det = np.where((mm == 1.0) | (mm == 0.0))[0]
        if len(det):
            detail[k] = (len(det), det.tolist())
        total += len(det)
    return total, detail


if __name__ == "__main__":
    for variant, nstages, vs in [("V0", 3, 0xA0), ("V1", 3, 0xB1),
                                 ("V2", 3, 0xC2), ("V3", 4, 0xD3)]:
        for tryno in (1, 2):
            rng = random.Random(0x34 ^ vs)
            stages = None
            for t in range(tryno):
                stages = make_stages(variant, nstages, rng)
            mix_fn = make_mix(variant, stages)
            total, detail = det_bits(mix_fn)
            print(f"{variant} try-{tryno}: {total} deterministic output bits "
                  f"over 64 single-bit deltas (logN={LOGN})", flush=True)
            for k, (n, det) in sorted(detail.items()):
                print(f"  delta-bit {k:2d}: {n} det bits {det}", flush=True)
    print("SKELETON TEST DONE", flush=True)
