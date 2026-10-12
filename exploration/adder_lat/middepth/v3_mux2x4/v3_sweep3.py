#!/usr/bin/env python3
"""Graded wiring: allocate MUX input slots by importance, honestly.

Importance weights: bits 0..5 -> 8 (LIN needs these everywhere, strongly);
bits 6..17 -> 4 (DIFF needs these into low-8); bits 18..63 -> 2 (honest:
they still influence, just weaker; Fisher doesn't test them).

Per stage, per output j: draw 3 DISTINCT inputs with P(i) propto weight(i).
E[slots to bit k] = 192 * w(k)/sum(w). Growth per stage ~ slots/2.

Also enforces: no degenerate triple (all three must be distinct).
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
import v3_sweep as VS  # noqa: E402

INNER_KEYS = [0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA]

W8 = 8
W4 = 4
W2 = 2


def weights(w8=W8, w4=W4, w2=W2):
    w = np.full(64, w2, dtype=float)
    w[0:6] = w8
    w[6:18] = w4
    return w / w.sum()


def gen_graded(seed, nstages=4, w8=W8, w4=W4, w2=W2):
    rng = np.random.default_rng(seed)
    p = weights(w8, w4, w2)
    stages = []
    for _ in range(nstages):
        triples = []
        for _ in range(64):
            # draw 3 distinct with proba propto p (rejection)
            while True:
                idx = rng.choice(64, size=3, replace=False, p=p)
                if len(set(int(v) for v in idx)) == 3:
                    triples.append(tuple(int(v) for v in idx))
                    break
        stages.append(triples)
    return stages


def n_varying(stages, key, nblocks=4):
    """How many output bits vary across 64-consecutive blocks (LIN proxy)."""
    M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
    V = np.arange(N, dtype=np.uint64)
    K = np.full(N, np.uint64(key), dtype=np.uint64)
    x = VS.apply_stages((V ^ K) & M64, stages)
    S = ((x ^ VS.rotl(K, 13)) & M64).astype(np.uint64)
    out = []
    for b in range(nblocks):
        blk = S[b * 64:(b + 1) * 64]
        v = sum(1 for j in range(64)
                if len(set((int(vv) >> j) & 1 for vv in blk)) > 1)
        out.append(v)
    return out


if __name__ == "__main__":
    for (w8, w4, w2) in [(8, 4, 2), (12, 4, 1), (16, 4, 1)]:
        for seed in [0x5EED, 0xBEEF]:
            stages = gen_graded(seed, w8=w8, w4=w4, w2=w2)
            nv = n_varying(stages, INNER_KEYS[0])
            t0 = time.time()
            seq = VS.gen_seq(stages, INNER_KEYS, N)
            res = screen_lin_diff(seq, verbose=False)
            dt = time.time() - t0
            lin_ds = [res["lin_detail"][k]["D"] for k in res["lin_detail"]]
            diff_zs = [res["diff_detail"][k]["worst_z"] for k in res["diff_detail"]]
            print(f"w=({w8},{w4},{w2}) seed={seed:#x} nvary={nv} "
                  f"LIN D={lin_ds} DIFF worst|z|={max(diff_zs):.1f} ({dt:.0f}s)",
                  flush=True)
