#!/usr/bin/env python3
"""Fused Wave-20: partial rotation-reuse 3-term-linear.

Wave-19 finding: full reuse x^=(ra&rb)^ra^rb destroys diffusion (S1 FLAG
catastrophic, worst|z|~272k). The linear term needs independent rotations.

Wave-20 hypothesis: partial reuse -- 3 distinct rotations instead of 4.
Stage: x ^= (ra&rb) ^ rc ^ ra
Linear part L(x) = x ^ rot(x,c) ^ rot(x,a) is 3-term (odd) bijective.
Uses rotations {a,b,c} (3 distinct). Cheaper than 4-rotation (less routing)
but keeps one independent rotation (c) for diffusion.

If per-stage drops to ~3.8u: 5 stages = 19.0u, beats 20.1u.

Candidates (all 5-stage):
  fz20_a: (a,b,c) = (1,7,13), (3,11,19), (5,15,25), (9,21,31), (13,27,37)
  fz20_b: (a,b,c) = (1,7,29), (3,11,37), (5,15,41), (9,21,49), (13,27,55)
          (c = fz15_c's d rotations, wider)

Pre-whiten x ^= k; post x ^= rotl(k,13).
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

SPECS = [
    ("fz20_a", [
        (1, 7, 13), (3, 11, 19), (5, 15, 25), (9, 21, 31), (13, 27, 37),
    ], "5-stage partial-reuse: x^=(ra&rb)^rc^ra"),
    ("fz20_b", [
        (1, 7, 29), (3, 11, 37), (5, 15, 41), (9, 21, 49), (13, 27, 55),
    ], "5-stage partial-reuse, wider c rotations"),
]

def gen_model(name, stages, desc):
    L = [f'"""Fused wave-20 {name}: {desc} (gen_fused20.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    for (a, b, c) in stages:
        L.append(f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{c}) ^ _rotl(x,{a})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused20.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for (a, b, c) in stages:
        L.append(f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c}) ^ rotl64(x,{a});")
    L += ["    x = x ^ rotl64(k, 13);", "    return x;", "}", ""]
    return "\n".join(L)

def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused20.py",
         f"module {name}(",
         "    input  wire [63:0] val,", "    input  wire [63:0] key,",
         "    output wire [63:0] out", ");",
         "    function [63:0] rotl;", "        input [63:0] x;",
         "        input integer r;", "        begin",
         "            r = r % 64;",
         "            rotl = r ? ((x << r) | (x >> (64 - r))) : x;",
         "        end", "    endfunction",
         "    wire [63:0] x0 = val ^ key;"]
    prev = "x0"
    for i, (a, b, c) in enumerate(stages):
        L.append(f"    wire [63:0] ra{i} = rotl({prev}, {a});")
        L.append(f"    wire [63:0] rb{i} = rotl({prev}, {b});")
        L.append(f"    wire [63:0] rc{i} = rotl({prev}, {c});")
        L.append(f"    wire [63:0] and{i} = ra{i} & rb{i};")
        # Balanced: (x ^ ra) ^ (AND ^ rc)
        L.append(f"    wire [63:0] t{i}a = {prev} ^ ra{i};")
        L.append(f"    wire [63:0] t{i}b = and{i} ^ rc{i};")
        L.append(f"    wire [63:0] x{i+1} = t{i}a ^ t{i}b;")
        prev = f"x{i+1}"
    L.append("    wire [63:0] k13 = rotl(key, 13);")
    L.append(f"    assign out = {prev} ^ k13;")
    L.append("endmodule")
    return "\n".join(L) + "\n"

def main():
    for name, stages, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, desc))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages))
        open(os.path.join(d, "meta.json"), "w").write(
            json.dumps({"name": name, "description": desc, "rtl_top": name,
                        "screen_keys": ["0x123456789abcdef0", "0x0"],
                        "practrand_keys": ["0x123456789abcdef0", "0x0"]}, indent=2))
        print(f"generated {name}")

if __name__ == "__main__":
    main()
