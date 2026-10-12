#!/usr/bin/env python3
"""Track-2 andor_form pilot: ANDOR form WITH LINEAR BYPASS TAP (O141 re-test).

Thesis (DESIGN.md pre-registered): O141 killed ANDOR+structured taps 0/36
at the inner gate and exonerated tap geometry AND the Boolean function f.
The re-test trigger names a FORM change. Three families:

  B = ANDORB: y = x ^ f(taps) ^ x_e, f=(p&q)|(r&s) verbatim, e a DISTINCT
      fifth tap. Replicates MUXD's guaranteed-diffusion skeleton
      (feedthrough + bypass) with f's stronger per-bit function.
  X = ANDORX: y = x ^ g2(taps) ^ x_e, g2 = f ^ NOR4(p,q,r,s): BALANCED
      (wt 8), uniform 1/2 differential response, E=2.0; NL 5->4 tradeoff.
  Y = ANDORY: y = x ^ g4(taps) ^ x_e, g4 = (p&q)^(r&s)^p: BENT (NL 6,
      max|W| 4 optimal), uniform 1/2, E=2.0; weight 6 (bias -2/16).

Taps: (a,b,c,d) quadrant-spread Q-style (O141 best case, held fixed);
e drawn FREE from [1,64)\\{a,b,c,d} (least-tuned). Frame MU5, H1/H3.
Gates: inner-DIFF-SEQ PRIMARY, fisher triage second. KEEP iff inner lin
PASS and diff PASS and fisher n_reject == 0.

Usage: t8_andor_form_screen.py andor_form <seed> [keep_jsonl]
       t8_andor_form_screen.py calibrate | selftest
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
import t8_hetstage_screen as HS  # noqa: E402  (MUXD verbatim, templates)
import t8_het8_screen as H  # noqa: E402
from lin_diff import diff_cell_logps, holm_reject, screen_lin_diff  # noqa: E402
from screen_lib import KEYS, N  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
INNER_KEYS = S2.INNER_KEYS
rotl = H.rotl


def apply_stage(x, st):
    """New-form stages; everything else delegates to HS (MUXD verbatim)."""
    tag = st[0]
    if tag == "ANDORB":
        _, a, b, c, d, e = st
        return (x ^ ((rotl(x, a) & rotl(x, b)) |
                     (rotl(x, c) & rotl(x, d))) ^ rotl(x, e)) & M64
    if tag == "ANDORX":
        _, a, b, c, d, e = st
        p, q, r, s = rotl(x, a), rotl(x, b), rotl(x, c), rotl(x, d)
        g2 = (((p & q) | (r & s)) ^ ((~(p | q | r | s)) & M64)) & M64
        return (x ^ g2 ^ rotl(x, e)) & M64
    if tag == "ANDORY":
        _, a, b, c, d, e = st
        p, q, r, s = rotl(x, a), rotl(x, b), rotl(x, c), rotl(x, d)
        g4 = ((p & q) ^ (r & s) ^ p) & M64
        return (x ^ g4 ^ rotl(x, e)) & M64
    return HS.apply_stage(x, st)


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

def _draw_5tap(rng):
    """Quadrant-spread (a,b,c,d) + FREE bypass tap e.

    a in [1,16), b in [16,32), c in [32,48), d in [48,64) (O141 Q-style
    best case, held fixed); e in [1,64) \\ {a,b,c,d} (least-tuned choice
    for the bypass position — a structured e would confound the form
    question with a new geometry thesis).
    """
    a = int(rng.integers(1, 16))
    b = int(rng.integers(16, 32))
    c = int(rng.integers(32, 48))
    d = int(rng.integers(48, 64))
    assert 1 <= a < 16 <= b < 32 <= c < 48 <= d < 64, "quadrant slip"
    assert len({a, b, c, d}) == 4, "tap collision"
    for _ in range(10000):
        e = int(rng.integers(1, 64))
        if e not in (a, b, c, d):
            return (a, b, c, d, e)
    raise RuntimeError("5-tap e draw-loop FAIL")


TEMPLATES = {"H1": HS.TEMPLATES["H1"], "H3": HS.TEMPLATES["H3"]}


def selftest():
    rng = np.random.default_rng(0xB805)
    xs = rng.integers(0, 2**64, size=100, dtype=np.uint64)

    def srot(v, r):
        r %= 64
        return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF if r else v

    def scalar(tag, xv, a, b, c, d, e):
        p, q, r, s = srot(xv, a), srot(xv, b), srot(xv, c), srot(xv, d)
        f = ((p & q) | (r & s)) & 0xFFFFFFFFFFFFFFFF
        if tag == "ANDORB":
            g = f
        elif tag == "ANDORX":
            g = (f ^ ((~(p | q | r | s)) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF
        elif tag == "ANDORY":
            g = (((p & q) ^ (r & s) ^ p)) & 0xFFFFFFFFFFFFFFFF
        else:
            raise AssertionError(tag)
        return (xv ^ g ^ srot(xv, e)) & 0xFFFFFFFFFFFFFFFF

    # (1) New forms bit-exact vs scalar, 50 draws each.
    for tag in ("ANDORB", "ANDORX", "ANDORY"):
        for _ in range(50):
            a, b, c, d, e = _draw_5tap(rng)
            st = (tag, a, b, c, d, e)
            got = apply_stage(xs, st)
            for xv, yv in zip(xs, got):
                assert int(yv) == scalar(tag, int(xv), a, b, c, d, e), \
                    "%s scalar mismatch" % tag
    # (2) Draw-gate soundness, 500 draws.
    for _ in range(500):
        a, b, c, d, e = _draw_5tap(rng)
        assert 1 <= a < 16 <= b < 32 <= c < 48 <= d < 64
        assert 1 <= e < 64 and e not in (a, b, c, d)
    # (3) inner gate smoke.
    r = eval_inner([("ANDORB",) + _draw_5tap(np.random.default_rng(1)),
                    H._draw_muxd(np.random.default_rng(2)),
                    H._draw_muxd(np.random.default_rng(3))])
    assert set(r) >= {"lin_verdict", "diff_verdict"}, "inner gate shape"
    # (4) templates H1/H3 shape.
    for tn in ("H1", "H3"):
        t = TEMPLATES[tn](rng, ("ANDORB",) + _draw_5tap(rng))
        assert t[0][0] == "ANDORB" and all(s[0] == "MUXD" for s in t[1:]), \
            "%s shape" % tn
    print("SELFTEST PASS: ANDORB/X/Y bit-exact (3x50 vs scalar); "
          "5-tap draw gates 500/500; H1/H3 shape; inner smoke OK",
          flush=True)


def _bool_props():
    """Independent truth-table properties of f, g2, g4 (CALIB-9)."""
    def bits4(i):
        return ((i >> 3) & 1, (i >> 2) & 1, (i >> 1) & 1, i & 1)

    def props(fn):
        vals = [fn(*bits4(i)) for i in range(16)]
        wt = sum(vals)
        sp = [1 if v == 0 else -1 for v in vals]
        for b in range(4):
            for i in range(16):
                if not (i >> b) & 1:
                    u, v = sp[i], sp[i + (1 << b)]
                    sp[i], sp[i + (1 << b)] = u + v, u - v
        maxw = max(abs(v) for v in sp)
        fps = []
        for var in range(4):
            c = sum(1 for i in range(16)
                    if fn(*bits4(i)) != fn(*bits4(i ^ (1 << (3 - var)))))
            fps.append(c / 16)
        return wt, 8 - maxw // 2, maxw, fps

    f = lambda p, q, r, s: (p & q) | (r & s)
    g2 = lambda p, q, r, s: (((p & q) | (r & s)) ^
                             (1 - (p | q | r | s)))
    g4 = lambda p, q, r, s: ((p & q) ^ (r & s) ^ p)
    return {"f": props(f), "g2": props(g2), "g4": props(g4)}


def _avalanche():
    """CALIB-8 mechanism: single-stage single-bit-delta avalanche.

    Fixed taps (3,20,40,55,7), fixed key, 4096 xs. Returns dict of mean
    flipped bits per form + bypass-determinism check for B.
    """
    a, b, c, d, e = 3, 20, 40, 55, 7
    key = 0x9E3779B97F4A7C15
    rng = np.random.default_rng(0xB805)
    xs = rng.integers(0, 2**64, size=4096, dtype=np.uint64)
    K = np.uint64(key)
    forms = {
        "old": lambda x: HS.apply_stage(x, ("ANDOR", a, b, c, d)),
        "B": lambda x: apply_stage(x, ("ANDORB", a, b, c, d, e)),
        "X": lambda x: apply_stage(x, ("ANDORX", a, b, c, d, e)),
        "Y": lambda x: apply_stage(x, ("ANDORY", a, b, c, d, e)),
        "MUXD": lambda x: HS.apply_stage(x, ("MUXD", 17, 22, 10, 55)),
    }
    means = {}
    det_ok = True
    for name, fn in forms.items():
        base = fn(xs ^ K)
        fl = []
        for j in range(64):
            dj = np.uint64(1) << np.uint64(j)
            out = fn((xs ^ K) ^ dj)
            diff = out ^ base
            fl.append(float(np.mean(
                [bin(int(v)).count("1") for v in diff])))
            if name == "B":
                # bypass determinism: bit (j+e) flips on ALL xs
                # (rotl(x,e)[i] = x[(i-e) mod 64], so input bit j lands
                # in output bit j+e; verified empirically).
                sh = np.uint64((j + e) % 64)
                if not bool(np.all(((diff >> sh) & np.uint64(1)) == 1)):
                    det_ok = False
        means[name] = float(np.mean(fl))
    return means, det_ok


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
    # CALIB-6: seed-pinned O131-verbatim random-tap ANDOR H3 draw must be
    # inner-REJECTED — the gate sees the old failure mode.
    r6 = np.random.default_rng(0xA6D0)
    st6 = HS._draw_andor(r6)
    stages6 = HS.TEMPLATES["H3"](np.random.default_rng(0xA6D1), st6)
    i6 = eval_inner(stages6)
    check("6 O131-verbatim random ANDOR H3 inner-REJECT (draw-level "
          "negative)", i6["diff_verdict"] != "PASS",
          "taps=%s lin=%s diff=%s"
          % (st6[1:], i6["lin_verdict"], i6["diff_verdict"]))
    # CALIB-7: 5-tap draw-gate soundness.
    r7 = np.random.default_rng(0xB805)
    ok7 = True
    for _ in range(500):
        a, b, c, d, e = _draw_5tap(r7)
        if not (1 <= a < 16 <= b < 32 <= c < 48 <= d < 64
                and 1 <= e < 64 and e not in (a, b, c, d)):
            ok7 = False
    check("7 5-tap draw gates 500/500 sound", ok7, "")
    # CALIB-8: mechanism — avalanche means match analysis; B bypass
    # determinism exact.
    means, det_ok = _avalanche()
    exp = {"old": 2.50, "B": 3.50, "X": 4.00, "Y": 4.00, "MUXD": 3.50}
    ok8 = det_ok and all(abs(means[k] - exp[k]) < 0.10 for k in exp)
    check("8 avalanche mechanism (means match + B bypass deterministic)",
          ok8, "means=%s det=%s"
          % (",".join("%s=%.2f" % (k, means[k]) for k in
                      ("old", "B", "X", "Y", "MUXD")), det_ok))
    # CALIB-9: Boolean property table (independent truth tables).
    bp = _bool_props()
    ok9 = (bp["f"][:3] == (7, 5, 6)
           and all(abs(p - 0.375) < 1e-9 for p in bp["f"][3])
           and bp["g2"][:3] == (8, 4, 8)
           and all(abs(p - 0.5) < 1e-9 for p in bp["g2"][3])
           and bp["g4"][:3] == (6, 6, 4)
           and all(abs(p - 0.5) < 1e-9 for p in bp["g4"][3]))
    check("9 f/g2/g4 truth-table properties", ok9, str(
        {k: (v[0], v[1], v[2]) for k, v in bp.items()}))
    return ok


def _ser(st):
    return list(st)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        sys.exit(0 if calibrate() else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    assert sys.argv[1] == "andor_form", sys.argv[1]
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB805
    keep_path = sys.argv[3] if len(sys.argv) > 3 else None
    rng = np.random.default_rng(seed)

    # Pilot plan (pre-registered, DESIGN.md section 1): 36 draws.
    plan = []
    plan += [("B", "H3", "ANDORB") for _ in range(10)]
    plan += [("B", "H1", "ANDORB") for _ in range(6)]
    plan += [("X", "H3", "ANDORX") for _ in range(6)]
    plan += [("X", "H1", "ANDORX") for _ in range(4)]
    plan += [("Y", "H3", "ANDORY") for _ in range(6)]
    plan += [("Y", "H1", "ANDORY") for _ in range(4)]

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
    for fam, tname, tag in plan:
        taps = _draw_5tap(rng)
        h = (tag,) + taps
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
        print("try %3d %s/%s %-7s%-28s inner lin=%-4s diff=%-4s fisher "
              "n_reject=%d maxworst|z|=%8.1f min_fisher=%7.1f worstkey=%#x "
              "%s" % (n_try - 1, fam, tname, tag, str(taps), ilin, idiff,
                      nrej, wz, flp, wkey, flag), flush=True)
        if flag == "KEEP":
            keep.append((wz, stages, fam, tname, ilin, idiff, nrej, flp))
            if keep_path:
                rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                       "stages": [_ser(s) for s in stages],
                       "form": "andor_form", "seed": seed, "family": fam,
                       "template": tname, "inner_lin": ilin,
                       "inner_diff": idiff}
                with open(keep_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
        if n_try % 6 == 0:
            heartbeat("keeps=%d inner_kills=%d fisher_kills=%d"
                      % (len(keep), inner_kills, fisher_kills))
    heartbeat("done")
    print("=== andor_form: %d/%d KEEP (inner_kills=%d fisher_kills=%d) "
          "(seed=%#x) ===" % (len(keep), n_try, inner_kills, fisher_kills,
                              seed), flush=True)
    for k in sorted(minz_by):
        print("    minz[%s]=%.1f" % (k, minz_by[k]), flush=True)
    if inner_kills + fisher_kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
