#!/usr/bin/env python3
"""Wave-32: 5-stage `x ^=` with 3-input-AND (and3) nonlinearity.

New primitive `and3` (a,b,c,d): x ^= (ra & rb & rc) ^ rd.
Rationale: the 5-stage DIFF wall (track-3) covers 2-input AND/OR cascades;
the chi-final escape died at S3 (low-bit). A 3-input AND has strictly
stronger per-stage nonlinearity (higher algebraic degree, different
differential spectrum) — a new escape axis. Pipeline: proxy (marg2+DIFF)
-> S0 -> S1 -> **S3-16MB early** (process lesson: S1+S2 missed the S3 kill)
-> S2 -> S3-full.

Candidates:
  fz32_a: [and,and,and,and,and3]          (and3 final on and-prefix)
  fz32_b: [t3,t3,and,and,and3]            (and3 final on hetero prefix)
  fz32_c: [and3,and3,and3,and3,and3]      (pure 3-input AND)
  fz32_d: [and,and,and3,and,and3]         (interleaved)
"""
import json, os, sys

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")
M64 = 0xFFFFFFFFFFFFFFFF

def rotl(x, r):
    r &= 63
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64

def apply(x, st):
    k, rots = st
    if k == "and":
        a, b, c = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    if k == "t3":
        a, b, c, d = rots
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, d)) & M64
    if k == "and3":
        a, b, c, d = rots
        return (x ^ (rotl(x, a) & rotl(x, b) & rotl(x, c)) ^ rotl(x, d)) & M64
    raise ValueError(st)

C_PRELUDE = """#include <stdint.h>
/* {name}: wave32 and3 */
static inline uint64_t rotl64(uint64_t x, unsigned r) {{
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }}
uint64_t mix_hash(uint64_t v, uint64_t k) {{
    uint64_t x = v ^ k;
{stages}
    x = x ^ rotl64(k, 13);
    return x;
}}
"""

def stage_c(st):
    k, rots = st
    if k == "and":
        a, b, c = rots
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c});")
    if k == "t3":
        a, b, c, d = rots
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}))"
                f" ^ rotl64(x,{c}) ^ rotl64(x,{d});")
    if k == "and3":
        a, b, c, d = rots
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}) & rotl64(x,{c}))"
                f" ^ rotl64(x,{d});")
    raise ValueError(st)

PY_PRELUDE = '''"""{name}: wave32 and3"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl(x, r):
    r &= 63
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M64 if r else x & M64
def mix_np(v, k):
    x = (np.uint64(v) ^ np.uint64(k))
{stages}
    x = (x ^ _rotl(np.uint64(k), 13)) & M64
    return x
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
'''

def stage_py(st):
    k, rots = st
    if k == "and":
        a, b, c = rots
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{c})) & M64")
    if k == "t3":
        a, b, c, d = rots
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
                f" ^ _rotl(x,{c}) ^ _rotl(x,{d})) & M64")
    if k == "and3":
        a, b, c, d = rots
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}) & _rotl(x,{c}))"
                f" ^ _rotl(x,{d})) & M64")
    raise ValueError(st)

V_PRELUDE = """// {name}: wave32 and3
module {name}(input [63:0] v, input [63:0] k, output [63:0] h);
function [63:0] rotl64(input [63:0] x, input [5:0] r);
  rotl64 = r == 0 ? x : ((x << r) | (x >> (6'd64 - r)));
endfunction
wire [63:0] x0 = v ^ k;
{stages}
assign h = x_last ^ rotl64(k, 13);
endmodule
"""

def stage_v(i, st):
    k, rots = st
    if k == "and":
        a, b, c = rots
        return f"wire [63:0] x{i+1} = x{i} ^ (rotl64(x{i},{a}) & rotl64(x{i},{b})) ^ rotl64(x{i},{c});"
    if k == "t3":
        a, b, c, d = rots
        return f"wire [63:0] x{i+1} = x{i} ^ (rotl64(x{i},{a}) & rotl64(x{i},{b})) ^ rotl64(x{i},{c}) ^ rotl64(x{i},{d});"
    if k == "and3":
        a, b, c, d = rots
        return f"wire [63:0] x{i+1} = x{i} ^ (rotl64(x{i},{a}) & rotl64(x{i},{b}) & rotl64(x{i},{c})) ^ rotl64(x{i},{d});"
    raise ValueError(st)

SPECS32 = [
    ("fz32_a",
     [("and", (1, 2, 13)), ("and", (7, 19, 5)), ("and", (3, 11, 29)),
      ("and", (17, 31, 7)), ("and3", (11, 23, 37, 19))],
     "5-stage [and,and,and,and,and3]: 3-input AND final"),
    ("fz32_b",
     [("t3", (1, 7, 13, 29)), ("t3", (3, 11, 19, 37)), ("and", (5, 15, 21)),
      ("and", (9, 23, 43)), ("and3", (13, 27, 41, 7))],
     "5-stage [t3,t3,and,and,and3]: and3 final on hetero prefix"),
    ("fz32_c",
     [("and3", (1, 7, 13, 29)), ("and3", (3, 11, 19, 37)),
      ("and3", (5, 15, 21, 9)), ("and3", (9, 23, 43, 17)),
      ("and3", (13, 27, 41, 31))],
     "5-stage pure and3"),
    ("fz32_d",
     [("and", (1, 2, 13)), ("and3", (7, 19, 5, 29)), ("and", (3, 11, 29)),
      ("and3", (17, 31, 7, 23)), ("and", (11, 23, 37))],
     "5-stage interleaved [and,and3,and,and3,and]"),
]

def main():
    for name, stages, desc in SPECS32:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(
            PY_PRELUDE.format(name=name, stages="\n".join(stage_py(s) for s in stages)))
        open(os.path.join(d, "impl.c"), "w").write(
            C_PRELUDE.format(name=name, stages="\n".join(stage_c(s) for s in stages)))
        n = len(stages)
        v = V_PRELUDE.format(
            name=name,
            stages="\n".join(stage_v(i, s) for i, s in enumerate(stages))).replace("x_last", f"x{n}")
        open(os.path.join(d, "rtl.v"), "w").write(v)
        open(os.path.join(d, "meta.json"), "w").write(json.dumps(
            {"name": name, "description": desc, "rtl_top": name}, indent=2))
        print(f"generated {name}", flush=True)

if __name__ == "__main__":
    main()
