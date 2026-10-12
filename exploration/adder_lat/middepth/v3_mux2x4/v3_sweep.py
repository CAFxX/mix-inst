#!/usr/bin/env python3
"""Sweep focused-wiring variants, measuring the REAL Fisher DIFF/LIN z.

Variants (per stage, seeded):
  A: j<8  <- bits<18;          j>=8 <- 1x bits<18 + 2x uniform(64)
  B: j<64 <- bits<18           (all outputs from low bits; high inputs ignored)
  C: j<8  <- bits<12;          j>=8 <- 1x bits<12 + 2x uniform(64)
  D: j<8  <- bits<18 (2 draws share inputs -> more paths); j>=8 as A
Each variant x 3 seeds. Reports DIFF worst|z| and LIN D per key (inner 2 keys
for speed, then full 10-key on the best).
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
from screen_lib import KEYS, N  # noqa: E402
import v3_focus as VF  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
INNER_KEYS = [0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA]
KEYS10 = [int(k) for k in KEYS]


def gen_variant(tag, seed, nstages=4):
    rng = np.random.default_rng(seed)
    stages = []
    for _ in range(nstages):
        triples = []
        for j in range(64):
            if tag == "A":
                fin, fout = 18, 8
            elif tag == "B":
                fin, fout = 18, 64
            elif tag == "C":
                fin, fout = 12, 8
            elif tag == "D":
                fin, fout = 18, 8
            if j < fout:
                pool = rng.choice(fin, size=3, replace=False)
            else:
                if tag == "B":
                    pool = rng.choice(fin, size=3, replace=False)
                else:
                    lo = rng.integers(0, fin)
                    pool = np.array([lo, rng.integers(0, 64), rng.integers(0, 64)])
                    while len(set(int(v) for v in pool)) < 3:
                        pool = np.array([lo, rng.integers(0, 64), rng.integers(0, 64)])
            triples.append(tuple(int(v) for v in pool))
        stages.append(triples)
    return stages


def apply_stages(x, stages):
    x = np.asarray(x, dtype=np.uint64)
    for triples in stages:
        y = np.zeros(x.shape, dtype=np.uint64)
        for j, (s, a, b) in enumerate(triples):
            sel = (x >> np.uint64(s)) & np.uint64(1)
            av = (x >> np.uint64(a)) & np.uint64(1)
            bv = (x >> np.uint64(b)) & np.uint64(1)
            y |= np.where(sel == 1, av, bv).astype(np.uint64) << np.uint64(j)
        x = y
    return x & M64


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x & M64


def gen_seq(stages, keys, n):
    seq = {}
    V = np.arange(n, dtype=np.uint64)
    for key in keys:
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        x = apply_stages((V ^ K) & M64, stages)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return seq


if __name__ == "__main__":
    for tag in ["A", "B", "C", "D"]:
        for seed in [0x5EED, 0xBEEF, 0xCAFE]:
            stages = gen_variant(tag, seed)
            t0 = time.time()
            seq = gen_seq(stages, INNER_KEYS, N)
            res = screen_lin_diff(seq, verbose=False)
            dt = time.time() - t0
            lin_ds = [res["lin_detail"][k]["D"] for k in res["lin_detail"]]
            diff_zs = [res["diff_detail"][k]["worst_z"] for k in res["diff_detail"]]
            print(f"var={tag} seed={seed:#x} LIN D={lin_ds} "
                  f"DIFF worst|z|={max(diff_zs):.1f} ({dt:.0f}s)", flush=True)
