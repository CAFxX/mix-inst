#!/usr/bin/env python3
"""Fused Wave-15: 3-term linear passthrough — genuinely new axis.

Waves 13-14 verdict: the `x ^= (AND-terms) ^ rc` AND-cascade family needs
>=6 stages for S1-clean (5-stage: DIFF worst_z 100-500; 4-stage: LIN+DIFF;
3-stage: worst_z ~20000). 20.1u (al_and6a) is the floor for THAT family.

Wave-15 hypothesis: differential diffusion speed is set by the LINEAR part's
weight expansion. chi's single `^rc` gives 2x weight growth/stage
(d -> d^rot(d,c)). A 3-term linear passthrough `^ rc ^ rd` gives 3x
(d -> d^rot(d,c)^rot(d,d), weight 1->3 for single-bit d, c,d distinct
nonzero). 3^4 = 81 > 64: 4 stages should fully diffuse. Per-stage cost is
~3u (one AND + 2-level XOR tree), so 4 stages ~= 12u -- far under 20.1u.

The 3-term linear L(x) = x ^ rot(x,c) ^ rot(x,d) is PROVEN bijective
(CANDIDATE_BRIEF: 1+x^c+x^d evaluated at 1 is 1, so x+1 does not divide it).
Even-term linears (2-term, 4-term) are NOT bijective -- never use.

Stage form: x ^= (ra & rb) ^ rc ^ rd   (nonlinear AND + 3-term linear)
Key schedule: pre-whiten x ^= k; post x ^= rotl(k,13) (waves 13-14 convention).

Candidates:
  fz15_a : 4-stage, rotation set A (primary hypothesis)
  fz15_b : 4-stage, rotation set B (robustness)
  fz15_c : 5-stage (safety: if 4 fails, does 5 pass? measures the threshold)
  fz15_d : 3-stage (aggressive: tests the 3^k weight-growth math; 3^3=27<64
           predicts FAIL -- a PASS would be a major surprise)
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

# (name, [(a,b,c,d) per stage], description)
SPECS = [
    ("fz15_a", [
        (1, 7, 13, 29),
        (3, 11, 19, 37),
        (7, 17, 23, 43),
        (11, 23, 31, 47),
    ], "4-stage 3-term-linear chi: x ^= (ra&rb)^rc^rd"),
    ("fz15_b", [
        (2, 9, 17, 33),
        (5, 13, 21, 39),
        (9, 19, 27, 45),
        (13, 27, 35, 53),
    ], "4-stage 3-term-linear chi (alt rotations)"),
    ("fz15_c", [
        (1, 7, 13, 29),
        (3, 11, 19, 37),
        (5, 15, 25, 41),
        (9, 21, 31, 49),
        (13, 27, 37, 55),
    ], "5-stage 3-term-linear chi (safety)"),
    ("fz15_d", [
        (1, 7, 13, 29),
        (5, 15, 25, 41),
        (11, 23, 37, 53),
    ], "3-stage 3-term-linear chi (aggressive)"),
]

def gen_model(name, stages, desc):
    L = [f'"""Fused wave-15 {name}: {desc} (gen_fused15.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    for (a, b, c, d) in stages:
        L.append(f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{c}) ^ _rotl(x,{d})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused15.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for (a, b, c, d) in stages:
        L.append(f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c}) ^ rotl64(x,{d});")
    L += ["    x = x ^ rotl64(k, 13);", "    return x;", "}", ""]
    return "\n".join(L)

def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused15.py",
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
    for i, (a, b, c, d) in enumerate(stages):
        wn = {}
        for r in sorted(set((a, b, c, d))):
            w = f"r{i}_{r}"
            L.append(f"    wire [63:0] {w} = rotl({prev}, {r});")
            wn[r] = w
        L.append(f"    wire [63:0] x{i+1} = ({prev} ^ ({wn[a]} & {wn[b]}) ^ {wn[c]} ^ {wn[d]});")
        prev = f"x{i+1}"
    L.append("    wire [63:0] k13 = rotl(k, 13);")
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
