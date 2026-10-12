#!/usr/bin/env python3
"""Track-2 revival pilot: 8-bit AES-class box as single hetero stage in a
non-SPN MU5 frame (post-O129 open lead).

Form: MU5 frame (pre-whiten x ^= k; final x ^= rotl(k,13)), stage types
BOX8 (8-bit box on bits[7:0], identity elsewhere), XOR4 (5-term circulant,
bijective for distinct taps), MUXD (measured ~3.86u).

Pre-registered design: DESIGN.md (co-design, cost thesis ~18.3u < 18.6u,
kill rules K1/K2/K3). Pilot: 36 draws (T1-T5 x 7, T6 x 1), gates =
fisher (verbatim) + inner screen_lin_diff on keeps (batch-62 calibration).

Usage: t8_het8_screen.py het8 <seed> [keep_jsonl]
       t8_het8_screen.py calibrate | selftest
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, holm_reject, screen_lin_diff
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
INNER_KEYS = [0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA]

HARVEST = os.path.expanduser(
    "~/workspace/mix/exploration/sbox_screen/ranked_sbox8_pool_20261012.json")

_BOX_LUTS = {}


def box_lut(name):
    if name not in _BOX_LUTS:
        for rec in json.load(open(HARVEST))["records"]:
            if rec["name"] == name:
                _BOX_LUTS[name] = np.array(
                    list(bytes.fromhex(rec["table"])), dtype=np.uint64)
                break
        assert name in _BOX_LUTS, f"box {name} not in harvest"
    return _BOX_LUTS[name]


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
    if tag == "XOR4":
        _, a, b, c, d = st
        assert len({a, b, c, d}) == 4, "degenerate xor4 draw"
        return (x ^ rotl(x, a) ^ rotl(x, b) ^ rotl(x, c) ^ rotl(x, d)) & M64
    assert tag == "BOX8", tag
    _, boxname = st
    lut = box_lut(boxname)
    return ((x & ~np.uint64(0xFF)) | lut[x & np.uint64(0xFF)]) & M64


def eval_sched(stages):
    """Exact S1-DIFF triage with the GATE's rule: KEEP iff n_reject == 0."""
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
    """Inner gate (batch-62 calibration): screen_lin_diff on full-range
    sequential outputs, keys 0xff..f + 0xaa..a. PASS iff both families clean."""
    seq = {}
    V = np.arange(N, dtype=np.uint64)
    for key in INNER_KEYS:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return screen_lin_diff(seq, verbose=False)


def _and1(x, a, b, c):
    return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64


B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]

MU5_324_SCHED = [("MUXD", 62, 50, 55, 2), ("MUXD", 48, 58, 23, 30),
                 ("MUXD", 44, 45, 7, 40), ("MUXD", 49, 26, 32, 35),
                 ("MUXD", 46, 51, 43, 44)]

LIN4_SCHED = [7, 23, 41, 55]


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


def eval_lin4(sched):
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
    return len(holm_reject(cells)), worst, min_flp


def _draw_xor4(rng):
    taps = rng.choice(64, size=4, replace=False)
    return ("XOR4",) + tuple(int(t) for t in taps)


def _draw_muxd(rng):
    sab = rng.choice(64, size=3, replace=False)
    d = int(rng.integers(0, 64))
    return ("MUXD", int(sab[0]), int(sab[1]), int(sab[2]), d)


# Pre-registered templates. Box stage carries the box name.
TEMPLATES = {
    "T1": lambda rng, b: [("BOX8", b), _draw_xor4(rng), _draw_muxd(rng)],
    "T2": lambda rng, b: [("BOX8", b), _draw_muxd(rng), _draw_xor4(rng)],
    "T3": lambda rng, b: [_draw_xor4(rng), ("BOX8", b), _draw_muxd(rng)],
    "T4": lambda rng, b: [("BOX8", b), _draw_xor4(rng), _draw_xor4(rng),
                           _draw_muxd(rng)],
    "T5": lambda rng, b: [("BOX8", b), _draw_xor4(rng), _draw_xor4(rng)],
    "T6": lambda rng, b: [_draw_xor4(rng), _draw_muxd(rng), ("BOX8", b)],
}

# Box mix per template of 7 draws: 5x cheapest + 2 alternates.
BOX_MIX = ["AFF8_06"] * 5 + ["AES_SBOX", "AFF8_03"]


