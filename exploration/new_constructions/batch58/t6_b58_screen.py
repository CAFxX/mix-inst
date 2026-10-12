#!/usr/bin/env python3
"""Batch-58 PRE-PILOT + PILOT: muxD4f with FISHER-MATCHED triage (track 6).

Trigger: batch-57 CLOSED 2026-10-12 (O115) -- fisher-matched triage on
global pure-MUXD 5-stage draws (80 draws, 13/80 keeps) yielded exactly
one frontier point (t6_b57_8, 19.2u, S1->S4+Q1 clean). The global-5-stage
axis is exhausted as an experiment. The instrument (holm_reject,
ALPHA=0.01, n_reject==0 -- the S1 per-bit DIFF gate's own rule, O97)
has never been pointed at 4-stage MUXD.

Form (x ^= k pre-whiten; final x ^= rotl(k,13) -- the MU5 frame,
bit-identical to hyb28_mu5_324 / t6_b57_8):
  muxD4f: 4x [x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)]
mux(s,a,b) = (s&a)|(~s&b).

Mechanism question: is 5 the minimal MUXD stage count for full S+Q
quality, or does 4 suffice? A Q1-clearing 4-stage keep at <19.2u ->
FRONTIER CHALLENGER (~3.8u move). 0/80 keeps -> FAMILY-KILL (4 MUXD
stages insufficient for the fisher bar).

Flagged risk (O111): 2/3 S1-S3-tested 5-stage keeps died at S3 in
Low1/64; 4 stages are strictly weaker mixing, so S3 is the risk
concentration point. The staged battery adjudicates it.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar = the S1 gate's own rule:
Holm-Bonferroni step-down (ALPHA=0.01) on per-key fisher_logp, ZERO
rejections (lin_diff.holm_reject verbatim).

Positive/negative controls (fail-loud, run `calibrate` first):
  CALIB-1: and1/b33c 6-stage must give z=3.3 (harness sanity).
  CALIB-2a: MU5-324 (5-stage, the 19.3u frontier) must KEEP under the
      fisher bar (n_reject=0) -- bar sanity vs known-good.
  CALIB-2b: linear-4 (4x x ^= rotl(x,s), same frame) must be REJECTED
      (n_reject>0) -- negative control, the gate fires on garbage.

Unit check (bit-exact, in `selftest`): MUXD stage on single-bit input
fires exactly 1 bit through the gate (no-zero-corner); degeneracy
asserts fire. Draw constraints verbatim from b57: MUX s,a,b pairwise
distinct (b51 cut #10); d free; duplicate stage-tuples re-drawn within
a try (b41); draw-loop cap 10000 (b45). KEEP schedules appended to
JSONL IMMEDIATELY per-try (b39 lesson).

Pre-registered pre-pilot rule: 12 draws (seed 0xB581) as a HARNESS
check (all 3 calibration gates PASS fail-loud; draws complete).
0/12 keeps -> WEAK-SIGNAL flag (plausible real signal at 4 stages),
PILOT (80 draws, seed 0xB582) runs regardless to confirm. Vacuity
(GATE-FAIL): keeps==n_try and kills==0 -> KILL LOUDLY, diagnose.

Usage: t6_b58_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: muxD4f | calibrate | selftest
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, holm_reject
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
    assert tag == "MUXD", tag
    _, s, a, b, d = st
    assert len({s, a, b}) == 3, "degenerate mux draw"
    return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b)) ^ rotl(x, d)) & M64


def eval_sched(stages):
    """Exact S1-DIFF triage with the GATE's rule: returns
    (n_reject, worst_z, worst_key, min_fisher_logp). KEEP iff
    n_reject == 0."""
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_key = None
    min_flp = 0.0
    cells = []
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, flp, _ = diff_cell_logps(S, key)
        cells.append((("DIFF", key), flp))
        if wz > worst:
            worst, worst_key = wz, key
        min_flp = min(min_flp, flp)
    n_reject = len(holm_reject(cells))
    return n_reject, worst, worst_key, min_flp


def eval_lin4(sched):
    """Negative-control evaluator: 4x x ^= rotl(x,s), MU5 frame."""
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    min_flp = 0.0
    cells = []
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for s in sched:
            x = (x ^ rotl(x, s)) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, flp, _ = diff_cell_logps(S, key)
        cells.append((("DIFF", key), flp))
        worst = max(worst, wz)
        min_flp = min(min_flp, flp)
    n_reject = len(holm_reject(cells))
    return n_reject, worst, min_flp


# b33c schedule for the positive control (and1, 6 stages) -- verbatim
# from t6_b57_screen.py so the z=3.3 reproduction is exact.
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


# MU5-324 schedule (5-stage frontier) -- (s,a,b,d) per stage, through
# the FULL MUX stage (with d). CALIB-2a: must KEEP (bar sanity).
MU5_324_SCHED = [("MUXD", 62, 50, 55, 2), ("MUXD", 48, 58, 23, 30),
                 ("MUXD", 44, 45, 7, 40), ("MUXD", 49, 26, 32, 35),
                 ("MUXD", 46, 51, 43, 44)]

# Linear-4 negative control schedule (arbitrary fixed rotations).
LIN4_SCHED = [7, 23, 41, 55]


def load_b57_prefixes():
    """First-4-stage tuples of the 13 b57 pilot keeps, for the
    [SCHEDULE-OVERLAP] honesty flag. Missing file -> empty set."""
    p = "/home/hatch/workspace/mix/exploration/new_constructions/batch57/pilot_keeps.jsonl"
    out = set()
    try:
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                st = [tuple(s) for s in e["stages"]]
                out.add(tuple(st[:4]))
    except OSError:
        pass
    return out


def selftest():
    """Bit-exact unit checks. Fail-loud: any failure exits nonzero."""
    # (1) MUXD stage on single-bit input fires exactly 1 bit through
    # the gate (no-zero-corner survives): gate output popcount == 1.
    x = np.uint64(1 << 7)
    g = mux(rotl(x, 5), rotl(x, 17), rotl(x, 33))
    assert bin(int(g)).count("1") == 1, "MUX gate popcount != 1: %#x" % int(g)
    # (2) Full MUXD stage bit-exact vs manual expansion.
    st = ("MUXD", 5, 17, 33, 41)
    got = int(apply_stage(x, st))
    want = int((x ^ g ^ rotl(x, 41)) & M64)
    assert got == want, "MUXD stage mismatch: %#x vs %#x" % (got, want)
    # (3) Degeneracy asserts fire.
    for bad in [("MUXD", 5, 5, 9, 1), ("MUXD", 5, 9, 5, 2)]:
        try:
            apply_stage(x, bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("degeneracy assert did not fire: %r" % (bad,))
    # (4) draw_muxD4f emits exactly 4 MUXD stages, s/a/b distinct.
    rng = np.random.default_rng(0xB581)
    for _ in range(200):
        ds = draw_muxD4f(rng)
        assert len(ds) == 4 and all(s[0] == "MUXD" for s in ds), ds
        assert all(len({s[1], s[2], s[3]}) == 3 for s in ds), ds
    print("SELFTEST PASS: MUX gate popcount=1; MUXD stage bit-exact; "
          "degeneracy asserts fire; draw_muxD4f 200/200 valid", flush=True)


def draw_mux(rng):
    while True:
        s = int(rng.integers(0, 64))
        a = int(rng.integers(0, 64))
        b = int(rng.integers(0, 64))
        if len({s, a, b}) == 3:
            d = int(rng.integers(0, 64))
            return ("MUXD", s, a, b, d)


def draw_muxD4f(rng):
    """4 stages: all MUXD (the frontier form, one stage fewer). MUX
    stages s,a,b pairwise distinct (b51 cut #10 degeneracy proof);
    d free."""
    return [draw_mux(rng) for _ in range(4)]


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        w1 = eval_calib_and1()
        ok1 = abs(w1 - 3.3) < 0.05
        print("CALIB-1 and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (w1, "PASS" if ok1 else "FAIL"), flush=True)
        nrej2a, w2a, _, flp2a = eval_sched(MU5_324_SCHED)
        ok2a = (nrej2a == 0)
        print("CALIB-2a mux/MU5-324(5st): n_reject=%d maxworst|z|=%.2f "
              "min_fisher=%.1f (expect KEEP: 0 rejections) %s"
              % (nrej2a, w2a, flp2a, "PASS" if ok2a else "FAIL"), flush=True)
        nrej2b, w2b, flp2b = eval_lin4(LIN4_SCHED)
        ok2b = (nrej2b > 0)
        print("CALIB-2b linear-4: n_reject=%d maxworst|z|=%.1f "
              "min_fisher=%.1f (expect REJECT: >0 rejections) %s"
              % (nrej2b, w2b, flp2b, "PASS" if ok2b else "FAIL"), flush=True)
        sys.exit(0 if (ok1 and ok2a and ok2b) else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    form = sys.argv[1]
    assert form == "muxD4f", form
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB581
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    b57_prefix = load_b57_prefixes()
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    minz = float("inf")
    for t in range(n_try):
        stages = []
        seen = set()
        draws = 0
        while len(stages) < 4:
            draws += 1
            if draws > 10000:
                print("DRAW-LOOP-FAIL: try %d" % t, flush=True)
                sys.exit(3)
            cand = draw_mux(rng)
            key = tuple(cand)
            if key in seen:
                continue
            seen.add(key)
            stages.append(cand)
        assert all(s[0] == "MUXD" for s in stages), "non-MUXD stage drawn"
        assert all(len({s[1], s[2], s[3]}) == 3 for s in stages), \
            "degenerate draw"
        nrej, wz, key, flp = eval_sched(stages)
        minz = min(minz, wz)
        flag = "KEEP" if nrej == 0 else "kill"
        if nrej > 0:
            kills += 1
        overlap = tuple(stages) in b57_prefix
        print("try %3d n_reject=%d maxworst|z|=%8.1f min_fisher=%7.1f "
              "worstkey=%#x %s%s" %
              (t, nrej, wz, flp, key, flag,
               " [SCHEDULE-OVERLAP]" if overlap else ""), flush=True)
        if nrej == 0:
            keep.append((wz, stages))
            if keep_path:
                rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                       "stages": [list(s) for s in stages],
                       "form": form, "seed": seed,
                       "is_324": False, "sched_overlap_b57": bool(overlap)}
                with open(keep_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
    print("=== %s: %d/%d KEEP minz=%.1f (seed=%#x) ===" %
          (form, len(keep), n_try, minz, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
