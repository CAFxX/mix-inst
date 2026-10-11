#!/usr/bin/env python3
"""Round 13 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round13/models/r13.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): balanced Feistel (except F5 Lai-Massey), 32-bit halves,
{R,L} output, NO whitening, affine r7/r8/r9 key schedule.

Families (all genuinely new axes; S-box swap / rotation pairs / 5r /
3-rot linear / partial-S-box / whitening exhausted in r8-r12):
  F1: 4r Feistel, double-strength F = lin(S1(lin(S1(R^rkA))^rkB)), 2 keys/round
      (rkA=RK32(key,2i-1), rkB=RK32(key,2i)), lin (3,11) and (7,13)
  F2: chi32 nonlinear b_i = a_i ^ (~a_{i+1} & a_{i+2}), F = lin(3,11)(chi(R))^rk,
      5/6/8 rounds
  F3: chi->S1 hybrid F = lin(3,11)(S1(chi(R)))^rk, 6r
  F4: heterogeneous rounds: alt (odd rounds S1-F, even chi-F) and
      s1x3/chix3 (first 3 rounds S1-F, last 3 chi-F), 6r
  F5: Lai-Massey with orthomorphism sigma(L,R) = (R, L^R):
        t = lin(S1(L^R))^rk; L' = R^t; R' = L^R, 4r/6r
      (the naive L'=R^t, R'=L^t leaves D = L^R invariant across rounds, so all
      rounds apply F to the same input -- a degenerate single-F-layer design;
      caught in r13 when S0 reported 5.5u/578 cells for 4r)
  F6: key-schedule variants on the r9 structure:
        midk: F = lin(3,11)(S1(R) ^ rk)   (key between S-box and linear)
        rkhi: rk = high32(RK64) on odd rounds, low32 on even rounds
  F7: sandwich F = lin(3,11)(S1(lin(3,11)(R)))^rk, 6r

RTL policy (rounds 8/11/12): direct boolean assigns inside ONE always @(*)
block (no Verilog functions; no module-level assign may read an
always-block-driven reg). Round-key indexing: C/Python call RK32(key, i) with
1-based i and the function itself bakes in (i+1) -> rotl64(k,13*(i+1)) ^
(i+1)*GOLDEN; the 0-based Verilog loop therefore uses (i+2) (round-11
off-by-one lesson). F1 uses two keys/round: C calls RK32(key,2i-1)/RK32(key,2i)
(1-based i) -> Verilog bakes (2*i+2)/(2*i+3) (derivation in the template).

Usage: python3 round13/gen_r13.py   (writes fast_battery/candidates/r13_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R13 = os.path.join(EXP, "round13")
sys.path.insert(0, os.path.join(R13, "models"))
import numpy as np  # noqa: E402
import r13  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

# (name, kind, rounds, lin(a,b), desc)
SPECS = [
    # F1: 4r double-strength F
    ("r13_feist4_s1x2_311_nw", "s1x2", 4, (3, 11),
     "4r Feistel, F=lin311(S1(lin311(S1(R^rkA))^rkB)), 2 keys/round, NO whitening"),
    ("r13_feist4_s1x2_713_nw", "s1x2", 4, (7, 13),
     "4r Feistel, F=lin713(S1(lin713(S1(R^rkA))^rkB)), 2 keys/round, NO whitening"),
    # F2: chi F at 5/6/8r
    ("r13_feist5_chi311_nw", "chi", 5, (3, 11),
     "5r Feistel, F=lin311(chi32(R))^rk, NO whitening"),
    ("r13_feist6_chi311_nw", "chi", 6, (3, 11),
     "6r Feistel, F=lin311(chi32(R))^rk, NO whitening"),
    ("r13_feist8_chi311_nw", "chi", 8, (3, 11),
     "8r Feistel, F=lin311(chi32(R))^rk, NO whitening"),
    # F3: chi->S1 hybrid
    ("r13_feist6_chis1_311_nw", "chis1", 6, (3, 11),
     "6r Feistel, F=lin311(S1(chi32(R)))^rk, NO whitening"),
    # F4: heterogeneous rounds
    ("r13_feist6_alt_s1chi_nw", "alt", 6, (3, 11),
     "6r Feistel, odd rounds S1-F / even rounds chi-F, NO whitening"),
    ("r13_feist6_s1x3_chix3_nw", "s1x3", 6, (3, 11),
     "6r Feistel, rounds 1-3 S1-F / rounds 4-6 chi-F, NO whitening"),
    # F5: Lai-Massey
    ("r13_lm4_s1_311_nw", "lm", 4, (3, 11),
     "4r Lai-Massey sigma(L,R)=(R,L^R), F=lin311(S1(L^R))^rk, NO whitening"),
    ("r13_lm6_s1_311_nw", "lm", 6, (3, 11),
     "6r Lai-Massey sigma(L,R)=(R,L^R), F=lin311(S1(L^R))^rk, NO whitening"),
    # F6: key-schedule variants
    ("r13_feist6_s1_midk311_nw", "midk", 6, (3, 11),
     "6r Feistel, F=lin311(S1(R)^rk) (key between S-box and linear), NO whitening"),
    ("r13_feist6_s1_rkhi311_nw", "rkhi", 6, (3, 11),
     "6r Feistel, F=lin311(S1(R))^rk, rk=high32(RK64) odd rounds / low32 even, NO whitening"),
    # F7: sandwich
    ("r13_feist6_sandw311_nw", "sandw", 6, (3, 11),
     "6r Feistel, F=lin311(S1(lin311(R)))^rk, NO whitening"),
]


# ---------------- Quine-McCluskey (4 vars), as in gen_r12.py ----------------
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


def _cube_verilog(mask, bits, base, src):
    lits = []
    for k in range(4):
        if (mask >> k) & 1:
            continue
        lits.append(f"{src}[{base + k}]" if (bits >> k) & 1 else f"~{src}[{base + k}]")
    if not lits:
        return "1'b1"
    return "(" + " & ".join(lits) + ")"


def sbox_dnf_assigns(dst, src):
    """32 assigns: dst[0..31] = S1(src[0..31]) as direct boolean DNF."""
    lines = []
    for j in range(8):
        b = 4 * j
        for bit in range(4):
            cubes = dnf_for_bit(bit)
            expr = (" | ".join(_cube_verilog(m, cb, b, src) for m, cb in cubes)
                    if cubes else "1'b0")
            lines.append(f"            {dst}[{b + bit}] = {expr};")
    return "\n".join(lines)


def chi_assigns(dst, src):
    """32 assigns: dst = chi32(src), b_i = a_i ^ (~a_{i+1} & a_{i+2})."""
    lines = []
    for i in range(32):
        lines.append(
            f"            {dst}[{i}] = {src}[{i}] ^ "
            f"(~{src}[{(i + 1) % 32}] & {src}[{(i + 2) % 32}]);")
    return "\n".join(lines)


def _rot_expr(reg, n):
    # rotl32(reg,n) = {reg[32-n-1:0], reg[31:32-n]}
    return f"{{{reg}[{32 - n - 1}:0], {reg}[31:{32 - n}]}}"


def lin_expr(reg, a, b):
    return f"{reg} ^ {_rot_expr(reg, a)} ^ {_rot_expr(reg, b)}"


# ---------------- C ----------------
C_COMMON = """/* {name}: {desc}
 * GENERATED by round13/gen_r13.py -- do not edit by hand.
 * Bit-exact vs Python model round13/models/r13.py ({name}). */
