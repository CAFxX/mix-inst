#!/usr/bin/env python3
"""Fused Wave-25: shared linear diffusion (cheaper triple fan-out).

Track-3's open direction #2 (orphaned by their pivot): "is there a <4.5u/stage
construction with M = I+R^c+R^e? (e.g., sharing XOR terms across stages)."

Wave-25: precompute p = rotl(x0,c) ^ rotl(x0,e) ONCE from the input, then
5 cheap AND stages each injecting a re-rotated p:
    x_{i+1} = x_i ^ (rotl(x_i,a_i) & rotl(x_i,b_i)) ^ rotl(p,f_i)

Why this might beat the wall: in t3, the linear terms see the PROPAGATED
difference d_i (bad if d_i is bad). Here, rotl(p,f_i) is linear in the
ORIGINAL single-bit delta, which always has perfect triple fan-out.
Every stage gets a dose of good diffusion regardless of d_i.

Cost: p precompute ~0.7u (parallel with stage-1 AND); per-stage ~3.5u
(AND + 2 XORs, one XOR is the p injection). Est ~18u.

Candidates:
  fz25_a: p=rotl(x0,13)^rotl(x0,29), f=(0,13,29,7,31), and-rots danger-free
  fz25_b: p=rotl(x0,7)^rotl(x0,41),  f=(0,17,33,11,47), and-rots variant
  fz25_c: p=rotl(x0,19)^rotl(x0,37), f=(0,23,5,39,15),  and-rots variant

Key schedule: pre-whiten x ^= k; post x ^= rotl(k,13) (wave-15 convention).
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

SPECS = [
    ("fz25_a",
     {"p": (13, 29), "f": (0, 13, 29, 7, 31),
      "ab": [(1, 7), (3, 11), (5, 15), (9, 21), (13, 25)]},
     "5-stage shared-lin-diff: p=rotl(x0,13)^rotl(x0,29)"),
    ("fz25_b",
     {"p": (7, 41), "f": (0, 17, 33, 11, 47),
      "ab": [(2, 9), (4, 13), (6, 17), (11, 23), (15, 27)]},
     "5-stage shared-lin-diff: p=rotl(x0,7)^rotl(x0,41)"),
    ("fz25_c",
     {"p": (19, 37), "f": (0, 23, 5, 39, 15),
      "ab": [(1, 11), (5, 19), (9, 25), (13, 31), (17, 35)]},
     "5-stage shared-lin-diff: p=rotl(x0,19)^rotl(x0,37)"),
]

def gen_model(name, spec, desc):
    pc, pe = spec["p"]
    L = [f'"""Fused wave-25 {name}: {desc} (gen_fused25.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64",
         f"    p = (_rotl(x, {pc}) ^ _rotl(x, {pe})) & M64"]
    for (a, b), f in zip(spec["ab"], spec["f"]):
        L.append(f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(p,{f})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, spec):
    pc, pe = spec["p"]
    L = ["#include <stdint.h>", f"/* {name}: gen_fused25.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;",
         f"    uint64_t p = rotl64(x, {pc}) ^ rotl64(x, {pe});"]
    for (a, b), f in zip(spec["ab"], spec["f"]):
        L.append(f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(p,{f});")
    L += ["    return x ^ rotl64(k, 13);", "}", ""]
    return "\n".join(L)

def gen_rtl(name, spec):
    pc, pe = spec["p"]
    L = [f"// {name}: gen_fused25.py",
         f"module {name}(",
         "    input  wire [63:0] val, input  wire [63:0] key,",
         "    output wire [63:0] out );",
         "    function [63:0] rotl;",
         "        input [63:0] x;",
         "        input integer r;",
         "        begin",
         "            r = r % 64;",
         "            rotl = r ? ((x << r) | (x >> (64 - r))) : x;",
         "        end", "    endfunction",
         "    wire [63:0] s0 = val ^ key;",
         f"    wire [63:0] p = rotl(s0, {pc}) ^ rotl(s0, {pe});"]
    for i, ((a, b), f) in enumerate(zip(spec["ab"], spec["f"])):
        L.append(f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i}, {a}) & rotl(s{i}, {b}))"
                 f" ^ rotl(p, {f});")
    n = len(spec["ab"])
    L.append(f"    assign out = s{n} ^ rotl(key, 13);")
    L.append("endmodule")
    return "\n".join(L) + "\n"

def main():
    for name, spec, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, spec, desc))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, spec))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, spec))
        open(os.path.join(d, "meta.json"), "w").write(
            json.dumps({"name": name, "description": desc, "rtl_top": name,
                        "screen_keys": ["0x123456789abcdef0", "0x0"],
                        "practrand_keys": ["0x123456789abcdef0", "0x0"]}, indent=2))
        print(f"generated {name}")

if __name__ == "__main__":
    main()
