#!/usr/bin/env python3
"""Round 12 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round12/models/r12.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
  F = S1 layer -> linear -> ^rk32, affine r7/r8/r9 key schedule.

Families:
  F1: 5 rounds + 3-rotation linear lin(a,b,c)
  F2: partial S-box (S1 on low 16 bits only) + lin(3,11), 6/7/8 rounds
  F3: 6 rounds + 3-rotation linear lin(a,b,c)
  F4: 6 rounds + heterogeneous lin16(x) = x ^ rotl32(x,3) ^ rot16half(x,7)

RTL policy (rounds 8/11): direct boolean assigns inside ONE always @(*) block
(no Verilog functions; no module-level assign may read an always-block-driven
reg). Round-key indexing: C/Python call RK32(key, i) with 1-based i and the
function itself bakes in (i+1) -> rotl64(k,13*(i+1)) ^ (i+1)*GOLDEN; the
0-based Verilog loop therefore uses (i+2) (round-11 off-by-one lesson).

Usage: python3 round12/gen_r12.py   (writes fast_battery/candidates/r12_*/)
"""
import os
import re
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R12 = os.path.join(EXP, "round12")
sys.path.insert(0, os.path.join(R12, "models"))
import numpy as np  # noqa: E402
import r12  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

# (name, rounds, lin_kind, lin_args, sbox_kind, desc)
# lin_kind: "abc" | "ab" | "rot16" ; sbox_kind: "full" | "half"
SPECS = [
    # F1: 5r + 3-rotation linear (phase-transition re-attack)
    ("r12_feist5_lin3711_nw", 5, "abc", (3, 7, 11), "full",
     "5r Feistel, F=S1+lin(3,7,11), NO whitening"),
    ("r12_feist5_lin31119_nw", 5, "abc", (3, 11, 19), "full",
     "5r Feistel, F=S1+lin(3,11,19), NO whitening"),
    ("r12_feist5_lin71319_nw", 5, "abc", (7, 13, 19), "full",
     "5r Feistel, F=S1+lin(7,13,19), NO whitening"),
    ("r12_feist5_lin31125_nw", 5, "abc", (3, 11, 25), "full",
     "5r Feistel, F=S1+lin(3,11,25), NO whitening"),
    # F2: partial S-box (low 16 bits), 6/7/8r
    ("r12_feist6_s1half311_nw", 6, "ab", (3, 11), "half",
     "6r Feistel, F=S1(low16)+lin(3,11), NO whitening"),
    ("r12_feist7_s1half311_nw", 7, "ab", (3, 11), "half",
     "7r Feistel, F=S1(low16)+lin(3,11), NO whitening"),
    ("r12_feist8_s1half311_nw", 8, "ab", (3, 11), "half",
     "8r Feistel, F=S1(low16)+lin(3,11), NO whitening"),
    # F3: 6r + 3-rotation linear
    ("r12_feist6_lin3711_nw", 6, "abc", (3, 7, 11), "full",
     "6r Feistel, F=S1+lin(3,7,11), NO whitening"),
    ("r12_feist6_lin71319_nw", 6, "abc", (7, 13, 19), "full",
     "6r Feistel, F=S1+lin(7,13,19), NO whitening"),
    # F4: heterogeneous 16-bit-half rotation mixing, 6r
    ("r12_feist6_s1_16rot_nw", 6, "rot16", (), "full",
     "6r Feistel, F=S1+lin16(x^rotl32(x,3)^rot16half(x,7)), NO whitening"),
]


# ---------------- Quine-McCluskey (4 vars), as in gen_r11.py ----------------
def _qm_primes(minterms):
    cubes = [(0, m) for m in sorted(minterms)]
    primes = set()
    while True:
        used = [False] * len(cubes)
        nxt = []
        seen = set()
        for i in range(len(cubes)):
            for j in range(i + 1, len(cubes)):
                m1, b1 = cubes[i]
                m2, b2 = cubes[j]
                if m1 != m2:
                    continue
                d = (b1 ^ b2) & ~m1 & 0xF
                if d and (d & (d - 1)) == 0:
                    nc = (m1 | d, (b1 & ~d) & 0xF)
                    if nc not in seen:
                        seen.add(nc)
                        nxt.append(nc)
                    used[i] = used[j] = True
        for i, c in enumerate(cubes):
            if not used[i]:
                primes.add(c)
        if not nxt:
            break
        cubes = nxt
    return primes


def _qm_cover(minterms, primes):
    uncovered = set(minterms)
    chosen = []
    primes = list(primes)
    while uncovered:
        def covers(p):
            m, b = p
            return [v for v in uncovered if (v & ~m) == (b & ~m)]
        best = max(primes, key=lambda p: len(covers(p)))
        cov = covers(best)
        assert cov, "prime cover failed"
        chosen.append(best)
        uncovered -= set(cov)
    return chosen


