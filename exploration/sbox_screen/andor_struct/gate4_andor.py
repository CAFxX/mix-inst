#!/usr/bin/env python3
"""andor_struct 4-gate bar on pilot keeps (CONDITIONAL: run only if the
pilot produced >=1 keep).

G1 (fisher) + G2 (inner-DIFF-SEQ) already passed in the pilot (adjudicated
from pilot.log). This runner applies:
  G0 bundle check: C emitter (ANDOR/MUXD) bit-exact vs Python model,
                   2000 vectors x 3 keys — fail-loud.
  G3 RD-SEQ: 9 reduction tests on SEQ x 10 keys, Fisher per key, Holm
             across keys (batch-62 verbatim rule). KEEP iff n_reject == 0.
  G4 Low1/64 PractRand prescreen at 256MB (batch-62 verbatim rule +
             2026-10-12 parser fix: ANY PractRand FAIL, not just
             Low1-family, is a real detection — try-35 was misclassified
             as INFRA twice): keep=False on any FAIL / suspicious /
             p < 1e-3; fail-loud if RNG_test never reaches 256MB.
Diagnostic: MU5-324 (het8, 5xMUXD) inner+fisher control.

Usage: gate4_andor.py  (reads pilot_keeps.jsonl, writes gate4_results.jsonl)
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/hetstage")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
import t8_andor_struct_screen as S2
import t8_het8_screen as H
from lin_diff import holm_reject
from screen_lib import KEYS, N
from screen_cal import _reduction_logps, fisher_logp

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
rotl = H.rotl
FB = "/home/hatch/workspace/mix/exploration/fast_battery"
RNG_TEST = "/home/hatch/tools/practrand/PractRand/RNG_test"
PRESCREEN_KEY = "123456789abcdef0"
PRESCREEN_TLMAX = "256MB"
BUILD = os.path.join(HERE, "build_gate4")

LOW1_RE = re.compile(
    r"\[(Low\d+/\d+)\](\S+)\s+R=\s*([+-]?\d+(?:\.\d+)?)\s+p\s*=\s*([\d.eE+-]+)\s*(.*)")
P_RANGE_RE = re.compile(
    r"^([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)-"
    r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)$")


def parse_low1_p(tok):
    try:
        return float(tok)
    except ValueError:
        pass
    m = P_RANGE_RE.match(tok)
    if m:
        return min(float(m.group(1)), float(m.group(2)))
    raise ValueError("unparseable PractRand p token: %r" % tok)


def deser(st):
    return tuple(st[0:1]) + tuple(int(v) for v in st[1:])


def seq_outputs(stages):
    V = np.arange(N, dtype=np.uint64)
    out = {}
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = S2.apply_stage(x, st)
        out[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return out


def eval_rdseq(stages):
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
         "// andor_struct gate4 %s" % tag,
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for st in stages:
        if st[0] == "ANDOR":
            _, a, b, c, d = st
            L.append(
                "    x = x ^ ((rotl64(x,%d)&rotl64(x,%d))|"
                "(rotl64(x,%d)&rotl64(x,%d)));"
                % (a, b, c, d))
        elif st[0] == "MUXD":
            _, s, a, b, d = st
            L.append(
                "    x = x ^ (((rotl64(x,%d)&rotl64(x,%d))|"
                "((~rotl64(x,%d))&rotl64(x,%d))) ^ rotl64(x,%d));"
                % (s, a, s, b, d))
        else:
            raise AssertionError("c-emit: unknown stage %r" % (st,))
    L += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    return "\n".join(L) + "\n"


def bit_exact_check(stages, tag):
    """Compile the C impl; compare 2000 vectors x 3 keys vs Python."""
    os.makedirs(BUILD, exist_ok=True)
    impl_c = os.path.join(BUILD, "impl_%s.c" % tag)
    gen_bin = os.path.join(BUILD, "gen_%s" % tag)
    with open(impl_c, "w") as f:
        f.write(c_impl_source(stages, tag))
    env = dict(os.environ, TMPDIR=BUILD)
    cp = subprocess.run(
        ["gcc", "-O2", "-o", gen_bin, FB + "/src/s3_gen.c", impl_c],
        capture_output=True, text=True, env=env)
    if cp.returncode != 0:
        return False, "COMPILE-FAIL: " + cp.stderr[:300]
    rng = np.random.default_rng(0xB804)
    V = np.arange(2000, dtype=np.uint64)
    for ki in range(3):
        key = int(rng.integers(0, 2**64, dtype=np.uint64))
        x = (V ^ np.uint64(key)) & M64
        for st in stages:
            x = S2.apply_stage(x, st)
        ref = ((x ^ rotl(np.uint64(key), 13)) & M64).astype(np.uint64)
        gp = subprocess.run(
            [gen_bin, "%x" % key, str(2000 * 8), "1"],
            capture_output=True, env=env)
        if gp.returncode != 0:
            return False, "GEN-FAIL key=%x rc=%d" % (key, gp.returncode)
        got = np.frombuffer(gp.stdout, dtype=np.uint64)
        if got.shape != ref.shape or not (got == ref).all():
            bad = int(np.sum(got != ref)) if got.shape == ref.shape else -1
            return False, "MISMATCH key=%x nbad=%d" % (key, bad)
    return True, "2000x3 bit-exact"


def eval_low1(stages, tag):
    os.makedirs(BUILD, exist_ok=True)
    impl_c = os.path.join(BUILD, "impl_%s.c" % tag)
    gen_bin = os.path.join(BUILD, "gen_%s" % tag)
    if not os.path.exists(gen_bin):
        with open(impl_c, "w") as f:
            f.write(c_impl_source(stages, tag))
        env = dict(os.environ, TMPDIR=BUILD)
        cp = subprocess.run(
            ["gcc", "-O2", "-o", gen_bin, FB + "/src/s3_gen.c", impl_c],
            capture_output=True, text=True, env=env)
        if cp.returncode != 0:
            return False, "COMPILE-FAIL: " + cp.stderr[:300]
    log_path = os.path.join(BUILD, "low1_%s.log" % tag)
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
    hits = []
    for line in text.splitlines():
        m = LOW1_RE.search(line)
        if not m or not m.group(1).startswith("Low1/"):
            continue
        p = parse_low1_p(m.group(4))
        ev = m.group(5)
        if p < worst_p:
            worst_p = p
        bad = ("FAIL" in ev) or ("suspicious" in ev.lower()) or (p < 1e-3)
        if bad:
            hits.append(line.strip())
    if hits:
        # PractRand defaults to -tlfail: a FAIL halts early (may never
        # reach 256MB). That is a real detection, not infra.
        return False, "LOW1-REJECT worst_p=%.2e :: %s" % (worst_p,
                                                         hits[0][:120])
    # 2026-10-12 parser fix (t6_b62_screen.py): ANY PractRand FAIL (not
    # just the Low1 family) halts the run early via -tlfail and is a real
    # detection, not infra. try-35 was misclassified as INFRA twice.
    for line in text.splitlines():
        if re.search(r"\bFAIL\b", line):
            return False, "G4-REJECT non-Low1 FAIL :: %s" % \
                line.strip()[:120]
    if "256 megabytes" not in text:
        return False, "LOUD INFRA FAILURE: RNG_test did not reach 256MB"
    return True, "LOW1-PASS worst_p=%.2e" % worst_p


def main():
    keeps = [json.loads(l) for l in open(
        os.path.join(HERE, "pilot_keeps.jsonl"))]
    keeps.sort(key=lambda r: r["z"])
    hb = os.path.join(HERE, "gate4_heartbeat.txt")
    outp = os.path.join(HERE, "gate4_results.jsonl")
    if os.path.exists(outp):
        os.remove(outp)

    def heartbeat(msg):
        with open(hb, "w") as f:
            f.write(msg + "\n")

    # Diagnostic control: MU5-324 (5xMUXD).
    mu5 = H.MU5_324_SCHED
    seq = {}
    V = np.arange(N, dtype=np.uint64)
    for key in S2.INNER_KEYS:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in mu5:
            x = S2.apply_stage(x, st)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    from lin_diff import screen_lin_diff
    mi = screen_lin_diff(seq, verbose=False)
    mn, mw, wk, mf = S2.eval_sched(mu5)
    print("CONTROL MU5-324 (5xMUXD): inner lin=%s diff=%s fisher "
          "n_reject=%d maxworst|z|=%.1f" % (mi["lin_verdict"],
                                           mi["diff_verdict"], mn, mw),
          flush=True)

    n = 0
    for rec in keeps:
        stages = [deser(s) for s in rec["stages"]]
        tag = "k%02d_%s_%s" % (n, rec["family"], rec["template"])
        n += 1
        heartbeat("%s start z=%.2f" % (tag, rec["z"]))
        nrej3, wkey3, wflp3, rej3 = eval_rdseq(stages)
        g3pass = (nrej3 == 0)
        print("%s G3 RD-SEQ n_reject=%d worst_key=%s worst_flp=%.1f %s" %
              (tag, nrej3, wkey3, wflp3, "PASS" if g3pass else "REJECT"),
              flush=True)
        okb, db = bit_exact_check(stages, tag)
        print("%s BUNDLE %s %s" % (tag, "PASS" if okb else "FAIL", db),
              flush=True)
        g4pass, d4 = (False, "SKIP") if not (g3pass and okb) else \
            eval_low1(stages, tag)
        print("%s G4 %s" % (tag, d4), flush=True)
        res = {"tag": tag, "z": rec["z"], "family": rec["family"],
               "template": rec["template"], "stages": rec["stages"],
               "g3_rdseq_reject": nrej3, "g3_pass": g3pass,
               "bundle_pass": okb, "bundle_detail": db,
               "g4_pass": g4pass, "g4_detail": d4,
               "advance": bool(g3pass and okb and g4pass)}
        with open(outp, "a") as f:
            f.write(json.dumps(res) + "\n")
        heartbeat("%s done advance=%s" % (tag, res["advance"]))
    adv = sum(1 for l in open(outp)
              if json.loads(l)["advance"])
    print("=== gate4: %d/%d ADVANCE ===" % (adv, len(keeps)), flush=True)


if __name__ == "__main__":
    main()
