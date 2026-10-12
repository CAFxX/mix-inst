#!/usr/bin/env python3
"""Batch-61 PRE-PILOT + PILOT: muxD5f local-2base with FISHER-MATCHED
triage (track 6).

Trigger: batch-60 TERMINAL 2026-10-12 (O120) -- the wider-radius
(m~Uniform{2,3,4}) basin-depth axis found NO sub-18.6u schedule
(best 18.7u). Remaining unexplored: the m=1 ring around the
t6_b59_47 frontier point, and the d<=3 neighborhood of t6_b60_27
(best wide-radius keep, 18.7u -- its d<=4 neighborhood in b60
contained only itself: unexplored, not proven narrow).
t6_b59_47 at 18.6u (speed point, d=2 from the winner) and t6_b59_0 at
19.1u (d=1). S0 cost spread across the basin is wide (18.5-20.3u);
the basin contains sub-18.6u schedules. This batch asks whether it
contains a sub-18.6u QUALITY-CLEAN one.

Form (x ^= k pre-whiten; final x ^= rotl(k,13) -- the MU5 frame,
bit-identical to t6_b59_47 / t6_b60_27):
  muxD5f-local2: 5x [x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)]
mux(s,a,b) = (s&a)|(~s&b).

Draw operator (fail-loud): per try, base ~ Uniform{t6_b59_47,
t6_b60_27}; m ~ Uniform{1,2,3} distinct rotation positions (of 20)
resampled Uniform{0..63}; per-stage s/a/b pairwise-distinctness
re-checked on resample (b51 cut #10); d free. m>=1 so exact base
rediscovery is impossible by construction (a draw can never equal
the OTHER base either: the bases differ by 6 positions > max m=3).

Mechanism question: does the proven-clean winner basin contain a
sub-18.6u schedule that survives the full battery?

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar = the S1 gate's own rule:
Holm-Bonferroni step-down (ALPHA=0.01) on per-key fisher_logp, ZERO
rejections (lin_diff.holm_reject verbatim).

Controls (fail-loud, run `calibrate` first):
  CALIB-1: and1/b33c 6-stage must give z=3.3 (harness sanity).
  CALIB-2a: MU5-324 (5-stage) must KEEP (n_reject=0) -- bar sanity.
  CALIB-2b: linear-4 must be REJECTED (n_reject>0) -- negative control.

Unit check (`selftest`, fail-loud): two-base perturbation operator --
200 draws, each 1..3 positions off the CHOSEN base, all stages
MUXD-valid with s/a/b distinct, never base-identical.

Pre-registered pre-pilot rule: 12 draws (seed 0xB611) as a HARNESS
check (all 3 calibration gates PASS fail-loud; draws complete).
0/12 -> PILOT (80 draws, seed 0xB612) runs regardless. Vacuity
(GATE-FAIL): keeps==n_try and kills==0 -> KILL LOUDLY, diagnose.

Usage: t6_b61_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: muxD5flocal2 | calibrate | selftest
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

# The two best known points (verbatim from disk).
# t6_b59_47: fast_battery/candidates/t6_b59_47/model.py STAGES (frontier 18.6u).
# t6_b60_27: new_constructions/batch60/bundle_t6_b60_27.log (best b60 keep, 18.7u).
BASE_47 = [("MUXD", 17, 22, 10, 55), ("MUXD", 63, 62, 49, 57),
           ("MUXD", 29, 39, 35, 6), ("MUXD", 9, 4, 44, 36),
           ("MUXD", 5, 54, 31, 34)]
BASE_27 = [("MUXD", 17, 22, 52, 55), ("MUXD", 63, 62, 51, 41),
           ("MUXD", 29, 39, 35, 6), ("MUXD", 9, 4, 49, 36),
           ("MUXD", 16, 54, 52, 34)]
BASES = {"t6_b59_47": [tuple(s) for s in BASE_47],
         "t6_b60_27": [tuple(s) for s in BASE_27]}
BASE_NAMES = ["t6_b59_47", "t6_b60_27"]


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


# MU5-324 schedule (5-stage frontier) -- CALIB-2a: must KEEP.
MU5_324_SCHED = [("MUXD", 62, 50, 55, 2), ("MUXD", 48, 58, 23, 30),
                 ("MUXD", 44, 45, 7, 40), ("MUXD", 49, 26, 32, 35),
                 ("MUXD", 46, 51, 43, 44)]

# Linear-4 negative control schedule (arbitrary fixed rotations).
LIN4_SCHED = [7, 23, 41, 55]


def draw_perturbed(rng):
    """One schedule: base ~ Uniform{t6_b59_47, t6_b60_27}; m ~
    Uniform{1,2,3} distinct rotation positions (of 20) resampled
    Uniform{0..63}; s/a/b distinctness re-checked per stage (b51 cut
    #10); d free. Never base-identical (m >= 1); never the other base
    (bases differ by 6 positions > max m=3)."""
    base_name = BASE_NAMES[int(rng.integers(0, 2))]
    base = BASES[base_name]
    vals = [list(st) for st in base]
    m = int(rng.integers(1, 4))
    positions = rng.choice(20, size=m, replace=False)
    for p in positions:
        st_i, rot_j = divmod(int(p), 4)  # rot_j: 0=s 1=a 2=b 3=d
        guard = 0
        while True:
            guard += 1
            assert guard <= 10000, "perturb resample loop exceeded cap"
            v = int(rng.integers(0, 64))
            if v == vals[st_i][1 + rot_j]:
                continue  # must actually move the position (diff == m)
            if rot_j < 3:
                cur = vals[st_i]
                others = {cur[1], cur[2], cur[3]} - {cur[1 + rot_j]}
                if v in others:
                    continue
            vals[st_i][1 + rot_j] = v
            break
    stages = [tuple(v) for v in vals]
    assert len(stages) == 5 and all(s[0] == "MUXD" for s in stages)
    assert all(len({s[1], s[2], s[3]}) == 3 for s in stages), \
        "degenerate perturbation: %r" % (stages,)
    assert stages != base, "perturbation reproduced its base"
    return stages, base_name, m


def selftest():
    """Fail-loud unit checks."""
    # (1) MUXD stage bit-exact vs manual expansion.
    x = np.uint64(1 << 7)
    st = ("MUXD", 5, 17, 33, 41)
    g = mux(rotl(x, 5), rotl(x, 17), rotl(x, 33))
    assert bin(int(g)).count("1") == 1, "MUX gate popcount != 1"
    got = int(apply_stage(x, st))
    want = int((x ^ g ^ rotl(x, 41)) & M64)
    assert got == want, "MUXD stage mismatch"
    # (2) Two-base perturbation operator: 200 draws, each 1..3
    # positions off the CHOSEN base, all stages valid, never
    # base-identical (either base).
    rng = np.random.default_rng(0xB611)
    bases_seen = set()
    for i in range(200):
        stages, base_name, m = draw_perturbed(rng)
        bases_seen.add(base_name)
        assert 1 <= m <= 3, "m out of range: %d" % m
        base = BASES[base_name]
        diff = 0
        for a, b in zip(stages, base):
            diff += sum(1 for u, v in zip(a[1:], b[1:]) if u != v)
        assert diff == m, "draw %d: %d positions differ, m=%d" % (i, diff, m)
        assert all(s[0] == "MUXD" for s in stages)
        assert all(len({s[1], s[2], s[3]}) == 3 for s in stages)
        assert stages != base
        assert stages not in (BASES["t6_b59_47"], BASES["t6_b60_27"]), \
            "draw %d reproduced a base" % i
    assert bases_seen == {"t6_b59_47", "t6_b60_27"}, \
        "both bases must be drawn in 200 tries: %r" % (bases_seen,)
    print("SELFTEST PASS: MUXD stage bit-exact; two-base perturbation "
          "operator 200/200 (1..3 positions differ from chosen base, "
          "stages valid, never base-identical, both bases drawn)",
          flush=True)


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
    assert form == "muxD5flocal2", form
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB611
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    minz = float("inf")
    for t in range(n_try):
        stages, base_name, m = draw_perturbed(rng)
        nrej, wz, key, flp = eval_sched(stages)
        minz = min(minz, wz)
        flag = "KEEP" if nrej == 0 else "kill"
        if nrej > 0:
            kills += 1
        print("try %3d base=%s m=%d n_reject=%d maxworst|z|=%8.1f "
              "min_fisher=%7.1f worstkey=%#x %s" %
              (t, base_name[-2:], m, nrej, wz, flp, key, flag), flush=True)
        if nrej == 0:
            keep.append((wz, stages))
            if keep_path:
                rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                       "stages": [list(s) for s in stages],
                       "form": "muxD5f", "seed": seed, "is_324": False,
                       "base": base_name, "n_perturb": m}
                with open(keep_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
    print("=== muxD5flocal2: %d/%d KEEP minz=%.1f (seed=%#x) ===" %
          (len(keep), n_try, minz, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
