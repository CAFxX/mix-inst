#!/usr/bin/env python3
"""Track-2 andor_struct pilot: ANDOR with co-designed structured taps.

Thesis (DESIGN.md pre-registered): O131 killed random-tap ANDOR (0/40,
best z=26k). The Boolean function f=(p&q)|(r&s) is NOT the weak link
(max|W|=6, NL=5/4vars, normalized 0.625 > MUX's 0.5); the stage-as-wired
is: no linear bypass tap, all-probabilistic 3/8 differential spread, 1/16
output bias, and random tap geometry that clusters/correlates the spread.
This lane tests whether TAP GEOMETRY is the binding constraint.

Families: Q=quadrant-spread (primary), P=paired +/- (secondary),
          R=random-tap O131-verbatim replay (control, expect inner-kill).
Frame MU5, templates H1/H3 (hetstage verbatim). Gates: inner-DIFF-SEQ
PRIMARY (batch-62 lesson), fisher triage second. KEEP iff inner lin PASS
and diff PASS and fisher n_reject == 0.

Usage: t8_andor_struct_screen.py andor_struct <seed> [keep_jsonl]
       t8_andor_struct_screen.py calibrate | selftest
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/hetstage2")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/hetstage")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
import t8_hetstage2_screen as S2  # noqa: E402  (gate instruments, patterns)
import t8_hetstage_screen as HS  # noqa: E402  (ANDOR verbatim, templates)
import t8_het8_screen as H  # noqa: E402
from lin_diff import diff_cell_logps, holm_reject, screen_lin_diff  # noqa: E402
from screen_lib import KEYS, N  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
INNER_KEYS = S2.INNER_KEYS
rotl = H.rotl

# hetstage verbatim: ANDOR + MUXD (MUXD via H delegation).
apply_stage = HS.apply_stage

# t6_b59_47: single proven-clean base, verbatim from
# new_constructions/batch62/t6_b62_screen.py (hetstage2 CALIB-5a).
BASE_47 = [("MUXD", 17, 22, 10, 55), ("MUXD", 63, 62, 49, 57),
           ("MUXD", 29, 39, 35, 6), ("MUXD", 9, 4, 44, 36),
           ("MUXD", 5, 54, 31, 34)]


def eval_inner(stages):
    """PRIMARY triage: screen_lin_diff, batch-62/hetstage2 verbatim."""
    seq = {}
    V = np.arange(N, dtype=np.uint64)
    for key in INNER_KEYS:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return screen_lin_diff(seq, verbose=False)


def eval_sched(stages):
    """Fisher triage, het8 verbatim: KEEP iff n_reject == 0."""
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


# ---------------- draw operators (fail-loud gates) ----------------

def _draw_andor_Q(rng):
    """Quadrant-spread taps: a in [1,16), b in [16,32), c in [32,48),
    d in [48,64). By construction each output bit's AND-OR spans the
    full word; the four differentially-affected bits are decorrelated."""
    a = int(rng.integers(1, 16))
    b = int(rng.integers(16, 32))
    c = int(rng.integers(32, 48))
    d = int(rng.integers(48, 64))
    st = ("ANDOR", a, b, c, d)
    assert 1 <= a < 16 <= b < 32 <= c < 48 <= d < 64, "Q quadrant slip"
    assert len(set(st[1:])) == 4, "Q tap collision"
    return st


def _draw_andor_P(rng):
    """Paired +/- taps: {a, -a, b, -b} mod 64, a,b in [1,32), a != b.
    Symmetric differential spread: delta e_j affects
    {j, j-a, j+a, j-b, j+b}."""
    for _ in range(10000):
        a = int(rng.integers(1, 32))
        b = int(rng.integers(1, 32))
        if a == b:
            continue
        taps = (a, (-a) % 64, b, (-b) % 64)
        assert len(set(taps)) == 4 and 0 not in taps, "P tap degenerate"
        return ("ANDOR",) + taps
    raise RuntimeError("ANDOR-P draw-loop FAIL")


def _draw_andor_R(rng):
    """O131-verbatim random taps: 4 distinct taps from 64. Control."""
    return HS._draw_andor(rng)


TEMPLATES = {"H1": HS.TEMPLATES["H1"], "H3": HS.TEMPLATES["H3"]}


def selftest():
    rng = np.random.default_rng(0xB804)
    xs = rng.integers(0, 2**64, size=100, dtype=np.uint64)

    def srot(v, r):
        r %= 64
        return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF if r else v

    # (1) ANDOR bit-exact vs scalar, all three families.
    for fam, fn in (("Q", _draw_andor_Q), ("P", _draw_andor_P),
                    ("R", _draw_andor_R)):
        for _ in range(50):
            st = fn(rng)
            _, a, b, c, d = st
            got = apply_stage(xs, st)
            for xv, yv in zip(xs, got):
                xv = int(xv)
                e = xv ^ ((srot(xv, a) & srot(xv, b)) |
                          (srot(xv, c) & srot(xv, d)))
                assert int(yv) == e & 0xFFFFFFFFFFFFFFFF, \
                    "ANDOR-%s scalar mismatch" % fam
    # (2) Q draw-gate soundness, 500 draws.
    for _ in range(500):
        a, b, c, d = _draw_andor_Q(rng)[1:]
        assert 1 <= a < 16 <= b < 32 <= c < 48 <= d < 64
    # (3) P draw-gate soundness, 500 draws.
    for _ in range(500):
        t = _draw_andor_P(rng)[1:]
        assert len(set(t)) == 4 and 0 not in t
        a, ma, b, mb = t
        assert (a + ma) % 64 == 0 and (b + mb) % 64 == 0, "P pairing slip"
    # (4) R draw-gate soundness, 200 draws.
    for _ in range(200):
        assert len(set(_draw_andor_R(rng)[1:])) == 4
    # (5) inner gate smoke.
    r = eval_inner([_draw_andor_Q(np.random.default_rng(1)),
                    H._draw_muxd(np.random.default_rng(2)),
                    H._draw_muxd(np.random.default_rng(3))])
    assert set(r) >= {"lin_verdict", "diff_verdict"}, "inner gate shape"
    # (6) templates H1/H3 shape.
    for tn in ("H1", "H3"):
        t = TEMPLATES[tn](rng, _draw_andor_Q(rng))
        assert t[0][0] == "ANDOR" and all(s[0] == "MUXD" for s in t[1:]), \
            "%s shape" % tn
    print("SELFTEST PASS: ANDOR bit-exact (3 families x50 vs scalar); "
          "Q/P/R draw gates 1200/1200; H1/H3 shape; inner smoke OK",
          flush=True)


def calibrate():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print("CALIB %s: %s %s" % (name, "PASS" if cond else "FAIL", detail),
              flush=True)
        ok = ok and cond

    w1 = H.eval_calib_and1()
    check("1 and1/b33c z=3.3 EXACT", abs(w1 - 3.3) < 0.05,
          "maxworst|z|=%.1f" % w1)
    # CALIB-2a: positive control — MU5-324 must PASS ALL gates.
    mu5 = H.MU5_324_SCHED
    seq = {}
    V = np.arange(N, dtype=np.uint64)
    for key in INNER_KEYS:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in mu5:
            x = apply_stage(x, st)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    mi = screen_lin_diff(seq, verbose=False)
    mn, mw, wk, mf = eval_sched(mu5)
    check("2a MU5-324 inner+fisher PASS (positive control)",
          mi["lin_verdict"] == "PASS" and mi["diff_verdict"] == "PASS"
          and mn == 0,
          "inner lin=%s diff=%s fisher n_reject=%d maxworst|z|=%.1f"
          % (mi["lin_verdict"], mi["diff_verdict"], mn, mw))
    # CALIB-2b: negative control — linear-4 must be REJECTED.
    nrej2b, w2b, flp2b = H.eval_lin4(H.LIN4_SCHED)
    check("2b linear-4 fisher REJECT (negative control)", nrej2b > 0,
          "n_reject=%d maxworst|z|=%.1f min_fisher=%.1f"
          % (nrej2b, w2b, flp2b))
    # CALIB-5a: t6_b59_47 inner PASS.
    i5a = eval_inner(BASE_47)
    check("5a t6_b59_47 inner PASS", i5a["lin_verdict"] == "PASS"
          and i5a["diff_verdict"] == "PASS",
          "lin=%s diff=%s" % (i5a["lin_verdict"], i5a["diff_verdict"]))
    # CALIB-6 (NEW): seed-pinned O131-verbatim random-tap ANDOR H3 draw
    # must be inner-REJECTED — the gate sees the old failure mode.
    r6 = np.random.default_rng(0xA6D0)
    st6 = HS._draw_andor(r6)
    stages6 = HS.TEMPLATES["H3"](np.random.default_rng(0xA6D1), st6)
    i6 = eval_inner(stages6)
    check("6 O131-verbatim random ANDOR H3 inner-REJECT (draw-level "
          "negative)", i6["diff_verdict"] != "PASS",
          "taps=%s lin=%s diff=%s"
          % (st6[1:], i6["lin_verdict"], i6["diff_verdict"]))
    # CALIB-7: structured draw-gate soundness (already in selftest;
    # re-asserted here as a calibration gate).
    r7 = np.random.default_rng(0xB804)
    ok7 = True
    for _ in range(500):
        a, b, c, d = _draw_andor_Q(r7)[1:]
        if not (1 <= a < 16 <= b < 32 <= c < 48 <= d < 64):
            ok7 = False
    for _ in range(500):
        t = _draw_andor_P(r7)[1:]
        if not (len(set(t)) == 4 and 0 not in t):
            ok7 = False
    check("7 Q/P draw gates 1000/1000 sound", ok7, "")
    return ok


def _ser(st):
    return list(st)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        sys.exit(0 if calibrate() else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    assert sys.argv[1] == "andor_struct", sys.argv[1]
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB804
    keep_path = sys.argv[3] if len(sys.argv) > 3 else None
    rng = np.random.default_rng(seed)

    # Pilot plan (pre-registered, DESIGN.md section 1): 36 draws.
    plan = []
    plan += [("Q", "H1", _draw_andor_Q) for _ in range(8)]
    plan += [("Q", "H3", _draw_andor_Q) for _ in range(8)]
    plan += [("P", "H1", _draw_andor_P) for _ in range(6)]
    plan += [("P", "H3", _draw_andor_P) for _ in range(6)]
    plan += [("R", "H1", _draw_andor_R) for _ in range(4)]
    plan += [("R", "H3", _draw_andor_R) for _ in range(4)]

    hb_path = os.path.join(HERE, "heartbeat.txt")
    n_try = 0
    keep = []
    inner_kills = 0
    fisher_kills = 0
    minz_by = {}

    def heartbeat(msg):
        with open(hb_path, "w") as f:
            f.write("%s draw=%d/%d %s\n" % (
                __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%SZ"), n_try, len(plan), msg))

    heartbeat("start")
    for fam, tname, hfn in plan:
        h = hfn(rng)
        stages = TEMPLATES[tname](rng, h)
        n_try += 1
        # PRIMARY triage first (pre-registered order).
        inner = eval_inner(stages)
        ilin, idiff = inner["lin_verdict"], inner["diff_verdict"]
        inner_pass = (ilin == "PASS" and idiff == "PASS")
        nrej, wz, wkey, flp = eval_sched(stages)
        key = "%s/%s" % (fam, tname)
        minz_by[key] = min(minz_by.get(key, float("inf")), wz)
        if inner_pass and nrej == 0:
            flag = "KEEP"
        elif not inner_pass:
            flag = "inner-kill"
            inner_kills += 1
        else:
            flag = "fisher-kill"
            fisher_kills += 1
        print("try %3d %s/%s ANDOR%-28s inner lin=%-4s diff=%-4s fisher "
              "n_reject=%d maxworst|z|=%8.1f min_fisher=%7.1f worstkey=%#x "
              "%s" % (n_try - 1, fam, tname, str(h[1:]), ilin, idiff, nrej,
                      wz, flp, wkey, flag), flush=True)
        if flag == "KEEP":
            keep.append((wz, stages, fam, tname, ilin, idiff, nrej, flp))
            if keep_path:
                rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                       "stages": [_ser(s) for s in stages],
                       "form": "andor_struct", "seed": seed, "family": fam,
                       "template": tname, "inner_lin": ilin,
                       "inner_diff": idiff}
                with open(keep_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
        if n_try % 6 == 0:
            heartbeat("keeps=%d inner_kills=%d fisher_kills=%d"
                      % (len(keep), inner_kills, fisher_kills))
    heartbeat("done")
    print("=== andor_struct: %d/%d KEEP (inner_kills=%d fisher_kills=%d) "
          "(seed=%#x) ===" % (len(keep), n_try, inner_kills, fisher_kills,
                              seed), flush=True)
    for k in sorted(minz_by):
        print("    minz[%s]=%.1f" % (k, minz_by[k]), flush=True)
    if inner_kills + fisher_kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
