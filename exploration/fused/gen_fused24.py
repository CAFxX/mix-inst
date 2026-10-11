#!/usr/bin/env python3
"""Fused Wave-24: escape the 5-stage DIFF wall with non-AND structure.

Wave-23 verdict: hetero t3/AND 5-stage dies at the DIFF wall (fz23_b 19.7u,
fz23_c 20.0u both S1-FLAG 9/10 DIFF; fz23_a 20.2u / fz23_d 20.8u S0-dominated).
Track-3's wall theorem covers 2-input AND/OR-with-rotation cascades: the
last stage needs d_4 to cover all 64 AND-input PAIRS (min pair-miss 0.50).

Wave-24 axes (NOT covered by the theorem, NOT duplicating other tracks):
  A. Non-AND FINAL stage on hetero prefix. A maj/ch final taps TRIPLES
     {i-a,i-b,i-c} per output bit: missing a triple implies missing its
     pair-subset, so triple-coverage is strictly easier than pair-coverage.
     The wall's quantitative bound does not transfer.
       fz24_a: [t3,t3,and,and,MAJ]   x ^= maj(ra,rb,rc) ^ rd
       fz24_b: [t3,t3,and,and,CH ]   x ^= ch (ra,rb,rc) ^ rd   (SHA-256 choose)
       fz24_c: [t3,t3,and,and,CHI]   x ^= (~ra & rb) ^ rc ^ rd (Keccak-chi term)
       fz24_d: [t3,and,and,and,MAJ]  cheaper prefix variant (~19.05u est)
       fz24_e: [t3,and,and,and,CH ]  cheaper prefix variant
       fz24_f: [t3,and,and,and,CHI]  cheaper prefix variant
  B. Nibble-chi 5-stage: per-nibble Keccak-chi nonlinear layer
       y[4n+i] = x[4n+i] ^ (~x[4n+(i+1)%4] & x[4n+(i+2)%4])
     Per-nibble quiet condition (all 4 bits quiet) is strictly stronger than
     a pair-miss -- the S-box escape hatch (Rule 6) at ~1/4 the S-box cost.
     Nobody has tested this primitive.
       fz24_g: [nch,nch,nch,nch,nch] lin rots (13,29,47,7,31)
       fz24_h: [nch,nch,nch,nch,nch] lin rots (7,19,37,11,43)

Coordination: track-5 owns dual-AND-last-stage (batch-18 in flight);
track-3 owns hetero-t3/AND (mission complete) + 4-stage-nonAND-NL pivot.
Key schedule: pre-whiten x ^= k; post x ^= rotl(k,13) (wave-15 convention).
"""
import json, os

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

M64 = 0xFFFFFFFFFFFFFFFF
PLANE = 0x1111111111111111

