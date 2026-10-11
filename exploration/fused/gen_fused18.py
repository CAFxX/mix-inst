#!/usr/bin/env python3
"""Fused Wave-18: balanced-XOR-tree 3-term-linear.

Wave-17 finding: hetero t3/chi dilutes diffusion (fz17_a S1 FLAG: LIN 1 + DIFF 2).

Wave-18 hypothesis: the 3-term stage's 4.5u/stage cost comes from an
unbalanced XOR tree. x ^ AND ^ rc ^ rd synthesizes as 3 XORs in series
(3u), but balanced (x^rc) ^ (AND^rd) is 2 levels -- same as chi's 2u.
If Yosys/ABC isn't balancing, forcing it in RTL should cut ~1u/stage:
5 stages x 3.5u = 17.5u, well under 20.1u.

Candidates (all 5-stage, fz15_c rotation sets):
  fz18_a: balanced tree: x_new = (x ^ rc) ^ ((ra&rb) ^ rd)
  fz18_b: balanced tree, fz16_e reversed rotations (robustness)
  fz18_c: 5-stage, alternative: x_new = (x ^ (ra&rb)) ^ (rc ^ rd)
          (groups nonlinear vs linear)

Pre-whiten x ^= k; post x ^= rotl(k,13).
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

# (name, [(a,b,c,d)], tree_mode, desc)
SPECS = [
    ("fz18_a", [
        (1, 7, 13, 29),
        (3, 11, 19, 37),
        (5, 15, 25, 41),
        (9, 21, 31, 49),
        (13, 27, 37, 55),
    ], "split", "5-stage balanced (x^rc)^((ra&rb)^rd), fz15_c rots"),
    ("fz18_b", [
        (13, 27, 37, 55),
        (9, 21, 31, 49),
        (5, 15, 25, 41),
        (3, 11, 19, 37),
        (1, 7, 13, 29),
    ], "split", "5-stage balanced, reversed rotations"),
    ("fz18_c", [
        (1, 7, 13, 29),
        (3, 11, 19, 37),
        (5, 15, 25, 41),
        (9, 21, 31, 49),
        (13, 27, 37, 55),
    ], "group", "5-stage (x^(ra&rb))^(rc^rd), fz15_c rots"),
]

def gen_model(name, stages, mode, desc):
    L = [f'"""Fused wave-18 {name}: {desc} (gen_fused18.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    # Model is functional (XOR is associative); tree shape only matters for RTL.
    for (a, b, c, d) in stages:
        L.append(f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{c}) ^ _rotl(x,{d})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, stages, mode):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused18.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for (a, b, c, d) in stages:
        L.append(f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c}) ^ rotl64(x,{d});")
    L += ["    x = x ^ rotl64(k, 13);", "    return x;", "}", ""]
    return "\n".join(L)

def gen_rtl(name, stages, mode):
    L = [f"// {name}: gen_fused18.py ({mode} tree)",
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
    for i, (a, b, c, d) in enumerate(stages):
        wn = {}
        for r in sorted(set((a, b, c, d))):
            w = f"r{i}_{r}"
            L.append(f"    wire [63:0] {w} = rotl({prev}, {r});")
            wn[r] = w
        L.append(f"    wire [63:0] and{i} = {wn[a]} & {wn[b]};")
        if mode == "split":
            # (x ^ rc) ^ (AND ^ rd): balanced 2-level
            L.append(f"    wire [63:0] t{i}a = {prev} ^ {wn[c]};")
            L.append(f"    wire [63:0] t{i}b = and{i} ^ {wn[d]};")
            L.append(f"    wire [63:0] x{i+1} = t{i}a ^ t{i}b;")
        elif mode == "group":
            # (x ^ AND) ^ (rc ^ rd): nonlinear vs linear groups
            L.append(f"    wire [63:0] t{i}a = {prev} ^ and{i};")
            L.append(f"    wire [63:0] t{i}b = {wn[c]} ^ {wn[d]};")
            L.append(f"    wire [63:0] x{i+1} = t{i}a ^ t{i}b;")
        else:
            raise ValueError(mode)
        prev = f"x{i+1}"
    L.append("    wire [63:0] k13 = rotl(key, 13);")
    L.append(f"    assign out = {prev} ^ k13;")
    L.append("endmodule")
    return "\n".join(L) + "\n"

def main():
    for name, stages, mode, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, mode, desc))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages, mode))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages, mode))
        open(os.path.join(d, "meta.json"), "w").write(
            json.dumps({"name": name, "description": desc, "rtl_top": name,
                        "screen_keys": ["0x123456789abcdef0", "0x0"],
                        "practrand_keys": ["0x123456789abcdef0", "0x0"]}, indent=2))
        print(f"generated {name}")

if __name__ == "__main__":
    main()
