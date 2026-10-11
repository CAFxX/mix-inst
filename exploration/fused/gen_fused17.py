#!/usr/bin/env python3
"""Fused Wave-17: hetero 3-term-linear + chi co-design.

Wave-16 findings:
- 4-stage 3-term-linear structurally dead (fz16_a: LIN 10 + DIFF 10 even
  with fz15_c's own rotations). Family needs >=5 stages.
- 5-stage 3-term-linear: fz15_c clean (22.6u), fz16_e borderline (1 RD rej).
- Per-stage: 3-term-linear 4.5u vs chi 3.35u. 5x4.5=22.6u > 20.1u frontier.

Wave-17 hypothesis: hetero 5-stage mixing 3-term-linear (strong diffuser)
with chi (cheap). 3x4.5 + 2x3.35 = 20.2u -- at the frontier, with the
3-term stages providing the diffusion that 5x chi lacks.

Stage forms:
  ("t3", a,b, e,f) : x ^= (ra&rb)^re^rf   (3-term linear)
  ("chi", a,b, c)  : x ^= (ra&rb)^rc       (standard chi)

Candidates:
  fz17_a: t3, chi, t3, chi, t3 (3-term bookends + middle)
  fz17_b: chi, t3, chi, t3, chi (chi bookends)
  fz17_c: t3, t3, chi, t3, chi (front-loaded diffusion)

Rotations from fz15_c's successful set; chi rotations chosen compatible.
Pre-whiten x ^= k; post x ^= rotl(k,13).
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

SPECS = [
    ("fz17_a", [
        ("t3", 1, 7, 13, 29),
        ("chi", 3, 11, 19),
        ("t3", 5, 15, 25, 41),
        ("chi", 9, 21, 31),
        ("t3", 13, 27, 37, 55),
    ], "5-stage hetero t3/chi/t3/chi/t3"),
    ("fz17_b", [
        ("chi", 1, 7, 13),
        ("t3", 3, 11, 19, 37),
        ("chi", 5, 15, 25),
        ("t3", 9, 21, 31, 49),
        ("chi", 13, 27, 37),
    ], "5-stage hetero chi/t3/chi/t3/chi"),
    ("fz17_c", [
        ("t3", 1, 7, 13, 29),
        ("t3", 3, 11, 19, 37),
        ("chi", 5, 15, 25),
        ("t3", 9, 21, 31, 49),
        ("chi", 13, 27, 37),
    ], "5-stage hetero t3/t3/chi/t3/chi (front-loaded)"),
]

def expr_py(kind, p):
    if kind == "t3":
        a, b, e, f = p
        return f"(_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{e}) ^ _rotl(x,{f})"
    if kind == "chi":
        a, b, c = p
        return f"(_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{c})"
    raise ValueError(kind)

def expr_c(kind, p):
    if kind == "t3":
        a, b, e, f = p
        return f"(rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{e}) ^ rotl64(x,{f})"
    if kind == "chi":
        a, b, c = p
        return f"(rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c})"
    raise ValueError(kind)

def gen_model(name, stages, desc):
    L = [f'"""Fused wave-17 {name}: {desc} (gen_fused17.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    for kind, *p in stages:
        L.append(f"    x = (x ^ ({expr_py(kind, p)})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused17.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for kind, *p in stages:
        L.append(f"    x = x ^ ({expr_c(kind, p)});")
    L += ["    x = x ^ rotl64(k, 13);", "    return x;", "}", ""]
    return "\n".join(L)

def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused17.py",
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
    for i, (kind, *p) in enumerate(stages):
        wn = {}
        for r in sorted(set(p)):
            w = f"r{i}_{r}"
            L.append(f"    wire [63:0] {w} = rotl({prev}, {r});")
            wn[r] = w
        if kind == "t3":
            a, b, e, f = p
            expr = f"({prev} ^ ({wn[a]} & {wn[b]}) ^ {wn[e]} ^ {wn[f]})"
        elif kind == "chi":
            a, b, c = p
            expr = f"({prev} ^ ({wn[a]} & {wn[b]}) ^ {wn[c]})"
        else:
            raise ValueError(kind)
        L.append(f"    wire [63:0] x{i+1} = {expr};")
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
