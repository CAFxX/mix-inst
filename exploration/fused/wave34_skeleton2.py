#!/usr/bin/env python3
"""Wave-34 skeleton test v2 (refined).

Counts always-1 (mm==1.0, deterministic DIFFERENCE — the skeleton signature)
separately from always-0 (mm==0.0, weak diffusion / untouched bits).
Track-6 hypothesis: V0 shows always-1 bits from the linear cross term;
V1/V2/V3 do not. Also reports worst|z| per the wave-34 gate for context.
"""
import sys
import random
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
from wave34_probe import make_stages, make_mix

LOGN = 16
KEY = np.uint64(0x123456789ABCDEF0)


def analyze(mix_fn, logN=LOGN):
    N = 1 << logN
    K = np.full(N, KEY)
    xs = np.arange(N, dtype=np.uint64)
    a1 = a0 = 0
    worst_z = 0.0
    worst = None
    npairs = N
    for k in range(64):
        d0 = np.uint64(1) << np.uint64(k)
        y0 = mix_fn(xs, K)
        y1 = mix_fn(xs ^ d0, K)
        d = y0 ^ y1
        bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :])) & np.uint64(1)).astype(np.float64)
        mm = bitmat.mean(axis=0)
        a1 += int(np.sum(mm == 1.0))
        a0 += int(np.sum(mm == 0.0))
        z = np.abs((mm - 0.5) / np.sqrt(0.25 / npairs))
        m = float(z.max())
        if m > worst_z:
            worst_z, worst = m, (k, int(np.argmax(z)))
    return a1, a0, worst_z, worst


if __name__ == "__main__":
    for variant, nstages, vs in [("V0", 3, 0xA0), ("V1", 3, 0xB1),
                                 ("V2", 3, 0xC2), ("V3", 4, 0xD3)]:
        for tryno in (1, 2):
            rng = random.Random(0x34 ^ vs)
            stages = None
            for t in range(tryno):
                stages = make_stages(variant, nstages, rng)
            mix_fn = make_mix(variant, stages)
            a1, a0, wz, w = analyze(mix_fn)
            print(f"{variant} try-{tryno}: always-1={a1} always-0={a0} "
                  f"worst|z|={wz:.1f} at {w}", flush=True)
    print("SKELETON2 DONE", flush=True)
