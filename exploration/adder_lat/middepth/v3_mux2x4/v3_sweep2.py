#!/usr/bin/env python3
"""Focused wiring v2: force low-6 bits into every output (LIN), low-18 into
low-8 outputs (DIFF).

D1: every output: s drawn from bits<6 (forced), a,b uniform distinct.
D2: D1 + outputs j<8: (s,a,b) all drawn from bits<18.
D3: D2 but for j<8, (s,a,b) drawn from bits<12.
D4: every output: s,a drawn from bits<6 (two forced), b uniform.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")

from lin_diff import screen_lin_diff  # noqa: E402
from screen_lib import N  # noqa: E402
import v3_sweep as VS  # noqa: E402 (apply_stages, gen_seq, rotl)

INNER_KEYS = [0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA]


def gen_D(tag, seed, nstages=4):
    rng = np.random.default_rng(seed)
    stages = []
    for _ in range(nstages):
        triples = []
        for j in range(64):
            if tag in ("D2", "D3") and j < 8:
                fin = 18 if tag == "D2" else 12
                pool = rng.choice(fin, size=3, replace=False)
                triples.append(tuple(int(v) for v in pool))
                continue
            if tag == "D4":
                s = int(rng.integers(0, 6)); a = int(rng.integers(0, 6))
                b = int(rng.integers(0, 64))
                while len({s, a, b}) < 3:
                    b = int(rng.integers(0, 64))
            else:  # D1
                s = int(rng.integers(0, 6))
                a = int(rng.integers(0, 64)); b = int(rng.integers(0, 64))
                while len({s, a, b}) < 3:
                    a = int(rng.integers(0, 64)); b = int(rng.integers(0, 64))
            triples.append((s, a, b))
        stages.append(triples)
    return stages


if __name__ == "__main__":
    for tag in ["D1", "D2", "D3", "D4"]:
        for seed in [0x5EED, 0xBEEF]:
            stages = gen_D(tag, seed)
            t0 = time.time()
            seq = VS.gen_seq(stages, INNER_KEYS, N)
            res = screen_lin_diff(seq, verbose=False)
            dt = time.time() - t0
            lin_ds = [res["lin_detail"][k]["D"] for k in res["lin_detail"]]
            diff_zs = [res["diff_detail"][k]["worst_z"] for k in res["diff_detail"]]
            print(f"{tag} seed={seed:#x} LIN D={lin_ds} "
                  f"DIFF worst|z|={max(diff_zs):.1f} ({dt:.0f}s)", flush=True)
