#!/usr/bin/env python3
"""Fused Wave-14: fewer stages of stronger functions.

Wave-13 proved: 5-stage chi/hetero is fast (16.6-19.0u) but S1-FAILS on DIFF.
The diffusion needs more per-stage strength OR more stages.

Wave-14 hypothesis: 4 stages of dual-AND chi (4.86u/stage = 19.4u total)
might diffuse enough to pass S1 while staying under 20.1u.
Also trying 3-stage triple-AND (5.65u/stage = 17u total) as aggressive.

If 4 dchi passes S1: win (19.4u < 20.1u).
If not: the AND-cascade family needs 6 stages, and 20.1u is the floor.
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

SPECS = [
    ("fz14_dchi4a", "dchi2", [
        (1, 7, 13, 29, 5),
        (5, 13, 23, 41, 11),
        (11, 23, 33, 51, 17),
        (17, 31, 43, 59, 23),
    ], "4-stage dual-AND chi: x ^= (ra&rb)^(rc&rd)^re"),
    ("fz14_dchi4b", "dchi2", [
        (2, 9, 17, 35, 7),
        (7, 15, 27, 45, 13),
        (13, 25, 37, 55, 19),
        (19, 33, 47, 61, 27),
    ], "4-stage dual-AND chi (alt rotations)"),
    ("fz14_tchi3a", "tchi", [
        (1, 7, 13, 19, 29, 37, 5),
        (7, 15, 25, 35, 45, 55, 13),
        (13, 23, 33, 43, 53, 61, 21),
    ], "3-stage triple-AND chi: x ^= (ra&rb)^(rc&rd)^(re&rf)^rg"),
]

def gen_model(name, op, stages, desc):
    L = [f'"""Fused wave-14 {name}: {desc} (gen_fused14.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    for st in stages:
        if op == "dchi2":
            a,b,c,d,e = st
            L.append(f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ (_rotl(x,{c}) & _rotl(x,{d})) ^ _rotl(x,{e})) & M64")
        elif op == "tchi":
            a,b,c,d,e,f,g = st
            L.append(f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ (_rotl(x,{c}) & _rotl(x,{d})) ^ (_rotl(x,{e}) & _rotl(x,{f})) ^ _rotl(x,{g})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, op, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused14.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for st in stages:
        rs = ", ".join(str(r) for r in st)
        L.append(f"    {{ uint64_t r[] = {{{rs}}};")
        if op == "dchi2":
            L.append("      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }")
        elif op == "tchi":
            L.append("      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ (rotl64(x,r[4]) & rotl64(x,r[5])) ^ rotl64(x,r[6]); }")
    L += ["    x = x ^ rotl64(k, 13);", "    return x;", "}", ""]
    return "\n".join(L)

def gen_rtl(name, op, stages):
    L = [f"// {name}: gen_fused14.py",
         f"module {name}(",
         "    input  wire [63:0] v,", "    input  wire [63:0] k,",
         "    output wire [63:0] out", ");",
         "    function [63:0] rotl;", "        input [63:0] x;",
         "        input integer r;", "        begin",
         "            r = r % 64;",
         "            rotl = r ? ((x << r) | (x >> (64 - r))) : x;",
         "        end", "    endfunction",
         "    wire [63:0] x0 = v ^ k;"]
    prev = "x0"
    for i, st in enumerate(stages):
        wn = {}
        for r in sorted(set(st)):
            w = f"r{i}_{r}"
            L.append(f"    wire [63:0] {w} = rotl({prev}, {r});")
            wn[r] = w
        if op == "dchi2":
            a,b,c,d,e = st
            L.append(f"    wire [63:0] x{i+1} = ({prev} ^ ({wn[a]} & {wn[b]}) ^ ({wn[c]} & {wn[d]}) ^ {wn[e]});")
        elif op == "tchi":
            a,b,c,d,e,f,g = st
            L.append(f"    wire [63:0] x{i+1} = ({prev} ^ ({wn[a]} & {wn[b]}) ^ ({wn[c]} & {wn[d]}) ^ ({wn[e]} & {wn[f]}) ^ {wn[g]});")
        prev = f"x{i+1}"
    L.append(f"    wire [63:0] k13 = rotl(k, 13);")
    L.append(f"    assign out = {prev} ^ k13;")
    L.append("endmodule")
    return "\n".join(L) + "\n"

def main():
    for name, op, stages, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, op, stages, desc))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, op, stages))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, op, stages))
        open(os.path.join(d, "meta.json"), "w").write(
            json.dumps({"name": name, "description": desc, "rtl_top": name,
                        "screen_keys": ["0x123456789abcdef0", "0x0"],
                        "practrand_keys": ["0x123456789abcdef0", "0x0"]}, indent=2))
        print(f"generated {name}")

if __name__ == "__main__":
    main()
