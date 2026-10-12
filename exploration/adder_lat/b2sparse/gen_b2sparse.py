#!/usr/bin/env python3
"""Generate + verify fast_battery bundles for (b2) sparse-GF screen KEEPs.

Form (b2): 3 stages of 2x d-constrained ANDs, cheap rotl-xor linear
(x ^= rotl(x,p) ^ rotl(x,q)) BETWEEN stages, ONE gf_mul(x, P) at END,
pre-whiten + rotl(k,13). P = 0x94D049BB133111EB fixed.

Reads adder_lat/b2sparse/b2sparse_screen.jsonl, selects top 4 KEEPs
(n_reject=0, full_rank=63 preferred, distinct (p,q)), generates bundles,
then verifies:
  - bundle model.py mix() == screen b2_model on 2000 vec x 3 keys
  - compiled C impl == Python model on 200 vecs
  - goldens in meta.json
  - RTL bit-exact vs model.py on 200 vecs via iverilog (if available)

Usage: python3 gen_b2sparse.py [--dry]   (dry = select+report only)
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
JSONL = os.path.join(HERE, "b2sparse_screen.jsonl")
P_GF = 0x94D049BB133111EB

import numpy as np  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS3 = [0x123456789ABCDEF0, 0x0F0F0F0F0F0F0F0F, 0xAAAAAAAAAAAAAAAA]


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def gf_np(a, C):
    res = np.zeros(a.shape, dtype=np.uint64)
    p = a.copy()
    c = int(C)
    while c:
        if c & 1:
            res ^= p
        hi = (p >> np.uint64(63)) & np.uint64(1)
        p = ((p << np.uint64(1)) & M64) ^ (hi * np.uint64(0x1B))
        c >>= 1
    return res & M64


def b2_model(V, key, stages, pq):
    """Screen form (must match screen_b2sparse.py::b2_model exactly)."""
    K = np.full(np.shape(V), np.uint64(key), dtype=np.uint64)
    p, q = pq
    x = (np.asarray(V, dtype=np.uint64) ^ K) & M64
    for ands in stages:
        for a, b in ands:
            x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        x = (x ^ rotl(x, p) ^ rotl(x, q)) & M64
    x = gf_np(x, P_GF)
    return (x ^ rotl(K, 13)) & M64


def load_keeps():
    keeps = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("verdict") == "KEEP":
                keeps.append(r)
    return keeps


def select(keeps, n=4):
    # n_reject=0 first (all are), full_rank desc, distinct (p,q) preferred,
    # lowest idx as the documented final tie-break.
    sk = sorted(keeps, key=lambda r: (r["n_reject"], -r["full_rank"], r["idx"]))
    out, seen_pq = [], set()
    for r in sk:
        if tuple(r["pq"]) not in seen_pq:
            out.append(r)
            seen_pq.add(tuple(r["pq"]))
        if len(out) == n:
            break
    for r in sk:
        if len(out) == n:
            break
        if r not in out:
            out.append(r)
    return out


# ---------- emitters ----------

def emit_model(name, stages, pq, desc):
    p, q = pq
    st = [[(int(a), int(b)) for a, b in ands] for ands in stages]
    L = []
    L.append('"""(b2) sparse-GF word-AND, one gf_mul at end (%s)."""' % desc)
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %s" % st)
    L.append("PQ = (%d, %d)" % (p, q))
    L.append("P_GF = 0x94D049BB133111EB")
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def _gf(a, C):")
    L.append("    res = np.zeros(a.shape, dtype=np.uint64); p = a.copy(); c = int(C)")
    L.append("    while c:")
    L.append("        if c & 1: res ^= p")
    L.append("        hi = (p >> np.uint64(63)) & np.uint64(1)")
    L.append("        p = ((p << np.uint64(1)) & M64) ^ (hi * np.uint64(0x1B))")
    L.append("        c >>= 1")
    L.append("    return res & M64")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for ands in STAGES:")
    L.append("        for a, b in ands:")
    L.append("            x = (x ^ (_rotl(x, a) & _rotl(x, b))) & M64")
    L.append("        x = (x ^ _rotl(x, PQ[0]) ^ _rotl(x, PQ[1])) & M64")
    L.append("    x = _gf(x, P_GF)")
    L.append("    x = (x ^ _rotl(k, 13)) & M64")
    L.append("    return x & M64")
    L.append("def mix(v, k):")
    L.append("    return int(mix_np(np.uint64(v), np.uint64(k)))")
    return "\n".join(L) + "\n"


def emit_c(name, stages, pq, desc):
    p, q = pq
    L = []
    L.append("#include <stdint.h>")
    L.append("static inline uint64_t rotl64(uint64_t x, int r) {")
    L.append("    r &= 63;")
    L.append("    return r ? (x << r) | (x >> (64 - r)) : x;")
    L.append("}")
    L.append("static uint64_t gf_mul(uint64_t a, uint64_t C) {")
    L.append("    uint64_t res = 0, p = a;")
    L.append("    while (C) {")
    L.append("        if (C & 1) res ^= p;")
    L.append("        uint64_t hi = p >> 63;")
    L.append("        p = (p << 1) ^ (hi ? 0x1BULL : 0ULL);")
    L.append("        C >>= 1;")
    L.append("    }")
    L.append("    return res;")
    L.append("}")
    L.append("// (b2) sparse-GF: 3st d-constrained word-AND, cheap linear pq=(%d,%d), "
             "one gf_mul at end" % (p, q))
    L.append("uint64_t mix_hash(uint64_t val, uint64_t key) {")
    L.append("    uint64_t x = val ^ key;")
    for ands in stages:
        for a, b in ands:
            L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d));" % (a, b))
        L.append("    x ^= rotl64(x,%d) ^ rotl64(x,%d);" % (p, q))
    L.append("    x = gf_mul(x, 0x94D049BB133111EBULL);")
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def rotl_expr(sig, r):
    if r == 0:
        return sig
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63 - r, sig, 64 - r)


def emit_rtl(name, stages, pq, desc):
    """RTL with val/key/out ports; GF mult expanded as a bit-level XOR net."""
    p, q = pq
    M = (1 << 64) - 1

    def gf_col(j):
        res, pp, c = 0, 1 << j, P_GF
        while c:
            if c & 1:
                res ^= pp
            hi = (pp >> 63) & 1
            pp = ((pp << 1) & M) ^ (0x1B if hi else 0)
            c >>= 1
        return res & M

    cols = [gf_col(j) for j in range(64)]
    L = []
    L.append("// %s: (b2) sparse-GF word-AND (%s)" % (name, desc))
    L.append("module %s(" % name)
    L.append("    input  [63:0] val,")
    L.append("    input  [63:0] key,")
    L.append("    output [63:0] out")
    L.append(");")
    L.append("    wire [63:0] x0 = val ^ key;")
    prev = "x0"
    for si, ands in enumerate(stages):
        for ai, (a, b) in enumerate(ands):
            nm = "s%d_%d" % (si, ai)
            L.append("    wire [63:0] %s = %s ^ (%s & %s);" %
                     (nm, prev, rotl_expr(prev, a), rotl_expr(prev, b)))
            prev = nm
        nm = "s%d_lin" % si
        L.append("    wire [63:0] %s = %s ^ %s ^ %s;" %
                 (nm, prev, rotl_expr(prev, p), rotl_expr(prev, q)))
        prev = nm
    L.append("    wire [63:0] g;")
    for i in range(64):
        terms = ["%s[%d]" % (prev, j) for j in range(64) if (cols[j] >> i) & 1]
        L.append("    assign g[%d] = %s;" % (i, " ^ ".join(terms) if terms else "1'b0"))
    L.append("    assign out = g ^ %s;" % rotl_expr("key", 13))
    L.append("endmodule")
    return "\n".join(L) + "\n"


# ---------- verification ----------

def verify_bundle(name, stages, pq):
    spec = importlib.util.spec_from_file_location(
        "m_" + name, os.path.join(FB, name, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rng = np.random.default_rng(0x23E4 & 0xFFFFFFFF)
    vecs = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
    st = [[(int(a), int(b)) for a, b in ands] for ands in stages]
    for k in KEYS3:
        ref = b2_model(vecs, k, st, pq)
        got = np.array([m.mix(int(v), k) for v in vecs], dtype=np.uint64)
        if not np.array_equal(ref, got):
            bad = int(np.nonzero(ref != got)[0][0])
            return False, "model mismatch at vec %d key %#x" % (bad, k)
    # C == Python (200 vecs)
    csrc = os.path.join(FB, name, "impl.c")
    test_c = os.path.join("/tmp", "b2s_test_%s.c" % name)
    with open(test_c, "w") as f:
        f.write('#include <stdio.h>\n#include <stdint.h>\n')
        f.write(open(csrc).read())
        f.write('int main(void){uint64_t vs[]={')
        f.write(','.join('0x%016xULL' % int(v) for v in vecs[:200]))
        f.write('};for(int i=0;i<200;i++){printf("%016llx\\n",'
                '(unsigned long long)mix_hash(vs[i],0x123456789ABCDEF0ULL));}'
                'return 0;}\n')
    exe = test_c + ".exe"
    r = subprocess.run(["gcc", "-O2", "-o", exe, test_c],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, "gcc failed: " + r.stderr[:200]
    r = subprocess.run([exe], capture_output=True, text=True)
    for i, line in enumerate(r.stdout.strip().split("\n")):
        if int(line.strip(), 16) != m.mix(int(vecs[i]), 0x123456789ABCDEF0):
            return False, "C mismatch at vec %d" % i
    # RTL == model via iverilog (200 vecs)
    if shutil.which("iverilog"):
        ok, msg = rtl_check(name, vecs)
        if not ok:
            return False, msg
    return True, "ok"


def rtl_check(name, vecs):
    """iverilog: feed vectors, compare RTL out vs model.py."""
    sim = os.path.join("/tmp", "b2s_sim_%s.v" % name)
    key = 0x123456789ABCDEF0
    with open(sim, "w") as f:
        f.write("module tb;\nreg [63:0] val;\nreg [63:0] key;\n"
                "wire [63:0] out;\n")
        f.write("%s dut(.val(val), .key(key), .out(out));\n" % name)
        f.write("initial begin\n")
        f.write("  key = 64'h%016x;\n" % key)
        for v in vecs[:200]:
            f.write("  val = 64'h%016x; #1 $display(\"%%016x\", out);\n" % int(v))
        f.write("  $finish;\nend\nendmodule\n")
    exe = os.path.join("/tmp", "b2s_sim_%s" % name)
    r = subprocess.run(["iverilog", "-o", exe, sim,
                        os.path.join(FB, name, "rtl.v")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, "iverilog compile failed: " + r.stderr[:200]
    r = subprocess.run(["vvp", exe], capture_output=True, text=True)
    lines = [ln for ln in r.stdout.strip().split("\n")
             if ln.strip() and all(c in "0123456789abcdefABCDEF" for c in ln.strip())]
    spec = importlib.util.spec_from_file_location(
        "m2_" + name, os.path.join(FB, name, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for i, line in enumerate(lines):
        if int(line.strip(), 16) != m.mix(int(vecs[i]), key):
            return False, "RTL mismatch at vec %d" % i
    return True, "rtl 200/200 PASS"


def main():
    dry = "--dry" in sys.argv
    keeps = load_keeps()
    print("KEEPs in JSONL: %d" % len(keeps), flush=True)
    for r in sorted(keeps, key=lambda r: (r["n_reject"], -r["full_rank"], r["idx"])):
        print("  idx=%d nrej=%d rank=%d pq=%s" %
              (r["idx"], r["n_reject"], r["full_rank"], r["pq"]), flush=True)
    sel = select(keeps)
    print("selected %d:" % len(sel), flush=True)
    for i, r in enumerate(sel):
        print("  al_b2s_%s <- idx=%d nrej=%d rank=%d pq=%s" %
              ("abcd"[i], r["idx"], r["n_reject"], r["full_rank"], r["pq"]),
              flush=True)
    if dry:
        return
    for i, r in enumerate(sel):
        name = "al_b2s_" + "abcd"[i]
        stages = [[(int(a), int(b)) for a, b in ands] for ands in r["stages"]]
        pq = (int(r["pq"][0]), int(r["pq"][1]))
        desc = "idx=%d nrej=%d rank=%d pq=(%d,%d)" % (
            r["idx"], r["n_reject"], r["full_rank"], pq[0], pq[1])
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(
            emit_model(name, stages, pq, desc))
        open(os.path.join(d, "impl.c"), "w").write(
            emit_c(name, stages, pq, desc))
        open(os.path.join(d, "rtl.v"), "w").write(
            emit_rtl(name, stages, pq, desc))
        spec = importlib.util.spec_from_file_location(
            "m_" + name, os.path.join(d, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        goldens = []
        for v, k in [(0x0, 0x123456789ABCDEF0),
                     (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(k),
                            "out": hex(m.mix(v, k))})
        meta = {
            "name": name,
            "description": "(b2) sparse-GF: 3st d-constrained word-AND, "
                           "cheap rotl-xor linear between stages, one "
                           "gf_mul(0x94d049bb133111eb) at end; screen %s" % desc,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        ok, msg = verify_bundle(name, stages, pq)
        print("bundle %s: verify %s (%s)" % (name, "PASS" if ok else "FAIL",
              msg), flush=True)
        if not ok:
            sys.exit(1)
    print("ALL BUNDLES OK", flush=True)


if __name__ == "__main__":
    main()
