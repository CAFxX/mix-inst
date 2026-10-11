#!/usr/bin/env python3
"""Wave-31 Axis C (PREP): S-box layer + fused diffusion cost probe.

Idea: 16x parallel 4-bit S-box (PRESENT) as the nonlinear primitive,
fused with rotation-XOR diffusion. If the S-box layer costs ~2u, then
  x ^= sbox(x) ^ rotl(x,a)          [~2-3u]
  + 3x fused t3/and stages          [~10u]
  + chi/maj final                   [~4u]
could land ~17-18u with SPN-grade nonlinearity per stage.

This script only GENERATES the probe candidates (model+C+RTL).
S0 runs when VM load clears (backoff gate).
Candidates:
  fz31_s1: [sboxlin(13), sboxlin(29)]                      (2 S-box layers)
  fz31_s2: [sboxlin(13), t3(1,7,13,29), and(5,15,21)]      (S-box + fused)
  fz31_s3: [t3(1,7,13,29), sboxlin(19), and(5,15,21)]      (fused-S-fused)
where sboxlin(r): x ^= psbox(x) ^ rotl(x,r), psbox = 16x PRESENT S-box.
"""
import json, os, sys

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")
sys.path.insert(0, os.path.join(EXP, "fused"))

# PRESENT 4-bit S-box
PSBOX = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]

def psbox64(x):
    y = 0
    for n in range(16):
        y |= PSBOX[(x >> (4*n)) & 0xF] << (4*n)
    return y & 0xFFFFFFFFFFFFFFFF

M64 = 0xFFFFFFFFFFFFFFFF
def rotl(x, r):
    r &= 63
    return ((x << r) | (x >> (64-r))) & M64 if r else x & M64

def apply(x, st):
    k = st[0]
    if k == "sboxlin":
        (_, (r,)) = st
        return (x ^ psbox64(x) ^ rotl(x, r)) & M64
    if k == "t3":
        (_, (a,b,c,d)) = st
        return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c) ^ rotl(x,d)) & M64
    if k == "and":
        (_, (a,b,c)) = st
        return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)) & M64
    raise ValueError(st)

C_PRELUDE = """#include <stdint.h>
/* {name}: wave31 axis C (S-box layer probe) */
static inline uint64_t rotl64(uint64_t x, unsigned r) {{
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }}
static inline uint64_t psbox(uint64_t x) {{
    static const uint8_t S[16] = {{0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2}};
    uint64_t y = 0;
    for (int n = 0; n < 16; n++) y |= (uint64_t)S[(x >> (4*n)) & 0xFu] << (4*n);
    return y; }}
uint64_t mix_hash(uint64_t v, uint64_t k) {{
    uint64_t x = v ^ k;
{stages}
    x = x ^ rotl64(k, 13);
    return x;
}}
"""

def stage_c(st):
    k = st[0]
    if k == "sboxlin":
        (_, (r,)) = st
        return f"    x = x ^ psbox(x) ^ rotl64(x,{r});"
    if k == "t3":
        (_, (a,b,c,d)) = st
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}))"
                f" ^ rotl64(x,{c}) ^ rotl64(x,{d});")
    if k == "and":
        (_, (a,b,c)) = st
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}))"
                f" ^ rotl64(x,{c});")
    raise ValueError(st)

PY_PRELUDE = '''""" {name}: wave31 axis C (S-box layer probe) """
import numpy as np
M64 = 0xFFFFFFFFFFFFFFFF
PSBOX = np.array([0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2], dtype=np.uint64)
def _rotl(x, r):
    r &= 63
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & np.uint64(M64) if r else x & np.uint64(M64)
def _psbox(x):
    y = np.zeros_like(x)
    for n in range(16):
        y |= PSBOX[(x >> np.uint64(4*n)) & np.uint64(0xF)] << np.uint64(4*n)
    return y & np.uint64(M64)
def mix_np(v, k):
    x = (np.uint64(v) ^ np.uint64(k))
{stages}
    x = (x ^ _rotl(np.uint64(k), 13)) & np.uint64(M64)
    return x
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
'''