def dnf_for_bit(bit):
    mt = [v for v in range(16) if (S1[v] >> bit) & 1]
    if not mt:
        return []
    if len(mt) == 16:
        return [(0xF, 0)]
    return _qm_cover(mt, _qm_primes(mt))


def _selftest_dnf():
    for bit in range(4):
        cubes = dnf_for_bit(bit)
        for v in range(16):
            got = 0
            for m, b in cubes:
                if (v & ~m) == (b & ~m):
                    got = 1
                    break
            want = (S1[v] >> bit) & 1
            assert got == want, (bit, v, got, want)
    print("DNF self-test: S1 x 4 bits x 16 inputs OK")


def _cube_verilog(mask, bits, base):
    lits = []
    for k in range(4):
        if (mask >> k) & 1:
            continue
        lits.append(f"R[{base + k}]" if (bits >> k) & 1 else f"~R[{base + k}]")
    if not lits:
        return "1'b1"
    return "(" + " & ".join(lits) + ")"


def sbox_dnf_assigns(nibbles):
    """DNF assigns for t[0..4*nibbles) = S1(R[0..4*nibbles))."""
    lines = []
    for j in range(nibbles):
        b = 4 * j
        for bit in range(4):
            cubes = dnf_for_bit(bit)
            expr = (" | ".join(_cube_verilog(m, cb, b) for m, cb in cubes)
                    if cubes else "1'b0")
            lines.append(f"            t[{b + bit}] = {expr};")
    return "\n".join(lines)


# ---------------- C ----------------
C_HDR = """/* {name}: {desc}
 * GENERATED by round12/gen_r12.py -- do not edit by hand.
 * Bit-exact vs Python model round12/models/r12.py ({pyfn}). */
#include <stdint.h>

static const uint8_t S1[16] = {{0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10}};

{sbox_layer_c}

static uint32_t rotl32(uint32_t x, int n) {{ return (x << n) | (x >> (32 - n)); }}
static uint64_t rotl64(uint64_t x, int n) {{
    n &= 63; return n ? (x << n) | (x >> (64 - n)) : x;
}}
static uint32_t RK32(uint64_t k, int i) {{
    /* affine schedule: low32(rotl64(k,13*(i+1)) ^ (i+1)*GOLDEN64) */
    uint64_t rkv = rotl64(k, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
    return (uint32_t)rkv;
}}

{lin_c}

static uint32_t F_f(uint32_t R, uint32_t rk32) {{
    uint32_t t = sbox_layer32(R);
    t = lin(t);
    return t ^ rk32;
}}

uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= {rounds}; i++) {{
        uint32_t F = F_f(R, RK32(key, i));
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }}
    return ((uint64_t)R << 32) | L;
}}
"""

C_LAYER_FULL = """
static uint32_t sbox_layer32(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)S1[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}"""

C_LAYER_HALF = """
static uint32_t sbox_layer32(uint32_t x) {
    /* S1 on the low 16 bits (4 nibbles) only; high 16 bits pass through */
    uint32_t r = x & 0xFFFF0000u;
    for (int i = 0; i < 4; i++)
        r |= (uint32_t)S1[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}"""

C_LIN_ABC = """
static uint32_t lin(uint32_t x) {{
    return x ^ rotl32(x, {a}) ^ rotl32(x, {b}) ^ rotl32(x, {c});
}}"""

C_LIN_AB = """
static uint32_t lin(uint32_t x) {{
    return x ^ rotl32(x, {a}) ^ rotl32(x, {b});
}}"""

C_LIN_ROT16 = """
static uint32_t rot16half(uint32_t x, int n) {
    /* rotate each 16-bit half left by n (within the half) */
    uint32_t lo = x & 0xFFFFu, hi = x >> 16;
    lo = ((lo << n) | (lo >> (16 - n))) & 0xFFFFu;
    hi = ((hi << n) | (hi >> (16 - n))) & 0xFFFFu;
    return (hi << 16) | lo;
}
static uint32_t lin(uint32_t x) {
    return x ^ rotl32(x, 3) ^ rot16half(x, 7);
}"""


