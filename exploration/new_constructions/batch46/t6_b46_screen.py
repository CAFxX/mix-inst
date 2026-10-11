#!/usr/bin/env python3
"""Batch-46 PILOT: hetero chi+AND interleave (track 6).
Trigger: batch-45 CLOSED -- pure-chi cascade QUALITY-CONFIRMED (chiS5
40/40, median z=2.8; 5-stage wall breached for dense degree-2) but
COST-CLOSED (S0 22.9-23.2u vs <19.3u; 5.77u/stage measured). This is the
pre-registered cost-engineering follow-up: buy quality from chi stages,
buy cheap depth from AND stages.

De-dup (grep-verified 2026-10-11, DESIGN.md):
- b8 het5a: hetero with DIFFERENT ops (maj/andor/sparse-chi/majxor/
  xor3and, fused + per-stage rk); 25.2u dominated. Different functions.
- b45 pure-chi: parent axis; hetero is the pre-registered follow-up.
- No batch interleaved true-chi-S-box stages with AND-mask stages in a
  masked cascade.

Co-design rationale:
- Cost thesis (measured components): 2x5.77 + 2x3.3 ~= 18.1u < 19.3u --
  LIVE but tight (1.2u margin); measured S0 decides.
- Quality question: does the hetero mix preserve chi quality? Pure chi
  4st kept 25%; pure AND 4st is structurally dead. Unknown -- needs the
  pilot, not an assumption.

Forms (x ^= k pre-whiten; S = cascade ^ rotl(k,13) final):
  hetCA4a: chi, AND, chi, AND   (chi-led)
  hetCA4b: AND, chi, AND, chi   (AND-led)
  chi stage: y=chi3(x); x = y ^ rotl(y,a) ^ rotl(y,b)   [b45 verbatim]
  AND stage: x ^= (ra&rb) ^ rc                          [b33c verbatim]
chi3 = chi_3, 21 contiguous 3-bit lanes, bit 63 identity (b42).

Cuts (defensible reason at each cut site; see DESIGN.md):
- 5-stage hetero (3C+2A): CUT on measured cost (23.9u).
- 3C+1A: CUT on measured cost (20.6u).
- Block order C-C-A-A: CUT from pilot (order follow-up; re-test trigger
  = any hetCA KEEP).
- chi_5 lanes / per-stage rk / fused forms / LIN proxy: see DESIGN.md.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive control:
and1/b33c 6-stage must give z=3.3 (fail-loud, run `calibrate` first).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).
Fail-loud draw-loop cap (b45 lesson).

Pre-registered kill rule: 0/40 keeps on an arm with min orders of
magnitude above bar -> arm closed (scoped). Both arms dead -> hetero
hypothesis FALSIFIED; next axis per the widen directive.

Escalation (pre-registered): any KEEP -> bundle gen bit-exact 2000/2000
-> S0 via run_synth.py (bar strictly <19.3u MEASURED, XCHECK clean) on
a STRATIFIED sample of keeps -> S1 FAIL-FAST on the first cost-eligible
keep -> survivors staged battery S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b46_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: hetCA4a | hetCA4b | and1 (calibration only)
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


def _chi_scalar(v, n):
    y = 0
    for k in range(n):
        vk = (v >> k) & 1
        v1 = (v >> ((k + 1) % n)) & 1
        v2 = (v >> ((k + 2) % n)) & 1
        y |= ((vk ^ ((1 ^ v1) & v2)) << k)
    return y


# b42 lane geometry, verbatim: 21 contiguous 3-bit lanes, bit 63 identity.
CHI3_LUT = np.array([_chi_scalar(v, 3) for v in range(8)], dtype=np.uint64)
assert len(set(CHI3_LUT.tolist())) == 8, "chi_3 must be bijective"


def chi3(x):
    y = x & np.uint64(0x8000000000000000)  # bit 63 passthrough
    for j in range(21):
        lane = ((x >> np.uint64(3 * j)) & np.uint64(0x7)).astype(np.uint64)
        y |= CHI3_LUT[lane] << np.uint64(3 * j)
    return y & M64


# Stage schedule: list of ("C", a, b) chi stages and ("A", a, b, c) AND stages.
def apply_stage(x, st):
    if st[0] == "C":
        _, a, b = st
        y = chi3(x)
        return (y ^ rotl(y, a) ^ rotl(y, b)) & M64
    if st[0] == "A":
        _, a, b, c = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    if st[0] == "and1":
        _, a, b, c = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(st[0])


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
# from t6_b44_screen.py so the z=3.3 reproduction is exact.
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def eval_calib():
    return eval_sched([("and1", a, b, c) for a, b, c in B33C_SCHED])[0]


ORDER = {"hetCA4a": ("C", "A", "C", "A"),
         "hetCA4b": ("A", "C", "A", "C")}


def draw_stage(rng, typ):
    if typ == "C":
        while True:
            a = int(rng.integers(1, 64))
            b = int(rng.integers(1, 64))
            if a != b:
                return ("C", a, b)
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        c = int(rng.integers(1, 64))
        if a != b:
            return ("A", a, b, c)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz = eval_calib()
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f (expect 3.3)" % wz,
              flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    assert form in ("hetCA4a", "hetCA4b"), form
    order = ORDER[form]
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB461
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    for t in range(n_try):
        stages, seen = [], set()
        draws = 0
        while len(stages) < 4:
            draws += 1
            if draws > 10000:
                print("DRAW-LOOP-FAIL: try %d" % t, flush=True)
                sys.exit(3)
            st = draw_stage(rng, order[len(stages)])
            if st in seen:
                continue
            seen.add(st)
            stages.append(st)
        assert all((s[1] != s[2]) for s in stages), "degenerate draw"
        wz, key = eval_sched(stages)
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
    print("=== %s: %d/%d KEEP (seed=%#x) ===" % (form, len(keep), n_try, seed),
          flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
