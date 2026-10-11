#!/usr/bin/env python3
"""Batch-33 pilot: proxy-guided 6-stage AND rotation schedule screen (track 6).

Triage = EXACT S1 DIFF computation (lin_diff.diff_cell_logps, all 10 keys,
sequential inputs, ~40s/candidate, no synthesis). KEEP bar: max worst|z| < 10
(al_and6a ~= 3; as6_200_106 = 71.4 on keys 0x0/0x1234).
Survivors escalate to S0 + full S1 via the normal pipeline.

Rotation sampling: per stage (a,b,c) with a,b in [1..63], c in [0..63],
a != b (AND operands distinct), deduped.
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, N_DIFF_PAIRS
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def eval_sched(stages):
    """stages = [(a,b,c)] x6. Returns max worst|z| over 10 keys."""
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_cfg = None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for a, b, c in stages:
            x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_cfg = wz, (key, )
    return worst, worst_cfg[0]


def main():
    rng = np.random.default_rng(0xB33)
    n_try = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    keep = []
    for t in range(n_try):
        stages = []
        seen = set()
        while len(stages) < 6:
            a = int(rng.integers(1, 64))
            b = int(rng.integers(1, 64))
            if a == b:
                continue
            c = int(rng.integers(0, 64))
            if (a, b, c) in seen:
                continue
            seen.add((a, b, c))
            stages.append((a, b, c))
        wz, key = eval_sched(stages)
        flag = "KEEP" if wz < 10 else "kill"
        print("try %2d maxworst|z|=%8.1f killkey=%#x %s stages=%s" %
              (t, wz, key, flag, stages), flush=True)
        if wz < 10:
            keep.append((wz, stages))
    print("=== %d/%d KEEP ===" % (len(keep), n_try), flush=True)
    for wz, stages in sorted(keep):
        print("KEEP z=%.1f %s" % (wz, stages), flush=True)


if __name__ == "__main__":
    main()
