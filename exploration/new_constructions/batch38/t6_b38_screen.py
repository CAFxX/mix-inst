#!/usr/bin/env python3
"""Batch-38 PILOT: exact-DIFF triage for ASYMMETRIC NESTED shift-AND (track 6).

Co-design rationale (incarnation VII):
- Batch-37 closed the no-mask shift family: the rotation mask is the
  diffusion engine (load-bearing); without it the zero-corner kill is
  structural (shand_nm min z=287285, shor_nm min z=10322, both 0/40).
- Batch-36's SYMMETRIC nested-AND `x ^= ((x^rc)&(ra^rb))` (rotation operands,
  both XOR-mixed) died 0/200. But the XOR-inside-AND idea was never tested
  with (a) SHIFT operands (b35 lesson: shifts avoid rotation resonances) or
  (b) ASYMMETRIC nesting (one bare operand + one XOR-mixed operand).
- The asymmetric forms keep b33c's gate count (XOR2+AND2+XOR2, 3 XOR-terms --
  inside the cost-disease limit) while folding linear diffusion INSIDE the
  AND operand instead of as an additive mask:
    nestA: x ^= ((x>>a)^(x<<b)) & (x>>c)        (shifts only)
    nestB: x ^= (x>>a) & ((x<<b) ^ rotl(x,c))   (bare shift + mixed shift/rot)
    nestS: x ^= ((x>>a)^(x<<b)) & ((x>>c)^(x<<d)) (symmetric shift-nested;
           direct shift-analog of b36's killed form -- boundary test: if b36's
           kill was rotation-resonance-driven, this may survive)
  Per-bit e.g. nestA: y_j = x_j ^ ((x_{j+a} ^ x_{j-b}) & x_{j+c}).
- None of these collapse to the OR family ((P^Q)&R has no simplification;
  verified against the (P&Q)^P^Q = P|Q trap).
- Cost bar: 6 stages must project < 19.8u. Gate count = b33c's -> ~4.0u
  DUT-relative expected; per-stage DUT probes run first in the pilot driver.
- Pilot scope: 40 draws/arm. 0/40 catastrophic -> close. Any KEEP -> full
  200-draw screen + S0 + staged battery.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs. KEEP bar max|z|<10. Positive control: and1/b33c
must give z=3.3 (fail-loud).

Usage: t6_b38_screen.py <form> <nstages> <amax> <n_try> <seed>
  form: nestA | nestB | nestS | and1 (calibration only)
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
    if form == "nestA":
        a, b, c = rots
        return (x ^ (((x >> np.uint64(a)) ^ (x << np.uint64(b)))
                    & (x >> np.uint64(c)))) & M64
    if form == "nestB":
        a, b, c = rots
        return (x ^ ((x >> np.uint64(a))
                    & ((x << np.uint64(b)) ^ rotl(x, c)))) & M64
    if form == "nestS":
        a, b, c, d = rots
        return (x ^ (((x >> np.uint64(a)) ^ (x << np.uint64(b)))
                     & ((x >> np.uint64(c)) ^ (x << np.uint64(d))))) & M64
    if form == "and1":
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def draw_stage(rng, form, amax):
    if form == "nestA":
        return (int(rng.integers(1, amax + 1)), int(rng.integers(1, amax + 1)),
                int(rng.integers(1, amax + 1)))
    if form == "nestB":
        return (int(rng.integers(1, amax + 1)), int(rng.integers(1, amax + 1)),
                int(rng.integers(1, 64)))
    if form == "nestS":
        return (int(rng.integers(1, amax + 1)), int(rng.integers(1, amax + 1)),
                int(rng.integers(1, amax + 1)), int(rng.integers(1, amax + 1)))
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
    seed = int(sys.argv[5], 0) if len(sys.argv) > 5 else 0xB38
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
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
