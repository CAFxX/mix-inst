#!/usr/bin/env python3
"""Batch-56 PRE-PILOT + PILOT: AND-FORM VARIANTS (ANDN / OR-AND hetero) in the
5-stage MUX cascade (track 6).

Trigger: batch-55 TERMINAL 2026-10-12 (O97) -- the pos1+fisher axis is
CLOSED: the fisher-clean AND3@pos1 keep t6_b55_f0 (18.8u cost-eligible,
triage n_reject=0 reproduced at S1's per-bit gate) S1-DIFF-KILLED on the
low-8-bit joint-distribution chi2 gate (rej=2, worst|z|=3.3 @ delta=16).
Combined with O96 (5/5 worst-z keeps per-bit-killed), no AND@pos1 schedule
clears S1 under either differential statistic -- IN THE AND3 FORM. The
combined b53-b55 read: triage/proxy-DIFF does not predict exact-DIFF for
AND-in-cascade, and the AND gate form itself is now the open question.
This batch varies ONLY the hetero stage's gate form, with the b55
instrument (gate-matched Holm-Bonferroni fisher triage) held verbatim --
any difference in keep rate or S1 fate isolates the FORM.

Forms (x ^= k pre-whiten; final x ^= rotl(k,13) -- the b33c/b45/MU5
frame, 4x MUXD + 1 hetero AND-variant stage at stage index 1, FIXED):
  hetMA5N : ANDN  x ^= (rotl(x,p) & ~rotl(x,q))             -- prize arm
            (= ra ^ (ra&rb): same product pair as AND3, firing on
            support (p,~q), INHERENT linear mask ra)
  hetMOA5 : OAAND x ^= ((rotl(x,p)|rotl(x,q)) & rotl(x,r)) ^ rotl(x,s)
            -- prize arm (OR-AND hetero: products (p,r),(q,r) + cubic
            (p,q,r) + linear mask rd; the rd term is load-bearing --
            without it the stage is identity on single-bit input)
  hetMA5p1f: AND3 x ^= (rotl(x,p)&rotl(x,q)) ^ rotl(x,r)     -- CONTROL
            (b55-identical; a RATE discriminator separating "gate form
            matters" from "draws bad". b55 measured 1/80)
mux(s,a,b) = (s&a)|(~s&b).

Mechanism question: does the AND gate form (ANDN/OR-AND vs AND3) change
exact-DIFF survival of the single hetero stage inside the 5st MUX cascade?
>=1 prize-arm fisher-KEEP -> bundle -> S0 (<19.3u strict) -> S1 fail-fast
-> staged battery -> Q1 (sac_z5=0). 0/160 prize-arm keeps (calibration
clean) -> CLOSE the AND-form-variant axis at the triage level (O-entry).

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar = the S1 gate's own rule:
Holm-Bonferroni step-down (ALPHA=0.01) on per-key fisher_logp, ZERO
rejections (lin_diff.holm_reject verbatim). Positive controls
(fail-loud, run `calibrate` first):
  (i)  and1/b33c 6-stage must give z=3.3 (harness sanity -- the DIFF
       computation reproduces bit-for-bit);
  (ii) MU5-324 (the 19.3u frontier, S1-clean) must KEEP under the
       fisher bar (0 rejections) -- validates the bar is not
       miscalibrated against a known-good schedule.
Unit check (bit-exact, in `selftest`): the AND3 stage on single-bit
input degrades to x ^= rc -- the mechanism's premise, verified not
assumed. Draw constraints verbatim from b53: MUX s,a,b pairwise
distinct; AND p,q,r pairwise distinct; duplicate stage-tuples re-drawn
(b41); draw-loop cap 10000 (b45). KEEP schedules appended to JSONL
IMMEDIATELY per-try (b39 lesson).

Pre-registered pre-pilot rule: 12 draws/arm (seeds 0xB561/0xB562/0xB563) as a
HARNESS
check (calibration must PASS both gates, fail-loud; draws must
complete). The pre-pilot does NOT falsify at 12 draws under the
strict fisher bar (a ~1% true keep rate gives P(0/12)~0.89) -> PILOT
(ANDN 80 draws 0xB564 + OAAND 80 draws 0xB565 + AND3-control 24 draws
0xB566) runs regardless. The PILOT adjudicates:
>=1 prize-arm fisher-KEEP -> bundle -> S0 -> S1 -> battery -> Q1;
0/160 prize-arm keeps -> CLOSE the AND-form-variant axis at the triage
level.

Usage: t6_b56_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: hetMA5N | hetMOA5 | hetMA5p1f | calibrate | selftest
"""
import json
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
    if tag == "MUXD":
        _, s, a, b, d = st
        assert len({s, a, b}) == 3, "degenerate mux draw"
        return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b)) ^ rotl(x, d)) & M64
    elif tag == "AND3":
        _, p, q, r = st
        assert len({p, q, r}) == 3, "degenerate and draw"
        return (x ^ (rotl(x, p) & rotl(x, q)) ^ rotl(x, r)) & M64
    elif tag == "ANDN":
        # ANDN: x ^= (ra & ~rb). Zero-corner: on single-bit input this
        # degrades to x ^= ra (linear mask, NOT identity -- b43 trap
        # avoided by construction). p==q would be identically 0
        # (ra&~ra=0) -- excluded fail-loud at draw time.
        _, p, q = st
        assert p != q, "degenerate andn draw"
        return (x ^ (rotl(x, p) & (~rotl(x, q)))) & M64
    elif tag == "OAAND":
        # OR-AND hetero: x ^= ((ra|rb)&rc) ^ rd. Zero-corner: the
        # ((ra|rb)&rc) term is 0 on single-bit input, so rd is the
        # load-bearing linear mask (b53 cut #6 trap avoided). All four
        # rotations distinct (fail-loud at draw time).
        _, p, q, r, s = st
        assert len({p, q, r, s}) == 4, "degenerate oaand draw"
        return (x ^ (((rotl(x, p) | rotl(x, q)) & rotl(x, r))) ^ rotl(x, s)) & M64
    else:
        raise AssertionError(tag)


