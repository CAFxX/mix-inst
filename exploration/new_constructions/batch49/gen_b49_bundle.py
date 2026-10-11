#!/usr/bin/env python3
"""Generate a fast_battery candidate bundle from a batch-49 KEEP entry.

Usage: gen_b49_bundle.py <keeps.jsonl> <rank> <bundle_name>
  <rank> = index into the z-sorted KEEP list (0 = best).
Writes fast_battery/candidates/<bundle_name>/{rtl.v,model.py,impl.c,meta.json}
with a bit-exactness self-check (C vs Python on 2000 vectors) and a
screener cross-check (LUT-based t6_b49_screen on 500 vectors).
Form: q4bS4/q4bS3  stage(x,a,b) = y ^ rotl(y,a) ^ rotl(y,b), y = Q4(x)
  Q4 = mined bijective quadratic 4-bit S-box (LUT below), 16 contiguous
  4-bit lanes (bits 0..63, full coverage). ANF (verified bit-exact vs the
  LUT on all 16 inputs):
    y0 = 1^x0^x2^x3^(x0&x1)^(x0&x2)^(x1&x2)
    y1 = 1^x0^x2
    y2 = x0^x1^x3^(x0&x1)^(x1&x2)^(x0&x3)^(x2&x3)
    y3 = x1^x3^(x0&x1)^(x1&x2)
  5 distinct AND monomials: x0x1,x0x2,x1x2,x0x3,x2x3.
"""
import json
import os
import subprocess
import sys

M64 = 0xFFFFFFFFFFFFFFFF
NIBM = 0x1111111111111111

Q4_LUT = [3, 4, 15, 5, 0, 6, 1, 10, 14, 13, 2, 12, 9, 11, 8, 7]


def rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64


def q4_py(x):
    # ANF form (what RTL/C synthesize); cross-checked vs the LUT below.
    X0 = x & NIBM
    X1 = (x >> 1) & NIBM
    X2 = (x >> 2) & NIBM
    X3 = (x >> 3) & NIBM
    A01, A02, A12 = X0 & X1, X0 & X2, X1 & X2
    A03, A23 = X0 & X3, X2 & X3
    Y0 = NIBM ^ X0 ^ X2 ^ X3 ^ A01 ^ A02 ^ A12
    Y1 = NIBM ^ X0 ^ X2
    Y2 = X0 ^ X1 ^ X3 ^ A01 ^ A12 ^ A03 ^ A23
    Y3 = X1 ^ X3 ^ A01 ^ A12
    return (Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3)) & M64


def q4_lut_py(x):
    y = 0
    for j in range(16):
        y |= Q4_LUT[(x >> (4 * j)) & 0xF] << (4 * j)
    return y & M64


# Fail-loud: ANF must be bit-exact vs the mined LUT (mining verdict basis).
assert all(q4_py(x) == q4_lut_py(x) for x in range(1 << 16)), "Q4 ANF != LUT"


def stage_py(x, a, b):
    y = q4_py(x)
    return (y ^ rotl(y, a) ^ rotl(y, b)) & M64


def mix_py(v, k, stages):
    x = (v ^ k) & M64
    for tag, a, b in stages:
        assert tag == "Q4", tag
        x = stage_py(x, a, b)
    return (x ^ rotl(k, 13)) & M64


def rtl_rot(x, r):
    return "{%s[%d:0], %s[63:%d]}" % (x, r - 1, x, 64 - r) if r else x


Q4_VLOG = """    // Q4: mined bijective quadratic 4-bit S-box (batch-49).
    // ANF bit-exact vs the mined LUT [3,4,15,5,0,6,1,10,14,13,2,12,9,11,8,7].
    function [63:0] q4;
        input [63:0] x;
        reg [63:0] X0, X1, X2, X3, A01, A02, A12, A03, A23;
        reg [63:0] Y0, Y1, Y2, Y3;
        begin
            X0 = x & 64'h1111111111111111;
            X1 = (x >> 1) & 64'h1111111111111111;
            X2 = (x >> 2) & 64'h1111111111111111;
            X3 = (x >> 3) & 64'h1111111111111111;
            A01 = X0 & X1; A02 = X0 & X2; A12 = X1 & X2;
            A03 = X0 & X3; A23 = X2 & X3;
            Y0 = 64'h1111111111111111 ^ X0 ^ X2 ^ X3 ^ A01 ^ A02 ^ A12;
            Y1 = 64'h1111111111111111 ^ X0 ^ X2;
            Y2 = X0 ^ X1 ^ X3 ^ A01 ^ A12 ^ A03 ^ A23;
            Y3 = X1 ^ X3 ^ A01 ^ A12;
            q4 = Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);
        end
    endfunction"""