def selftest():
    # (1) BOX8 stage: low byte replaced per table, high bits untouched.
    lut = box_lut("AFF8_06")
    x = np.array([np.uint64(0xDEADBEEFCAFEBABE)], dtype=np.uint64)
    got = apply_stage(x, ("BOX8", "AFF8_06"))
    want = (int(x[0]) & ~0xFF) | int(lut[0xBE])
    assert int(got[0]) == want, "BOX8 stage mismatch"
    # box is a permutation of 0..255 (bijective gate)
    assert len(set(int(v) for v in lut)) == 256, "box not bijective"
    # (2) XOR4 / MUXD bit-exact (verbatim xorh5).
    xm = np.uint64(1 << 7)
    assert int(apply_stage(xm, ("XOR4", 5, 17, 33, 41))) == int(
        (xm ^ rotl(xm, 5) ^ rotl(xm, 17) ^ rotl(xm, 33) ^ rotl(xm, 41)) & M64)
    g = mux(rotl(xm, 5), rotl(xm, 17), rotl(xm, 33))
    assert int(apply_stage(xm, ("MUXD", 5, 17, 33, 41))) == int(
        (xm ^ g ^ rotl(xm, 41)) & M64)
    # (3) Draw operators: 200 draws per template, structure valid.
    rng = np.random.default_rng(0xB801)
    for tname, fn in TEMPLATES.items():
        for i in range(200):
            st = fn(rng, "AFF8_06")
            assert sum(1 for s in st if s[0] == "BOX8") == 1, tname
            for s in st:
                if s[0] == "XOR4":
                    assert len(set(s[1:])) == 4, tname
                elif s[0] == "MUXD":
                    assert len({s[1], s[2], s[3]}) == 3, tname
    # (4) inner gate fires on a keep-shaped input (smoke: returns dict).
    r = eval_inner([("BOX8", "AFF8_06"), _draw_xor4(
        np.random.default_rng(1)), _draw_muxd(np.random.default_rng(2))])
    assert set(r) >= {"lin_verdict", "diff_verdict"}, "inner gate shape"
    print("SELFTEST PASS: BOX8 bit-exact + bijective; XOR4/MUXD bit-exact; "
          "draw operators 1200/1200; inner gate smoke OK", flush=True)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        w1 = eval_calib_and1()
        ok1 = abs(w1 - 3.3) < 0.05
        print("CALIB-1 and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (w1, "PASS" if ok1 else "FAIL"), flush=True)
        nrej2a, w2a, _, flp2a = eval_sched(MU5_324_SCHED)
        ok2a = (nrej2a == 0)
        print("CALIB-2a mux/MU5-324(5st): n_reject=%d maxworst|z|=%.2f "
              "min_fisher=%.1f (expect KEEP) %s"
              % (nrej2a, w2a, flp2a, "PASS" if ok2a else "FAIL"), flush=True)
        nrej2b, w2b, flp2b = eval_lin4(LIN4_SCHED)
        ok2b = (nrej2b > 0)
        print("CALIB-2b linear-4: n_reject=%d maxworst|z|=%.1f "
              "min_fisher=%.1f (expect REJECT) %s"
              % (nrej2b, w2b, flp2b, "PASS" if ok2b else "FAIL"), flush=True)
        sys.exit(0 if (ok1 and ok2a and ok2b) else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    assert sys.argv[1] == "het8", sys.argv[1]
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB801
    keep_path = sys.argv[3] if len(sys.argv) > 3 else None
    rng = np.random.default_rng(seed)
    n_try = 0
    keep = []
    kills = 0
    minz = float("inf")
    plan = [("T1", 7), ("T2", 7), ("T3", 7), ("T4", 7), ("T5", 7), ("T6", 1)]
    for tname, ndraw in plan:
        for i in range(ndraw):
            box = BOX_MIX[i % len(BOX_MIX)] if tname != "T6" else "AFF8_06"
            stages = TEMPLATES[tname](rng, box)
            nrej, wz, key, flp = eval_sched(stages)
            n_try += 1
            minz = min(minz, wz)
            flag = "KEEP" if nrej == 0 else "kill"
            if nrej > 0:
                kills += 1
            print("try %3d %s box=%-8s n_reject=%d maxworst|z|=%8.1f "
                  "min_fisher=%7.1f worstkey=%#x %s" %
                  (n_try - 1, tname, box, nrej, wz, flp, key, flag), flush=True)
            if nrej == 0:
                inner = eval_inner(stages)
                ilin, idiff = (inner["lin_verdict"], inner["diff_verdict"])
                print("    INNER lin=%s diff=%s" % (ilin, idiff), flush=True)
                keep.append((wz, stages, tname, box, ilin, idiff))
                if keep_path:
                    rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                           "stages": [list(s) for s in stages],
                           "form": "het8", "seed": seed, "template": tname,
                           "box": box, "inner_lin": ilin, "inner_diff": idiff}
                    with open(keep_path, "a") as f:
                        f.write(json.dumps(rec) + "\n")
    print("=== het8: %d/%d KEEP minz=%.1f (seed=%#x) ===" %
          (len(keep), n_try, minz, seed), flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)
    cost_viable = [k for k in keep if k[2] in ("T1", "T2", "T3", "T5")]
    print("cost-viable keeps (T1/T2/T3/T5): %d" % len(cost_viable), flush=True)


if __name__ == "__main__":
    main()
