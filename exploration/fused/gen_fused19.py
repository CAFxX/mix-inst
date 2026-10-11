#!/usr/bin/env python3
"""Fused Wave-19: rotation-reuse 3-term-linear.

Wave-18 finding: balanced XOR tree gives 22.5u (no speedup). The 4.5u/stage
cost is fundamental to the 4-distinct-rotation structure.

Wave-19 hypothesis: reuse the AND rotations in the linear term.
Stage: x ^= (ra&rb) ^ ra ^ rb
The linear part L(x) = x ^ rot(x,a) ^ rot(x,b) is 3-term (odd) so bijective
(1+1+1=1 at x=1, x+1 does not divide it). Only 2 distinct rotations/stage
vs 4 -- should synthesize much faster (less routing, smaller XOR tree).

If per-stage drops from 4.5u to ~3.5u: 5 stages = 17.5u, beats 20.1u.

Candidates (all 5-stage):
  fz19_a: (a,b) = (1,7), (3,11), (5,15), (9,21), (13,27)
  fz19_b: (a,b) = (1,13), (7,29), (3,19), (11,37), (5,25) (wider spread)
  fz19_c: 6-stage rotation-reuse (safety: if 5-stage diffusion insufficient)

Pre-whiten x ^= k; post x ^= rotl(k,13).
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

SPECS = [
    ("fz19_a", [
        (1, 7), (3, 11), (5, 15), (9, 21), (13, 27),
    ], "5-stage rotation-reuse: x^=(ra&rb)^ra^rb"),
    ("fz19_b", [
        (1, 13), (7, 29), (3, 19), (11, 37), (5, 25),
    ], "5-stage rotation-reuse, wider spread"),
    ("fz19_c", [
        (1, 7), (3, 11), (5, 15), (9, 21), (13, 27), (17, 33),
    ], "6-stage rotation-reuse (safety)"),
]

def gen_model(name, stages, desc):
    L = [f'"""Fused wave-19 {name}: {desc} (gen_fused19.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    for (a, b) in stages:
        L.append(f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{a}) ^ _rotl(x,{b})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused19.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for (a, b) in stages:
        L.append(f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{a}) ^ rotl64(x,{b});")
    L += ["    x = x ^ rotl64(k, 13);", "    return x;", "}", ""]
    return "\n".join(L)

def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused19.py",
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
    for i, (a, b) in enumerate(stages):
        L.append(f"    wire [63:0] ra{i} = rotl({prev}, {a});")
        L.append(f"    wire [63:0] rb{i} = rotl({prev}, {b});")
        L.append(f"    wire [63:0] and{i} = ra{i} & rb{i};")
        # Balanced: (x ^ ra) ^ (AND ^ rb)
        L.append(f"    wire [63:0] t{i}a = {prev} ^ ra{i};")
        L.append(f"    wire [63:0] t{i}b = and{i} ^ rb{i};")
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
