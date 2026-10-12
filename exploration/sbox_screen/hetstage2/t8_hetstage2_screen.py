#!/usr/bin/env python3
"""Track-2 hetstage2 pilot: dense GF-mul-by-constant pool + [CIRC2, MUXD x4],
inner-DIFF-SEQ as the PRIMARY triage (batch-62 lesson).

Types: D=dense GF-mul-by-constant (stratified pc 8..40 + sparse controls),
       R5=[CIRC2, MUXD x4] size-axis xorh5-recipe challenger.
Templates H1/H2/H3 (hetstage verbatim) + T5=[CIRC2, MUXD x4].

Gate order (pre-registered, DESIGN.md): inner screen_lin_diff FIRST on every
draw (PRIMARY triage); fisher triage second (diagnostic continuity with O131
dose-response). KEEP iff inner lin==PASS and diff==PASS and fisher n_reject==0.

Usage: t8_hetstage2_screen.py hetstage2 <seed> [keep_jsonl]
       t8_hetstage2_screen.py calibrate | selftest
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/hetstage2")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/hetstage")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
import t8_het8_screen as H
import t8_hetstage_screen as HS
from stage_cost import gf_mat  # noqa: E402  (mirror of the synth emitter)
from lin_diff import diff_cell_logps, holm_reject, screen_lin_diff  # noqa: E402
from screen_lib import KEYS, N  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
INNER_KEYS = [0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA]
rotl = H.rotl

# t6_b59_47: single proven-clean base, verbatim from
# new_constructions/batch62/t6_b62_screen.py.
BASE_47 = [("MUXD", 17, 22, 10, 55), ("MUXD", 63, 62, 49, 57),
           ("MUXD", 29, 39, 35, 6), ("MUXD", 9, 4, 44, 36),
           ("MUXD", 5, 54, 31, 34)]

_GF_MATS = {}


def gf_masks(C):
    if C not in _GF_MATS:
        _GF_MATS[C] = tuple(gf_mat(C))
    return _GF_MATS[C]


def _parity(v):
    v = v ^ (v >> np.uint64(32))
    v = v ^ (v >> np.uint64(16))
    v = v ^ (v >> np.uint64(8))
    v = v ^ (v >> np.uint64(4))
    v = v ^ (v >> np.uint64(2))
    v = v ^ (v >> np.uint64(1))
    return v & np.uint64(1)


def apply_stage(x, st):
    tag = st[0]
    if tag == "CIRC2":
        _, a, b = st
        return (x ^ rotl(x, a) ^ rotl(x, b)) & M64
    if tag == "GFMUL":
        _, C = st
        y = np.zeros(x.shape, dtype=np.uint64)
        for j, m in enumerate(gf_masks(C)):
            y |= _parity(x & np.uint64(m)) << np.uint64(j)
        return y
    return H.apply_stage(x, st)  # MUXD verbatim


def eval_inner(stages):
    """PRIMARY triage: screen_lin_diff on 2^17... N=2^18 sequential outputs,
    INNER_KEYS. Verbatim instrument (hetstage/batch-62)."""
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
    """Fisher triage, gate rule verbatim: KEEP iff n_reject == 0."""
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

def _gf2_rank(rows):
    rows = [int(r) for r in rows]
    rank = 0
    for k in range(63, -1, -1):
        b = 1 << k
        piv = -1
        for i in range(rank, 64):
            if rows[i] & b:
                piv = i
                break
        if piv < 0:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        pr = rows[rank]
        for i in range(64):
            if i != rank and (rows[i] & b):
                rows[i] ^= pr
        rank += 1
    return rank


def _circ_rows(taps):
    rows = []
    for j in range(64):
        m = 0
        for t in taps:
            m |= 1 << ((j - t) % 64)
        rows.append(m)
    return rows


def _circ2_minw2(a, b):
    t = {0, a % 64, b % 64}
    m = 64
    for d in range(1, 64):
        u = {d % 64, (a + d) % 64, (b + d) % 64}
        w = len(t ^ u)
        if w < m:
            m = w
    return m


def _draw_circ2(rng):
    for _ in range(10000):
        a, b = (int(x) for x in rng.choice(64, size=2, replace=False))
        if a == 0 or b == 0:
            continue
        if _gf2_rank(_circ_rows([0, a, b])) != 64:
            continue
        if _circ2_minw2(a, b) < 4:
            continue
        return ("CIRC2", a, b)
    raise RuntimeError("CIRC2 draw-loop FAIL")


DENSE_PCS = [8, 10, 12, 16, 20, 24, 32, 40]
# GHA pool widening (2026-10-12): intermediate pcs for the dense gradient.
# Added post-pilot; the pilot's draws hardcode pcs per draw, so its RNG
# stream and artifacts are unaffected.
POOL_PCS = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40]


def _draw_gfmul(rng, pc):
    assert pc in DENSE_PCS or pc in POOL_PCS or pc in (3, 5, 7), \
        "pc outside design set"
    for _ in range(10000):
        bits = rng.choice(64, size=pc, replace=False)
        C = 0
        for b_ in bits:
            C |= 1 << int(b_)
        if C.bit_length() - 1 < 8 or C == 1:
            continue
        return ("GFMUL", C)
    raise RuntimeError("GFMUL draw-loop FAIL")


def _gf_weight(C):
    return sum(bin(int(m)).count("1") for m in gf_masks(C))


# ---------------- templates ----------------
def _T_H1(rng, h):
    return [h, H._draw_muxd(rng), H._draw_muxd(rng)]


def _T_H2(rng, h):
    return [H._draw_muxd(rng), h, H._draw_muxd(rng)]


def _T_H3(rng, h):
    return [h, H._draw_muxd(rng), H._draw_muxd(rng), H._draw_muxd(rng)]


def _T_R5(rng, h):
    return [h, H._draw_muxd(rng), H._draw_muxd(rng),
            H._draw_muxd(rng), H._draw_muxd(rng)]


TEMPLATES = {"H1": _T_H1, "H2": _T_H2, "H3": _T_H3, "R5": _T_R5}


def _stage_tag(st):
    if st[0] == "GFMUL":
        pc = bin(st[1]).count("1")
        return "GFMUL(pc=%d,wt=%d)" % (pc, _gf_weight(st[1]))
    return st[0]


def selftest():
    rng = np.random.default_rng(0xB803)
    # (1) CIRC2 bit-exact vs scalar.
    xs = rng.integers(0, 2**64, size=100, dtype=np.uint64)

    def srot(v, r):
        r %= 64
        return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF if r else v

    for _ in range(20):
        st = _draw_circ2(rng)
        got = apply_stage(xs, st)
        for x, y in zip(xs, got):
            x = int(x)
            e = x ^ srot(x, st[1]) ^ srot(x, st[2])
            assert int(y) == e, "CIRC2 scalar mismatch"
    # (2) GFMUL: matrix == INDEPENDENT carryless bit-loop reference, 30
    # random C. This is the transpose-class check (hetstage caught one).
    P = (1 << 64) | (1 << 4) | (1 << 3) | (1 << 1) | 1

    def gf_ref(x, C):
        prod = 0
        b = 0
        cc = C
        while cc:
            if cc & 1:
                prod ^= x << b
            cc >>= 1
            b += 1
        for i in range(prod.bit_length() - 1, 63, -1):
            if (prod >> i) & 1:
                prod ^= P << (i - 64)
        return prod & ((1 << 64) - 1)

    for i in range(30):
        C = int(rng.integers(2, 2**64, dtype=np.uint64))
        x = np.array([int(v) for v in rng.integers(0, 2**64, size=8,
                                                   dtype=np.uint64)],
                     dtype=np.uint64)
        got = apply_stage(x, ("GFMUL", C))
        for xv, yv in zip(x, got):
            assert int(yv) == gf_ref(int(xv), C), \
                "GFMUL ref mismatch (transpose-class), C=%#x" % C
        if i == 0:
            # known-answer: 2^63 x 2^63 reduction per P.
            e = gf_ref(1 << 63, 1 << 63)
            assert int(apply_stage(np.array([1 << 63], dtype=np.uint64),
                                   ("GFMUL", 1 << 63))[0]) == e
    x = np.array([int(v) for v in rng.integers(0, 2**64, size=64,
                                               dtype=np.uint64)],
                 dtype=np.uint64)
    assert (apply_stage(x, ("GFMUL", 1)) == x).all(), "gf(x,1)!=x"
    assert (apply_stage(x, ("GFMUL", 0)) == 0).all(), "gf(x,0)!=0"
    C = int(rng.integers(2, 2**64, dtype=np.uint64))
    y = np.array([int(v) for v in rng.integers(0, 2**64, size=64,
                                               dtype=np.uint64)],
                 dtype=np.uint64)
    assert (apply_stage(x ^ y, ("GFMUL", C)) ==
            (apply_stage(x, ("GFMUL", C)) ^
             apply_stage(y, ("GFMUL", C)))).all(), "gf distributivity"
    # (3) draw-gate soundness, 200 dense draws.
    for _ in range(200):
        for pc in DENSE_PCS + [3, 5, 7]:
            sg = _draw_gfmul(rng, pc)
            assert bin(sg[1]).count("1") == pc, "pc slip"
            assert sg[1].bit_length() - 1 >= 8, "deg slip"
        s2 = _draw_circ2(rng)
        assert _gf2_rank(_circ_rows([0, s2[1], s2[2]])) == 64
        assert _circ2_minw2(s2[1], s2[2]) >= 4
    # (4) R5 template shape.
    t5 = TEMPLATES["R5"](rng, _draw_circ2(rng))
    assert len(t5) == 5 and t5[0][0] == "CIRC2" and \
        all(s[0] == "MUXD" for s in t5[1:]), "R5 shape"
    # (5) inner gate smoke.
    r = eval_inner([("CIRC2", 13, 37), H._draw_muxd(
        np.random.default_rng(1)), H._draw_muxd(np.random.default_rng(2))])
    assert set(r) >= {"lin_verdict", "diff_verdict"}, "inner gate shape"
    print("SELFTEST PASS: CIRC2/GFMUL bit-exact (30 random C vs independent "
          "carryless ref); draw gates 2200/2200; R5 shape; inner smoke OK",
          flush=True)


def _replay_hetstage_tries():
    """Replay the hetstage pilot RNG verbatim (seed 0xB802); return the stage
    specs for tries 53 (dense C, H1) and 78 (sparse pc=5, H3)."""
    rng = np.random.default_rng(0xB802)
    a1 = lambda r: HS._draw_circ1(r)  # noqa: E731
    a2 = lambda r: HS._draw_circ2(r)  # noqa: E731
    pcs = [3, 5, 7]
    pi = [0]

    def b_sparse(r, _pi=pi):
        pc = pcs[_pi[0] % 3]
        _pi[0] += 1
        return HS._draw_gfmul(r, pc)

    def b_dense(r):
        return HS._draw_gfmul(r, int(r.integers(24, 41)))

    plan = []
    plan += [("A", "H1", a1, 7), ("A", "H1", a2, 7), ("A", "H2", a1, 7),
             ("A", "H2", a2, 6), ("A", "H3", a1, 6), ("A", "H3", a2, 7)]
    plan += [("B", "H1", b_sparse, 10), ("B", "H1", b_dense, 4),
             ("B", "H2", b_sparse, 13), ("B", "H3", b_sparse, 13)]
    got = {}
    n = 0
    for _, tname, hfn, ndraw in plan:
        for _ in range(ndraw):
            h = hfn(rng)
            stages = HS.TEMPLATES[tname](rng, h)
            if n in (53, 78):
                got[n] = stages
            n += 1
    assert got[53][0][0] == "GFMUL" and bin(got[53][0][1]).count("1") >= 24, \
        "try53 not the dense draw"
    assert got[78][0][0] == "GFMUL" and bin(got[78][0][1]).count("1") == 5, \
        "try78 not the sparse pc=5 draw"
    return got


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
    nrej2a, w2a, _, flp2a = H.eval_sched(H.MU5_324_SCHED)
    check("2a mux/MU5-324(5st) fisher KEEP", nrej2a == 0,
          "n_reject=%d maxworst|z|=%.2f min_fisher=%.1f"
          % (nrej2a, w2a, flp2a))
    nrej2b, w2b, flp2b = H.eval_lin4(H.LIN4_SCHED)
    check("2b linear-4 fisher REJECT", nrej2b > 0,
          "n_reject=%d maxworst|z|=%.1f min_fisher=%.1f"
          % (nrej2b, w2b, flp2b))
    rng = np.random.default_rng(0xB803)
    ok3 = True
    for _ in range(200):
        for pc in DENSE_PCS + [3, 5, 7]:
            sg = _draw_gfmul(rng, pc)
            if bin(sg[1]).count("1") != pc or sg[1].bit_length() - 1 < 8:
                ok3 = False
        s2 = _draw_circ2(rng)
        if _gf2_rank(_circ_rows([0, s2[1], s2[2]])) != 64 or \
                _circ2_minw2(s2[1], s2[2]) < 4:
            ok3 = False
    check("3 draw gates 2200/2200 sound", ok3, "")
    # CALIB-4: cost flow on-scale (MUXD anchor) + new GF(pc=12) anchor.
    import subprocess
    r = subprocess.run(
        ["python3", "../hetstage/stage_cost.py"], capture_output=True,
        text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    ok4 = (r.returncode == 0 and "muxd" in r.stdout)
    check("4 stage_cost.py flow runs, muxd anchor on-scale", ok4,
          "rc=%d" % r.returncode)
    rng4 = np.random.default_rng(0xB803)
    c12 = _draw_gfmul(rng4, 12)
    w12 = _gf_weight(c12[1])
    check("4b GF(pc=12) matrix weight in [1200,1600]", 1200 <= w12 <= 1600,
          "wt=%d" % w12)
    # CALIB-5a: positive — t6_b59_47 inner PASS.
    i5a = eval_inner(BASE_47)
    check("5a t6_b59_47 inner PASS", i5a["lin_verdict"] == "PASS"
          and i5a["diff_verdict"] == "PASS",
          "lin=%s diff=%s" % (i5a["lin_verdict"], i5a["diff_verdict"]))
    # CALIB-5b: negative — hetstage tries 53/78 replay → inner diff != PASS.
    rep = _replay_hetstage_tries()
    i53 = eval_inner(rep[53])
    i78 = eval_inner(rep[78])
    check("5b hetstage try53 replay inner diff!=PASS",
          i53["diff_verdict"] != "PASS",
          "lin=%s diff=%s" % (i53["lin_verdict"], i53["diff_verdict"]))
    check("5c hetstage try78 replay inner diff!=PASS",
          i78["diff_verdict"] != "PASS",
          "lin=%s diff=%s" % (i78["lin_verdict"], i78["diff_verdict"]))
    # CALIB-5d: gate order — inner is evaluated before fisher (log order).
    print("CALIB 5d: gate order = inner FIRST (primary triage), fisher "
          "second; KEEP requires inner-PASS AND fisher-PASS — pre-registered",
          flush=True)
    return ok


def _ser(st):
    if st[0] == "GFMUL":
        return ["GFMUL", hex(st[1])]
    return list(st)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        sys.exit(0 if calibrate() else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    assert sys.argv[1] == "hetstage2", sys.argv[1]
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB803
    keep_path = sys.argv[3] if len(sys.argv) > 3 else None
    rng = np.random.default_rng(seed)

    # Pilot plan: (type, template, hetero-draw-fn, pcs list or None, label)
    plan = []
    # Type D dense: H1/H3 stratified 8..40, H2 position control 12..32
    for tname, pcs in [("H1", DENSE_PCS), ("H3", DENSE_PCS),
                       ("H2", [12, 16, 24, 32])]:
        for pc in pcs:
            plan.append(("D", tname, ("GFMUL", pc), "GFM-dense"))
    # Sparse controls (O131 gradient anchors): pc 3/5/7/5 on H1/H3/H1/H3
    for tname, pc in [("H1", 3), ("H3", 5), ("H1", 7), ("H3", 5)]:
        plan.append(("S", tname, ("GFMUL", pc), "GFM-sparse"))
    # Type R5: [CIRC2, MUXD x4], 12 draws
    plan += [("R5", "R5", "CIRC2", "R5") for _ in range(12)]

    hb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "heartbeat.txt")
    n_try = 0
    keep = []
    inner_kills = 0
    fisher_kills = 0
    minz_by = {}
    minw_by = {}

    def heartbeat(msg):
        with open(hb_path, "w") as f:
            f.write("%s draw=%d/%d %s\n" % (
                __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%SZ"), n_try, len(plan), msg))

    heartbeat("start")
    for ttype, tname, hspec, label in plan:
        if hspec == "CIRC2":
            h = _draw_circ2(rng)
        else:
            _, pc = hspec
            h = _draw_gfmul(rng, pc)
        stages = TEMPLATES[tname](rng, h)
        n_try += 1
        # PRIMARY triage first (pre-registered order).
        inner = eval_inner(stages)
        ilin, idiff = inner["lin_verdict"], inner["diff_verdict"]
        inner_pass = (ilin == "PASS" and idiff == "PASS")
        nrej, wz, wkey, flp = eval_sched(stages)
        minz_by[label] = min(minz_by.get(label, float("inf")), wz)
        wtag = _stage_tag(h)
        if h[0] == "GFMUL":
            minw_by[label] = min(minw_by.get(label, float("inf")),
                                 _gf_weight(h[1]))
        if inner_pass and nrej == 0:
            flag = "KEEP"
        elif not inner_pass:
            flag = "inner-kill"
            inner_kills += 1
        else:
            flag = "fisher-kill"
            fisher_kills += 1
        print("try %3d %s/%s %-10s inner lin=%-4s diff=%-4s fisher "
              "n_reject=%d maxworst|z|=%8.1f min_fisher=%7.1f worstkey=%#x "
              "%s  %s" % (n_try - 1, ttype, tname, label, ilin, idiff, nrej,
                          wz, flp, wkey, flag,
                          [wtag if s[0] in ("CIRC2", "GFMUL") else s[0]
                           for s in stages]), flush=True)
        if flag == "KEEP":
            keep.append((wz, stages, ttype, tname, label, ilin, idiff,
                         nrej, flp))
            if keep_path:
                rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                       "stages": [_ser(s) for s in stages],
                       "form": "hetstage2", "seed": seed, "type": ttype,
                       "template": tname, "label": label,
                       "inner_lin": ilin, "inner_diff": idiff}
                with open(keep_path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
        if n_try % 6 == 0:
            heartbeat("keeps=%d inner_kills=%d fisher_kills=%d"
                      % (len(keep), inner_kills, fisher_kills))
    heartbeat("done")
    print("=== hetstage2: %d/%d KEEP (inner_kills=%d fisher_kills=%d) "
          "(seed=%#x) ===" % (len(keep), n_try, inner_kills, fisher_kills,
                              seed), flush=True)
    for label in sorted(minz_by):
        extra = (" minwt=%d" % minw_by[label]) if label in minw_by else ""
        print("    minz[%s]=%.1f%s" % (label, minz_by[label], extra),
              flush=True)
    if inner_kills + fisher_kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
