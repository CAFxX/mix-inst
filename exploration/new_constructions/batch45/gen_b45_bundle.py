#!/usr/bin/env python3
"""Generate a fast_battery candidate bundle from a batch-45 KEEP entry.

Usage: gen_b45_bundle.py <keeps.jsonl> <rank> <bundle_name>
  <rank> = index into the z-sorted KEEP list (0 = best).
Writes fast_battery/candidates/<bundle_name>/{rtl.v,model.py,impl.c,meta.json}
with a bit-exactness self-check (C vs Python on 2000 vectors).
Form: chiS  stage(x,a,b) = chi3(x) ^ rotl(chi3(x),a) ^ rotl(chi3(x),b)
  chi3 = chi_3 on 21 contiguous 3-bit lanes (bits 0..62), bit 63 identity
  (b42 lane geometry; y_k = x_k ^ (~x_{k+1} & x_{k+2}) within each lane).
"""
import json
import os
import subprocess
import sys

M64 = 0xFFFFFFFFFFFFFFFF


def rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64


def chi3_py(x):
    # Bitwise chi_3, 21 contiguous lanes; verified bit-exact vs the b42 LUT.
    m0 = 0x9249249249249249 & 0x7FFFFFFFFFFFFFFF  # bits 3j, j<21
    m1 = 0x2492492492492492  # bits 3j+1
    m2 = 0x4924924924924924  # bits 3j+2
    y0 = (x & m0) ^ ((~(x >> 1) & m0) & ((x >> 2) & m0))
    y1 = (x & m1) ^ ((~(x >> 1) & m1) & ((x << 1) & m1))
    y2 = (x & m2) ^ ((~(x << 2) & m2) & ((x << 1) & m2))
    return (y0 | y1 | y2 | (x & 0x8000000000000000)) & M64


def stage_py(x, a, b):
    y = chi3_py(x)
    return (y ^ rotl(y, a) ^ rotl(y, b)) & M64


def mix_py(v, k, stages):
    x = (v ^ k) & M64
    for a, b in stages:
        x = stage_py(x, a, b)
    return (x ^ rotl(k, 13)) & M64


def rtl_rot(x, r):
    return "{%s[%d:0], %s[63:%d]}" % (x, r - 1, x, 64 - r) if r else x


CHI3_VLOG = """    // chi_3 S-box: 21 contiguous 3-bit lanes (bits 0..62), bit 63 identity.
    // y[3j+k] = x[3j+k] ^ (~x[3j+(k+1)%3] & x[3j+(k+2)%3])  (b42 geometry)
    function [63:0] chi3;
        input [63:0] x;
        integer j;
        reg [63:0] y;
        begin
            y[63] = x[63];
            for (j = 0; j < 21; j = j + 1) begin
                y[3*j]   = x[3*j]   ^ (~x[3*j+1] & x[3*j+2]);
                y[3*j+1] = x[3*j+1] ^ (~x[3*j+2] & x[3*j]);
                y[3*j+2] = x[3*j+2] ^ (~x[3*j]   & x[3*j+1]);
            end
            chi3 = y;
        end
    endfunction"""


