#!/usr/bin/env python3
"""Batch-52 PRE-PILOT + PILOT: 5-stage 3-rotation MUX cascade, linear-term
ablation (track 6).

Trigger: batch-51 CLOSED 2026-10-11T17:40:48Z -- MUX-4st/MUX-3st both 0/6
(b47-class); mechanism (b) CONFIRMED. Frontier is MU5 (MUX-5st, 19.3u).
This batch attacks the frontier's own stage cost: drop the linear `d`
term -> one fewer XOR level per stage -> projects ~16-17u < 19.3u.

Forms (x ^= k pre-whiten; final x ^= rotl(k,13) -- the b33c/b45/MU5 frame;
the ONLY delta from MU5-324 is the dropped linear term):
  muxS5nl: 5x [x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b))] (prize, no d)
  muxS5d:  5x [x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)] (control)
mux(s,a,b) = (s&a)|(~s&b).

Mechanism question: is the linear d term load-bearing for MUX-5st
quality? First-principles asymmetry (DESIGN.md): on single-bit input
with s,a,b distinct, the MUX fires exactly 1 bit (b's position) with NO
linear term -- the no-zero-corner property survives the ablation, unlike
the AND form where dropping rc gives the identity. The triage decides.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive controls
(fail-loud, run `calibrate` first):
  (i)  and1/b33c 6-stage must give z=3.3 (harness sanity);
  (ii) MU5-324 schedule [(62,50,55,2),(48,58,23,30),(44,45,7,40),
       (49,26,32,35),(46,51,43,44)] through the FULL MUX stage (with d)
       must KEEP (z<10; b51 harness measured 3.24).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).
Fail-loud draw-loop cap 10000 (b45 lesson). Duplicate stage-tuples
re-drawn (b41). s,a,b pairwise distinct asserted at draw (degeneracy
proof in DESIGN.md cut #8).

Pre-registered pre-pilot rule: 6 draws/arm (seeds 0xB521 muxS5nl,
0xB522 muxS5d). >=1 KEEP on muxS5nl -> mechanism alive -> S0
spot-check -> pilot. 0 keeps on muxS5nl with min z >= 1e3 AND muxS5d
keeping >=1 -> KILL LOUDLY (d is load-bearing), scoped, no pilot.
0 keeps with min z < 100 (near-misses) -> pilot. 0 keeps on BOTH arms
-> no d-verdict; diagnose draws, do NOT close.

Escalation (pre-registered): any muxS5nl KEEP -> bundle gen bit-exact
2000/2000 -> S0 via run_synth.py (bar strictly <19.3u MEASURED, XCHECK
clean) on a STRATIFIED keep sample (lesson a) -> S1 FAIL-FAST on the
first cost-eligible keep (lesson b) -> survivors staged battery
S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b52_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: muxS5nl | muxS5d | calibrate
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
    tag = st[0]
    if tag == "MUXD":
        _, s, a, b, d = st
        assert len({s, a, b}) == 3, "degenerate mux draw"
        return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b)) ^ rotl(x, d)) & M64
    elif tag == "MUXNL":
        _, s, a, b = st
        assert len({s, a, b}) == 3, "degenerate mux draw"
        return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b))) & M64
    else:
        raise AssertionError(tag)


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


# MU5-324 schedule (track-5 batch-28 frontier) -- (s,a,b,d) per stage,
# through the FULL MUX stage (with d).
MU5_324_SCHED = [("MUXD", 62, 50, 55, 2), ("MUXD", 48, 58, 23, 30),
                 ("MUXD", 44, 45, 7, 40), ("MUXD", 49, 26, 32, 35),
                 ("MUXD", 46, 51, 43, 44)]


STAGE_TAG = {"muxS5nl": "MUXNL", "muxS5d": "MUXD"}
N_STAGES = {"muxS5nl": 5, "muxS5d": 5}


def draw_stage(rng, tag):
    # s,a,b in 0..63 pairwise distinct (degeneracy proof: s==a -> s|b,
    # s==b -> s&a, a==b -> a); d in 0..63 free for MUXD (linear term,
    # no degeneracy -- b51 cut #10).
    while True:
        s = int(rng.integers(0, 64))
        a = int(rng.integers(0, 64))
        b = int(rng.integers(0, 64))
        if len({s, a, b}) == 3:
            if tag == "MUXD":
                d = int(rng.integers(0, 64))
                return ("MUXD", s, a, b, d)
            return ("MUXNL", s, a, b)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        w1 = eval_calib_and1()
        ok1 = abs(w1 - 3.3) < 0.05
        print("CALIB-1 and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (w1, "PASS" if ok1 else "FAIL"), flush=True)
        w2, _ = eval_sched(MU5_324_SCHED)
        ok2 = w2 < 10.0
        print("CALIB-2 mux/MU5-324: maxworst|z|=%.2f (expect KEEP z<10; "
              "b51 harness measured 3.24) %s" % (w2, "PASS" if ok2 else "FAIL"),
              flush=True)
        sys.exit(0 if (ok1 and ok2) else 1)
    form = sys.argv[1]
    assert form in STAGE_TAG, form
    tag = STAGE_TAG[form]
    n_stages = N_STAGES[form]
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB521
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
            st = draw_stage(rng, tag)
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