# stage: (kind, rots...). kinds: t3, and, maj, ch, chi, nch
SPECS = [
    ("fz24_a",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 21)),
      ("and", (9, 23, 43)),
      ("maj", (13, 27, 41, 7))],
     "5-stage hetero [t3,t3,AND,AND,MAJ]: maj final x^=maj(ra,rb,rc)^rd"),
    ("fz24_b",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 21)),
      ("and", (9, 23, 43)),
      ("ch", (13, 27, 41, 7))],
     "5-stage hetero [t3,t3,AND,AND,CH]: ch final x^=ch(ra,rb,rc)^rd"),
    ("fz24_c",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 21)),
      ("and", (9, 23, 43)),
      ("chi", (13, 27, 41, 7))],
     "5-stage hetero [t3,t3,AND,AND,CHI]: chi final x^=(~ra&rb)^rc^rd"),
    ("fz24_d",
     [("t3", (1, 7, 13, 29)),
      ("and", (3, 11, 17)),
      ("and", (5, 15, 25)),
      ("and", (9, 21, 43)),
      ("maj", (13, 27, 41, 7))],
     "5-stage hetero [t3,AND,AND,AND,MAJ]: cheap prefix, maj final"),
    ("fz24_e",
     [("t3", (1, 7, 13, 29)),
      ("and", (3, 11, 17)),
      ("and", (5, 15, 25)),
      ("and", (9, 21, 43)),
      ("ch", (13, 27, 41, 7))],
     "5-stage hetero [t3,AND,AND,AND,CH]: cheap prefix, ch final"),
    ("fz24_f",
     [("t3", (1, 7, 13, 29)),
      ("and", (3, 11, 17)),
      ("and", (5, 15, 25)),
      ("and", (9, 21, 43)),
      ("chi", (13, 27, 41, 7))],
     "5-stage hetero [t3,AND,AND,AND,CHI]: cheap prefix, chi final"),
    ("fz24_g",
     [("nch", (13,)), ("nch", (29,)), ("nch", (47,)),
      ("nch", (7,)), ("nch", (31,))],
     "5-stage nibble-chi: x^=nibchi(x)^rotl(x,c), rots (13,29,47,7,31)"),
    ("fz24_h",
     [("nch", (7,)), ("nch", (19,)), ("nch", (37,)),
      ("nch", (11,)), ("nch", (43,))],
     "5-stage nibble-chi: x^=nibchi(x)^rotl(x,c), rots (7,19,37,11,43)"),
    # --- wave-24b rescue: nch2 double-rotation kills the even-chi dead bit ---
    # Dead-bit theorem: single-bit input diff at within-nibble pos i forces
    # nch output bit (i+1)%4 of that nibble to 0 for all x. With stage
    #   x ^= nch(x) ^ rotl(x,1) ^ rotl(x,61):
    # output-diff bit p(q) = 0 ^ [q+1==p(q)] ^ [q+61==p(q)].
    # p(q)-q is +1 for i=0,1,2 (fixed by c1=1) and -3 for i=3 (fixed by
    # c2=61, since 4n+3+61 = 4n+64 == 4n = p(q) mod 64). Airtight for all
    # 64 single-bit deltas. Multi-bit deltas have no guaranteed dead bit.
    ("fz24_i",
     [("nch2", (1, 61)), ("nch2", (1, 61)), ("nch2", (1, 61)),
      ("nch2", (1, 61)), ("nch2", (1, 61))],
     "5-stage nibble-chi-2rot: x^=nibchi(x)^rotl(x,1)^rotl(x,61) (dead-bit fix)"),
    ("fz24_j",
     [("nch2", (1, 61)), ("nch2", (1, 61)),
      ("nch2", (1, 61)), ("nch2", (1, 61))],
     "4-stage nibble-chi-2rot: x^=nibchi(x)^rotl(x,1)^rotl(x,61) (dead-bit fix)"),
    # --- wave-24c: widen after 24a/b kills ---
    # k/l: nch2 + large rotation for diffusion (dead-bit fix needs 1,61;
    # diffusion needs a large C; 3-stage is the only budget-viable count).
    ("fz24_k",
     [("nch2L", (1, 61, 27)), ("nch2L", (1, 61, 27)), ("nch2L", (1, 61, 27))],
     "3-stage nibble-chi-2rot+diff: x^=nibchi(x)^rotl(x,1)^rotl(x,61)^rotl(x,27)"),
    ("fz24_l",
     [("nch2L", (1, 61, 27)), ("nch2L", (1, 61, 27)),
      ("nch2L", (1, 61, 27)), ("nch2L", (1, 61, 27))],
     "4-stage nibble-chi-2rot+diff (likely over budget; proxy probe only)"),
    # m/n: 4-stage with chi FINAL (wall theorem is 5-stage AND-final;
    # 4-stage chi-final uncovered; coordination note: track-3 pivot is
    # 4-stage non-AND NL — this is the chi-final sub-axis, joint if live).
    ("fz24_m",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 21)),
      ("chi", (13, 27, 41, 7))],
     "4-stage [t3,t3,AND,CHI]: chi final, ~16.3u est"),
    ("fz24_n",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("t3", (5, 15, 25, 41)),
      ("chi", (13, 27, 41, 7))],
     "4-stage [t3,t3,t3,CHI]: chi final, ~17.3u est"),
    # --- wave-24d: chi-final schedule-search hits (v2 proxy logN=16) ---
    ("fz24_o",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 21)),
      ("and", (9, 23, 43)),
      ("chi", (31, 19, 35, 53))],
     "5-stage [t3,t3,AND,AND,CHI(31,19,35,53)]: search hit z=9.6@16, 13.9@18"),
    ("fz24_p",
     [("t3", (1, 7, 13, 29)),
      ("t3", (3, 11, 19, 37)),
      ("and", (5, 15, 21)),
      ("and", (9, 23, 43)),
      ("chi", (27, 35, 7, 44))],
     "5-stage [t3,t3,AND,AND,CHI(27,35,7,44)]: search hit z=9.7@16, 16.4@18"),
]