#include <stdint.h>

static const uint8_t S1[16] = {{0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10}};

static uint32_t sbox_layer32(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)S1[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}}

/* chi32: b_i = a_i ^ (~a_{{i+1}} & a_{{i+2}}). NOT a permutation for even
 * width -- fine, a Feistel F need not be invertible. */
static uint32_t chi32(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + 1) % 32)) & 1u;
        uint32_t a2 = (x >> ((i + 2) % 32)) & 1u;
        r |= (a0 ^ ((~a1) & a2)) << i;
    }}
    return r;
}}

static uint32_t rotl32(uint32_t x, int n) {{ return (x << n) | (x >> (32 - n)); }}
static uint64_t rotl64(uint64_t x, int n) {{
    n &= 63; return n ? (x << n) | (x >> (64 - n)) : x;
}}
static uint64_t RK64(uint64_t k, int i) {{
    /* affine schedule: rotl64(k,13*(i+1)) ^ (i+1)*GOLDEN64, i 1-based */
    return rotl64(k, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}}
static uint32_t RK32(uint64_t k, int i) {{ return (uint32_t)RK64(k, i); }}

static uint32_t lin_ab(uint32_t x, int a, int b) {{
    return x ^ rotl32(x, a) ^ rotl32(x, b);
}}

static uint32_t F_s1(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(sbox_layer32(R), a, b) ^ rk;
}}
static uint32_t F_chi(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(chi32(R), a, b) ^ rk;
}}
static uint32_t F_chis1(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(sbox_layer32(chi32(R)), a, b) ^ rk;
}}
static uint32_t F_s1x2(uint32_t R, uint32_t rkA, uint32_t rkB, int a, int b) {{
    uint32_t t = lin_ab(sbox_layer32(R ^ rkA), a, b) ^ rkB;
    return lin_ab(sbox_layer32(t), a, b);
}}
static uint32_t F_sandw(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(sbox_layer32(lin_ab(R, a, b)), a, b) ^ rk;
}}
static uint32_t F_midk(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(sbox_layer32(R) ^ rk, a, b);
}}

