#!/usr/bin/env python3
"""Generate a fast_battery candidate bundle from a batch-50 KEEP entry.

Usage: gen_b50_bundle.py <keeps.jsonl> <rank> <bundle_name>
  <rank> = index into the z-sorted KEEP list (0 = best).
Writes fast_battery/candidates/<bundle_name>/{rtl.v,model.py,impl.c,meta.json}
with a bit-exactness self-check (C vs Python on 2000 vectors) and a
screener cross-check (LUT-based t6_b50_screen on 500 vectors).
Form: qlowS4/qlowS3  stage(x,a,b) = y ^ rotl(y,a) ^ rotl(y,b), y = QLOW(x)
  QLOW = probe-mined minimal-AND bijective quadratic 4-bit S-box (LUT
  below), 16 contiguous 4-bit lanes (bits 0..63, full coverage). The ANF
  is DERIVED from the LUT by Moebius transform (fail-loud bit-exact on
  all 16 inputs) -- no hand transcription.
"""
import json
import os
import subprocess
import sys

M64 = 0xFFFFFFFFFFFFFFFF
NIBM = 0x1111111111111111

QLOW_LUT = [10,13,6,15,8,11,4,9,0,1,12,3,2,7,14,5]


def rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64


def moebius_anf(lut):
    """Return per-output-bit ANF: list of 4 lists of masks (0..15)."""
    anf = []
    for j in range(4):
        f = [(lut[x] >> j) & 1 for x in range(16)]
        a = f[:]
        step = 1
        for _ in range(4):
            for x in range(16):
                if x & step:
                    a[x] ^= a[x ^ step]
            step <<= 1
        anf.append([m for m in range(16) if a[m]])
    return anf


ANF = moebius_anf(QLOW_LUT)
# Fail-loud: derived ANF must be bit-exact vs the LUT on all 16 inputs,
# and purely quadratic (no cubic+ terms -- the mining family constraint).
for x in range(16):
    for j in range(4):
        v = 0
        for m in ANF[j]:
            t = 1
            for b in range(4):
                if m >> b & 1:
                    t &= (x >> b) & 1
            v ^= t
        assert v == ((QLOW_LUT[x] >> j) & 1), "ANF != LUT at x=%d bit=%d" % (x, j)
for j in range(4):
    for m in ANF[j]:
        assert bin(m).count("1") <= 2, "non-quadratic term in ANF"

QUAD_MASKS = sorted({m for j in range(4) for m in ANF[j]
                     if bin(m).count("1") == 2})
print("QLOW ANF: %d distinct AND monomials: %s"
      % (len(QUAD_MASKS),
         ["x%dx%d" % (b0, b1) for m in QUAD_MASKS
          for b0, b1 in [[b for b in range(4) if m >> b & 1]]]))
for j in range(4):
    print("  y%d = %s" % (j, " ^ ".join(
        "1" if m == 0 else "^".join("x%d" % b for b in range(4) if m >> b & 1)
        for m in ANF[j])))


def qlow_py(x):
    # Bitsliced ANF form (what RTL/C synthesize); cross-checked vs LUT.
    X = [(x >> b) & NIBM for b in range(4)]
    A = {}
    for m in QUAD_MASKS:
        bs = [b for b in range(4) if m >> b & 1]
        A[m] = X[bs[0]] & X[bs[1]]
    Y = []
    for j in range(4):
        y = 0
        for m in ANF[j]:
            if m == 0:
                y ^= NIBM
            elif bin(m).count("1") == 1:
                y ^= X[[b for b in range(4) if m >> b & 1][0]]
            else:
                y ^= A[m]
        Y.append(y)
    return (Y[0] | (Y[1] << 1) | (Y[2] << 2) | (Y[3] << 3)) & M64


def qlow_lut_py(x):
    y = 0
    for j in range(16):
        y |= QLOW_LUT[(x >> (4 * j)) & 0xF] << (4 * j)
    return y & M64


assert all(qlow_py(x) == qlow_lut_py(x) for x in range(1 << 16)), \
    "QLOW ANF != LUT"


def stage_py(x, a, b):
    y = qlow_py(x)
    return (y ^ rotl(y, a) ^ rotl(y, b)) & M64


def mix_py(v, k, stages):
    x = (v ^ k) & M64
    for tag, a, b in stages:
        assert tag == "QLOW", tag
        x = stage_py(x, a, b)
    return (x ^ rotl(k, 13)) & M64


def rtl_rot(x, r):
    return "{%s[%d:0], %s[63:%d]}" % (x, r - 1, x, 64 - r) if r else x