def stage_py(kind, rots):
    if kind == "t3":
        a, b, c, d = rots
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
                f" ^ _rotl(x,{c}) ^ _rotl(x,{d})) & M64")
    if kind == "and":
        a, b, c = rots
        return (f"    x = (x ^ (_rotl(x,{a}) & _rotl(x,{b}))"
                f" ^ _rotl(x,{c})) & M64")
    if kind == "maj":
        a, b, c, d = rots
        return (f"    x = (x ^ _maj(_rotl(x,{a}), _rotl(x,{b}), _rotl(x,{c}))"
                f" ^ _rotl(x,{d})) & M64")
    if kind == "ch":
        a, b, c, d = rots
        return (f"    x = (x ^ _ch(_rotl(x,{a}), _rotl(x,{b}), _rotl(x,{c}))"
                f" ^ _rotl(x,{d})) & M64")
    if kind == "chi":
        a, b, c, d = rots
        return (f"    x = (x ^ ((~_rotl(x,{a})) & _rotl(x,{b}))"
                f" ^ _rotl(x,{c}) ^ _rotl(x,{d})) & M64")
    if kind == "nch":
        (c,) = rots
        return f"    x = (x ^ _nibchi(x) ^ _rotl(x,{c})) & M64"
    if kind == "nch2":
        c1, c2 = rots
        return f"    x = (x ^ _nibchi(x) ^ _rotl(x,{c1}) ^ _rotl(x,{c2})) & M64"
    if kind == "nch2L":
        c1, c2, c3 = rots
        return (f"    x = (x ^ _nibchi(x) ^ _rotl(x,{c1})"
                f" ^ _rotl(x,{c2}) ^ _rotl(x,{c3})) & M64")
    raise ValueError(kind)

PRELUDE = '''"""Fused wave-24 {name}: {desc} (gen_fused24.py)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
_PLANE = np.uint64(0x1111111111111111)
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _maj(p, q, r):
    return ((p & q) ^ (p & r) ^ (q & r)) & M64
def _ch(p, q, r):
    return ((p & q) ^ ((~p) & r)) & M64
def _nibchi(x):
    p0 = x & _PLANE
    p1 = (x >> np.uint64(1)) & _PLANE
    p2 = (x >> np.uint64(2)) & _PLANE
    p3 = (x >> np.uint64(3)) & _PLANE
    q0 = p0 ^ ((~p1) & p2)
    q1 = p1 ^ ((~p2) & p3)
    q2 = p2 ^ ((~p3) & p0)
    q3 = p3 ^ ((~p0) & p1)
    return (q0 | (q1 << np.uint64(1)) | (q2 << np.uint64(2))
            | (q3 << np.uint64(3))) & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
'''

def gen_model(name, stages, desc):
    L = [PRELUDE.format(name=name, desc=desc)]
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
    if kind == "and":
        a, b, c = rots
        return (f"    x = x ^ (rotl64(x,{a}) & rotl64(x,{b}))"
                f" ^ rotl64(x,{c});")
    if kind == "maj":
        a, b, c, d = rots
        return (f"    {{ uint64_t p=rotl64(x,{a}),q=rotl64(x,{b}),r=rotl64(x,{c});"
                f" x = x ^ ((p&q)^(p&r)^(q&r)) ^ rotl64(x,{d}); }}")
    if kind == "ch":
        a, b, c, d = rots
        return (f"    {{ uint64_t p=rotl64(x,{a}),q=rotl64(x,{b}),r=rotl64(x,{c});"
                f" x = x ^ ((p&q)^(~p&r)) ^ rotl64(x,{d}); }}")
    if kind == "chi":
        a, b, c, d = rots
        return (f"    x = x ^ ((~rotl64(x,{a})) & rotl64(x,{b}))"
                f" ^ rotl64(x,{c}) ^ rotl64(x,{d});")
    if kind == "nch":
        (c,) = rots
        return f"    x = x ^ nibchi(x) ^ rotl64(x,{c});"
    if kind == "nch2":
        c1, c2 = rots
        return f"    x = x ^ nibchi(x) ^ rotl64(x,{c1}) ^ rotl64(x,{c2});"
    if kind == "nch2L":
        c1, c2, c3 = rots
        return (f"    x = x ^ nibchi(x) ^ rotl64(x,{c1})"
                f" ^ rotl64(x,{c2}) ^ rotl64(x,{c3});")
    raise ValueError(kind)