def main():
    kj, rank, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(kj) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    entries.sort(key=lambda e: e["z"])
    e = entries[rank]
    form = e["form"]
    assert form in ("chiS4", "chiS5"), form
    stages = [tuple(s) for s in e["stages"]]
    z = e["z"]
    print("selected rank %d: form=%s z=%.2f stages=%s" % (rank, form, z, stages))
    outdir = "/home/hatch/workspace/mix/exploration/fast_battery/candidates/%s" % name
    os.makedirs(outdir, exist_ok=True)

    L = ["// %s: batch-45 %s schedule (triage z=%.2f)" % (name, form, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         CHI3_VLOG,
         "    wire [63:0] x0 = val ^ key;"]
    for j, (a, b) in enumerate(stages):
        xj = "x%d" % j
        cj = "c%d" % (j + 1)
        # NOTE: Verilog-2005 forbids part-selecting a function-call result
        # (chi3(xj)[22:0] is a syntax error in Yosys) -- bind to an
        # intermediate wire first (also helps the synthesizer CSE).
        L.append("    wire [63:0] %s = chi3(%s);" % (cj, xj))
        L.append("    wire [63:0] x%d = %s ^ %s ^ %s;"
                 % (j + 1, cj, rtl_rot(cj, a), rtl_rot(cj, b)))
    n = len(stages)
    L.append("    assign out = x%d ^ %s;" % (n, rtl_rot("key", 13)))
    L.append("endmodule")
    open(os.path.join(outdir, "rtl.v"), "w").write("\n".join(L) + "\n")

    mp = ['"""%s: batch-45 %s cascade (triage z=%.2f)."""' % (name, form, z),
          "M64 = 0xFFFFFFFFFFFFFFFF",
          "STAGES = %s" % (stages,),
          "def _rotl(x, r):",
          "    r %= 64",
          "    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64",
          "def _chi3(x):",
          "    m0 = 0x9249249249249249 & 0x7FFFFFFFFFFFFFFF",
          "    m1 = 0x2492492492492492",
          "    m2 = 0x4924924924924924",
          "    y0 = (x & m0) ^ ((~(x >> 1) & m0) & ((x >> 2) & m0))",
          "    y1 = (x & m1) ^ ((~(x >> 1) & m1) & ((x << 1) & m1))",
          "    y2 = (x & m2) ^ ((~(x << 2) & m2) & ((x << 1) & m2))",
          "    return (y0 | y1 | y2 | (x & 0x8000000000000000)) & M64",
          "def mix_np(V, K):",
          "    import numpy as np",
          "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
          "    x = (x ^ k) & np.uint64(M64)",
          "    for a, b in STAGES:",
          "        y = np.array([_chi3(int(v)) for v in x], dtype=np.uint64)",
          "        ra = ((y << np.uint64(a)) | (y >> np.uint64(64-a)))",
          "        rb = ((y << np.uint64(b)) | (y >> np.uint64(64-b)))",
          "        x = (y ^ ra ^ rb) & np.uint64(M64)",
          "    x = (x ^ ((k << np.uint64(13)) | (k >> np.uint64(51)))) & np.uint64(M64)",
          "    return x",
          "def mix(v, k):",
          "    x = (v ^ k) & M64",
          "    for a, b in STAGES:",
          "        y = _chi3(x)",
          "        x = (y ^ _rotl(y, a) ^ _rotl(y, b)) & M64",
          "    return (x ^ _rotl(k, 13)) & M64"]
    open(os.path.join(outdir, "model.py"), "w").write("\n".join(mp) + "\n")

    cl = ["#include <stdint.h>",
          "static inline uint64_t rotl64(uint64_t x, int r) {",
          "    r &= 63;",
          "    return r ? (x << r) | (x >> (64 - r)) : x;",
          "}",
          "// chi_3 S-box, 21 contiguous 3-bit lanes, bit 63 identity (b42)",
          "static inline uint64_t chi3(uint64_t x) {",
          "    uint64_t m0 = 0x9249249249249249ULL & 0x7FFFFFFFFFFFFFFFULL;",
          "    uint64_t m1 = 0x2492492492492492ULL;",
          "    uint64_t m2 = 0x4924924924924924ULL;",
          "    uint64_t y0 = (x & m0) ^ ((~(x >> 1) & m0) & ((x >> 2) & m0));",
          "    uint64_t y1 = (x & m1) ^ ((~(x >> 1) & m1) & ((x << 1) & m1));",
          "    uint64_t y2 = (x & m2) ^ ((~(x << 2) & m2) & ((x << 1) & m2));",
          "    return y0 | y1 | y2 | (x & 0x8000000000000000ULL);",
          "}",
          "// batch-45 %s schedule (triage z=%.2f)" % (form, z),
          "uint64_t mix_hash(uint64_t val, uint64_t key) {",
          "    uint64_t x = val ^ key;",
          "    uint64_t y;"]
    for a, b in stages:
        cl.append("    y = chi3(x); x = y ^ rotl64(y,%d) ^ rotl64(y,%d);" % (a, b))
    cl += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    open(os.path.join(outdir, "impl.c"), "w").write("\n".join(cl) + "\n")

    goldens = []
    for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
        goldens.append({"val": hex(v), "key": hex(k),
                        "out": hex(mix_py(v, k, stages))})
    meta = {"name": name,
            "description": "batch-45 %s %d-stage schedule (triage z=%.2f)" % (form, len(stages), z),
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
    # Cross-check the bundle model against the SCREENER (different chi3
    # implementation: LUT vs bitwise). Catches any lane-geometry drift.
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch45")
    for mod in list(sys.modules):
        if mod == "t6_b45_screen":
            del sys.modules[mod]
    import numpy as np
    import t6_b45_screen as scr
    import random
    random.seed(0xB450)
    bad2 = 0
    for _ in range(500):
        v = random.getrandbits(64)
        k = random.getrandbits(64)
        # screener path, stage-by-stage (LUT chi3 inside apply_stage)
        xx = np.uint64((v ^ k) & 0xFFFFFFFFFFFFFFFF)
        for a, b in stages:
            xx = scr.apply_stage(form, xx, a, b)
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
