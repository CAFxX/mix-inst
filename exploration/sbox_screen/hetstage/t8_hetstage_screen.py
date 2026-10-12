#!/usr/bin/env python3
"""Track-2 hetstage pilot: cheap non-S-box hetero stage pool in the MU5 frame.

Types: A=linear circulants (CIRC1 2-term control / CIRC2 3-term),
       B=GF-mul-by-constant (sparse C, pc in {3,5,7} + dense control arm),
       C=AND-OR mixes. Templates H1/H2/H3 (DESIGN.md, pre-registered).

Gates: fisher verbatim (KEYS10, N=2^18, diff_cell_logps, holm_reject
ALPHA=0.01 -> KEEP iff n_reject==0); inner screen_lin_diff on keeps
(batch-62 calibration: INNER_KEYS full-range SEQ).

Usage: t8_hetstage_screen.py hetstage <seed> [keep_jsonl]
       t8_hetstage_screen.py calibrate | selftest
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/hetstage")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
import t8_het8_screen as H
from stage_cost import gf_mat  # noqa: E402  (mirror of the synth emitter)
from lin_diff import diff_cell_logps, holm_reject, screen_lin_diff  # noqa: E402
from screen_lib import KEYS, N  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
INNER_KEYS = [0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA]
rotl = H.rotl

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
    if tag == "CIRC1":
        _, a = st
        return (x ^ rotl(x, a)) & M64
    if tag == "CIRC2":
        _, a, b = st
        return (x ^ rotl(x, a) ^ rotl(x, b)) & M64
    if tag == "GFMUL":
        _, C = st
        y = np.zeros(x.shape, dtype=np.uint64)
        for j, m in enumerate(gf_masks(C)):
            y |= _parity(x & np.uint64(m)) << np.uint64(j)
        return y
    if tag == "ANDOR":
        _, a, b, c, d = st
        return (x ^ ((rotl(x, a) & rotl(x, b)) |
                     (rotl(x, c) & rotl(x, d)))) & M64
    return H.apply_stage(x, st)  # MUXD / XOR4 verbatim


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


def eval_inner(stages):
    seq = {}
    V = np.arange(N, dtype=np.uint64)
    for key in INNER_KEYS:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return screen_lin_diff(seq, verbose=False)


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


def _draw_circ1(rng):
    a = int(rng.integers(1, 64))
    if a % 2 == 0:
        a = (a + 1) % 64 or 1  # force odd -> rank exactly 63 (proven)
    st = ("CIRC1", a)
    assert _gf2_rank(_circ_rows([0, a])) == 63, "CIRC1 rank slip"
    return st


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


def _draw_gfmul(rng, pc):
    for _ in range(10000):
        bits = rng.choice(64, size=pc, replace=False)
        C = 0
        for b_ in bits:
            C |= 1 << int(b_)
        if C.bit_length() - 1 < 8 or C == 1:
            continue
        return ("GFMUL", C)
    raise RuntimeError("GFMUL draw-loop FAIL")


def _draw_andor(rng):
    t = rng.choice(64, size=4, replace=False)
    st = ("ANDOR",) + tuple(int(x) for x in t)
    assert len(set(st[1:])) == 4, "ANDOR tap collision"
    return st


# ---------------- templates ----------------
def _T_H1(rng, h):
    return [h, H._draw_muxd(rng), H._draw_muxd(rng)]


def _T_H2(rng, h):
    return [H._draw_muxd(rng), h, H._draw_muxd(rng)]


def _T_H3(rng, h):
    return [h, H._draw_muxd(rng), H._draw_muxd(rng), H._draw_muxd(rng)]


TEMPLATES = {"H1": _T_H1, "H2": _T_H2, "H3": _T_H3}


def _stage_tag(st):
    if st[0] == "GFMUL":
        return "GFMUL(pc=%d)" % bin(st[1]).count("1")
    if st[0] == "CIRC1":
        return "CIRC1"
    if st[0] == "CIRC2":
        return "CIRC2"
    return "ANDOR"


def selftest():
    rng = np.random.default_rng(0xB802)
    # (1) CIRC bit-exact vs scalar.
    xs = rng.integers(0, 2**64, size=100, dtype=np.uint64)
    for st in [("CIRC1", 13), ("CIRC2", 13, 37)]:
        got = apply_stage(xs, st)

        def srot(v, r):
            r %= 64
            return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF if r else v

        for x, y in zip(xs, got):
            x = int(x)
            e = x ^ srot(x, st[1])
            if len(st) == 3:
                e ^= srot(x, st[2])
            assert int(y) == e, "CIRC scalar mismatch"
    # (2) GFMUL: matrix == bit-loop reference; algebraic properties.
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

    for _ in range(200):
        C = int(rng.integers(2, 2**64, dtype=np.uint64))
        x = np.array([int(v) for v in rng.integers(0, 2**64, size=8,
                                                   dtype=np.uint64)],
                     dtype=np.uint64)
        got = apply_stage(x, ("GFMUL", C))
        for xv, yv in zip(x, got):
            assert int(yv) == gf_ref(int(xv), C), "GFMUL ref mismatch"
    x = np.array([int(v) for v in rng.integers(0, 2**64, size=64,
                                               dtype=np.uint64)],
                 dtype=np.uint64)
    assert (apply_stage(x, ("GFMUL", 1)) == x).all(), "gf(x,1)!=x"
    assert (apply_stage(x, ("GFMUL", 0)) == 0).all(), "gf(x,0)!=0"
    C = int(rng.integers(2, 2**64, dtype=np.uint64))
    # distributivity: gf(x^y) == gf(x)^gf(y)
    y = np.array([int(v) for v in rng.integers(0, 2**64, size=64,
                                               dtype=np.uint64)],
                 dtype=np.uint64)
    assert (apply_stage(x ^ y, ("GFMUL", C)) ==
            (apply_stage(x, ("GFMUL", C)) ^
             apply_stage(y, ("GFMUL", C)))).all(), "gf distributivity"
    # (3) ANDOR bit-exact vs scalar.
    def srot(v, r):
        r %= 64
        return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF if r else v
    for _ in range(50):
        st = _draw_andor(rng)
        _, a, b, c, d = st
        got = apply_stage(xs, st)
        for xv, yv in zip(xs, got):
            xv = int(xv)
            e = xv ^ ((srot(xv, a) & srot(xv, b)) |
                      (srot(xv, c) & srot(xv, d)))
            assert int(yv) == e & 0xFFFFFFFFFFFFFFFF, "ANDOR scalar mismatch"
    # (4) draw-gate soundness, 200 draws each.
    for _ in range(200):
        s1 = _draw_circ1(rng)
        assert _gf2_rank(_circ_rows([0, s1[1]])) == 63
        s2 = _draw_circ2(rng)
        assert _gf2_rank(_circ_rows([0, s2[1], s2[2]])) == 64
        assert _circ2_minw2(s2[1], s2[2]) >= 4
        sg = _draw_gfmul(rng, 3)
        assert bin(sg[1]).count("1") == 3 and sg[1].bit_length() - 1 >= 8
        sa = _draw_andor(rng)
        assert len(set(sa[1:])) == 4
    # (5) inner gate smoke.
    r = eval_inner([("CIRC2", 13, 37), H._draw_muxd(
        np.random.default_rng(1)), H._draw_muxd(np.random.default_rng(2))])
    assert set(r) >= {"lin_verdict", "diff_verdict"}, "inner gate shape"
    print("SELFTEST PASS: CIRC/GFMUL/ANDOR bit-exact; draw gates 800/800; "
          "inner smoke OK", flush=True)


def _ser(st):
    if st[0] == "GFMUL":
        return ["GFMUL", hex(st[1])]
    return list(st)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        w1 = H.eval_calib_and1()
        ok1 = abs(w1 - 3.3) < 0.05
        print("CALIB-1 and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (w1, "PASS" if ok1 else "FAIL"), flush=True)
        nrej2a, w2a, _, flp2a = H.eval_sched(H.MU5_324_SCHED)
        ok2a = (nrej2a == 0)
        print("CALIB-2a mux/MU5-324(5st): n_reject=%d maxworst|z|=%.2f "
              "min_fisher=%.1f (expect KEEP) %s"
              % (nrej2a, w2a, flp2a, "PASS" if ok2a else "FAIL"), flush=True)
        nrej2b, w2b, flp2b = H.eval_lin4(H.LIN4_SCHED)
        ok2b = (nrej2b > 0)
        print("CALIB-2b linear-4: n_reject=%d maxworst|z|=%.1f "
              "min_fisher=%.1f (expect REJECT) %s"
              % (nrej2b, w2b, flp2b, "PASS" if ok2b else "FAIL"), flush=True)
        # CALIB-3: per-type gate soundness already in selftest; re-run quick
        rng = np.random.default_rng(0xB802)
        ok3 = True
        for _ in range(50):
            s = _draw_circ2(rng)
            if _gf2_rank(_circ_rows([0, s[1], s[2]])) != 64:
                ok3 = False
        print("CALIB-3 draw gates: %s" % ("PASS" if ok3 else "FAIL"),
              flush=True)
        sys.exit(0 if (ok1 and ok2a and ok2b and ok3) else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    assert sys.argv[1] == "hetstage", sys.argv[1]
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB802
    keep_path = sys.argv[3] if len(sys.argv) > 3 else None
    rng = np.random.default_rng(seed)

    # Pilot plan: (type, template, hetero-draw-fn, count, label)
    plan = []
    # Type A: 20 CIRC1 + 20 CIRC2
    a1 = lambda r: _draw_circ1(r)  # noqa: E731
    a2 = lambda r: _draw_circ2(r)  # noqa: E731
    plan += [("A", "H1", a1, 7, "CIRC1"), ("A", "H1", a2, 7, "CIRC2"),
             ("A", "H2", a1, 7, "CIRC1"), ("A", "H2", a2, 6, "CIRC2"),
             ("A", "H3", a1, 6, "CIRC1"), ("A", "H3", a2, 7, "CIRC2")]
    # Type B: 36 sparse (pc cycle 3,5,7) + 4 dense controls in H1
    pcs = [3, 5, 7]
    pi = [0]

    def b_sparse(r, _pi=pi):
        pc = pcs[_pi[0] % 3]
        _pi[0] += 1
        return _draw_gfmul(r, pc)

    def b_dense(r):
        return _draw_gfmul(r, int(r.integers(24, 41)))

    plan += [("B", "H1", b_sparse, 10, "GFM-sp"),
             ("B", "H1", b_dense, 4, "GFM-dense"),
             ("B", "H2", b_sparse, 13, "GFM-sp"),
             ("B", "H3", b_sparse, 13, "GFM-sp")]
    # Type C: 40 ANDOR
    plan += [("C", "H1", _draw_andor, 14, "ANDOR"),
             ("C", "H2", _draw_andor, 13, "ANDOR"),
             ("C", "H3", _draw_andor, 13, "ANDOR")]

    n_try = 0
    keep = []
    kills = 0
    minz = float("inf")
    minz_by = {}
    for ttype, tname, hfn, ndraw, label in plan:
        for _ in range(ndraw):
            h = hfn(rng)
            stages = TEMPLATES[tname](rng, h)
            nrej, wz, key, flp = eval_sched(stages)
            n_try += 1
            minz = min(minz, wz)
            minz_by[label] = min(minz_by.get(label, float("inf")), wz)
            flag = "KEEP" if nrej == 0 else "kill"
            if nrej > 0:
                kills += 1
            print("try %3d %s/%s %-9s n_reject=%d maxworst|z|=%8.1f "
                  "min_fisher=%7.1f worstkey=%#x %s  %s" %
                  (n_try - 1, ttype, tname, label, nrej, wz, flp, key, flag,
                   [_stage_tag(s) if s[0] in ("CIRC1", "CIRC2", "GFMUL",
                                              "ANDOR") else s[0]
                    for s in stages]), flush=True)
            if nrej == 0:
                inner = eval_inner(stages)
                ilin, idiff = (inner["lin_verdict"], inner["diff_verdict"])
                print("    INNER lin=%s diff=%s" % (ilin, idiff), flush=True)
                keep.append((wz, stages, ttype, tname, label, ilin, idiff))
                if keep_path:
                    rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                           "stages": [_ser(s) for s in stages],
                           "form": "hetstage", "seed": seed, "type": ttype,
                           "template": tname, "label": label,
                           "inner_lin": ilin, "inner_diff": idiff}
                    with open(keep_path, "a") as f:
                        f.write(json.dumps(rec) + "\n")
    print("=== hetstage: %d/%d KEEP minz=%.1f (seed=%#x) ===" %
          (len(keep), n_try, minz, seed), flush=True)
    for label in sorted(minz_by):
        print("    minz[%s]=%.1f" % (label, minz_by[label]), flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
