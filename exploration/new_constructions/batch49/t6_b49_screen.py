#!/usr/bin/env python3
"""Batch-49 PRE-PILOT + PILOT: bijective quadratic 4-bit S-box repeated
stage (track 6).

Trigger: batch-48 CLOSED 2026-10-11T12:44Z (1-XOR linear layer provably
singular for every rotation; linear layer at cost floor 2 XORs; dense
chi-stage line fully cost-closed). The S-box is the only remaining
per-stage lever. chi_4 is non-bijective (b42 proof, chi-specific); the
queued lead is a BJECTIVE QUADRATIC 4-bit S-box as a repeated stage --
never screened (de-dup: batches 19-48; see DESIGN.md).

Forms (x ^= k pre-whiten; S = cascade ^ rotl(k,13) final -- b33c/b45 frame):
  q4bS4: 4x [y=Q4(x); x = y ^ rotl(y,a) ^ rotl(y,b)]   (prize arm)
  q4bS3: 3x [y=Q4(x); x = y ^ rotl(y,a) ^ rotl(y,b)]   (wall probe)
Q4 = mined bijective quadratic 4-bit S-box on 16 contiguous 4-bit lanes
(bits 0..63, full coverage, no passthrough bits). S(0)!=0 (no-zero-corner
co-design). Linear layer = b45's 2-rotation tree VERBATIM (cheapest
nonsingular option per b48 proof; comparability frame: the ONLY delta
from chiS4 is the S-box).

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive control:
and1/b33c 6-stage must give z=3.3 (fail-loud, run `calibrate` first).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).
Fail-loud draw-loop cap 10000 (b45 lesson). Duplicate stage-tuples
re-drawn (b41).

Pre-registered pre-pilot rule: ~6 draws/arm. Any KEEP -> mechanism alive ->
synthesis spot-check on one schedule (cost thesis S-box+tree <4.83u/stage)
-> pilot. 0 keeps with min z in b48-class (>=1e4) or b47-class (>=1e3)
with killkey-0x0 dominance -> KILL LOUDLY, scoped, close pre-pilot, no
pilot. 0 keeps with min z < 100 (near-misses) -> not catastrophe -> pilot.

Escalation (pre-registered): any pilot KEEP -> bundle gen bit-exact
2000/2000 -> S0 via run_synth.py (bar strictly <19.3u MEASURED, XCHECK
clean) on a STRATIFIED keep sample (lesson a: triage z does not rank S0
within a form) -> S1 FAIL-FAST on the first cost-eligible keep (lesson b:
exact-DIFF triage is blind to the S1 marginal/inner-DIFF kill) ->
survivors staged battery S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b49_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: q4bS4 | q4bS3 | calibrate
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

# Q4_LUT: mined bijective quadratic 4-bit S-box (anneal_q4_fast.py,
# 12 starts x 25000 steps, seeds 0xB492..0xB49D, 2026-10-11).
# BEST: energy=9.0 = 64*coll + DU + LATbias/8 (coll=0, DU=8, LATbias=8
# in miner units; compdeg=[1,2] verified by Moebius over all 15 masks).
# DU=4 unreachable in the pure-quadratic family per 12-start anneal
# evidence (6x DU=8 / 6x DU=16); the anneal IS the optimizer over the
# family, so this is the family's empirical floor (not a proof).
Q4_LUT = np.array([
    3, 4, 15, 5, 0, 6, 1, 10, 14, 13, 2, 12, 9, 11, 8, 7
], dtype=np.uint64)

assert len(Q4_LUT) == 16, "Q4 LUT must have 16 entries"
assert len(set(Q4_LUT.tolist())) == 16, "Q4 must be bijective (b42 hard gate)"
assert int(Q4_LUT[0]) != 0, "Q4 must have no zero-corner (S(0)!=0)"


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def q4(x):
    y = np.uint64(0)
    for j in range(16):
        lane = ((x >> np.uint64(4 * j)) & np.uint64(0xF)).astype(np.uint64)
        y |= Q4_LUT[lane] << np.uint64(4 * j)
    return y & M64


def apply_stage(x, st):
    tag, a, b = st
    assert tag == "Q4", tag
    y = q4(x)
    return (y ^ rotl(y, a) ^ rotl(y, b)) & M64


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


def eval_calib():
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


STAGE_TAG = {"q4bS4": "Q4", "q4bS3": "Q4"}
N_STAGES = {"q4bS4": 4, "q4bS3": 3}


def draw_stage(rng):
    # b45 verbatim: a,b in 1..63, a!=b. (No mod-4 cut: comparability frame;
    # the ONLY delta from chiS4 is the S-box. See DESIGN.md cut note.)
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        if a != b:
            return ("Q4", a, b)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz = eval_calib()
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (wz, "PASS" if abs(wz - 3.3) < 0.05 else "FAIL"), flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    assert form in STAGE_TAG, form
    n_stages = N_STAGES[form]
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB491
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
        assert all(s[1] != s[2] for s in stages), "degenerate draw"
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