C_PRELUDE = """#include <stdint.h>
/* {name}: gen_fused24.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {{
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }}
static inline uint64_t nibchi(uint64_t x) {{
    uint64_t y = 0;
    for (int n = 0; n < 16; n++) {{
        uint64_t b = (x >> (4*n)) & 0xFu;
        uint64_t b0=(b>>0)&1u, b1=(b>>1)&1u, b2=(b>>2)&1u, b3=(b>>3)&1u;
        uint64_t y0 = b0 ^ ((~b1) & b2);
        uint64_t y1 = b1 ^ ((~b2) & b3);
        uint64_t y2 = b2 ^ ((~b3) & b0);
        uint64_t y3 = b3 ^ ((~b0) & b1);
        y |= ((y0 | (y1<<1) | (y2<<2) | (y3<<3)) << (4*n));
    }}
    return y; }}
uint64_t mix_hash(uint64_t v, uint64_t k) {{
    uint64_t x = v ^ k;
"""

def gen_c(name, stages):
    L = [C_PRELUDE.format(name=name)]
    for kind, rots in stages:
        L.append(stage_c(kind, rots))
    L += ["    return x ^ rotl64(k, 13);",
          "}", ""]
    return "\n".join(L)

V_PRELUDE = """// {name}: gen_fused24.py
module {name}(
    input  wire [63:0] val, input  wire [63:0] key,
    output wire [63:0] out );
    function [63:0] rotl;
        input [63:0] x;
        input integer r;
        begin
            r = r % 64;
            rotl = r ? ((x << r) | (x >> (64 - r))) : x;
        end
    endfunction
    function [63:0] nibchi;
        input [63:0] x;
        integer n;
        reg b0, b1, b2, b3;
        begin
            for (n = 0; n < 16; n = n + 1) begin
                b0 = x[4*n]; b1 = x[4*n+1]; b2 = x[4*n+2]; b3 = x[4*n+3];
                nibchi[4*n]   = b0 ^ (~b1 & b2);
                nibchi[4*n+1] = b1 ^ (~b2 & b3);
                nibchi[4*n+2] = b2 ^ (~b3 & b0);
                nibchi[4*n+3] = b3 ^ (~b0 & b1);
            end
        end
    endfunction
    wire [63:0] s0 = val ^ key;
"""

def stage_v(kind, rots, i):
    if kind == "t3":
        a, b, c, d = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i}, {a}) & rotl(s{i}, {b}))"
                f" ^ rotl(s{i}, {c}) ^ rotl(s{i}, {d});")
    if kind == "and":
        a, b, c = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ (rotl(s{i}, {a}) & rotl(s{i}, {b}))"
                f" ^ rotl(s{i}, {c});")
    if kind == "maj":
        a, b, c, d = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ ((rotl(s{i},{a}) & rotl(s{i},{b}))"
                f" ^ (rotl(s{i},{a}) & rotl(s{i},{c})) ^ (rotl(s{i},{b}) & rotl(s{i},{c})))"
                f" ^ rotl(s{i}, {d});")
    if kind == "ch":
        a, b, c, d = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ ((rotl(s{i},{a}) & rotl(s{i},{b}))"
                f" ^ (~rotl(s{i},{a}) & rotl(s{i},{c}))) ^ rotl(s{i}, {d});")
    if kind == "chi":
        a, b, c, d = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ (~rotl(s{i},{a}) & rotl(s{i},{b}))"
                f" ^ rotl(s{i},{c}) ^ rotl(s{i},{d});")
    if kind == "nch":
        (c,) = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ nibchi(s{i}) ^ rotl(s{i}, {c});")
    if kind == "nch2":
        c1, c2 = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ nibchi(s{i})"
                f" ^ rotl(s{i}, {c1}) ^ rotl(s{i}, {c2});")
    if kind == "nch2L":
        c1, c2, c3 = rots
        return (f"    wire [63:0] s{i+1} = s{i} ^ nibchi(s{i})"
                f" ^ rotl(s{i}, {c1}) ^ rotl(s{i}, {c2}) ^ rotl(s{i}, {c3});")
    raise ValueError(kind)

def gen_rtl(name, stages):
    L = [V_PRELUDE.format(name=name)]
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
