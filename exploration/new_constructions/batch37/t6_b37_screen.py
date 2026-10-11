#!/usr/bin/env python3
"""Batch-37 PILOT: exact-DIFF triage for NO-MASK shift cascades (track 6).

Co-design rationale (incarnation VII):
- Batch-35 masked shift-AND `x ^= ((x>>a)&(x<<b)) ^ rotl(x,c)` is DIFF-clean
  at 10 stages but ~4.0u/stage (UNVERIFIED claim -- re-measuring in parallel),
  i.e. ~40u, cost-dominated. The mask ^rotl(x,c) costs ~1u/stage.
- The NO-MASK forms drop the linear diffusion engine entirely:
    shand_nm: x ^= (x>>a)&(x<<b)      (~3.0u/stage claimed, unverified)
    shor_nm:  x ^= (x>>a)|(x<<b)      (untriaged; OR fires 3/4 vs AND 1/4)
  6 stages x 3.0u = 18u < 19.8u frontier -- cost-eligible IF quality clears.
- Mechanism prediction (to be falsified by this pilot): batch-35 arm-C died
  STRUCTURALLY at 6 stages because differences cannot circulate out of the
  key-0 zero corner with only 6 rounds of the shift+rotation-mask diffusion
  engine. The no-mask forms REMOVE the rotation-mask engine, leaving only
  local AND/OR spread (+x^= feedback) -- strictly less diffusion. The
  zero-corner argument applies A FORTIORI: for sparse x (key 0x0, sequential
  inputs), (x_{j+a} & x_{j-b}) almost never fires, so shand_nm ~= identity on
  the sparse corner -> catastrophic DIFF z. shor_nm is the interesting
  counter-bet: (x_{j+a} | x_{j-b}) fires on a SINGLE set bit, and sequential
  inputs keep low bits dense, so the OR form may escape the corner that kills
  the AND form. This pilot tests both predictions with bounded compute.
- Pilot scope: 40 draws/arm (not 200). If 0/40 with huge z -> mechanism
  confirmed, lead closed cheaply. Any KEEP -> escalate to full 200-draw
  screen + S0 + staged battery.

Method = validated batch-33/34/35 triage: EXACT S1 DIFF via
lin_diff.diff_cell_logps, 10 keys, sequential inputs. KEEP bar max|z|<10.
Positive control: and1 form + b33c schedule must give z=3.3 (fail-loud).

Usage: t6_b37_screen.py <form> <nstages> <amax> <n_try> <seed>
  form: shand_nm | shor_nm | and1 (calibration only)
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
    a, b = rots[0], rots[1]
    if form == "shand_nm":
        return (x ^ ((x >> np.uint64(a)) & (x << np.uint64(b)))) & M64
    if form == "shor_nm":
        return (x ^ ((x >> np.uint64(a)) | (x << np.uint64(b)))) & M64
    if form == "and1":
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def draw_stage(rng, form, amax):
    # shift amounts a,b in [1..amax]; 0 excluded (degenerate: (x>>0)&(x<<b)
    # collapses toward the track-5 self-masking form)
    a = int(rng.integers(1, amax + 1))
    b = int(rng.integers(1, amax + 1))
    return (a, b)


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
    n_try = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    seed = int(sys.argv[5], 0) if len(sys.argv) > 5 else 0xB37
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
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
        if wz >= 10:
            kills += 1
        print("try %3d maxworst|z|=%8.1f killkey=%#x %s" % (t, wz, key, flag),
              flush=True)
        if wz < 10:
            keep.append((wz, stages))
    print("=== %s-%d-amax%d: %d/%d KEEP (seed=%#x) ==="
          % (form, nstages, amax, len(keep), n_try, seed), flush=True)
    # fail-loud non-vacuous gate: a screen that kills nothing is untrusted
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
