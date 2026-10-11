#!/usr/bin/env python3
"""Batch-53 PRE-PILOT + PILOT: 5-stage hetero MUX/AND cascade (track 6).

Trigger: batch-52 CLOSED 2026-10-11T18:40:25Z -- KILL LOUDLY (d is
load-bearing for MUX-5st; no-zero-corner firing insufficient without the
linear mixing term). The frontier's own stage cannot be cheapened by
ablation. This batch changes the stage MIX: 4 proven MUX stages + 1
cheaper b33 AND stage.

Forms (x ^= k pre-whiten; final x ^= rotl(k,13) -- the b33c/b45/MU5
frame; the ONLY delta from MU5-324 is one stage's gate swap):
  hetMA5:  4x [x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)]
           + 1x [x ^= (rotl(x,p)&rotl(x,q)) ^ rotl(x,r)]  (prize)
           AND position drawn Uniform{0..4} per try, recorded per try.
  muxS5d:  5x full MUX form, fresh draws (control -- the b52 arm verbatim)
mux(s,a,b) = (s&a)|(~s&b).

Mechanism question: does one AND stage poison the proven 5st MUX cascade
(zero-corner: on single-bit input the AND stage degrades to linear
x ^= rc), or does the cascade absorb its single-bit linearity? The
b33 AND-6st cascade keeps at S1 (t6_b33b full battery pass), so AND
stages contribute quality at sufficient depth; b43's wall is about
HOMOGENEOUS sparse-AND at <=4st. Genuinely untested at 5st hetero.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive controls
(fail-loud, run `calibrate` first):
  (i)  and1/b33c 6-stage must give z=3.3 (harness sanity);
  (ii) MU5-324 schedule [(62,50,55,2),(48,58,23,30),(44,45,7,40),
       (49,26,32,35),(46,51,43,44)] through the FULL MUX stage (with d)
       must KEEP (z<10; b51/b52 harnesses measured 3.24).
Unit check (bit-exact, in `selftest`): the AND3 stage on single-bit
input degrades to x ^= rc -- the mechanism's premise, verified not
assumed.
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).
Fail-loud draw-loop cap 10000 (b45 lesson). Duplicate stage-tuples
re-drawn (b41). MUX s,a,b pairwise distinct (b51 cut #10); AND p,q,r
pairwise distinct (p==q -> 2-XOR layer, proven by substitution).

Pre-registered pre-pilot rule: 6 draws/arm (seeds 0xB531 hetMA5,
0xB532 muxS5d). >=1 KEEP on hetMA5 -> S0 spot-check (stratified) ->
pilot. 0 keeps on hetMA5 with min z >= 1e3 AND muxS5d keeping >=1 ->
KILL LOUDLY (AND stage poisons the MUX-5st cascade), scoped, no pilot.
0 keeps with min z < 100 (near-misses) -> pilot. 0 keeps on BOTH arms
-> no hetero-verdict; diagnose, do NOT close.

Usage: t6_b53_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: hetMA5 | muxS5d | calibrate | selftest
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
    elif tag == "AND3":
        _, p, q, r = st
        assert len({p, q, r}) == 3, "degenerate and draw"
        return (x ^ (rotl(x, p) & rotl(x, q)) ^ rotl(x, r)) & M64
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


def selftest():
    """Bit-exact unit checks. Fail-loud: any failure exits nonzero."""
    # (1) AND3 stage on single-bit input degrades to x ^= rc.
    # Take x = 1<<7 (single bit), stage (p,q,r) = (13,29,41) with
    # 7+13=20, 7+29=36 distinct positions -> (ra&rb) fires 0 bits.
    x = np.uint64(1 << 7)
    got = apply_stage(x, ("AND3", 13, 29, 41))
    want = (x ^ rotl(x, 41)) & M64
    assert int(got) == int(want), "AND3 zero-corner degradation mismatch: " \
        "%#x vs %#x" % (int(got), int(want))
    # (2) MUXD stage on single-bit input fires exactly 1 bit through
    # the gate (no-zero-corner survives): gate output popcount == 1.
    g = mux(rotl(x, 5), rotl(x, 17), rotl(x, 33))
    assert bin(int(g)).count("1") == 1, "MUX gate popcount != 1: %#x" % int(g)
    # (3) Degeneracy asserts fire.
    for bad in [("MUXD", 5, 5, 9, 1), ("AND3", 13, 13, 41)]:
        try:
            apply_stage(x, bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("degeneracy assert did not fire: %r" % (bad,))
    print("SELFTEST PASS: AND3 zero-corner=x^rc bit-exact; "
          "MUX gate popcount=1; degeneracy asserts fire", flush=True)


def draw_mux(rng):
    while True:
        s = int(rng.integers(0, 64))
        a = int(rng.integers(0, 64))
        b = int(rng.integers(0, 64))
        if len({s, a, b}) == 3:
            d = int(rng.integers(0, 64))
            return ("MUXD", s, a, b, d)


def draw_and(rng):
    while True:
        p = int(rng.integers(0, 64))
        q = int(rng.integers(0, 64))
        r = int(rng.integers(0, 64))
        if len({p, q, r}) == 3:
            return ("AND3", p, q, r)


def draw_hetMA5(rng):
    """5 stages: 4 MUXD + 1 AND3; AND position Uniform{0..4}."""
    and_pos = int(rng.integers(0, 5))
    stages = []
    for i in range(5):
        stages.append(draw_and(rng) if i == and_pos else draw_mux(rng))
    return stages, and_pos


def draw_muxS5d(rng):
    return [draw_mux(rng) for _ in range(5)]


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        w1 = eval_calib_and1()
        ok1 = abs(w1 - 3.3) < 0.05
        print("CALIB-1 and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (w1, "PASS" if ok1 else "FAIL"), flush=True)
        w2, _ = eval_sched(MU5_324_SCHED)
        ok2 = w2 < 10.0
        print("CALIB-2 mux/MU5-324: maxworst|z|=%.2f (expect KEEP z<10; "
              "b51/b52 harnesses measured 3.24) %s"
              % (w2, "PASS" if ok2 else "FAIL"), flush=True)
        sys.exit(0 if (ok1 and ok2) else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    form = sys.argv[1]
    assert form in ("hetMA5", "muxS5d"), form
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB531
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    minz = float("inf")
    for t in range(n_try):
        stages, seen = [], set()
        and_pos = None
        draws = 0
        while len(stages) < 5:
            draws += 1
            if draws > 10000:
                print("DRAW-LOOP-FAIL: try %d" % t, flush=True)
                sys.exit(3)
            if form == "hetMA5":
                cand, and_pos = draw_hetMA5(rng)
                key = tuple(cand)
                if key in seen:
                    continue
                seen.add(key)
                stages = cand
            else:
                st = draw_mux(rng)
                if st in seen:
                    continue
                seen.add(st)
                stages.append(st)
        if form == "hetMA5":
            assert sum(1 for s in stages if s[0] == "AND3") == 1, \
                "not exactly one AND3 stage"
            assert all(len({s[1], s[2], s[3]}) == 3 for s in stages), \
                "degenerate draw"
        else:
            assert all(len({s[1], s[2], s[3]}) == 3 for s in stages), \
                "degenerate draw"
        wz, key = eval_sched(stages)
        minz = min(minz, wz)
        flag = "KEEP" if wz < 10 else "kill"
        if wz >= 10:
            kills += 1
        extra = (" andpos=%d" % and_pos) if form == "hetMA5" else ""
        print("try %3d maxworst|z|=%8.1f killkey=%#x %s%s" %
              (t, wz, key, flag, extra), flush=True)
        if wz < 10:
            keep.append((wz, stages))
            if keep_path:
                rec = {"z": wz, "stages": [list(s) for s in stages],
                       "form": form, "seed": seed}
                if form == "hetMA5":
                    rec["and_pos"] = and_pos
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
