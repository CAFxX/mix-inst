#!/usr/bin/env python3
"""Fused Wave-23: 3-term-linear + AND heterogeneous 5-stage — NEW AXIS.

Wave-22 verdict: fz22_maj4a (16.8u) S1-FLAG (LIN 10/10 + DIFF 10/10) — the
4-stage majority-cascade dies with the same signature as dd7/wave-13/14.
The 5-stage DIFF wall holds for every uniform family.

Remaining untested: HETEROGENEOUS 5-stage mixing the one S1-clean 5-stage
family (3-term-linear, fz15_c 22.6u clean) with cheap AND stages (3.35u).
Wave-17 found t3/chi hetero dilutes diffusion — but t3/AND was never
tested, and AND is the "native" nonlinear term of the t3 stage.

Hypothesis: t3 stages provide the S1-clean diffusion backbone; AND stages
are cheap fill. 2 t3 + 3 AND ~= 19.05u < 20.1u. If the hetero doesn't
dilute the t3 backbone's diffusion, this beats the frontier.

Stage forms:
  t3 : x ^= (ra & rb) ^ rc ^ rd   (~4.5u, from fz15_c's S1-clean sets)
  AND: x ^= (ra & rb) ^ rc        (~3.35u, danger-zone-free rotations)

Key schedule: pre-whiten x ^= k; post x ^= rotl(k,13) (wave-15 convention).

Candidates:
  fz23_a: [t3, AND, t3, AND, AND]  interleaved, t3 early+mid
  fz23_b: [t3, t3, AND, AND, AND]  t3 backbone first
  fz23_c: [AND, t3, AND, t3, AND]  alternating
  fz23_d: [t3, AND, t3, AND, t3]   3 t3 + 2 AND (~20.2u, diffusion margin)
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

# stage: ("t3", (a,b,c,d)) or ("and", (a,b,c))
SPECS = [
    ("fz23_a",
     [("t3", (1, 7, 13, 29)),
      ("and", (3, 11, 17)),
      ("t3", (5, 15, 25, 41)),
      ("and", (9, 21, 43)),
      ("and", (13, 23, 47))],
     "5-stage hetero t3/AND: [t3,AND,t3,AND,AND]"),
    ("fz23_b",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 21)),
      ("and", (9, 23, 43)),
      ("and", (13, 25, 47))],
     "5-stage hetero t3/AND: [t3,t3,AND,AND,AND]"),
    ("fz23_c",
     [("and", (1, 7, 13)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 25)),
      ("t3", (9, 21, 31, 49)),
      ("and", (13, 27, 43))],
     "5-stage hetero t3/AND: [AND,t3,AND,t3,AND]"),
    ("fz23_d",
     [("t3", (1, 7, 13, 29)),
      ("and", (3, 11, 17)),
      ("t3", (5, 15, 25, 41)),
      ("and", (9, 21, 43)),
      ("t3", (13, 27, 37, 55))],
     "5-stage hetero t3/AND: [t3,AND,t3,AND,t3] (margin)"),
]

def stage_py(kind, rots):
    if kind == "t3":
        a, b, c, d = rots
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
                f" ^ _rotl(x,{c}) ^ _rotl(x,{d})) & M64")
    a, b, c = rots
    return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
            f" ^ _rotl(x,{c})) & M64")

def gen_model(name, stages, desc):
    L = [f'\"\"\"Fused wave-23 {name}: {desc} (gen_fused23.py).\"\"\"',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    for kind, rots in stages:
        L.append(stage_py(kind, rots))
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def stage_c(kind, rots):
    if kind == "t3":
        a, b, c, d = rots
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}))"
                f" ^ rotl64(x,{c}) ^ rotl64(x,{d});")
    a, b, c = rots
    return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}))"
            f" ^ rotl64(x,{c});")

def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused23.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for kind, rots in stages:
        L.append(stage_c(kind, rots))
    L += ["    return x ^ rotl64(k, 13);",
          "}", ""]
    return "\n".join(L)

def stage_v(kind, rots, i):
    if kind == "t3":
        a, b, c, d = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i}, {a}) & rotl(s{i}, {b}))"
                f" ^ rotl(s{i}, {c}) ^ rotl(s{i}, {d});")
    a, b, c = rots
    return (f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i}, {a}) & rotl(s{i}, {b}))"
            f" ^ rotl(s{i}, {c});")

def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused23.py",
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
         "    wire [63:0] s0 = val ^ key;"]
    for i, (kind, rots) in enumerate(stages):
        L.append(stage_v(kind, rots, i))
    n = len(stages)
    L.append(f"    assign out = s{n} ^ rotl(key, 13);")
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