def main():
    kj, rank, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(kj) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    entries.sort(key=lambda e: e["z"])
    e = entries[rank]
    form = e["form"]
    assert form in ("q4bS4", "q4bS3"), form
    stages = [tuple(s) for s in e["stages"]]
    z = e["z"]
    print("selected rank %d: form=%s z=%.2f stages=%s" % (rank, form, z, stages))
    outdir = "/home/hatch/workspace/mix/exploration/fast_battery/candidates/%s" % name
    os.makedirs(outdir, exist_ok=True)

    L = ["// %s: batch-49 %s schedule (triage z=%.2f)" % (name, form, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         Q4_VLOG,
         "    wire [63:0] x0 = val ^ key;"]
    for j, (tag, a, b) in enumerate(stages):
        xj = "x%d" % j
        cj = "c%d" % (j + 1)
        # Verilog-2005 forbids part-selecting a function-call result --
        # bind to an intermediate wire first (b45 precedent).
        L.append("    wire [63:0] %s = q4(%s);" % (cj, xj))
        L.append("    wire [63:0] x%d = %s ^ %s ^ %s;"
                 % (j + 1, cj, rtl_rot(cj, a), rtl_rot(cj, b)))
    n = len(stages)
    L.append("    assign out = x%d ^ %s;" % (n, rtl_rot("key", 13)))
    L.append("endmodule")
    open(os.path.join(outdir, "rtl.v"), "w").write("\n".join(L) + "\n")

    mp = ['"""%s: batch-49 %s cascade (triage z=%.2f)."""' % (name, form, z),
          "M64 = 0xFFFFFFFFFFFFFFFF",
          "NIBM = 0x1111111111111111",
          "STAGES = %s" % (stages,),
          "def _rotl(x, r):",
          "    r %= 64",
          "    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64",
          "def _q4(x):",
          "    X0 = x & NIBM; X1 = (x >> 1) & NIBM",
          "    X2 = (x >> 2) & NIBM; X3 = (x >> 3) & NIBM",
          "    A01, A02, A12 = X0 & X1, X0 & X2, X1 & X2",
          "    A03, A23 = X0 & X3, X2 & X3",
          "    Y0 = NIBM ^ X0 ^ X2 ^ X3 ^ A01 ^ A02 ^ A12",
          "    Y1 = NIBM ^ X0 ^ X2",
          "    Y2 = X0 ^ X1 ^ X3 ^ A01 ^ A12 ^ A03 ^ A23",
          "    Y3 = X1 ^ X3 ^ A01 ^ A12",
          "    return (Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3)) & M64",
          "def mix_np(V, K):",
          "    import numpy as np",
          "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
          "    x = (x ^ k) & np.uint64(M64)",
          "    for tag, a, b in STAGES:",
          "        y = np.array([_q4(int(v)) for v in x], dtype=np.uint64)",
          "        ra = ((y << np.uint64(a)) | (y >> np.uint64(64-a)))",
          "        rb = ((y << np.uint64(b)) | (y >> np.uint64(64-b)))",
          "        x = (y ^ ra ^ rb) & np.uint64(M64)",
          "    x = (x ^ ((k << np.uint64(13)) | (k >> np.uint64(51)))) & np.uint64(M64)",
          "    return x",
          "def mix(v, k):",
          "    x = (v ^ k) & M64",
          "    for tag, a, b in STAGES:",
          "        y = _q4(x)",
          "        x = (y ^ _rotl(y, a) ^ _rotl(y, b)) & M64",
          "    return (x ^ _rotl(k, 13)) & M64"]
    open(os.path.join(outdir, "model.py"), "w").write("\n".join(mp) + "\n")

    cl = ["#include <stdint.h>",
          "static inline uint64_t rotl64(uint64_t x, int r) {",
          "    r &= 63;",
          "    return r ? (x << r) | (x >> (64 - r)) : x;",
          "}",
          "// Q4: mined bijective quadratic 4-bit S-box (batch-49),",
          "// ANF bit-exact vs LUT [3,4,15,5,0,6,1,10,14,13,2,12,9,11,8,7].",
          "static inline uint64_t q4(uint64_t x) {",
          "    const uint64_t M = 0x1111111111111111ULL;",
          "    uint64_t X0 = x & M, X1 = (x >> 1) & M,",
          "               X2 = (x >> 2) & M, X3 = (x >> 3) & M;",
          "    uint64_t A01 = X0 & X1, A02 = X0 & X2, A12 = X1 & X2,",
          "               A03 = X0 & X3, A23 = X2 & X3;",
          "    uint64_t Y0 = M ^ X0 ^ X2 ^ X3 ^ A01 ^ A02 ^ A12;",
          "    uint64_t Y1 = M ^ X0 ^ X2;",
          "    uint64_t Y2 = X0 ^ X1 ^ X3 ^ A01 ^ A12 ^ A03 ^ A23;",
          "    uint64_t Y3 = X1 ^ X3 ^ A01 ^ A12;",
          "    return Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);",
          "}",
          "// batch-49 %s schedule (triage z=%.2f)" % (form, z),
          "uint64_t mix_hash(uint64_t val, uint64_t key) {",
          "    uint64_t x = val ^ key;",
          "    uint64_t y;"]
    for tag, a, b in stages:
        cl.append("    y = q4(x); x = y ^ rotl64(y,%d) ^ rotl64(y,%d);" % (a, b))
    cl += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    open(os.path.join(outdir, "impl.c"), "w").write("\n".join(cl) + "\n")

    goldens = []
    for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
        goldens.append({"val": hex(v), "key": hex(k),
                        "out": hex(mix_py(v, k, stages))})
    meta = {"name": name,
            "description": "batch-49 %s %d-stage schedule (triage z=%.2f)" % (form, len(stages), z),
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
    # Catches any ANF-vs-mined-LUT drift.
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch49")
    for mod in list(sys.modules):
        if mod == "t6_b49_screen":
            del sys.modules[mod]
    import numpy as np
    import t6_b49_screen as scr
    import random
    random.seed(0xB490)
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
