#!/usr/bin/env python3
"""Fused Wave-16: co-design around fz15_c's 3-term-linear success.

fz15_c (5-stage `x ^= (ra&rb)^rc^rd`, 22.6u): S1 CAL_PASS + S2 PASS.
fz15_a/b (4-stage, 18.7u): S1 FLAG (LIN 10 + DIFF 10).
fz15_d (3-stage, 14.4u): S1 FLAG (predicted).

The 3x/stage linear weight-growth math (3^4=81>64) is insufficient --
the AND-term differential diffusion is the bottleneck. Wave-16 co-designs
around what made fz15_c work:

Batch A (4-stage, push below 20.1u):
  fz16_a: 4-stage using fz15_c's first-4 rotation sets (is rotation set the key?)
  fz16_b: 4-stage dual-AND per stage: x ^= (ra&rb)^(rc&rd)^re^rf^rg
          (more nonlinearity/stage; tests AND-density hypothesis)
  fz16_c: 4-stage chi-style: x ^= (ra&(rb^rc))^rd^re^rf
          (chi nonlinearity + 3-term linear)

Batch B (5-stage, push below 20.1u via speed):
  fz16_d: 5-stage, small Yosys-friendly rotations (speed-optimized)
  fz16_e: 5-stage, fz15_c rotation sets permuted (robustness + speed variance)

All keep: pre-whiten x ^= k; post x ^= rotl(k,13).
3-term linear L(x) = x^rot(x,e)^rot(x,f) proven bijective (odd terms).
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

# Each spec: (name, [stages], desc)
# Stage formats:
#   ("and", a,b, e,f)       : x ^= (ra&rb)^re^rf
#   ("dual", a,b,c,d, e,f,g): x ^= (ra&rb)^(rc&rd)^re^rf^rg
#   ("chi3", a,b,c, e,f,g)  : x ^= (ra&(rb^rc))^re^rf^rg
SPECS = [
    ("fz16_a", [
        ("and", 1, 7, 13, 29),
        ("and", 3, 11, 19, 37),
        ("and", 5, 15, 25, 41),
        ("and", 9, 21, 31, 49),
    ], "4-stage 3-term-linear, fz15_c first-4 rotation sets"),
    ("fz16_b", [
        ("dual", 1, 7, 13, 29, 37, 43, 53),
        ("dual", 3, 11, 19, 31, 41, 47, 59),
        ("dual", 5, 15, 23, 37, 43, 53, 61),
        ("dual", 9, 21, 29, 41, 49, 57, 7),
    ], "4-stage dual-AND 3-term-linear: x^=(ra&rb)^(rc&rd)^re^rf^rg"),
    ("fz16_c", [
        ("chi3", 1, 7, 13, 29, 37, 43),
        ("chi3", 3, 11, 19, 31, 41, 47),
        ("chi3", 5, 15, 25, 37, 43, 53),
        ("chi3", 9, 21, 31, 41, 49, 57),
    ], "4-stage chi-style 3-term-linear: x^=(ra&(rb^rc))^rd^re^rf"),
    ("fz16_d", [
        ("and", 1, 5, 9, 13),
        ("and", 2, 6, 11, 17),
        ("and", 3, 8, 14, 19),
        ("and", 5, 11, 18, 23),
        ("and", 7, 13, 21, 27),
    ], "5-stage 3-term-linear, small Yosys-friendly rotations (speed)"),
    ("fz16_e", [
        ("and", 13, 27, 37, 55),
        ("and", 9, 21, 31, 49),
        ("and", 5, 15, 25, 41),
        ("and", 3, 11, 19, 37),
        ("and", 1, 7, 13, 29),
    ], "5-stage 3-term-linear, fz15_c rotations reversed (robustness)"),
]

def stage_expr_py(kind, p):
    if kind == "and":
        a, b, e, f = p
        return f"(_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{e}) ^ _rotl(x,{f})"
    if kind == "dual":
        a, b, c, d, e, f, g = p
        return (f"(_rotl(x,{a}) & _rotl(x,{b})) ^ (_rotl(x,{c}) & _rotl(x,{d})) "
                f"^ _rotl(x,{e}) ^ _rotl(x,{f}) ^ _rotl(x,{g})")
    if kind == "chi3":
        a, b, c, e, f, g = p
        return (f"(_rotl(x,{a}) & (_rotl(x,{b}) ^ _rotl(x,{c}))) "
                f"^ _rotl(x,{e}) ^ _rotl(x,{f}) ^ _rotl(x,{g})")
    raise ValueError(kind)

def stage_expr_c(kind, p):
    if kind == "and":
        a, b, e, f = p
        return f"(rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{e}) ^ rotl64(x,{f})"
    if kind == "dual":
        a, b, c, d, e, f, g = p
        return (f"(rotl64(x,{a}) & rotl64(x,{b})) ^ (rotl64(x,{c}) & rotl64(x,{d})) "
                f"^ rotl64(x,{e}) ^ rotl64(x,{f}) ^ rotl64(x,{g})")
    if kind == "chi3":
        a, b, c, e, f, g = p
        return (f"(rotl64(x,{a}) & (rotl64(x,{b}) ^ rotl64(x,{c}))) "
                f"^ rotl64(x,{e}) ^ rotl64(x,{f}) ^ rotl64(x,{g})")
    raise ValueError(kind)

def stage_rots(kind, p):
    return sorted(set(p))

def gen_model(name, stages, desc):
    L = [f'"""Fused wave-16 {name}: {desc} (gen_fused16.py)."""',
         "import numpy as np", "",
         "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
         "def mix_np(V, K):",
         "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
         "    x = (x ^ k) & M64"]
    for kind, *p in stages:
        L.append(f"    x = (x ^ ({stage_expr_py(kind, p)})) & M64")
    L += ["    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)

def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused16.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {",
         "    uint64_t x = v ^ k;"]
    for kind, *p in stages:
        L.append(f"    x = x ^ ({stage_expr_c(kind, p)});")
    L += ["    x = x ^ rotl64(k, 13);", "    return x;", "}", ""]
    return "\n".join(L)

def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused16.py",
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
        for r in stage_rots(kind, p):
            w = f"r{i}_{r}"
            L.append(f"    wire [63:0] {w} = rotl({prev}, {r});")
            wn[r] = w
        if kind == "and":
            a, b, e, f = p
            expr = f"({prev} ^ ({wn[a]} & {wn[b]}) ^ {wn[e]} ^ {wn[f]})"
        elif kind == "dual":
            a, b, c, d, e, f, g = p
            expr = (f"({prev} ^ ({wn[a]} & {wn[b]}) ^ ({wn[c]} & {wn[d]}) "
                    f"^ {wn[e]} ^ {wn[f]} ^ {wn[g]})")
        elif kind == "chi3":
            a, b, c, e, f, g = p
            expr = (f"({prev} ^ ({wn[a]} & ({wn[b]} ^ {wn[c]})) "
                    f"^ {wn[e]} ^ {wn[f]} ^ {wn[g]})")
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
