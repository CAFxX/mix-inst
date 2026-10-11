#!/usr/bin/env python3
"""Batch-44 PILOT: dual-nonlinear-tap cascades (track 6).
Trigger: batch-43 COMPLETED 2026-10-11T09:48:05Z, all arms 0 KEEP
(complemented-output-5st axis TERMINALLY KILLED, scoped).

De-dup (grep-verified 2026-10-11, DESIGN.md):
- `x ^= (ra&rb) ^ (rc|rd)` (OR-mask, NO linear mask): NEVER triaged.
- adder-lat al_orand (`x ^= (ra&rb) ^ (rc|rd) ^ re`): different form
  (extra linear mask) + different key schedule (O83 bias) -- caution,
  not a kill.
- b36 dual-AND2 `x ^= (ra&rb)^(rc&rd)`: different secondary gate
  (sparse-firing); 0/200 kill motivates the OR choice.
- b5 andor / fz15_c dual-mask / sparse complement space: all different,
  see DESIGN.md.

Co-design rationale:
- The 5-stage wall is a nonlinear-tap-count deficit, not purely
  sequential depth: the two quality-proven 5st forms (MUX-5st = frontier
  19.3u; fz15_c dual-mask S1+S2 clean) both have >1 tap/stage.
- OR is the dense-firing secondary: on single-bit input e_p, (ra&rb)=0
  but (rc|rd) fires 2 bits -- every sparse input gets a nonlinear
  response where the AND term vanishes (b36's second AND shares the
  zero-corner pathology and died 0/200).
- Cost: AND2/OR2 in parallel (~1.5u) + 2-level XOR tree (~1.8u) = same
  gate depth as the frontier stage (~3.3u). Projected 5st ~= 16.5u.

Forms (x ^= k pre-whiten; S = cascade ^ rotl(k,13) final, same as
b33c/b41/b43):
  andorM5: x ^= (ra&rb) ^ (rc|rd)   (5 stages)
  andorM6: x ^= (ra&rb) ^ (rc|rd)   (6 stages)

Cuts (defensible reason at each cut site; see DESIGN.md):
- orandM-5: CUT from pilot (gate-order follow-up; re-test trigger = any
  andorM-5 KEEP).
- 4st: CUT (structurally dead three ways + b34 0/200).
- 7+st: CUT on measured cost (7x3.3u ~= 23u > 19.3u).
- Extra linear mask ^re: CUT on measured cost (fz15_c 4.5u/stage).
- LIN proxy: N/A (b39/b40/b41 precedent).

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive control:
and1/b33c 6-stage must give z=3.3 (fail-loud, run `calibrate` first).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).

Pre-registered kill rule: 0/40 keeps on an arm with min orders of
magnitude above bar -> arm closed, mechanism refuted for that form
(scoped). Both arms dead -> dual-nonlinear-tap hypothesis FALSIFIED;
next axis per the widen directive (never stop silently).

Escalation (pre-registered): any KEEP -> bundle gen bit-exact 2000/2000
-> S0 via run_synth.py (bar strictly <19.3u MEASURED, XCHECK clean) on
a STRATIFIED sample of keeps (triage z does not rank S0 within a form --
wave-38/ormM lesson; do not S0 only top-z) -> S1 FAIL-FAST on the first
cost-eligible keep (exact-DIFF triage is blind to the marginal/inner-DIFF
kills) -> survivors staged battery S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b44_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: andorM5 | andorM6 | and1 (calibration only)
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


def apply_stage(form, x, a, b, c, d):
    ra, rb, rc, rd = rotl(x, a), rotl(x, b), rotl(x, c), rotl(x, d)
    if form in ("andorM5", "andorM6"):
        return (x ^ (ra & rb) ^ (rc | rd)) & M64
    if form == "and1":
        return (x ^ (ra & rb) ^ rc) & M64
    raise ValueError(form)


def eval_sched(form, stages):
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_key = None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for s in stages:
            x = apply_stage(form, x, *s)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


# b33c schedule for the positive control (and1, 6 stages)
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def eval_calib():
    return eval_sched("and1", [(a, b, c, 1) for a, b, c in B33C_SCHED])[0]


def draw_stage(rng):
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        if a != b:
            break
    while True:
        c = int(rng.integers(1, 64))
        d = int(rng.integers(1, 64))
        if c != d:
            break
    return (a, b, c, d)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz = eval_calib()
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f (expect 3.3)" % wz,
              flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    assert form in ("andorM5", "andorM6"), form
    nstages = 5 if form == "andorM5" else 6
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB441
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    for t in range(n_try):
        stages, seen = [], set()
        while len(stages) < nstages:
            s = draw_stage(rng)
            if s in seen:
                continue
            seen.add(s)
            stages.append(s)
        assert all(s[0] != s[1] and s[2] != s[3] for s in stages), \
            "degenerate draw"
        wz, key = eval_sched(form, stages)
        flag = "KEEP" if wz < 10 else "kill"
        if wz >= 10:
            kills += 1
        print("try %3d maxworst|z|=%8.1f killkey=%#x %s" % (t, wz, key, flag),
              flush=True)
        if wz < 10:
            keep.append((wz, stages))
            if keep_path:
                with open(keep_path, "a") as f:
                    f.write(json.dumps({"z": wz,
                                        "stages": [list(s) for s in stages],
                                        "form": form, "seed": seed}) + "\n")
    print("=== %s-%d: %d/%d KEEP (seed=%#x) ==="
          % (form, nstages, len(keep), n_try, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