"""

C_MAIN_FEISTEL = """uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= {rounds}; i++) {{
{f_line}
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }}
    return ((uint64_t)R << 32) | L;
}}
"""

C_MAIN_LM = """uint64_t mix_hash(uint64_t val, uint64_t key) {{
    /* Lai-Massey with orthomorphism sigma(L,R) = (R, L^R):
     * t = F(L^R)^rk; L' = R^t; R' = L^R. Bijective for fixed key
     * (R' = D recovers t). The orthomorphism is load-bearing: without it
     * D = L^R is invariant across rounds and the design degenerates. */
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= {rounds}; i++) {{
        uint32_t F = F_s1(L ^ R, RK32(key, i), {a}, {b});
        uint32_t nL = R ^ F, nR = L ^ R;
        L = nL; R = nR;
    }}
    return ((uint64_t)R << 32) | L;
}}
"""

C_F_LINE = {
    "s1x2": "        uint32_t F = F_s1x2(R, RK32(key, 2*i-1), RK32(key, 2*i), {a}, {b});",
    "chi": "        uint32_t F = F_chi(R, RK32(key, i), {a}, {b});",
    "chis1": "        uint32_t F = F_chis1(R, RK32(key, i), {a}, {b});",
    "alt": "        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), {a}, {b})\n"
           "                           : F_chi(R, RK32(key, i), {a}, {b});",
    "s1x3": "        uint32_t F = (i <= 3) ? F_s1(R, RK32(key, i), {a}, {b})\n"
            "                            : F_chi(R, RK32(key, i), {a}, {b});",
    "midk": "        uint32_t F = F_midk(R, RK32(key, i), {a}, {b});",
    "rkhi": ("        uint64_t rkv = RK64(key, i);\n"
             "        /* rotating key-half: high32 on odd rounds, low32 on even */\n"
             "        uint32_t rk = (i & 1) ? (uint32_t)(rkv >> 32) : (uint32_t)rkv;\n"
             "        uint32_t F = F_s1(R, rk, {a}, {b});"),
    "sandw": "        uint32_t F = F_sandw(R, RK32(key, i), {a}, {b});",
}


def gen_impl(name, kind, rounds, lin, desc):
    a, b = lin
    body = C_COMMON.format(name=name, desc=desc)
    if kind == "lm":
        body += C_MAIN_LM.format(rounds=rounds, a=a, b=b)
    else:
        body += C_MAIN_FEISTEL.format(rounds=rounds,
                                     f_line=C_F_LINE[kind].format(a=a, b=b))
    return body


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round13/gen_r13.py -- do not edit by hand.
// Bit-exact vs Python model round13/models/r13.py ({name}).
// Direct boolean assigns inside one always @(*) block (no functions).
module {name}(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
"""

V_DECL = """
reg [31:0] L, R;
reg [31:0] Lt, Rt;
reg [31:0] D, t, u;
reg [31:0] rk32;
reg [63:0] rkv;
integer i, r;
"""