def vlog_anf():
    # Generate the Verilog function body from the derived ANF.
    L = ["    // QLOW: probe-mined minimal-AND bijective quadratic 4-bit",
         "    // S-box (batch-50). ANF derived from the LUT by Moebius,",
         "    // bit-exact vs the LUT on all 16 inputs.",
         "    function [63:0] qlow;",
         "        input [63:0] x;",
         "        reg [63:0] X0, X1, X2, X3;"]
    for m in QUAD_MASKS:
        bs = [b for b in range(4) if m >> b & 1]
        L.append("        reg [63:0] A%d%d;" % (bs[0], bs[1]))
    L.append("        reg [63:0] Y0, Y1, Y2, Y3;")
    L.append("        begin")
    for b in range(4):
        L.append("            X%d = %s;" % (b, "(x >> %d) & 64'h1111111111111111" % b if b else "x & 64'h1111111111111111"))
    for m in QUAD_MASKS:
        bs = [b for b in range(4) if m >> b & 1]
        L.append("            A%d%d = X%d & X%d;" % (bs[0], bs[1], bs[0], bs[1]))
    for j in range(4):
        terms = []
        for m in ANF[j]:
            if m == 0:
                terms.append("64'h1111111111111111")
            elif bin(m).count("1") == 1:
                terms.append("X%d" % [b for b in range(4) if m >> b & 1][0])
            else:
                bs = [b for b in range(4) if m >> b & 1]
                terms.append("A%d%d" % (bs[0], bs[1]))
        L.append("            Y%d = %s;" % (j, " ^ ".join(terms)))
    L.append("            qlow = Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);")
    L.append("        end")
    L.append("    endfunction")
    return "\n".join(L)


def c_anf():
    L = []
    for b in range(4):
        L.append("    uint64_t X%d = %s;" % (b, "(x >> %d) & M" % b if b else "x & M"))
    for m in QUAD_MASKS:
        bs = [b for b in range(4) if m >> b & 1]
        L.append("    uint64_t A%d%d = X%d & X%d;" % (bs[0], bs[1], bs[0], bs[1]))
    for j in range(4):
        terms = []
        for m in ANF[j]:
            if m == 0:
                terms.append("M")
            elif bin(m).count("1") == 1:
                terms.append("X%d" % [b for b in range(4) if m >> b & 1][0])
            else:
                bs = [b for b in range(4) if m >> b & 1]
                terms.append("A%d%d" % (bs[0], bs[1]))
        L.append("    uint64_t Y%d = %s;" % (j, " ^ ".join(terms)))
    L.append("    return Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);")
    return "\n".join(L)


def py_anf():
    L = ["    X = [(x >> b) & NIBM for b in range(4)]"]
    for m in QUAD_MASKS:
        bs = [b for b in range(4) if m >> b & 1]
        L.append("    A%d%d = X[%d] & X[%d]" % (bs[0], bs[1], bs[0], bs[1]))
    for j in range(4):
        terms = []
        for m in ANF[j]:
            if m == 0:
                terms.append("NIBM")
            elif bin(m).count("1") == 1:
                terms.append("X[%d]" % [b for b in range(4) if m >> b & 1][0])
            else:
                bs = [b for b in range(4) if m >> b & 1]
                terms.append("A%d%d" % (bs[0], bs[1]))
        L.append("    Y%d = %s" % (j, " ^ ".join(terms) if terms else "0"))
    L.append("    return (Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3)) & M64")
    return "\n".join(L)