def eval_sched(stages):
    """Exact S1-DIFF triage with the GATE's rule: returns
    (n_reject, worst_z, worst_key, min_fisher_logp) where n_reject is the
    Holm-Bonferroni rejection count on per-key fisher_logp (ALPHA=0.01),
    verbatim the S1 DIFF gate (lin_diff.screen_lin_diff). KEEP iff
    n_reject == 0. O96: worst-z selection cannot see the aggregated
    deviations that kill hetMA5p1 at the gate."""
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
    # (3) ANDN stage on single-bit input degrades to x ^= ra (NOT identity:
    # the b43 trap is avoided by construction). x = 1<<7, (p,q) = (13,29):
    # ra = bit 20, ~rb clears bit 36 -- ra&~rb = bit 20 = ra.
    got = apply_stage(x, ("ANDN", 13, 29))
    want = (x ^ rotl(x, 13)) & M64
    assert int(got) == int(want), "ANDN zero-corner degradation mismatch: " \
        "%#x vs %#x" % (int(got), int(want))
    # (4) OAAND stage on single-bit input degrades to x ^= rd: the
    # ((ra|rb)&rc) term is 0 (single-bit ra|rb at bits 20/36, rc = bit 48),
    # so the stage is x ^= rd -- the linear mask is load-bearing.
    got = apply_stage(x, ("OAAND", 13, 29, 41, 7))
    want = (x ^ rotl(x, 7)) & M64
    assert int(got) == int(want), "OAAND zero-corner degradation mismatch: " \
        "%#x vs %#x" % (int(got), int(want))
    # (5) Degeneracy asserts fire.
    for bad in [("MUXD", 5, 5, 9, 1), ("AND3", 13, 13, 41),
                ("ANDN", 13, 13), ("OAAND", 13, 29, 41, 41)]:
        try:
            apply_stage(x, bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("degeneracy assert did not fire: %r" % (bad,))
    print("SELFTEST PASS: AND3 zero-corner=x^rc bit-exact; "
          "ANDN zero-corner=x^ra bit-exact; OAAND zero-corner=x^rd bit-exact; "
          "MUX gate popcount=1; degeneracy asserts fire", flush=True)


def draw_mux(rng):
    while True:
        s = int(rng.integers(0, 64))
        a = int(rng.integers(0, 64))
        b = int(rng.integers(0, 64))
        if len({s, a, b}) == 3:
            d = int(rng.integers(0, 64))
            return ("MUXD", s, a, b, d)


def draw_and3(rng):
    while True:
        p = int(rng.integers(0, 64))
        q = int(rng.integers(0, 64))
        r = int(rng.integers(0, 64))
        if len({p, q, r}) == 3:
            return ("AND3", p, q, r)


def draw_andn(rng):
    while True:
        p = int(rng.integers(0, 64))
        q = int(rng.integers(0, 64))
        if p != q:
            return ("ANDN", p, q)


def draw_oaand(rng):
    while True:
        p = int(rng.integers(0, 64))
        q = int(rng.integers(0, 64))
        r = int(rng.integers(0, 64))
        s = int(rng.integers(0, 64))
        if len({p, q, r, s}) == 4:
            return ("OAAND", p, q, r, s)


AND_DRAW = {"hetMA5N": (draw_andn, "ANDN"),
            "hetMOA5": (draw_oaand, "OAAND"),
            "hetMA5p1f": (draw_and3, "AND3")}


def draw_het(rng, form):
    """5 stages: 4 MUXD + 1 hetero AND-variant stage with the AND
    position FIXED at 1 (the only position with measured S1-clearing
    evidence -- O94/O95/O97, AND3-specific; other positions are a
    reserved escalation if a prize form shows quality life -- b56
    cut #1).

    (b56: draw structure identical to b54/b55; only the hetero stage's
    gate form varies.)
    """
    draw_and, and_tag = AND_DRAW[form]
    stages = []
    for i in range(5):
        stages.append(draw_and(rng) if i == 1 else draw_mux(rng))
    return stages, 1, and_tag


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        w1 = eval_calib_and1()
        ok1 = abs(w1 - 3.3) < 0.05
        print("CALIB-1 and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (w1, "PASS" if ok1 else "FAIL"), flush=True)
        nrej2, w2, _, flp2 = eval_sched(MU5_324_SCHED)
        ok2 = (nrej2 == 0)
        print("CALIB-2 mux/MU5-324: n_reject=%d maxworst|z|=%.2f "
              "min_fisher=%.1f (expect KEEP: 0 rejections; b51/b52/b53 "
              "measured z=3.24) %s"
              % (nrej2, w2, flp2, "PASS" if ok2 else "FAIL"), flush=True)
        sys.exit(0 if (ok1 and ok2) else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    form = sys.argv[1]
    assert form in AND_DRAW, form
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB561
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    draw_and, and_tag = AND_DRAW[form]
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
            cand, and_pos, seen_tag = draw_het(rng, form)
            assert and_pos == 1, "AND position drifted: %d" % and_pos
            assert seen_tag == and_tag, "AND tag drifted: %s" % seen_tag
            key = tuple(cand)
            if key in seen:
                continue
            seen.add(key)
            stages = cand
        assert sum(1 for s in stages if s[0] == and_tag) == 1, \
            "not exactly one %s stage" % and_tag
        assert stages[1][0] == and_tag, "%s not at stage index 1" % and_tag
        if and_tag == "AND3":
            assert all(len({s[1], s[2], s[3]}) == 3 for s in stages), \
                "degenerate draw"
        elif and_tag == "ANDN":
            assert all(s[1] != s[2] for s in stages if s[0] == "ANDN"), \
                "degenerate draw"
        elif and_tag == "OAAND":
            assert all(len({s[1], s[2], s[3], s[4]}) == 4
                       for s in stages if s[0] == "OAAND"), \
                "degenerate draw"
        nrej, wz, key, flp = eval_sched(stages)
        minz = min(minz, wz)
        flag = "KEEP" if nrej == 0 else "kill"
        if nrej > 0:
            kills += 1
        extra = " andpos=1"
        print("try %3d n_reject=%d maxworst|z|=%8.1f min_fisher=%7.1f "
              "worstkey=%#x %s%s" %
              (t, nrej, wz, flp, key, flag, extra), flush=True)
        if nrej == 0:
            keep.append((wz, stages))
            if keep_path:
                rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                       "stages": [list(s) for s in stages],
                       "form": form, "seed": seed, "and_pos": 1}
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