# Standard round-key block. NOTE: loop i is 0-based; C/Python call RK32(key,i)
# with 1-based i, and RK32 itself bakes in (i+1). Round r = i+1 (1-based)
# therefore needs 13*((i+1)+1) = 13*(i+2) and ((i+2)*GOLDEN) here.
# (round-11 off-by-one lesson: this was (i+1) before; check_rtl failed 10/10
# and passes 10/10 after the fix.)
V_RK_STD = """\
        r = (13 * (i + 2)) % 64;
        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 2) * 64'h9E3779B97F4A7C15);
        rk32 = rkv[31:0];"""

V_TAIL_FEISTEL = """\
        Lt = R;
        Rt = L ^ t ^ rk32;
        L = Lt;
        R = Rt;"""

V_TAIL_FEISTEL_NOKEY = """\
        Lt = R;
        Rt = L ^ t;
        L = Lt;
        R = Rt;"""


def _chi_block(src, a, b):
    return (chi_assigns("t", src) + "\n"
            f"            t = {lin_expr('t', a, b)};\n")


def gen_rtl(name, kind, rounds, lin, desc):
    a, b = lin
    body = []
    body.append("always @(*) begin")
    body.append("    L = val[63:32];")
    body.append("    R = val[31:0];")
    body.append(f"    for (i = 0; i < {rounds}; i = i + 1) begin")

    if kind == "s1x2":
        # Two keys/round: C calls RK32(key,2*i-1)/RK32(key,2*i) with 1-based i;
        # RK32 bakes (j+1), so 0-based i0 needs (2*i0+2) and (2*i0+3).
        body.append("        // ---- F = lin(S1(lin(S1(R^rkA))^rkB)) ----")
        body.append("        r = (13 * (2*i + 2)) % 64;")
        body.append("        rkv = ((key << r) | (key >> (64 - r))) ^ ((2*i + 2) * 64'h9E3779B97F4A7C15);")
        body.append("        t = R ^ rkv[31:0];")
        body.append(sbox_dnf_assigns("u", "t"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append("        r = (13 * (2*i + 3)) % 64;")
        body.append("        rkv = ((key << r) | (key >> (64 - r))) ^ ((2*i + 3) * 64'h9E3779B97F4A7C15);")
        body.append("        t = t ^ rkv[31:0];")
        body.append(sbox_dnf_assigns("u", "t"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append(V_TAIL_FEISTEL_NOKEY)
    elif kind == "chi":
        body.append("        // ---- F = lin(chi(R)) ^ rk ----")
        body.append(_chi_block("R", a, b))
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "chis1":
        body.append("        // ---- F = lin(S1(chi(R))) ^ rk ----")
        body.append(chi_assigns("t", "R"))
        body.append(sbox_dnf_assigns("u", "t"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt":
        # 0-based even i <-> 1-based odd round -> S1 (matches C (i&1), 1-based)
        body.append("        // ---- odd rounds S1-F, even rounds chi-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns("u", "R"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append("        end else begin")
        body.append(_chi_block("R", a, b))
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "s1x3":
        # 0-based i<3 <-> 1-based i<=3 -> S1 (matches C (i<=3), 1-based)
        body.append("        // ---- rounds 1-3 S1-F, rounds 4-6 chi-F ----")
        body.append("        if (i < 3) begin")
        body.append(sbox_dnf_assigns("u", "R"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append("        end else begin")
        body.append(_chi_block("R", a, b))
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "lm":
        body.append("        // ---- Lai-Massey sigma(L,R)=(R,L^R): t=F(L^R)^rk; L'=R^t; R'=L^R ----")
        body.append("        D = L ^ R;")
        body.append(sbox_dnf_assigns("u", "D"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append(V_RK_STD)
        body.append("        Lt = R ^ t ^ rk32;")
        body.append("        Rt = D;")
        body.append("        L = Lt;")
        body.append("        R = Rt;")
    elif kind == "midk":
        body.append("        // ---- F = lin(S1(R) ^ rk): key between S-box and linear ----")
        body.append(V_RK_STD)
        body.append(sbox_dnf_assigns("u", "R"))
        body.append("            u = u ^ rk32;")
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append(V_TAIL_FEISTEL_NOKEY)
    elif kind == "rkhi":
        body.append("        // ---- rotating key-half: high32 on odd rounds, low32 on even ----")
        body.append("        // 0-based even i <-> 1-based odd round -> high32 (matches C (i&1), 1-based)")
        body.append("        r = (13 * (i + 2)) % 64;")
        body.append("        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 2) * 64'h9E3779B97F4A7C15);")
        body.append("        rk32 = (i[0] == 1'b0) ? rkv[63:32] : rkv[31:0];")
        body.append(sbox_dnf_assigns("u", "R"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append(V_TAIL_FEISTEL)
    elif kind == "sandw":
        body.append("        // ---- F = lin(S1(lin(R))) ^ rk ----")
        body.append(f"            t = {lin_expr('R', a, b)};")
        body.append(sbox_dnf_assigns("u", "t"))
        body.append(f"            t = {lin_expr('u', a, b)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    else:
        raise ValueError(kind)

    body.append("    end")
    body.append("end")
    body.append("")
    body.append("assign out = {R, L};")
    body.append("")
    body.append("endmodule")
    return V_HDR.format(name=name, desc=desc) + V_DECL + "\n".join(body) + "\n"


# ---------------- model.py / meta.json ----------------
MODEL_PY = '''"""Python model wrapper for {name} (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round13/models")
from r13 import {name} as _np

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
    # sanity: chi model spot-check vs a brute-force bit loop
    xv = np.array([0x0123456789ABCDEF, 0xFFFFFFFFFFFFFFFF, 0x0,
                   0x8000000000000001], dtype=np.uint64)
    for x in xv:
        xi = int(x)
        want = 0
        for i in range(32):
            a0 = (xi >> i) & 1
            a1 = (xi >> ((i + 1) % 32)) & 1
            a2 = (xi >> ((i + 2) % 32)) & 1
            want |= (a0 ^ ((1 - a1) & a2)) << i
        got = int(r13._chi32_np(np.uint64(xi)))
        assert got == want, (hex(xi), hex(got), hex(want))
    print("chi32 spot-check: 4 vectors OK")
    # invertibility self-test for the fixed Lai-Massey (round-trip through
    # the explicit inverse, 2000 random vectors x 2 keys)
    def _lm_inv(y, k, rounds):
        # output word is {R_out, L_out}: high half = R, low half = L
        L = y & r13.MASK32
        R = (y >> np.uint64(32)) & r13.MASK32
        for i in range(rounds, 0, -1):
            D = R  # R' = D
            t = r13._F_s1_311(D, r13._rk32_std_np(k, i))
            Rprev = (L ^ t) & r13.MASK32
            Lprev = (D ^ Rprev) & r13.MASK32
            L, R = Lprev, Rprev
        # input word convention is {L, R} (output is {R, L}): pack as input
        return ((L << np.uint64(32)) | R) & r13.MASK64
    rng2 = np.random.default_rng(999)
    for name, rounds in [("r13_lm4_s1_311_nw", 4),
                         ("r13_lm6_s1_311_nw", 6)]:
        fn = getattr(r13, name)
        for kk in (np.uint64(0x123456789ABCDEF0), np.uint64(0x0)):
            V = rng2.integers(0, 2**64, size=2000, dtype=np.uint64)
            Y = fn(V, kk)
            Vb = _lm_inv(Y, kk, rounds)
            assert np.array_equal(Vb, V), f"LM inverse failed: {name}"
    print("Lai-Massey invertibility: 2 candidates x 2 keys x 2000 vectors OK")
    # dedupe: pairwise-distinct model outputs across the spec set
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    outs = {}
    for name, kind, rounds, lin, desc in SPECS:
        fn = getattr(r13, name)
        o = fn(V, K).tobytes()
        assert o not in outs.values(), f"DUPLICATE model output: {name}"
        outs[name] = o
    print(f"dedupe: {len(SPECS)} specs pairwise-distinct OK")
    for name, kind, rounds, lin, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, kind, rounds, lin, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, kind, rounds, lin, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(r13, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
