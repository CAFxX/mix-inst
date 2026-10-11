#!/usr/bin/env python3
"""Batch-39 PILOT: exact-DIFF triage for 2-TERM ANDN / OR cascades (track 6).

Co-design rationale (incarnation VII):
- Every 3-term AND-cascade variant is now closed (quality-dead or
  cost-doomed); track-5's conclusion: the next challenger must come from
  OUTSIDE the (x^AND^lin-terms) shape. This axis drops the linear mask
  term entirely -- 2-term stages -- and restores fixed-point breaking
  ENDOGENOUSLY via a complemented AND input:
    andn:  x ^= (ra & ~rb)          -- ANDN fires on sparse input when a!=b
           (the ~rb operand is 1 almost everywhere for sparse x), so the
           sparse fixed point e_p -> e_p ^ e_{p-a} is broken WITHOUT a lin
           term. Complement-inside is free-ish in CMOS (ANDN2/NAND+INV);
           output-complement would be differentially vacuous, this is not.
    andnM: x ^= (ra & ~rb) ^ rc     -- masked control (3-term, ~b33c cost)
    orr:   x ^= (ra | rb)           -- unmasked rotation-OR; OR fires on a
           single set bit, also endogenous fixed-point breaking. (b37 killed
           SHIFT-OR; rotation-OR unmasked was never triaged; the t5
           complement-conjugacy analysis was uniform-input-only.)
- Cost hypothesis: 2 logic levels (ANDN2+XOR2) vs b33c's 3 -> ~2.5-3.0u/stage
  (measured, not estimated, in the pilot driver). 6-7 stages then project
  15-21u -- challenger territory IF the DIFF wall clears.
- CRITICAL draw constraint: a==b makes ANDN identically zero (ra&~ra=0) and
  makes OR degenerate (ra|ra=ra, pure linear) -- excluded from draws.
- Pilot scope: 40 draws/arm. 0/40 catastrophic -> close. Any KEEP -> full
  200-draw screen + S0 + staged battery.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs. KEEP bar max|z|<10. Positive control: and1/b33c
must give z=3.3 (fail-loud).

Usage: t6_b39_screen.py <form> <nstages> <n_try> <seed>
  form: andn | andnM | orr | and1 (calibration only)
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
    if form == "andn":
        a, b = rots
        return (x ^ (rotl(x, a) & ~rotl(x, b))) & M64
    if form == "andnM":
        a, b, c = rots
        return (x ^ (rotl(x, a) & ~rotl(x, b)) ^ rotl(x, c)) & M64
    if form == "orr":
        a, b = rots
        return (x ^ (rotl(x, a) | rotl(x, b))) & M64
    if form == "and1":
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def draw_stage(rng, form):
    # a,b in [1..63], a!=b (a==b degenerates ANDN to 0 / OR to linear)
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        if a != b:
            break
    if form == "andnM":
        return (a, b, int(rng.integers(1, 64)))
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
    n_try = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    seed = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0xB39
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    for t in range(n_try):
        stages, seen = [], set()
        while len(stages) < nstages:
            s = draw_stage(rng, form)
            if s in seen:
                continue
            seen.add(s)
            stages.append(s)
        # fail-loud: andn/orr draws must never contain a==b
        assert all(s[0] != s[1] for s in stages), "degenerate a==b draw"
        wz, key = eval_sched(form, stages)
        flag = "KEEP" if wz < 10 else "kill"
        if wz >= 10:
            kills += 1
        print("try %3d maxworst|z|=%8.1f killkey=%#x %s" % (t, wz, key, flag),
              flush=True)
        if wz < 10:
            keep.append((wz, stages))
    print("=== %s-%d: %d/%d KEEP (seed=%#x) ==="
          % (form, nstages, len(keep), n_try, seed), flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
