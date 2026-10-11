#!/usr/bin/env python3
"""Fused Wave-22: carry-save redundant-state mixer — NEW AXIS.

Wave-21 finding (pending final multiply numbers): word-level ops with carry
propagation (add: 44-83u, shift-add: 73-79u) are far too slow per stage.
The 64-bit multiply was already killed at 88.7u.

New idea: keep the addition-like nonlinearity (majority/carry) but ELIMINATE
carry propagation by holding redundant (sum, carry) state across stages.
Each stage is one layer of full adders — no carry chain.

Stage (state s[63:0], c[63:0]):
    ra = rotl(s, a);  rb = rotl(c, b)      // wires
    s' = s ^ c ^ ra ^ rb                    // XOR4, ~2u
    m  = maj(s, c, ra)                      // (s&c)|(s&ra)|(c&ra), ~2u
    c' = rotl(m, 1)                         // carry shift (wires)

Init: s = v ^ k; c = rotl(k, 13).
Final: sc = s ^ c; o = sc ^ rotl(sc, 17).

Why this might work:
- Majority is balanced (4/8) unlike AND (1/4) — better LIN behavior.
- 2u/stage (XOR4 and MAJ3 in parallel); 6 stages ~ 12u < 20.1u.
- Cross-bit coupling via carry shift + rotations; long-range via (a,b).
- Genuinely untested: no prior wave used redundant state or majority.

Candidates:
  fz22_cs6a: 6-stage, (a,b) = (1,11),(7,19),(13,29),(17,37),(23,43),(31,47)
  fz22_cs5a: 5-stage, (a,b) = (1,11),(7,19),(13,29),(17,37),(23,43)
  fz22_cs6b: 6-stage, (a,b) = (3,13),(9,23),(15,33),(21,41),(27,49),(35,53)
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

SPECS = [
    ("fz22_cs6a",
     [(1, 11), (7, 19), (13, 29), (17, 37), (23, 43), (31, 47)],
     "6-stage carry-save: s^=c^ra^rb, c=maj(s,c,ra)<<<1"),
    ("fz22_cs5a",
     [(1, 11), (7, 19), (13, 29), (17, 37), (23, 43)],
     "5-stage carry-save"),
    ("fz22_cs6b",
     [(3, 13), (9, 23), (15, 33), (21, 41), (27, 49), (35, 53)],
     "6-stage carry-save, alt schedule"),
]

def gen_model(name, stages, desc):
    L = [f'\"\"\"Fused wave-22 {name}: {desc} (gen_fused22.py).\"\"\"',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def _maj(a, b, c):",
         "    return (a & b) | (a & c) | (b & c)",
         "def mix_np(V, K):",
         "    s = np.asarray(V, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)",
         "    c = _rotl(np.asarray(K, dtype=np.uint64), 13)"]
    for (a, b) in stages:
        L.append(f"    ra = _rotl(s, {a}); rb = _rotl(c, {b})")
        L.append(f"    m = _maj(s, c, ra)")
        L.append(f"    s = (s ^ c ^ ra ^ rb) & M64")
        L.append(f"    c = _rotl(m, 1)")
    L += ["    sc = (s ^ c) & M64",
          "    return (sc ^ _rotl(sc, 17)) & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused22.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t s = v ^ k;",
         "    uint64_t c = rotl64(k, 13);"]
    for (a, b) in stages:
        L.append(f"    {{ uint64_t ra = rotl64(s, {a}), rb = rotl64(c, {b});")
        L.append(f"       uint64_t m = (s & c) | (s & ra) | (c & ra);")
        L.append(f"       s = s ^ c ^ ra ^ rb;")
        L.append(f"       c = rotl64(m, 1); }}")
    L += ["    uint64_t sc = s ^ c;",
          "    return sc ^ rotl64(sc, 17);",
          "}", ""]
    return "\n".join(L)

def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused22.py",
         f"module {name}(",
         "    input  wire [63:0] val,", "    input  wire [63:0] key,",
         "    output wire [63:0] out", ");",
         "    function [63:0] rotl;",
         "        input [63:0] x;",
         "        input integer r;",
         "        begin",
         "            r = r % 64;",
         "            rotl = r ? ((x << r) | (x >> (64 - r))) : x;",
         "        end", "    endfunction",
         "    wire [63:0] s0 = val ^ key;",
         "    wire [63:0] c0 = rotl(key, 13);"]
    for i, (a, b) in enumerate(stages):
        L.append(f"    wire [63:0] ra{i} = rotl(s{i}, {a});")
        L.append(f"    wire [63:0] rb{i} = rotl(c{i}, {b});")
        L.append(f"    wire [63:0] m{i} = (s{i} & c{i}) | (s{i} & ra{i}) | (c{i} & ra{i});")
        L.append(f"    wire [63:0] s{i+1} = s{i} ^ c{i} ^ ra{i} ^ rb{i};")
        L.append(f"    wire [63:0] c{i+1} = rotl(m{i}, 1);")
    n = len(stages)
    L.append(f"    wire [63:0] sc = s{n} ^ c{n};")
    L.append(f"    assign out = sc ^ rotl(sc, 17);")
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
