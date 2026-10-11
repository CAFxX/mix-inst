#!/usr/bin/env python3
"""Fused Wave-26: 4-stage with fused AND+CHI final stage.

fz24_o ([t3,t3,and,and,CHI]) is S1/S2-clean but 20.3u (0.2u over).
Wave-26: fuse the 4th AND and CHI final into ONE stage with TWO nonlinear
terms: x ^= (ra&rb) ^ (~rc&rd) ^ re ^ rf.
Cost est: 4.5+4.5+3.35+4.5 = 16.85u. If DIFF holds, this wins big.

Coordination: track-3 pivot is on 4-stage non-AND NL (sboxL); this is the
fused-AND+CHI sub-axis (different nonlinearity, no S-box).

Candidates:
  fz26_a: [t3(1,7,13,29), t3(3,11,19,37), and(5,15,21), FUSED((1,7),(13,27),41,53)]
  fz26_b: [t3(1,7,13,29), t3(3,11,19,37), and(5,15,21), FUSED((3,11),(17,29),43,55)]
"""
import json, os
EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")
SPECS = [
    ("fz26_a",
     [("t3", (1, 7, 13, 29)), ("t3", (3, 11, 19, 37)), ("and", (5, 15, 21)),
      ("fused", ((1, 7), (13, 27), 41, 53))],
     "4-stage [t3,t3,and,FUSED]: x^=(ra&rb)^(~rc&rd)^re^rf"),
    ("fz26_b",
     [("t3", (1, 7, 13, 29)), ("t3", (3, 11, 19, 37)), ("and", (5, 15, 21)),
      ("fused", ((3, 11), (17, 29), 43, 55))],
     "4-stage [t3,t3,and,FUSED] alt schedule"),
]
def stage_py(kind, rots):
    if kind == "t3":
        a,b,c,d = rots
        return f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{c}) ^ _rotl(x,{d})) & M64"
    if kind == "and":
        a,b,c = rots
        return f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b})) ^ _rotl(x,{c})) & M64"
    if kind == "fused":
        (a,b),(c,d),e,f = rots
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
                f" ^ ((~_rotl(x,{c})) & _rotl(x,{d})) ^ _rotl(x,{e}) ^ _rotl(x,{f})) & M64")
    raise ValueError(kind)
PRE = '"""Fused wave-26 {name}: {desc} (gen_fused26.py)."""\nimport numpy as np\n\nM64 = np.uint64(0xFFFFFFFFFFFFFFFF)\ndef _rotl(x, r):\n    r %= 64\n    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x\ndef mix_np(V, K):\n    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n    x = (x ^ k) & M64\n'
def gen_model(name, stages, desc):
    L = [PRE.format(name=name, desc=desc)]
    for kind, rots in stages: L.append(stage_py(kind, rots))
    L += ["    x = (x ^ _rotl(k, 13)) & M64", "    return x & M64",
          "def mix(v, k):", "    return int(mix_np(np.uint64(v), np.uint64(k)))", ""]
    return "\n".join(L)
def stage_c(kind, rots):
    if kind == "t3":
        a,b,c,d = rots
        return f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c}) ^ rotl64(x,{d});"
    if kind == "and":
        a,b,c = rots
        return f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c});"
    if kind == "fused":
        (a,b),(c,d),e,f = rots
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}))"
                f" ^ ((~rotl64(x,{c})) & rotl64(x,{d})) ^ rotl64(x,{e}) ^ rotl64(x,{f});")
    raise ValueError(kind)
def gen_c(name, stages):
    L = ["#include <stdint.h>", f"/* {name}: gen_fused26.py */",
         "static inline uint64_t rotl64(uint64_t x, unsigned r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k) {", "    uint64_t x = v ^ k;"]
    for kind, rots in stages: L.append(stage_c(kind, rots))
    L += ["    return x ^ rotl64(k, 13);", "}", ""]
    return "\n".join(L)
def stage_v(kind, rots, i):
    if kind == "t3":
        a,b,c,d = rots
        return f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i}, {a}) & rotl(s{i}, {b})) ^ rotl(s{i}, {c}) ^ rotl(s{i}, {d});"
    if kind == "and":
        a,b,c = rots
        return f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i}, {a}) & rotl(s{i}, {b})) ^ rotl(s{i}, {c});"
    if kind == "fused":
        (a,b),(c,d),e,f = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i},{a}) & rotl(s{i},{b}))"
                f" ^ (~rotl(s{i},{c}) & rotl(s{i},{d})) ^ rotl(s{i},{e}) ^ rotl(s{i},{f});")
    raise ValueError(kind)
def gen_rtl(name, stages):
    L = [f"// {name}: gen_fused26.py", f"module {name}(",
         "    input  wire [63:0] val, input  wire [63:0] key,",
         "    output wire [63:0] out );",
         "    function [63:0] rotl;", "        input [63:0] x;", "        input integer r;",
         "        begin", "            r = r % 64;",
         "            rotl = r ? ((x << r) | (x >> (64 - r))) : x;",
         "        end", "    endfunction",
         "    wire [63:0] s0 = val ^ key;"]
    for i, (kind, rots) in enumerate(stages): L.append(stage_v(kind, rots, i))
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
