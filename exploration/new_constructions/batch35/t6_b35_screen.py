#!/usr/bin/env python3
"""Batch-35: exact-DIFF triage for SHIFT-AND deep cascades (track 6).

Genuinely new axis: no prior batch (b8/b15/b30-34, track-5 b22, diffwall v2b)
uses logical shifts -- all use rotations. Shifts are FREE in hardware
(wiring), so a deeper cascade (10 stages) can fit under the 19.8u frontier.

Form:
  shand: x ^= ((x>>a) & (x<<b)) ^ rotl(x, c)
Per-bit: y_j = x_j ^ (x_{j+a} & x_{j-b}) ^ x_{j+c}  (indices mod 64 for the
rotation mask; shift operands zero past the edge -> a+b edge bits/stage have
zero AND term and ride the linear rotation mask).

Co-design rationale:
- Cost: per stage = 1 AND2 + 2 XOR2 (~2 logic levels after the free shifts)
  vs b33c's AND2 + 2 XOR2 with 3 rotation wirings -- same gate count, so
  ~10 stages may cost ~15-20u, competitive with the 19.8u frontier.
- Diffusion: nonlinear influence spreads ~max(a,b) bits/stage; 10 stages x
  up-to-16 shift ~= full 64-bit coverage. Edge-degenerate bits are handled
  by the full-width rotation mask (linear) and by later stages.
- Risk (fmaj lesson): shift maps are non-bijective -> possible difference
  contraction. Mitigated: every output bit keeps its x_j feedback term
  (x^= structure, load-bearing per batch 8+10). Triage decides.

Method = validated batch-33/34 triage: EXACT S1 DIFF (lin_diff.diff_cell_logps,
10 keys, sequential inputs, ~40s/candidate, no synthesis). KEEP bar: max
worst|z| < 10. Positive control: and1 form + b33c schedule must give z=3.3.

Usage: t6_b35_screen.py <form> <nstages> <amax> <n_try> <seed>
  form: shand | and1 (calibration only)
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
    if form == "shand":
        a, b, c = rots
        return (x ^ ((x >> np.uint64(a)) & (x << np.uint64(b))) ^ rotl(x, c)) & M64
    if form == "and1":
        # calibration form: the batch-33 1-AND stage (positive control)
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def draw_stage(rng, form, amax):
    # shift amounts a,b in [1..amax] (0 excluded: (x>>0)&(x<<b) is the
    # track-5 self-masking form -- de-duped); rotation mask c in [1..63]
    # (c=0 would cancel the x^= feedback: x^x^AND = AND, degenerate)
    a = int(rng.integers(1, amax + 1))
    b = int(rng.integers(1, amax + 1))
    c = int(rng.integers(1, 64))
    return (a, b, c)


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


# b33c schedule (from gen_t6_b33.py) for the positive control
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
    amax = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    n_try = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    seed = int(sys.argv[5], 0) if len(sys.argv) > 5 else 0xB35
    rng = np.random.default_rng(seed)
    keep = []
    for t in range(n_try):
        stages, seen = [], set()
        while len(stages) < nstages:
            s = draw_stage(rng, form, amax)
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
    print("=== %s-%d-amax%d: %d/%d KEEP (seed=%#x) ==="
          % (form, nstages, amax, len(keep), n_try, seed), flush=True)
    for wz, stages in sorted(keep):
        print("KEEP z=%.1f %s" % (wz, stages), flush=True)


if __name__ == "__main__":
    main()
