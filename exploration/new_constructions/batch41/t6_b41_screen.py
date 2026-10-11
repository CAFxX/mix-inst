#!/usr/bin/env python3
"""Batch-41 PILOT: exact-DIFF triage for COMPLEMENTED-OUTPUT masked cascades (track 6).

Co-design rationale (incarnation XI, from the wave-37 consolidated finding +
the track-6 closure state):
- Track 6 closed every sparse 3-term form whose nonlinear term is a plain or
  inside-complemented AND/OR: and1 (frontier b33c 19.8u), andnM (S0 21.8u),
  ormM (S0 spread 20.8/21.3/21.9u), shandnM (0/40), nested-AND (0/200),
  no-mask shifts (structural), AND3/MAJ3/AOI21 (b34 dense kills). Wave-37's
  durable finding: dense forms win DIFF and lose synthesis superlinearly --
  the SPARSE 3-term stage is the synthesis sweet spot, so the next axis must
  stay sparse and find a QUALITY edge inside the 3-term shape.
- The one complement placement never triaged in a sparse stage is the
  OUTPUT of the nonlinear gate (de-dup grep-verified 2026-10-11: "nand"
  occurs in the tree only as a CMOS cost comment in b39; the only
  complemented-output gate ever screened is b34's AOI21
  ~((ra&rb)|rc)^rd -- mask INSIDE the complement, 4 rotations, dense
  complex gate, different cost class):
    nandM: x ^= ~(ra & rb) ^ rc     (NAND2 term + rotation mask)
    norM:  x ^= ~(ra | rb) ^ rc     (NOR2 term + rotation mask)
- Mechanism (firing-geometry inversion): the plain-AND term is 0 on 3/4 of
  random bits and ~identically 0 on the sparse zero corner (key 0,
  sequential inputs) -- the corner where DIFF kills concentrate in nearly
  every killed arm (killkey 0x0 dominant). There the frontier stage
  degenerates to its linear mask and only searched schedules survive.
  Complemented-output gates invert the geometry: on sparse x the NAND term
  is ~ALLONES (0 only where BOTH rotations have a bit) and the NOR term is
  ~ALLONES minus the union of the two sparse supports; the stage maps
  0 -> ALLONES -> 0 (a 2-cycle, no sparse fixed point) and a sparse input
  becomes dense in ONE stage. This is the endogenous fixed-point breaking
  that andnM validated (62.5% KEEP, best z=2.4) but via a SYMMETRIC output
  complement instead of andnM's asymmetric single-input complement --
  different truth tables: ANDN fires on {10}, NAND on {00,01,10}, NOR on
  {00}; NAND's firing set is the complement of AND's, NOR's of OR's, and a
  per-stage ^ALLONES does NOT commute through later stages' gates (the
  NAND cascade is complement-conjugate to a DENSE form, not to ormM), so
  neither arm is a relabeling of a closed form.
- Cost: NAND2/NOR2 are the primitive CMOS gates (AND2 = NAND2+INV,
  OR2 = NOR2+INV), so the complemented stage should synthesize at or below
  the frontier's AND stage (~4.0u/stage measured for and1/andnM DUTs) ->
  6st in the 19.8u class; measured S0 decides on any KEEP.
- CRITICAL draw constraint: a==b collapses BOTH arms to the affine form
  x ^ ~ra ^ rc ( ~(ra&ra) = ~(ra|ra) = ~ra ) -- excluded, fail-loud assert.
- LIN proxy: not applicable to pure rotation cascades (dependency
  saturates by construction; the S1 battery's LIN family is the real gate
  on escalation, per the b39/b40 precedent which ran DIFF-only triage).
- Pilot scope: 40 draws/arm, 6 stages. 0/40 with margins orders of
  magnitude above bar + mechanism confirmed -> close scoped, open next
  axis. Any KEEP -> bundle gen (bit-exact) -> S0 via run_synth.py (bar
  strictly <19.8u) -> staged battery S1->S2->S3->S4->Q1 (b33 playbook).

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs. KEEP bar max|z|<10. Positive control: and1/b33c
must give z=3.3 (fail-loud, run `calibrate` first). KEEP schedules are
appended to the JSONL IMMEDIATELY per-try (b39 lesson: a dead run must
not lose its keeps).

Usage: t6_b41_screen.py <form> <nstages> <n_try> <seed> [keep_jsonl]
  form: nandM | norM | and1 (calibration only)
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
    if form == "nandM":
        a, b, c = rots
        return (x ^ (~(rotl(x, a) & rotl(x, b)) & M64) ^ rotl(x, c)) & M64
    if form == "norM":
        a, b, c = rots
        return (x ^ (~(rotl(x, a) | rotl(x, b)) & M64) ^ rotl(x, c)) & M64
    if form == "and1":
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def draw_stage(rng, form):
    # a,b in [1..63], a!=b (a==b collapses nandM/norM to affine x ^ ~ra ^ rc)
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
    seed = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0xB41
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
        # fail-loud: draws must never contain a==b (affine collapse)
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
