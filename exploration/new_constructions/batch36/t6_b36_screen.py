#!/usr/bin/env python3
"""Batch-36: exact-DIFF triage for nested-AND and dual-AND2 stages (track 6).

Two untested degree-2 stage structures at the b33c gate budget
(AND2+2XOR ~= 3 logic levels ~= 3.3u/stage -> 6 stages ~= 19.8u, cost-eligible):

  nested: x ^= ((x^rc) & (ra^rb))     -- linear terms INSIDE the AND
          (batch-32 sandwich had them OUTSIDE: x^=ra^(rb&rc)^rd -- de-duped).
          Per-bit AND input1 flips at 2 positions (x and rc), input2 flips at
          2 positions (ra, rb) -> ~3 expected AND-flips/stage vs b33c's ~2.
          Draw: a,b distinct in [1..63], c in [1..63] (c=0 -> (x^x)=0 kills
          the AND; a=b -> (ra^rb)=0 kills the AND).
  a2a2:   x ^= (ra&rb) ^ (rc&rd)      -- linear mask REPLACED by 2nd AND2
          (the "designed but never triaged" batch-34 follow-up; batch-34's
          dense kill was degree-3 AND3 / dual-AND3 -- this is degree-2).
          Draw: a,b distinct and c,d distinct in [1..63]; {a,b}!={c,d} as
          sets (else the two ANDs cancel -> identity stage).

Method = validated triage: EXACT S1 DIFF (lin_diff.diff_cell_logps, 10 keys,
sequential inputs). KEEP bar: max worst|z| < 10. Positive control: and1 form
+ b33c schedule must give z=3.3.

Usage: t6_b36_screen.py <form> <nstages> <n_try> <seed>
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
    if form == "nested":
        a, b, c = rots
        return (x ^ ((x ^ rotl(x, c)) & (rotl(x, a) ^ rotl(x, b)))) & M64
    if form == "a2a2":
        a, b, c, d = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ (rotl(x, c) & rotl(x, d))) & M64
    if form == "and1":
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def draw_stage(rng, form):
    while True:
        if form == "nested":
            a, b = (int(v) for v in rng.choice(64, size=2, replace=False))
            if a == 0 or b == 0:
                continue
            c = int(rng.integers(1, 64))
            return (a, b, c)
        if form == "a2a2":
            a, b = (int(v) for v in rng.choice(64, size=2, replace=False))
            c, d = (int(v) for v in rng.choice(64, size=2, replace=False))
            if 0 in (a, b, c, d):
                continue
            if {a, b} == {c, d}:
                continue
            return (a, b, c, d)
        raise ValueError(form)


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


B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz, key = eval_sched("and1", B33C_SCHED)
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f killkey=%#x (expect 3.3)"
              % (wz, key), flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    nstages = int(sys.argv[2])
    n_try = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    seed = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0xB36
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
