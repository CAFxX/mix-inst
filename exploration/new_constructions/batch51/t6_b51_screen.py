#!/usr/bin/env python3
"""Batch-51 PRE-PILOT + PILOT: 4-stage MUX-gate masked cascade (track 6).

Trigger: batch-50 CLOSED 2026-10-11T17:02Z -- QLOW quality-confirmed
(2/40) but S0 cost-closed (24.6/25.7u). The dense-S-box line is
cost-closed twice. This batch attacks the cost thesis directly: MUX is
the cheapest no-zero-corner gate (track-5 MU5: 3.86u/stage, frontier
19.3u). Axis audit (DESIGN.md): fz24_g/h DEAD (track-8 kills +
dead-bit proof); cubic mining deferred (weak cost thesis); MUX-4st
never screened, strongest cost thesis (4x3.86=15.4u).

Forms (x ^= k pre-whiten; final x ^= rotl(k,13) -- the b33c/b45/MU5
frame; the ONLY delta from MU5-324 is the stage count):
  muxS4: 4x [x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)] (prize)
  muxS3: 3x [same] (wall probe)
mux(s,a,b) = (s&a)|(~s&b).

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive
controls (fail-loud, run `calibrate` first):
  (i)  and1/b33c 6-stage must give z=3.3 (harness sanity);
  (ii) MU5-324 schedule [(62,50,55,2),(48,58,23,30),(44,45,7,40),
       (49,26,32,35),(46,51,43,44)] through the MUX stage must KEEP
       (z<10; track-5 measured 2.34).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).
Fail-loud draw-loop cap 10000 (b45 lesson). Duplicate stage-tuples
re-drawn (b41). s,a,b pairwise distinct asserted at draw (degeneracy
proof in DESIGN.md cut #10).

Pre-registered pre-pilot rule: ~6 draws/arm. Any KEEP -> mechanism
alive -> S0 spot-check on one schedule -> pilot. 0 keeps with min z in
b48-class (>=1e4) or b47-class (>=1e3) with killkey-0x0 dominance ->
KILL LOUDLY, scoped, no pilot. 0 keeps with min z < 100 (near-misses)
-> pilot.

Escalation (pre-registered): any pilot KEEP -> bundle gen bit-exact
2000/2000 -> S0 via run_synth.py (bar strictly <19.3u MEASURED, XCHECK
clean) on a STRATIFIED keep sample (lesson a) -> S1 FAIL-FAST on the
first cost-eligible keep (lesson b) -> survivors staged battery
S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b51_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: muxS4 | muxS3 | calibrate
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


def mux(s, a, b):
    return ((s & a) | ((~s) & b)) & M64


def apply_stage(x, st):
    tag, s, a, b, d = st
    assert tag == "MUX", tag
    assert len({s, a, b}) == 3, "degenerate mux draw: s,a,b must be distinct"
    return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b)) ^ rotl(x, d)) & M64


def eval_sched(stages):
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_key = None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


# b33c schedule for the positive control (and1, 6 stages) -- verbatim
# from t6_b47_screen.py so the z=3.3 reproduction is exact.
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def _and1(x, a, b, c):
    return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64


def eval_calib_and1():
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for (a, b, c) in B33C_SCHED:
            x = _and1(x, a, b, c)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        worst = max(worst, wz)
    return worst


# MU5-324 schedule (track-5 batch-28 frontier; triage-exact DIFF z=2.34)
# -- (s,a,b,d) per stage, through the MUX stage form above.
MU5_324_SCHED = [("MUX", 62, 50, 55, 2), ("MUX", 48, 58, 23, 30),
                 ("MUX", 44, 45, 7, 40), ("MUX", 49, 26, 32, 35),
                 ("MUX", 46, 51, 43, 44)]


STAGE_TAG = {"muxS4": "MUX", "muxS3": "MUX"}
N_STAGES = {"muxS4": 4, "muxS3": 3}


def draw_stage(rng):
    # s,a,b in 0..63 pairwise distinct (degeneracy proof: s==a -> s|b,
    # s==b -> s&a, a==b -> a); d in 0..63 free (linear term, no
    # degeneracy -- DESIGN.md cut #10).
    while True:
        s = int(rng.integers(0, 64))
        a = int(rng.integers(0, 64))
        b = int(rng.integers(0, 64))
        if len({s, a, b}) == 3:
            d = int(rng.integers(0, 64))
            return ("MUX", s, a, b, d)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        w1 = eval_calib_and1()
        ok1 = abs(w1 - 3.3) < 0.05
        print("CALIB-1 and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (w1, "PASS" if ok1 else "FAIL"), flush=True)
        w2, _ = eval_sched(MU5_324_SCHED)
        ok2 = w2 < 10.0
        print("CALIB-2 mux/MU5-324: maxworst|z|=%.2f (expect KEEP z<10; "
              "track-5 measured 2.34) %s" % (w2, "PASS" if ok2 else "FAIL"),
              flush=True)
        sys.exit(0 if (ok1 and ok2) else 1)
    form = sys.argv[1]
    assert form in STAGE_TAG, form
    n_stages = N_STAGES[form]
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB511
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    minz = float("inf")
    for t in range(n_try):
        stages, seen = [], set()
        draws = 0
        while len(stages) < n_stages:
            draws += 1
            if draws > 10000:
                print("DRAW-LOOP-FAIL: try %d" % t, flush=True)
                sys.exit(3)
            st = draw_stage(rng)
            if st in seen:
                continue
            seen.add(st)
            stages.append(st)
        assert all(len({s[1], s[2], s[3]}) == 3 for s in stages), \
            "degenerate draw"
        wz, key = eval_sched(stages)
        minz = min(minz, wz)
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
    print("=== %s: %d/%d KEEP minz=%.1f (seed=%#x) ===" %
          (form, len(keep), n_try, minz, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
