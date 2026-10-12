#!/usr/bin/env python3
"""Queued-lead adjudication: xorh5 -- 4xMUXD + 1xXOR4 hetero stage
(track 6, 2026-10-12).

Proposal (LEADS_LEDGER 04:20 entry, XXXV's unlaunched co-design): one
XOR4 stage  x ^= ra^rb^rc^rd  inside 4 MUXD stages, MU5 frame
bit-identical (pre-whiten x ^= k; final x ^= rotl(k,13)), position
p drawn Uniform{0..4}.

Nonsingularity: the stage map is y = (I + R^a + R^b + R^c + R^d) x
over GF(2) -- 5 terms (odd). p(z) = 1+z^a+z^b+z^c+z^d has p(1)=1,
hence gcd(p, z^64+1)=gcd(p,(z+1)^64)=1: the circulant is bijective
for ANY tap choice (b48 proof machinery). Taps required pairwise
distinct anyway (fail-loud) so no term silently cancels.

Honest risk (proposal's own): quality -- no existence proof.
AND3-hetero precedent (h0) says 4 nonlinear stages can clear S1-LIN.
This pilot is the ~1-min existence test.

Cost thesis: 4 MUXD stages (~3.86u each, b58 measured) + 1 XOR4
stage (2 XOR levels, cheap) -> projected ~17.4u. S0 adjudicates.

Triage: the proven fisher-matched instrument (holm_reject,
ALPHA=0.01, n_reject==0) -- same bar as b57/b59.

Pre-registered rule: pre-pilot 12 draws (seed 0xB6A1, harness
check) -> pilot 80 draws (seed 0xB6A2). >=1 fisher-KEEP -> bundle
(gen script TBD, bit-exact 2000/2000 + 500/500) -> S0
(run_synth.py, strict bar <18.6u, XCHECK clean) -> staged battery
S1->S4 -> Q1 (sac_z5=0 mandatory). 0/80 keeps -> FORM-KILL at the
triage level (O-entry, scoped to the tested construction).

Usage: t6_xorh5_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: xorh5 | calibrate | selftest
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
    assert tag == "XOR4", tag
    _, a, b, c, d = st
    assert len({a, b, c, d}) == 4, "degenerate xor4 draw"
    return (x ^ rotl(x, a) ^ rotl(x, b) ^ rotl(x, c) ^ rotl(x, d)) & M64


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
# from t6_b59_screen.py so the z=3.3 reproduction is exact.
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


def draw_xorh5(rng):
    """One schedule: p ~ Uniform{0..4} = XOR4 stage position; the
    XOR4 stage gets 4 pairwise-distinct taps Uniform{0..63}; the 4
    MUXD stages get s/a/b pairwise-distinct (d free), all draws
    global (b57-style), MU5 frame."""
    p = int(rng.integers(0, 5))
    stages = []
    for i in range(5):
        if i == p:
            taps = rng.choice(64, size=4, replace=False)
            stages.append(("XOR4",) + tuple(int(t) for t in taps))
        else:
            sab = rng.choice(64, size=3, replace=False)
            d = int(rng.integers(0, 64))
            stages.append(("MUXD", int(sab[0]), int(sab[1]),
                           int(sab[2]), d))
    assert sum(1 for s in stages if s[0] == "XOR4") == 1
    assert sum(1 for s in stages if s[0] == "MUXD") == 4
    return stages, p


def selftest():
    """Fail-loud unit checks."""
    # (1) XOR4 stage bit-exact vs manual expansion; bijectivity spot
    # check: 64 distinct single-bit inputs -> 64 distinct outputs.
    x = np.uint64(1 << 7)
    st = ("XOR4", 5, 17, 33, 41)
    got = int(apply_stage(x, st))
    want = int((x ^ rotl(x, 5) ^ rotl(x, 17) ^ rotl(x, 33)
                ^ rotl(x, 41)) & M64)
    assert got == want, "XOR4 stage mismatch"
    outs = {int(apply_stage(np.uint64(1) << np.uint64(i), st))
            for i in range(64)}
    assert len(outs) == 64, "XOR4 stage not bijective on basis"
    # (2) MUXD stage still bit-exact.
    xm = np.uint64(1 << 7)
    stm = ("MUXD", 5, 17, 33, 41)
    g = mux(rotl(xm, 5), rotl(xm, 17), rotl(xm, 33))
    assert int(apply_stage(xm, stm)) == int((xm ^ g ^ rotl(xm, 41)) & M64)
    # (3) Draw operator: 200 draws, exactly one XOR4 stage at the
    # drawn position, 4 distinct taps; MUXD stages valid.
    rng = np.random.default_rng(0xB6A1)
    for i in range(200):
        stages, p = draw_xorh5(rng)
        assert 0 <= p <= 4
        assert stages[p][0] == "XOR4"
        assert len({stages[p][1], stages[p][2], stages[p][3],
                    stages[p][4]}) == 4, "xor4 taps not distinct"
        for j, s in enumerate(stages):
            if j == p:
                continue
            assert s[0] == "MUXD"
            assert len({s[1], s[2], s[3]}) == 3, "mux s/a/b not distinct"
    print("SELFTEST PASS: XOR4 bit-exact + bijective on basis; MUXD "
          "bit-exact; draw operator 200/200 (1 XOR4 at p, taps "
          "distinct, MUXD valid)", flush=True)


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
    assert form == "xorh5", form
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB6A1
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    minz = float("inf")
    for t in range(n_try):
        stages, p = draw_xorh5(rng)
        nrej, wz, key, flp = eval_sched(stages)
        minz = min(minz, wz)
        flag = "KEEP" if nrej == 0 else "kill"
        if nrej > 0:
            kills += 1
        print("try %3d p=%d n_reject=%d maxworst|z|=%8.1f min_fisher=%7.1f "
              "worstkey=%#x %s" %
              (t, p, nrej, wz, flp, key, flag), flush=True)
        if nrej == 0:
            keep.append((wz, stages))
            if keep_path:
                rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                       "stages": [list(s) for s in stages],
                       "form": "xorh5", "seed": seed, "xor4_pos": p}
                with open(keep_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
    print("=== xorh5: %d/%d KEEP minz=%.1f (seed=%#x) ===" %
          (len(keep), n_try, minz, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