def gen_impl(name, rounds, lin_kind, lin_args, sbox_kind, desc):
    layer_c = C_LAYER_FULL if sbox_kind == "full" else C_LAYER_HALF
    if lin_kind == "abc":
        a, b, c = lin_args
        lin_c = C_LIN_ABC.format(a=a, b=b, c=c)
    elif lin_kind == "ab":
        a, b = lin_args
        lin_c = C_LIN_AB.format(a=a, b=b)
    elif lin_kind == "rot16":
        lin_c = C_LIN_ROT16
    else:
        raise ValueError(lin_kind)
    return C_HDR.format(name=name, desc=desc, pyfn=name, rounds=rounds,
                        sbox_layer_c=layer_c, lin_c=lin_c)


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round12/gen_r12.py -- do not edit by hand.
// Bit-exact vs Python model round12/models/r12.py ({pyfn}).
// S-box as direct boolean assigns inside one always @(*) block (no functions).
module {name}(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
"""

V_DECL = """
reg [31:0] L, R;
reg [31:0] Lt, Rt;
reg [31:0] t;
reg [31:0] rk32;
reg [63:0] rkv;
integer i, r;
"""

V_MAIN_TMPL = """
always @(*) begin
    L = val[63:32];
    R = val[31:0];
    for (i = 0; i < {rounds}; i = i + 1) begin
        // ---- S-box layer: R -> t (direct boolean assigns) ----
{sbox_assigns}
{passthrough}
// ---- linear layer ----
        t = {lin_expr};
// ---- round key: low32(rotl64(key,13*(i+1)) ^ (i+1)*GOLDEN64) ----
        // NOTE: loop i is 0-based; C/Python call RK32(key, i) with 1-based i,
        // and RK32 itself bakes in (i+1). Round r = i+1 (1-based) therefore
        // needs 13*((i+1)+1) = 13*(i+2) and ((i+2)*GOLDEN) here.
        // (round-11 off-by-one lesson: this was (i+1) before; check_rtl
        //  failed 10/10 and passes 10/10 after the fix.)
        r = (13 * (i + 2)) % 64;
        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 2) * 64'h9E3779B97F4A7C15);
        rk32 = rkv[31:0];
// ---- Feistel step ----
        Lt = R;
        Rt = L ^ t ^ rk32;
        L = Lt;
        R = Rt;
    end
end

assign out = {{R, L}};

endmodule
"""


def _rot_parts(n):
    # rotl32(t,n) = {t[32-n-1:0], t[31:32-n]}
    return (32 - n - 1, 32 - n)


def _rot_expr(n):
    hi, lo = _rot_parts(n)
    return f"{{t[{hi}:0], t[31:{lo}]}}"


def gen_rtl(name, rounds, lin_kind, lin_args, sbox_kind, desc):
    nibbles = 8 if sbox_kind == "full" else 4
    sbox_assigns = sbox_dnf_assigns(nibbles)
    if sbox_kind == "half":
        passthrough = "        t[31:16] = R[31:16]; // high 16 bits: no S-box"
    else:
        passthrough = ""
    if lin_kind == "abc":
        parts = " ^ ".join(["t"] + [_rot_expr(n) for n in lin_args])
        lin_expr = parts + ";"
        comment = f"// lin{lin_args}: t ^= rotl32(t,{lin_args[0]}) ^ rotl32(t,{lin_args[1]}) ^ rotl32(t,{lin_args[2]})"
    elif lin_kind == "ab":
        parts = " ^ ".join(["t"] + [_rot_expr(n) for n in lin_args])
        lin_expr = parts + ";"
        comment = f"// lin{lin_args}"
    elif lin_kind == "rot16":
        # rot16half(t,7): hi half {t[24:16],t[31:25]}, lo half {t[8:0],t[15:9]}
        lin_expr = ("t ^ {t[28:0], t[31:29]} ^ "
                    "{t[24:16], t[31:25], t[8:0], t[15:9]};")
        comment = "// lin16: t ^= rotl32(t,3) ^ rot16half(t,7)"
    else:
        raise ValueError(lin_kind)
    body = V_MAIN_TMPL.format(rounds=rounds, sbox_assigns=sbox_assigns,
                              passthrough=passthrough, lin_expr=lin_expr)
    # insert the linear comment above the lin line
    body = body.replace("// ---- linear layer ----",
                        "// ---- linear layer ----\n        " + comment)
    return V_HDR.format(name=name, desc=desc, pyfn=name) + V_DECL + body


# ---------------- model.py / meta.json ----------------
MODEL_PY = '''""\"Python model wrapper for {name} (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."\"\"
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round12/models")
from r12 import {name} as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
'''

META_JSON = """{{
 "name": "{name}",
 "description": "{desc}",
 "composition": "{desc}",
 "rtl_top": "{name}",
 "screen_keys": [
  "0x123456789abcdef0",
  "0x0"
 ],
 "practrand_keys": [
  "0x123456789abcdef0",
  "0x0"
 ],
 "goldens": [
  {{
   "val": "0x0",
   "key": "0x123456789abcdef0",
   "out": "{golden0}"
  }},
  {{
   "val": "0x123456789abcdef0",
   "key": "0x0",
   "out": "{golden1}"
  }}
 ]
}}"""


def emit():
    _selftest_dnf()
    # dedupe: pairwise-distinct model outputs across the spec set
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    outs = {}
    for name, rounds, lin_kind, lin_args, sbox_kind, desc in SPECS:
        fn = getattr(r12, name)
        o = fn(V, K).tobytes()
        assert o not in outs.values(), f"DUPLICATE model output: {name}"
        outs[name] = o
    print(f"dedupe: {len(SPECS)} specs pairwise-distinct OK")
    for name, rounds, lin_kind, lin_args, sbox_kind, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, rounds, lin_kind, lin_args, sbox_kind, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, rounds, lin_kind, lin_args, sbox_kind, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(r12, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
