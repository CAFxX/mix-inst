#!/usr/bin/env python3
"""Batch-43 PILOT: complemented-gate 5-stage rotation cascades (track 6).
Trigger: batch-42 COMPLETED 2026-10-11T08:15:28Z, all arms 0 KEEP
(odd-chi-final-repair hypothesis TERMINALLY KILLED, scoped).

De-dup (grep-verified 2026-10-11, DESIGN.md):
- nandM/norM @ 6st: batch-41 (cost-closed 21.5/21.9u, scoped kill). @ 5st:
  NEVER triaged (b41 logs show 6st pilots only).
- ornM (any stage count): NEVER triaged -- zero hits for `ornM`,
  `(ra | ~rb)`, `(ra|~rb)` across new_constructions/batch*/t6_*.py,
  fused/gen_fused*.py, hybrid/, directed_design/, adder_lat/.
- Dual-mask 5st: fused fz15_c (22.6u S1+S2 PASS, cost-doomed); fz18
  balanced-tree hypothesis FALSIFIED (synthesizer already optimal, 22.5u).
- andnM-5: batch-39 pilot 0/40 (dead). 4st: structurally dead three ways
  (fz16_a catastrophic S1 FLAG; xc4a S1-killed; dual4a S1-killed).

Co-design rationale:
- The 5-stage wall is about per-stage avalanche strength on the sparse
  corner, not stage count. Sparse-corner single-bit-input flip count:
  AND 0 < ANDN 1 < OR 2 << NOR ~62 < NAND ~63, ORN ~63.
- andnM-5 died 0/40 (batch-39) with the 1-flip gate; track-3's 5-stage
  DIFF-wall theorem (0/500 hetero AND-masking pass); the only 5-stage
  single-mask family to pass S1+S2 is fz15_c's DUAL-mask (22.6u,
  cost-doomed).
- Batch-41 proved complemented-output gates have the best triage keep
  rates of any sparse form (nandM 29/40, norM 22/40, best z 2.15/2.76)
  via the 0->ALLONES->0 2-cycle (endogenous fixed-point breaking), but
  +0.3u/stage output-complement cost killed them at 6 stages (21.5/21.9u).
  This batch keeps the violent-avalanche quality mechanism and fixes
  cost by stage count: 5 stages x ~3.4-3.6u. ornM is the untested
  violent gate that may dodge the output-complement cost (complement on
  the input, like ANDN).

Forms (x ^= k pre-whiten; S = cascade ^ rotl(k,13) final, same as
b33c/b41):
  nandM5: x ^= ~(ra & rb) ^ rc   (5 stages)
  norM5:  x ^= ~(ra | rb) ^ rc   (5 stages)
  ornM5:  x ^= (ra | ~rb) ^ rc   (5 stages)

Cuts (defensible reason at each cut site; see DESIGN.md):
- and1-5 / ormM-5: DEPRIORITIZED, not killed -- andnM-5 (strictly
  stronger sparse-corner gate: ANDN 1-flip beats AND 0-flip and OR 2-flip
  on the key-0 corner) died 0/40 with z in the hundreds-thousands.
  Prediction: both die. Re-test trigger: if any arm here clears triage,
  the violent-avalanche hypothesis is confirmed and ormM-5 stays
  deprioritized; if all die, the 5-stage single-mask wall is confirmed
  and this cut is revisited only with a new diffusion mechanism.
- Dual-mask 5st: CUT (covered: fz15_c 22.6u, fz18 falsified).
- Keyed AND inputs: CUT on cost (4th logic level, ~+1.1u/stage).
- Complement-inside-mask: CUT as vacuous (constant, synthesis-absorbed,
  DIFF-invariant).
- 5 stages ONLY: 6st cost-doomed for nandM/norM (measured); 4st
  structurally dead.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive control:
and1/b33c 6-stage must give z=3.3 (fail-loud, run `calibrate` first).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).

Pre-registered kill rule: 0/40 keeps on an arm with margins orders of
magnitude above bar -> arm closed, mechanism refuted for that gate
(scoped). All three arms dead -> the violent-avalanche-5st hypothesis
is FALSIFIED; next axis per the widen directive (never stop silently).

Escalation (pre-registered): any KEEP -> bundle gen bit-exact 2000/2000
-> S0 via run_synth.py (bar strictly <19.8u MEASURED, XCHECK clean) on
a STRATIFIED sample of keeps (triage z does not rank S0 within a form --
wave-38/ormM lesson; do not S0 only top-z) -> S1 FAIL-FAST on the first
cost-eligible keep (exact-DIFF triage is blind to the marginal/inner-DIFF
kills) -> survivors staged battery S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b43_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: nandM5 | norM5 | ornM5 | and1 (calibration only)
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


def apply_stage(form, x, a, b, c):
    ra, rb, rc = rotl(x, a), rotl(x, b), rotl(x, c)
    if form == "nandM5":
        return (x ^ (~(ra & rb) & M64) ^ rc) & M64
    if form == "norM5":
        return (x ^ (~(ra | rb) & M64) ^ rc) & M64
    if form == "ornM5":
        return (x ^ ((ra | (~rb & M64))) ^ rc) & M64
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
        for a, b, c in stages:
            x = apply_stage(form, x, a, b, c)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


# b33c schedule for the positive control (and1, 6 stages)
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def eval_calib():
    return eval_sched("and1", B33C_SCHED)[0]


def draw_stage(rng):
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        if a != b:
            break
    return (a, b, int(rng.integers(1, 64)))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz = eval_calib()
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f (expect 3.3)" % wz,
              flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    assert form in ("nandM5", "norM5", "ornM5"), form
    nstages = 5
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB431
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
        assert all(s[0] != s[1] for s in stages), "degenerate a==b draw"
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
