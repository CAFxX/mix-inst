#!/usr/bin/env python3
"""Batch-62 PRE-PILOT + PILOT: muxD5f weakness-gated local (track 6).

Trigger: batch-61 COST-TERMINAL (O126) -- 3 sub-18.6u keeps all killed
in the battery on properties the fisher bar cannot see:
  t6_b61_56: S1-KILLED by the inner calibrated DIFF-SEQ gate
             (rej on keys 0xffffffffffffffff + 0xaaaaaaaaaaaaaaaa)
  t6_b61_24: S1-KILLED (RD rej=1, ('SEQ','0xffffffffffffffff'))
  t6_b61_38: S3-KILLED @1GB [Low1/64]Gap-16:A (suspicion at 256MB)
b61's triage used the OUTER lin_diff gate (2^16 pairs, low input
region); the 56-kill came from the INNER screen_lindiff gate (2^17
pairs, full range) -- strictly more powerful. This batch triages with
the failing instruments themselves.

Form (x ^= k pre-whiten; final x ^= rotl(k,13) -- the MU5 frame,
bit-identical to t6_b59_47):
  5x [x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)]
mux(s,a,b) = (s&a)|(~s&b).

Draw operator (fail-loud): single base t6_b59_47 (the only proven
S1->S4+Q1-clean basin center); m ~ Uniform{1,2,3} distinct rotation
positions (of 20) resampled Uniform{0..63}; per-stage s/a/b
pairwise-distinctness re-checked on resample (b51 cut #10); d free.
m>=1 so exact base rediscovery is impossible by construction.

KEEP bar (all four gates, cost order):
  G1 fisher triage: n_reject == 0, Holm-Bonferroni ALPHA=0.01 on
     per-key DIFF fisher_logp (outer lin_diff gate verbatim).
  G2 inner DIFF-SEQ + LIN gate (screen_lindiff.screen_lindiff, the
     exact gate that killed t6_b61_56): zero Holm rejections.
  G3 RD-SEQ reduction gate (the cell class that killed t6_b61_24):
     9 reduction tests on SEQ x 10 keys, Fisher per key, Holm across
     keys; zero rejections.
  G4 Low1/64 PractRand prescreen at 256MB (battery key
     0x123456789abcdef0): REJECT on any [Low1/64] FAIL / suspicious /
     p < 1e-3.

Controls (fail-loud, run `calibrate` first):
  CALIB-1: and1/b33c 6-stage must give z=3.3 (harness sanity).
  CALIB-2a: MU5-324 (5-stage) must KEEP (n_reject=0) -- bar sanity.
  CALIB-2b: linear-4 must be REJECTED (n_reject>0) -- negative control.
  CALIB-3a: t6_b59_47 inner screen_lindiff CAL_PASS (positive).
  CALIB-3b: t6_b61_56 inner screen_lindiff CAL_FLAG, rej on
           0xffffffffffffffff + 0xaaaaaaaaaaaaaaaa (negative -- the
           exact kill reproduced).
  CALIB-3c: t6_b61_24 inner screen_lindiff CAL_PASS (passed DIFF; the
           gate must not over-reject).
  CALIB-3d: t6_b61_24 RD-SEQ REJECT (negative for gate 3).
  CALIB-4a: t6_b61_38 Low1/64 prescreen REJECT at 256MB (negative --
           mild suspicion p=3.7e-5 must trip the p<1e-3 rule).
  CALIB-4b: t6_b59_47 Low1/64 prescreen PASS (positive).
  CALIB-4c: t6_b57_0 Low1/64 prescreen REJECT (failed at 16MB).

Unit check (`selftest`, fail-loud): single-base perturbation operator
-- 200 draws, each 1..3 positions off t6_b59_47, all stages MUXD-valid
with s/a/b distinct, never base-identical.

Usage: t6_b62_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: muxD5fweakgated | calibrate | selftest
"""
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
FB = EXP + "/fast_battery"
B62 = EXP + "/new_constructions/batch62"
sys.path.insert(0, FB + "/src")
sys.path.insert(0, EXP)
from lin_diff import diff_cell_logps, holm_reject
from screen_lib import KEYS, N
from screen_lindiff import screen_lindiff
from screen_cal import _reduction_logps, fisher_logp

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
RNG_TEST = "/home/hatch/tools/practrand/PractRand/RNG_test"
PRESCREEN_KEY = "123456789abcdef0"
# PractRand LENGTH syntax: bare number = log2(bytes); use the MB suffix.
# (s3_practrand.sh passes the stage NAME "256MB" as -tlmax; a bare
# 268435456 would mean 2^268435456 bytes -> "length out of bounds".)
PRESCREEN_TLMAX = "256MB"

