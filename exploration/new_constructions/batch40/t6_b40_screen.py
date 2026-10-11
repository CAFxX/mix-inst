#!/usr/bin/env python3
"""Batch-40 PILOT: exact-DIFF triage for SHIFT-ANDN + MASKED-OR cascades (track 6).

Co-design rationale (incarnation VIII):
- Batch-39 proved two independent mechanisms: (1) ANDN breaks sparse fixed
  points endogenously (unmasked arms dead anyway -- the mask is still
  load-bearing; andnM6 62.5% KEEP, best z=2.4 < b33c 3.3); (2) batch-35 proved
  logical shifts avoid the rotation-resonance DIFF failures (shift-AND
  DIFF-clean and schedule-insensitive at 10st). Batch-40 COMBINES both
  validated mechanisms in one 3-term stage -- not a blind tweak, a co-design:
    shandnM: x ^= ((x>>a) & ~(x<<b)) ^ rotl(x,c)
      sparse corner: ~(x<<b) is 1 almost everywhere -> ANDN fires as (x>>a);
      e_p -> e_p ^ e_{p-a} ^ e_{p-c} (fixed point broken endogenously);
      shifts kill the rotation-resonance alignments that b33c-style forms
      depend on schedule search to avoid.
    ormM: x ^= (ra|rb) ^ rc   -- masked rotation-OR, the OR analog of andnM.
      b37 killed SHIFT-OR unmasked; b39 killed ROTATION-OR unmasked (0/40);
      MASKED rotation-OR was never triaged in any batch (grep-verified).
      OR fires 3/4 vs ANDN's ~1/4 -- different differential profile, same
      3-term gate shape (~4.0u/stage est).
- De-dup (grep-verified 2026-10-11): no batch 28-39 screened shift-ANDN or
  masked-OR. b34's AOI21 (~((ra&rb)|rc)^rd) is a different gate (AND inside
  OR, complemented). b35 = shift+plain-AND. b39 = rotation+ANDN.
- Cost: 3-term shape, ~4.0u/stage -> 6st ~= 19.8u-class; 5st ~= 16.5u
  challenger territory IF the DIFF wall clears (andnM5 pilot in flight is the
  rotation-ANDN data point on this).

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs. KEEP bar max|z|<10. Positive control: and1/b33c
must give z=3.3 (fail-loud). KEEP schedules dumped to JSONL for S0 harvest.

Usage: t6_b40_screen.py <form> <nstages> <n_try> <seed> [keep_jsonl]
  form: shandnM | ormM | and1 (calibration only)
"""
import json
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
    if form == "shandnM":
        a, b, c = rots
        return (x ^ ((x >> np.uint64(a)) & ~(x << np.uint64(b))) ^ rotl(x, c)) & M64
    if form == "ormM":
        a, b, c = rots
        return (x ^ (rotl(x, a) | rotl(x, b)) ^ rotl(x, c)) & M64
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
    return (a, b, int(rng.integers(1, 64)))


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
    seed = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0xB40
    keep_path = sys.argv[5] if len(sys.argv) > 5 else None
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
        # fail-loud: draws must never contain a==b
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
    if keep_path and keep:
        with open(keep_path, "w") as f:
            for wz, stages in sorted(keep, key=lambda k: k[0]):
                f.write(json.dumps({"z": wz, "stages": [list(s) for s in stages],
                                    "form": form, "seed": seed}) + "\n")
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