def stage_py(st):
    k = st[0]
    if k == "sboxlin":
        (_, (r,)) = st
        return f"    x = (x ^ _psbox(x) ^ _rotl(x, {r})) & np.uint64(M64)"
    if k == "t3":
        (_, (a,b,c,d)) = st
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
                f" ^ _rotl(x,{c}) ^ _rotl(x,{d})) & np.uint64(M64)")
    if k == "and":
        (_, (a,b,c)) = st
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
                f" ^ _rotl(x,{c})) & np.uint64(M64)")
    raise ValueError(st)

# RTL: structural S-box via case statement (synth will map to gates)
V_PRELUDE = """// {name}: wave31 axis C (S-box layer probe)
module {name}(input [63:0] v, input [63:0] k, output [63:0] h);
function [63:0] rotl64(input [63:0] x, input [5:0] r);
  rotl64 = (x << r) | (x >> (6'd64 - r));
endfunction
function [3:0] sbox4(input [3:0] b);
  case (b)
    4'h0: sbox4 = 4'hC; 4'h1: sbox4 = 4'h5;
    4'h2: sbox4 = 4'h6; 4'h3: sbox4 = 4'hB;
    4'h4: sbox4 = 4'h9; 4'h5: sbox4 = 4'h0;
    4'h6: sbox4 = 4'hA; 4'h7: sbox4 = 4'hD;
    4'h8: sbox4 = 4'h3; 4'h9: sbox4 = 4'hE;
    4'hA: sbox4 = 4'hF; 4'hB: sbox4 = 4'h8;
    4'hC: sbox4 = 4'h4; 4'hD: sbox4 = 4'h7;
    4'hE: sbox4 = 4'h1; 4'hF: sbox4 = 4'h2;
  endcase
endfunction
function [63:0] psbox(input [63:0] x);
  integer n;
  begin
    for (n = 0; n < 16; n = n + 1)
      psbox[4*n +: 4] = sbox4(x[4*n +: 4]);
  end
endfunction
wire [63:0] x0 = v ^ k;
{stages}
assign h = x_last ^ rotl64(k, 13);
endmodule
"""

def gen_all():
    specs = [
        ("fz31_s1", [("sboxlin",(13,)), ("sboxlin",(29,))],
         "2x S-box layer + linear diffusion (cost probe)"),
        ("fz31_s2", [("sboxlin",(13,)), ("t3",(1,7,13,29)), ("and",(5,15,21))],
         "S-box + t3 + and fused (cost probe)"),
        ("fz31_s3", [("t3",(1,7,13,29)), ("sboxlin",(19,)), ("and",(5,15,21))],
         "t3 + S-box + and fused (cost probe)"),
    ]
    for name, stages, desc in specs:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        # python model
        pylines = [PY_PRELUDE.format(name=name, stages="\n".join(stage_py(s) for s in stages))]
        open(os.path.join(d, "model.py"), "w").write("\n".join(pylines))
        # C
        open(os.path.join(d, "impl.c"), "w").write(
            C_PRELUDE.format(name=name, stages="\n".join(stage_c(s) for s in stages)))
        # RTL (chain wires x0..xn)
        vlines = []
        for i, s in enumerate(stages):
            k = s[0]
            if k == "sboxlin":
                (_, (rr,)) = s
                vlines.append(f"wire [63:0] x{i+1} = x{i} ^ psbox(x{i}) ^ rotl64(x{i}, {rr});")
            elif k == "t3":
                (_, (a,b,c,dd)) = s
                vlines.append(f"wire [63:0] x{i+1} = x{i} ^ (rotl64(x{i},{a}) & rotl64(x{i},{b})) ^ rotl64(x{i},{c}) ^ rotl64(x{i},{dd});")
            elif k == "and":
                (_, (a,b,c)) = s
                vlines.append(f"wire [63:0] x{i+1} = x{i} ^ (rotl64(x{i},{a}) & rotl64(x{i},{b})) ^ rotl64(x{i},{c});")
        n = len(stages)
        v = V_PRELUDE.format(name=name, stages="\n".join(vlines)).replace("x_last", f"x{n}")
        open(os.path.join(d, "rtl.v"), "w").write(v)
        open(os.path.join(d, "meta.json"), "w").write(json.dumps(
            {"name": name, "description": desc, "rtl_top": name}, indent=2))
        print(f"generated {name}", flush=True)

if __name__ == "__main__":
    gen_all()