# t6_b59_47: the single proven-clean base (verbatim from
# fast_battery/candidates/t6_b59_47/model.py).
BASE_47 = [("MUXD", 17, 22, 10, 55), ("MUXD", 63, 62, 49, 57),
           ("MUXD", 29, 39, 35, 6), ("MUXD", 9, 4, 44, 36),
           ("MUXD", 5, 54, 31, 34)]


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


def seq_outputs(stages):
    """SEQ outputs (N=2^18) for the 10 calibrated keys. Returns dict."""
    V = np.arange(N, dtype=np.uint64)
    out = {}
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        out[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return out


def eval_fisher(stages):
    """G1: outer DIFF gate + Holm. Returns (n_reject, worst_z, worst_key,
    min_fisher_logp). KEEP iff n_reject == 0."""
    seq = seq_outputs(stages)
    worst = 0.0
    worst_key = None
    min_flp = 0.0
    cells = []
    for key in KEYS10:
        _, wz, flp, _ = diff_cell_logps(seq[key], key)
        cells.append((("DIFF", key), flp))
        if wz > worst:
            worst, worst_key = wz, key
        min_flp = min(min_flp, flp)
    n_reject = len(holm_reject(cells))
    return n_reject, worst, worst_key, min_flp


def eval_inner(stages, name="try"):
    """G2: inner screen_lindiff (LIN+DIFF on SEQ x 10 keys). Returns
    (verdict, n_reject_total, diff_worst_z). KEEP iff CAL_PASS."""
    seq = seq_outputs(stages)
    S_cache = {("SEQ", k): seq[k] for k in KEYS10}
    res = screen_lindiff(S_cache, name, verbose=False)
    n_rej = len(res["rej_lin"]) + len(res["rej_diff"])
    dw = max((w for w, _ in res["diff_worst"].values()), default=0.0)
    return res["verdict"], n_rej, dw, res


def eval_rdseq(stages):
    """G3: RD-SEQ reduction gate. 9 reduction tests on SEQ x 10 keys,
    Fisher-combined per key, Holm across keys. Returns (n_reject,
    worst_key). KEEP iff n_reject == 0."""
    seq = seq_outputs(stages)
    cells = []
    worst_key = None
    worst_flp = 0.0
    for key in KEYS10:
        lps = _reduction_logps(seq[key])
        flp = fisher_logp(lps)
        cells.append((("RD-SEQ", key), flp))
        if flp < worst_flp:
            worst_flp, worst_key = flp, key
    rej = holm_reject(cells)
    return len(rej), worst_key, worst_flp, [c for c, _ in rej]


def c_impl_source(stages, tag):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63;",
         "    return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "// batch-62 prescreen %s" % tag,
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for st in stages:
        assert st[0] == "MUXD", st
        _, s, a, b, d = st
        L.append(
            "    x = x ^ (((rotl64(x,%d)&rotl64(x,%d))|"
            "((~rotl64(x,%d))&rotl64(x,%d))) ^ rotl64(x,%d));"
            % (s, a, s, b, d))
    L += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    return "\n".join(L) + "\n"


LOW1_RE = re.compile(
    r"\[(Low\d+/\d+)\](\S+)\s+R=\s*([+-]?\d+(?:\.\d+)?)\s+p\s*=\s*([\d.eE+-]+)\s*(.*)")


def eval_low1(stages, tag):
    """G4: Low1/64 PractRand prescreen at 256MB. Returns (keep, detail).
    keep=False on any [Low1/64] FAIL / suspicious / p < 1e-3.
    Fail-loud on infrastructure problems (no length= guard)."""
    bd = os.path.join(B62, "build_prescreen")
    os.makedirs(bd, exist_ok=True)
    impl_c = os.path.join(bd, "impl_%s.c" % tag)
    gen_bin = os.path.join(bd, "gen_%s" % tag)
    with open(impl_c, "w") as f:
        f.write(c_impl_source(stages, tag))
    cp = subprocess.run(
        ["gcc", "-O2", "-o", gen_bin, FB + "/src/s3_gen.c", impl_c],
        capture_output=True, text=True)
    if cp.returncode != 0:
        return False, "COMPILE-FAIL: " + cp.stderr[:300]
    # s3_practrand.sh pattern: 4GB stream, -tlmax bounds the test, -tlmin 10
    # keeps progressive checkpoints visible. Generator dies on SIGPIPE.
    # NOTE: -tlmax takes PractRand LENGTH syntax (see PRESCREEN_TLMAX).
    log_path = os.path.join(bd, "low1_%s.log" % tag)
    try:
        gen = subprocess.Popen(
            [gen_bin, PRESCREEN_KEY, "4294967296", "1"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        with open(log_path, "w") as lf:
            pr = subprocess.run(
                [RNG_TEST, "stdin64", "-tlmax", PRESCREEN_TLMAX,
                 "-tlmin", "10"],
                stdin=gen.stdout, stdout=lf, timeout=900)
        gen.stdout.close()
        try:
            gen.wait(timeout=30)
        except subprocess.TimeoutExpired:
            gen.kill()
    except subprocess.TimeoutExpired:
        return False, "PRACTRAND-TIMEOUT"
    text = open(log_path).read()
    worst_p = 1.0
    worst_line = ""
    hits = []
    for line in text.splitlines():
        m = LOW1_RE.search(line)
        if not m or not m.group(1).startswith("Low1/"):
            continue
        p = float(m.group(4))
        ev = m.group(5)
        if p < worst_p:
            worst_p, worst_line = p, line.strip()
        bad = ("FAIL" in ev) or ("suspicious" in ev.lower()) or (p < 1e-3)
        if bad:
            hits.append(line.strip())
    if hits:
        # Note: PractRand defaults to -tlfail, so a FAIL halts the run
        # early (it may never reach 256MB). That is a real detection,
        # not an infra failure.
        return False, "LOW1-REJECT worst_p=%.2e :: %s" % (worst_p, hits[0][:120])
    if "256 megabytes" not in text:
        # Hardened guard: the target length must actually have been
        # reached when nothing was detected. ("length=" alone is
        # insufficient: the out-of-bounds error line contains
        # "length=" too.)
        return False, "LOUD INFRA FAILURE: RNG_test did not reach 256MB"
    return True, "LOW1-PASS worst_p=%.2e" % worst_p


# ---- calibration schedules (verbatim from disk) ----
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]
MU5_324_SCHED = [("MUXD", 62, 50, 55, 2), ("MUXD", 48, 58, 23, 30),
                 ("MUXD", 44, 45, 7, 40), ("MUXD", 49, 26, 32, 35),
                 ("MUXD", 46, 51, 43, 44)]
LIN4_SCHED = [7, 23, 41, 55]
# raw-adjudicated kill schedules (verbatim from bundle logs / model.py)
T6_B61_56 = [("MUXD", 17, 22, 52, 55), ("MUXD", 63, 62, 51, 41),
             ("MUXD", 29, 18, 35, 6), ("MUXD", 9, 4, 49, 36),
             ("MUXD", 16, 54, 52, 16)]
T6_B61_24 = [("MUXD", 17, 22, 10, 55), ("MUXD", 63, 62, 49, 57),
             ("MUXD", 29, 39, 35, 6), ("MUXD", 9, 13, 44, 36),
             ("MUXD", 5, 54, 31, 34)]
T6_B61_38 = [("MUXD", 17, 22, 13, 55), ("MUXD", 63, 62, 51, 41),
             ("MUXD", 0, 39, 35, 6), ("MUXD", 9, 4, 10, 36),
             ("MUXD", 16, 54, 52, 34)]
T6_B57_0 = [("MUXD", 13, 15, 12, 43), ("MUXD", 32, 55, 29, 11),
            ("MUXD", 17, 58, 27, 26), ("MUXD", 42, 27, 57, 8),
            ("MUXD", 44, 59, 3, 7)]


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


def eval_lin4():
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    min_flp = 0.0
    cells = []
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for s in LIN4_SCHED:
            x = (x ^ rotl(x, s)) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, flp, _ = diff_cell_logps(S, key)
        cells.append((("DIFF", key), flp))
        worst = max(worst, wz)
        min_flp = min(min_flp, flp)
    return len(holm_reject(cells)), worst, min_flp


def calibrate():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print("CALIB %s: %s %s" % (name, "PASS" if cond else "FAIL", detail),
              flush=True)
        ok = ok and cond

    w1 = eval_calib_and1()
    check("1 and1/b33c z=3.3 EXACT", abs(w1 - 3.3) < 0.05,
          "maxworst|z|=%.1f" % w1)
    n2a, w2a, _, f2a = eval_fisher(MU5_324_SCHED)
    check("2a MU5-324 fisher KEEP", n2a == 0,
          "n_reject=%d z=%.2f" % (n2a, w2a))
    n2b, w2b, f2b = eval_lin4()
    check("2b linear-4 fisher REJECT", n2b > 0,
          "n_reject=%d z=%.1f" % (n2b, w2b))
    v3a, r3a, d3a, _ = eval_inner(BASE_47, name="calib-3a")
    check("3a t6_b59_47 inner CAL_PASS", v3a == "CAL_PASS",
          "verdict=%s rej=%d" % (v3a, r3a))
    v3b, r3b, d3b, res3b = eval_inner(T6_B61_56, name="calib-3b")
    rejkeys = {k for _, k in res3b["rej_diff"]}
    check("3b t6_b61_56 inner CAL_FLAG on 0xffff..+0xaa..",
          v3b == "CAL_FLAG" and "0xffffffffffffffff" in rejkeys
          and "0xaaaaaaaaaaaaaaaa" in rejkeys,
          "verdict=%s rej_diff=%s" % (v3b, res3b["rej_diff"]))
    v3c, r3c, d3c, _ = eval_inner(T6_B61_24, name="calib-3c")
    check("3c t6_b61_24 inner CAL_PASS (no over-reject)", v3c == "CAL_PASS",
          "verdict=%s rej=%d" % (v3c, r3c))
    n3d, wk3d, f3d, rej3d = eval_rdseq(T6_B61_24)
    check("3d t6_b61_24 RD-SEQ REJECT", n3d > 0,
          "n_reject=%d rej=%s" % (n3d, rej3d))
    n3e, wk3e, f3e, rej3e = eval_rdseq(BASE_47)
    check("3e t6_b59_47 RD-SEQ no-reject (positive)", n3e == 0,
          "n_reject=%d" % n3e)
    k4a, d4a = eval_low1(T6_B61_38, "calib-38")
    check("4a t6_b61_38 Low1 prescreen REJECT", not k4a, d4a)
    k4b, d4b = eval_low1(BASE_47, "calib-47")
    check("4b t6_b59_47 Low1 prescreen PASS", k4b, d4b)
    k4c, d4c = eval_low1(T6_B57_0, "calib-570")
    check("4c t6_b57_0 Low1 prescreen REJECT", not k4c, d4c)
    print("CALIBRATION %s" % ("PASS" if ok else "FAIL"), flush=True)
    sys.exit(0 if ok else 1)


def draw_perturbed(rng):
    """One schedule: m ~ Uniform{1,2,3} distinct rotation positions (of
    20) resampled Uniform{0..63} around BASE_47; s/a/b distinctness
    re-checked per stage (b51 cut #10); d free. Never base-identical
    (m >= 1)."""
    base = BASE_47
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
    return stages, m


def selftest():
    # (1) MUXD stage bit-exact vs manual expansion.
    x = np.uint64(1 << 7)
    st = ("MUXD", 5, 17, 33, 41)
    g = mux(rotl(x, 5), rotl(x, 17), rotl(x, 33))
    assert bin(int(g)).count("1") == 1, "MUX gate popcount != 1"
    got = int(apply_stage(x, st))
    want = int((x ^ g ^ rotl(x, 41)) & M64)
    assert got == want, "MUXD stage mismatch"
    # (2) Single-base perturbation operator: 200 draws, each 1..3
    # positions off BASE_47, all stages valid, never base-identical.
    rng = np.random.default_rng(0xB621)
    for i in range(200):
        stages, m = draw_perturbed(rng)
        assert 1 <= m <= 3, "m out of range: %d" % m
        diff = 0
        for a, b in zip(stages, BASE_47):
            diff += sum(1 for u, v in zip(a[1:], b[1:]) if u != v)
        assert diff == m, "draw %d: %d positions differ, m=%d" % (i, diff, m)
        assert all(s[0] == "MUXD" for s in stages)
        assert all(len({s[1], s[2], s[3]}) == 3 for s in stages)
        assert stages != BASE_47
    print("SELFTEST PASS: MUXD stage bit-exact; single-base perturbation "
          "operator 200/200 (1..3 positions differ from t6_b59_47, stages "
          "valid, never base-identical)", flush=True)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        calibrate()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        return
    form = sys.argv[1]
    assert form == "muxD5fweakgated", form
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB621
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    gkills = [0, 0, 0, 0]
    minz = float("inf")
    for t in range(n_try):
        stages, m = draw_perturbed(rng)
        tag = "t%03d" % t
        # G1: fisher
        nrej, wz, key, flp = eval_fisher(stages)
        minz = min(minz, wz)
        if nrej > 0:
            kills += 1
            gkills[0] += 1
            print("try %3d m=%d G1-fisher KILL n_reject=%d z=%.1f" %
                  (t, m, nrej, wz), flush=True)
            continue
        # G2: inner DIFF-SEQ/LIN
        v2, r2, d2, _ = eval_inner(stages, name="b62-%s" % tag)
        if v2 != "CAL_PASS":
            kills += 1
            gkills[1] += 1
            print("try %3d m=%d G2-inner KILL rej=%d diffworstz=%.1f" %
                  (t, m, r2, d2), flush=True)
            continue
        # G3: RD-SEQ
        n3, wk3, f3, rej3 = eval_rdseq(stages)
        if n3 > 0:
            kills += 1
            gkills[2] += 1
            print("try %3d m=%d G3-rdseq KILL n_reject=%d rej=%s" %
                  (t, m, n3, rej3), flush=True)
            continue
        # G4: Low1/64 PractRand prescreen
        k4, d4 = eval_low1(stages, tag)
        if not k4:
            kills += 1
            gkills[3] += 1
            print("try %3d m=%d G4-low1 KILL %s" % (t, m, d4), flush=True)
            continue
        print("try %3d m=%d KEEP fisher z=%.1f inner diffz=%.1f %s" %
              (t, m, wz, d2, d4), flush=True)
        keep.append((wz, stages, m))
        if keep_path:
            rec = {"z": wz, "n_reject": nrej, "min_fisher": flp,
                   "inner_diffz": d2,
                   "stages": [list(s) for s in stages],
                   "form": "muxD5f", "seed": seed, "is_324": False,
                   "base": "t6_b59_47", "n_perturb": m}
            with open(keep_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
    print("=== muxD5fweakgated: %d/%d KEEP minz=%.1f "
          "gkills=%s (seed=%#x) ===" %
          (len(keep), n_try, minz, gkills, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
