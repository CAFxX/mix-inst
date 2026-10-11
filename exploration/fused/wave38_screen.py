#!/usr/bin/env python3
"""Wave-38 (track 8): SYNTHESIS-AWARE sparse schedule search -- a COST-FIRST
axis on the frontier sparse form. Not a new gate; a new selection criterion.

Why this axis (co-design, 2026-10-11, incarnation 12):
- Wave-37's binding lesson: dense XOR trees map SUPERLINEARLY in synthesis;
  the sparse 3-term stage `x ^= (ra&rb) ^ rc` is the synthesis sweet spot.
  Quality-rich/cost-poor axes are dead ends. So wave-38 stays inside the
  exact frontier stage form (6 stages, pre-whiten x^K, post ^rotl(K,13))
  and attacks COST, the axis wave-37 showed is decisive.
- Every prior screen of this form selected by DIFF quality and S0'd only
  the top-z few: b33 screened 20 -> S0'd b33a/b/c (19.8/20.1u); track-3's
  as6_200 pool S0'd quality-DEAD schedules at 19.2-19.8u (cost spread is
  real: >=0.6u within-form) but its winners die at exact DIFF (as6_200_106
  seq z=71.4, wave-14 canary). Track-6's ormM settlement PROVED triage z
  does not rank S0 within a form (20.8/21.3/21.9u, best-z was slowest).
  => The S0-cost distribution AMONG exact-DIFF KEEPS of the frontier form
     is unmapped. Nobody has ever S0'd a median-z or structurally-chosen
     keep. That is the hole wave-38 fills.
- Method: (1) exact-DIFF screen (b41-validated triage: lin_diff
  diff_cell_logps, 10 keys, sequential inputs, N=2^18, KEEP bar max|z|<10,
  positive control b33c z=3.3 fail-loud) over 120 random 6-stage schedules,
  dumping EVERY keep to JSONL per-try; (2) per-keep synthesis-cost
  FEATURES recorded at draw time (distinct rotation count, cross-stage
  rotation alignment, repeated AND-pair count) -- hypotheses for ABC
  sharing, to be TESTED against measured S0, not assumed; (3) stratified
  S0 sample (next step, separate runner): min-z / median-z / max-z /
  max-align / min-align / max-distinct / min-distinct / seeded-random
  keeps via run_synth.py, bar strictly <19.8u MEASURED. Any cost-eligible
  survivor -> b33 playbook S1->S2->S3->S4->Q1.
- De-dup (grep-verified 2026-10-11): NOT track-6 batch-41 (nandM/norM
  complemented-output gates, live at S0 stage -- different form); NOT
  track-5 batch-28 MUX cascade (live, 324 at battery stage -- different
  form); NOT track-3 wave-14 W1/W3 (word-level GF/adder forms); NOT
  fused waves 19/20 (rotation REUSE inside stages of a 5-stage hetero
  form -- different construction, and reuse here is a measured feature,
  not a design constraint); NOT b34 AOI21 (0/200 at 5st, dense complex
  gate); NOT b31 P-box/bitrev diffusion (S1-killed). The 2-input-gate
  complement space in a sparse stage is fully enumerated/taken:
  AND (frontier), ANDN (closed 21.8u), ~(ra|rb)=~ra&~rb (norM, live),
  ~(ra&rb) (nandM, live), OR (closed 20.8-21.9u). No new sparse gate
  remains untriaged, which is WHY the lever is cost-side.
- Search-space cuts, each with its reason recorded: (a) 6 stages only --
  5-stage wall for this form is multiply-proven (b22 0/200, b34 arms,
  andnM5 0/40; a 5st arm would need a mechanism, none proposed);
  (b) a==b draws excluded -- stage collapses to affine x^ra^rc (proof:
  ra&ra=ra), fail-loud assert; (c) duplicate stage-tuples within a
  schedule re-drawn (b41 precedent; a repeated stage is a distinct
  design point already representable and wastes a draw).
- LIN proxy N/A (b39/b40 precedent for pure rotation cascades; S1's LIN
  family gates any escalation).

Usage: wave38_screen.py calibrate | screen <n_try> <seed> [keep_jsonl]
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
assert len(KEYS10) == 10 and N == (1 << 18), "fail-loud: triage config drift"

B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def apply_stage(x, rots):
    a, b, c = rots
    return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64


def eval_sched(stages):
    V = np.arange(N, dtype=np.uint64)
    worst, worst_key = 0.0, None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for rots in stages:
            x = apply_stage(x, rots)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


def cost_features(stages):
    """Schedule-structure features hypothesised to move synthesis cost.
    Recorded for every KEEP; correlation with measured S0 is the test."""
    rots = [r for s in stages for r in s]
    distinct = len(set(rots))
    # cross-stage alignment: slot pairs in DIFFERENT stages with equal rot
    align = 0
    for i in range(len(stages)):
        for j in range(i + 1, len(stages)):
            align += sum(1 for a in stages[i] for b in stages[j] if a == b)
    and_pairs = [(s[0], s[1]) for s in stages]
    pair_reps = len(and_pairs) - len(set(and_pairs))
    return {"distinct_rots": distinct, "cross_stage_align": align,
            "and_pair_repeats": pair_reps}


def main():
    if sys.argv[1] == "calibrate":
        wz, key = eval_sched(B33C_SCHED)
        print("CALIBRATION and1/b33c: maxworst|z|=%.2f killkey=%#x "
              "(expect 3.3)" % (wz, key), flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    assert sys.argv[1] == "screen"
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x3838
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep, kills = [], 0
    for t in range(n_try):
        stages, seen = [], set()
        while len(stages) < 6:
            while True:
                a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
                if a != b:
                    break
            s = (a, b, int(rng.integers(1, 64)))
            if s in seen:
                continue
            seen.add(s); stages.append(s)
        assert all(s[0] != s[1] for s in stages), "degenerate a==b draw"
        wz, key = eval_sched(stages)
        flag = "KEEP" if wz < 10 else "kill"
        if wz >= 10:
            kills += 1
        print("try %3d maxworst|z|=%8.1f killkey=%#x %s"
              % (t, wz, key, flag), flush=True)
        if wz < 10:
            rec = {"z": wz, "stages": [list(s) for s in stages],
                   "seed": seed, "try": t}
            rec.update(cost_features(stages))
            keep.append(rec)
            if keep_path:
                with open(keep_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
    print("=== wave38 and1-6: %d/%d KEEP (seed=%#x) ==="
          % (len(keep), n_try, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