def main():
    kj, rank, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(kj) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    entries.sort(key=lambda e: e["z"])
    e = entries[rank]
    form = e["form"]
    assert form in ("qlowS4", "qlowS3"), form
    stages = [tuple(s) for s in e["stages"]]
    z = e["z"]
    print("selected rank %d: form=%s z=%.2f stages=%s" % (rank, form, z, stages))
    outdir = "/home/hatch/workspace/mix/exploration/fast_battery/candidates/%s" % name
    os.makedirs(outdir, exist_ok=True)

    L = ["// %s: batch-50 %s schedule (triage z=%.2f)" % (name, form, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         vlog_anf(),
         "    wire [63:0] x0 = val ^ key;"]
    for j, (tag, a, b) in enumerate(stages):
        xj = "x%d" % j
        cj = "c%d" % (j + 1)
        # Verilog-2005 forbids part-selecting a function-call result --
        # bind to an intermediate wire first (b45 precedent).
        L.append("    wire [63:0] %s = qlow(%s);" % (cj, xj))
        L.append("    wire [63:0] x%d = %s ^ %s ^ %s;"
                 % (j + 1, cj, rtl_rot(cj, a), rtl_rot(cj, b)))
    n = len(stages)
    L.append("    assign out = x%d ^ %s;" % (n, rtl_rot("key", 13)))
    L.append("endmodule")
    open(os.path.join(outdir, "rtl.v"), "w").write("\n".join(L) + "\n")

    mp = ['"""%s: batch-50 %s cascade (triage z=%.2f)."""' % (name, form, z),
          "M64 = 0xFFFFFFFFFFFFFFFF",
          "NIBM = 0x1111111111111111",
          "STAGES = %s" % (stages,),
          "def _rotl(x, r):",
          "    r %= 64",
          "    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64",
          "def _qlow(x):",
          py_anf(),
          "def mix_np(V, K):",
          "    import numpy as np",
          "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
          "    x = (x ^ k) & np.uint64(M64)",
          "    for tag, a, b in STAGES:",
          "        y = np.array([_qlow(int(v)) for v in x], dtype=np.uint64)",
          "        ra = ((y << np.uint64(a)) | (y >> np.uint64(64-a)))",
          "        rb = ((y << np.uint64(b)) | (y >> np.uint64(64-b)))",
          "        x = (y ^ ra ^ rb) & np.uint64(M64)",
          "    x = (x ^ ((k << np.uint64(13)) | (k >> np.uint64(51)))) & np.uint64(M64)",
          "    return x",
          "def mix(v, k):",
          "    x = (v ^ k) & M64",
          "    for tag, a, b in STAGES:",
          "        y = _qlow(x)",
          "        x = (y ^ _rotl(y, a) ^ _rotl(y, b)) & M64",
          "    return (x ^ _rotl(k, 13)) & M64"]
    open(os.path.join(outdir, "model.py"), "w").write("\n".join(mp) + "\n")

    cl = ["#include <stdint.h>",
          "static inline uint64_t rotl64(uint64_t x, int r) {",
          "    r &= 63;",
          "    return r ? (x << r) | (x >> (64 - r)) : x;",
          "}",
          "// QLOW: probe-mined minimal-AND bijective quadratic 4-bit",
          "// S-box (batch-50); ANF derived from the LUT by Moebius,",
          "// bit-exact on all 16 inputs.",
          "static inline uint64_t qlow(uint64_t x) {",
          "    const uint64_t M = 0x1111111111111111ULL;",
          c_anf(),
          "}",
          "// batch-50 %s schedule (triage z=%.2f)" % (form, z),
          "uint64_t mix_hash(uint64_t val, uint64_t key) {",
          "    uint64_t x = val ^ key;",
          "    uint64_t y;"]
    for tag, a, b in stages:
        cl.append("    y = qlow(x); x = y ^ rotl64(y,%d) ^ rotl64(y,%d);" % (a, b))
    cl += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    open(os.path.join(outdir, "impl.c"), "w").write("\n".join(cl) + "\n")

    goldens = []
    for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
        goldens.append({"val": hex(v), "key": hex(k),
                        "out": hex(mix_py(v, k, stages))})
    meta = {"name": name,
            "description": "batch-50 %s %d-stage schedule (triage z=%.2f)" % (form, len(stages), z),
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name}
    open(os.path.join(outdir, "meta.json"), "w").write(json.dumps(meta, indent=1))

    chk = os.path.join(outdir, "check_exact.c")
    open(chk, "w").write(
        '#include <stdio.h>\n#include <stdint.h>\n#include "impl.c"\n'
        'int main(void){uint64_t s=0x123456789abcdefULL;\n'
        'for(int i=0;i<2000;i++){s=s*6364136223846793005ULL+1442695040888963407ULL;\n'
        'uint64_t v=s;s=s*6364136223846793005ULL+1442695040888963407ULL;uint64_t k=s;\n'
        'printf("%llx %llx %llx\\n",(unsigned long long)v,(unsigned long long)k,\n'
        '       (unsigned long long)mix_hash(v,k));}return 0;}\n')
    subprocess.run(["gcc", "-O2", "-o", os.path.join(outdir, "check_exact"), chk],
                   check=True, cwd=outdir)
    out = subprocess.run([os.path.join(outdir, "check_exact")], capture_output=True,
                         text=True, check=True).stdout.strip().split("\n")
    sys.path.insert(0, outdir)
    for mod in list(sys.modules):
        if mod == "model":
            del sys.modules[mod]
    import model
    bad = 0
    for line in out:
        v, k, o = [int(t, 16) for t in line.split()]
        if model.mix(v, k) != o:
            bad += 1
    print("bit-exact C-vs-Python: %d/2000 %s" % (2000 - bad, "OK" if bad == 0 else "FAIL"))
    if bad:
        sys.exit(4)
    # Cross-check the bundle (ANF form) against the SCREENER (LUT form).
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch50")
    for mod in list(sys.modules):
        if mod == "t6_b50_screen":
            del sys.modules[mod]
    import numpy as np
    import t6_b50_screen as scr
    import random
    random.seed(0xB500)
    bad2 = 0
    for _ in range(500):
        v = random.getrandbits(64)
        k = random.getrandbits(64)
        xx = np.uint64((v ^ k) & 0xFFFFFFFFFFFFFFFF)
        for st in stages:
            xx = scr.apply_stage(xx, st)
        ref = int((xx ^ scr.rotl(np.uint64(k), 13)) & np.uint64(0xFFFFFFFFFFFFFFFF))
        if model.mix(v, k) != ref:
            bad2 += 1
            if bad2 < 3:
                print("SCREENER-MISMATCH v=%x k=%x" % (v, k))
    print("screener-vs-bundle: %d/500 %s" % (500 - bad2, "OK" if bad2 == 0 else "FAIL"))
    if bad2:
        sys.exit(5)
    print("bundle %s written (form=%s triage z=%.2f)" % (name, form, z))


if __name__ == "__main__":
    main()
