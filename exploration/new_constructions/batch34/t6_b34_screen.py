#!/usr/bin/env python3
"""Batch-34: exact-DIFF triage for DENSE nonlinear stage families (track 6).

Method = the validated batch-33 triage: EXACT S1 DIFF computation
(lin_diff.diff_cell_logps, all 10 keys, sequential inputs, ~40s/candidate,
no synthesis). KEEP bar: max worst|z| < 10. This bit-for-bit reproduces the
S1 DIFF verdict (validated on b33: 7/7 KEEPs S1-clean, kills predicted).

Families (all with frontier key schedule: pre-whiten x0=v^k,
final out = xN ^ rotl(k,13); linear mask term kept per the load-bearing
proof -- batch 8+10 lesson, fat autopsy):
  d2a3 : x ^= (ra&rb&rc) ^ (rd&re&rf) ^ rg   (dual-AND3, 6 probes/stage) NEW
  a3   : x ^= (ra&rb&rc) ^ rd                 (AND3+mask, 3 probes/stage)
  aoi  : x ^= ~((ra&rb)|rc) ^ rd              (AOI21 complex gate, 3 probes) NEW

Rotation sampling: a,b,c distinct in [1..63] (AND operands distinct,
nonzero -- SEQ-safe close-pair rule inherited); d,e,f distinct in [1..63];
g in [0..63]; deduped per stage.

Usage: t6_b34_screen.py <form> <nstages> <n_try> <seed>
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def apply_stage(x, form, rots):
    if form == "d2a3":
        a, b, c, d, e, f, g = rots
        return (x ^ (rotl(x, a) & rotl(x, b) & rotl(x, c))
                  ^ (rotl(x, d) & rotl(x, e) & rotl(x, f)) ^ rotl(x, g)) & M64
    if form == "a3":
        a, b, c, d = rots
        return (x ^ (rotl(x, a) & rotl(x, b) & rotl(x, c)) ^ rotl(x, d)) & M64
    if form == "aoi":
        a, b, c, d = rots
        return (x ^ (~((rotl(x, a) & rotl(x, b)) | rotl(x, c)) & M64)
                  ^ rotl(x, d)) & M64
    if form == "and1":
        # calibration form: the batch-33 1-AND stage (positive control)
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def nrots(form):
    return {"d2a3": 7, "a3": 4, "aoi": 4}[form]


def draw_stage(rng, form):
    # returns rotation tuple; AND-operand rotations distinct and nonzero
    while True:
        abc = rng.choice(64, size=3, replace=False)
        if 0 in abc:
            continue
        a, b, c = (int(v) for v in abc)
        if form == "d2a3":
            while True:
                df = rng.choice(64, size=3, replace=False)
                if 0 in df:
                    continue
                d, e, f = (int(v) for v in df)
                break
            g = int(rng.integers(0, 64))
            return (a, b, c, d, e, f, g)
        d = int(rng.integers(0, 64))
        return (a, b, c, d)


def eval_sched(form, stages):
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_key = None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for rots in stages:
            x = apply_stage(x, form, rots)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


def main():
    form = sys.argv[1]
    nstages = int(sys.argv[2])
    n_try = int(sys.argv[3]) if len(sys.argv) > 4 else 200
    seed = int(sys.argv[4], 0) if len(sys.argv) > 5 else 0xB34
    rng = np.random.default_rng(seed)
    keep = []
    for t in range(n_try):
        stages, seen = [], set()
        while len(stages) < nstages:
            s = draw_stage(rng, form)
            if s in seen:
                continue
            seen.add(s)
            stages.append(s)
        wz, key = eval_sched(form, stages)
        flag = "KEEP" if wz < 10 else "kill"
        print("try %3d maxworst|z|=%8.1f killkey=%#x %s" % (t, wz, key, flag),
              flush=True)
        if wz < 10:
            keep.append((wz, stages))
    print("=== %s-%d: %d/%d KEEP (seed=%#x) ===" % (form, nstages, len(keep),
                                                   n_try, seed), flush=True)
    for wz, stages in sorted(keep):
        print("KEEP z=%.1f %s" % (wz, stages), flush=True)


if __name__ == "__main__":
    main()
