#!/usr/bin/env python3
"""Round 14 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round14/models/r14.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
affine r7/r8/r9 key schedule. All r14 designs are Feistel-based (fixed-key
bijectivity structural); F5's final 64-bit diffusion is an invertible linear
map (proof in models/r14.py), verified empirically by a no-collision
self-test in emit().

Families (exploit the r13 heterogeneity breakthrough; everything in the
EXHAUSTED list in the task brief is out):
  F1: alt variants (6r):
      alt_rev: round order reversed (odd rounds chi-F, even rounds S1-F)
      alt713: alt with (7,13) rotmix on both S1 and chi rounds
      alt_chinolin: alt, but chi-F = chi32(R) ^ rk (NO rotmix on chi rounds)
      alt_chioff: alt with chi offsets (i+2,i+3): b_i=a_i^(~a_{i+2}&a_{i+3})
      alt_rkhi: alt; S1 rounds (odd) standard rk, chi rounds (even) rotating
                key-half
  F2: 4r lighter-strong-F probes:
      chis1l4: F = lin(3,11)(chi32(S1(R ^ rk))) (single key), 4r
      pars1chi: F = lin(3,11)(S1(R ^ rk)) ^ lin(3,11)(chi32(R)), 4r
  F3: 5r double-strength-F: F = lin(S1(lin(S1(R^rkA))^rkB)), (3,11), 5r
      (closes the round-strength question; S1 verdict first, full battery
      only if not dominated)
  F4: 6r heterogeneous placement:
      chi25: chi-F on rounds {2,5}, S1-F elsewhere
      chi16: chi-F on rounds {1,6}, S1-F elsewhere
  F5: r9 structure + cheap invertible 64-bit final diffusion:
      out = W ^ rotl64(W,a) ^ rotl64(W,b), W = {R,L}; (a,b) = (13,37),(7,29)
      p(t) = 1 + t^a + t^b, p(1) = 1 (mod 2) -> coprime with (t+1)^64 =
      t^64+1 -> permutation of GF(2)^64. (Single-term out ^= rotl64(out,r)
      is NOT bijective: kernel = r-periodic vectors -> excluded.)
  F6: s1chi: 6r, F = lin(3,11)(chi32(S1(R))) ^ rk (reverse of r13 chi->S1)

RTL policy (rounds 8/11/12/13): direct boolean assigns inside ONE always @(*)
block (no Verilog functions; no module-level assign may read an
always-block-driven reg and feed it BACK inside the block -- feed-forward
reads like `assign out = {R,L}` are the established safe pattern). Round-key
indexing: C/Python call RK32(key, i) with 1-based i and the function itself
bakes in (i+1) -> rotl64(k,13*(i+1)) ^ (i+1)*GOLDEN; the 0-based Verilog loop
therefore uses (i+2) (round-11 off-by-one lesson). F3 uses two keys/round:
C calls RK32(key,2*i-1)/RK32(key,2*i) (1-based i) -> Verilog bakes
(2*i+2)/(2*i+3).

Usage: python3 round14/gen_r14.py   (writes fast_battery/candidates/r14_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R14 = os.path.join(EXP, "round14")
sys.path.insert(0, os.path.join(R14, "models"))
import numpy as np  # noqa: E402
import r14  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

# (name, kind, rounds, lin(a,b) or outdiff(a,b), desc)
SPECS = [
    # F1: alt variants, 6r
    ("r14_feist6_chi_s1alt_nw", "alt_rev", 6, (3, 11),
     "6r Feistel, odd rounds chi-F / even rounds S1-F (reversed alt), NO whitening"),
    ("r14_feist6_alt713_nw", "alt713", 6, (7, 13),
     "6r Feistel, odd rounds S1-F / even rounds chi-F, rotmix (7,13), NO whitening"),
    ("r14_feist6_alt_chinolin_nw", "alt_chinolin", 6, (3, 11),
     "6r Feistel, odd rounds S1-F(lin311) / even rounds chi32(R)^rk (no rotmix), NO whitening"),
    ("r14_feist6_alt_chioff_nw", "alt_chioff", 6, (3, 11),
     "6r Feistel, odd rounds S1-F / even rounds chi(i+2,i+3)-F, NO whitening"),
    ("r14_feist6_alt_rkhi_nw", "alt_rkhi", 6, (3, 11),
     "6r Feistel, odd rounds S1-F std rk / even rounds chi-F rotating key-half, NO whitening"),
    # F2: 4r lighter-strong-F probes
    ("r14_feist4_chis1l_nw", "chis1l4", 4, (3, 11),
     "4r Feistel, F=lin311(chi32(S1(R^rk))), NO whitening"),
    ("r14_feist4_pars1chi_nw", "pars1chi", 4, (3, 11),
     "4r Feistel, F=lin311(S1(R^rk))^lin311(chi32(R)), NO whitening"),
    # F3: 5r double-strength-F
    ("r14_feist5_s1x2_311_nw", "s1x2", 5, (3, 11),
     "5r Feistel, F=lin311(S1(lin311(S1(R^rkA))^rkB)), 2 keys/round, NO whitening"),
    # F4: heterogeneous placement, 6r
    ("r14_feist6_chi25_nw", "chi25", 6, (3, 11),
     "6r Feistel, chi-F on rounds {2,5}, S1-F elsewhere, NO whitening"),
    ("r14_feist6_chi16_nw", "chi16", 6, (3, 11),
     "6r Feistel, chi-F on rounds {1,6}, S1-F elsewhere, NO whitening"),
    # F5: r9 + invertible 64-bit final diffusion
    ("r14_feist6_r9_outdiff_nw", "r9out", 6, (13, 37),
     "6r r9 Feistel + out = W^rotl64(W,13)^rotl64(W,37), NO whitening"),
    ("r14_feist6_r9_outdiff2_nw", "r9out", 6, (7, 29),
     "6r r9 Feistel + out = W^rotl64(W,7)^rotl64(W,29), NO whitening"),
    # F6: S1->chi->lin single pass
    ("r14_feist6_s1chi_311_nw", "s1chi", 6, (3, 11),
     "6r Feistel, F=lin311(chi32(S1(R)))^rk, NO whitening"),
]


# ---------------- Quine-McCluskey (4 vars), as in gen_r13.py ----------------
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


def chi_assigns(dst, src, off=(1, 2)):
    """32 assigns: dst = chi(src), b_i = a_i ^ (~a_{i+o0} & a_{i+o1})."""
    o0, o1 = off
    lines = []
    for i in range(32):
        lines.append(
            f"            {dst}[{i}] = {src}[{i}] ^ "
            f"(~{src}[{(i + o0) % 32}] & {src}[{(i + o1) % 32}]);")
    return "\n".join(lines)


def _rot_expr(reg, n):
    # rotl32(reg,n) = {reg[32-n-1:0], reg[31:32-n]}
    return f"{{{reg}[{32 - n - 1}:0], {reg}[31:{32 - n}]}}"


def _rot64_expr(reg, n):
    return f"{{{reg}[{64 - n - 1}:0], {reg}[63:{64 - n}]}}"


def lin_expr(reg, a, b):
    return f"{reg} ^ {_rot_expr(reg, a)} ^ {_rot_expr(reg, b)}"


# ---------------- C ----------------
C_COMMON = """/* {name}: {desc}
 * GENERATED by round14/gen_r14.py -- do not edit by hand.
 * Bit-exact vs Python model round14/models/r14.py ({name}). */
#include <stdint.h>

static const uint8_t S1[16] = {{0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10}};

static uint32_t sbox_layer32(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)S1[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}}

/* chi32: b_i = a_i ^ (~a_{{i+o0}} & a_{{i+o1}}). Even width -> not a
 * permutation -- fine, a Feistel F need not be invertible. */
static uint32_t chi32(uint32_t x, int o0, int o1) {{
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + o0) % 32)) & 1u;
        uint32_t a2 = (x >> ((i + o1) % 32)) & 1u;
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
static uint32_t RK32_hi_lo(uint64_t k, int i) {{
    /* rotating key-half: high32 on odd rounds, low32 on even (i 1-based) */
    return (i & 1) ? (uint32_t)(RK64(k, i) >> 32) : (uint32_t)RK64(k, i);
}}

static uint32_t lin_ab(uint32_t x, int a, int b) {{
    return x ^ rotl32(x, a) ^ rotl32(x, b);
}}

static uint32_t F_s1(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(sbox_layer32(R), a, b) ^ rk;
}}
static uint32_t F_chi(uint32_t R, uint32_t rk, int a, int b, int o0, int o1) {{
    return lin_ab(chi32(R, o0, o1), a, b) ^ rk;
}}
static uint32_t F_chi_nolin(uint32_t R, uint32_t rk) {{
    return chi32(R, 1, 2) ^ rk;
}}
static uint32_t F_s1chi(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(chi32(sbox_layer32(R), 1, 2), a, b) ^ rk;
}}
static uint32_t F_chis1l(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(chi32(sbox_layer32(R ^ rk), 1, 2), a, b);
}}
static uint32_t F_pars1chi(uint32_t R, uint32_t rk, int a, int b) {{
    return lin_ab(sbox_layer32(R ^ rk), a, b) ^ lin_ab(chi32(R, 1, 2), a, b);
}}
static uint32_t F_s1x2(uint32_t R, uint32_t rkA, uint32_t rkB, int a, int b) {{
    uint32_t t = lin_ab(sbox_layer32(R ^ rkA), a, b) ^ rkB;
    return lin_ab(sbox_layer32(t), a, b);
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
{tail}
}}
"""

C_TAIL_STD = """    return ((uint64_t)R << 32) | L;"""

C_TAIL_OUTDIFF = """    /* invertible 64-bit final diffusion: p(t)=1+t^{a}+t^{b},
     * p(1)=1 (mod 2) -> coprime with (t+1)^64=t^64+1 -> permutation. */
    uint64_t W = ((uint64_t)R << 32) | L;
    return W ^ rotl64(W, {a}) ^ rotl64(W, {b});"""

C_F_LINE = {
    "alt_rev": ("        uint32_t F = (i & 1) ? F_chi(R, RK32(key, i), {a}, {b}, 1, 2)\n"
                "                           : F_s1(R, RK32(key, i), {a}, {b});"),
    "alt713": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), {a}, {b})\n"
               "                           : F_chi(R, RK32(key, i), {a}, {b}, 1, 2);"),
    "alt_chinolin": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), {a}, {b})\n"
                     "                           : F_chi_nolin(R, RK32(key, i));"),
    "alt_chioff": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), {a}, {b})\n"
                   "                           : F_chi(R, RK32(key, i), {a}, {b}, 2, 3);"),
    "alt_rkhi": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), {a}, {b})\n"
                 "                           : F_chi(R, RK32_hi_lo(key, i), {a}, {b}, 1, 2);"),
    "chis1l4": "        uint32_t F = F_chis1l(R, RK32(key, i), {a}, {b});",
    "pars1chi": "        uint32_t F = F_pars1chi(R, RK32(key, i), {a}, {b});",
    "s1x2": "        uint32_t F = F_s1x2(R, RK32(key, 2*i-1), RK32(key, 2*i), {a}, {b});",
    "chi25": ("        uint32_t F = (i == 2 || i == 5)\n"
              "                 ? F_chi(R, RK32(key, i), {a}, {b}, 1, 2)\n"
              "                 : F_s1(R, RK32(key, i), {a}, {b});"),
    "chi16": ("        uint32_t F = (i == 1 || i == 6)\n"
              "                 ? F_chi(R, RK32(key, i), {a}, {b}, 1, 2)\n"
              "                 : F_s1(R, RK32(key, i), {a}, {b});"),
    "r9out": "        uint32_t F = F_s1(R, RK32(key, i), {a0}, {b0});",
    "s1chi": "        uint32_t F = F_s1chi(R, RK32(key, i), {a}, {b});",
}


def gen_impl(name, kind, rounds, ab, desc):
    a, b = ab
    body = C_COMMON.format(name=name, desc=desc)
    f_line = C_F_LINE[kind]
    if kind == "r9out":
        f_line = f_line.format(a0=3, b0=11)
        tail = C_TAIL_OUTDIFF.format(a=a, b=b)
    else:
        f_line = f_line.format(a=a, b=b)
        tail = C_TAIL_STD
    body += C_MAIN_FEISTEL.format(rounds=rounds, f_line=f_line, tail=tail)
    return body


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round14/gen_r14.py -- do not edit by hand.
// Bit-exact vs Python model round14/models/r14.py ({name}).
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
reg [31:0] t, u;
reg [31:0] rk32;
reg [63:0] rkv;
reg [63:0] W;
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


def _s1_block(a, b):
    return (sbox_dnf_assigns("u", "R") + "\n"
            f"            t = {lin_expr('u', a, b)};\n")


def _chi_block(a, b, off=(1, 2)):
    return (chi_assigns("t", "R", off) + "\n"
            f"            t = {lin_expr('t', a, b)};\n")


def gen_rtl(name, kind, rounds, ab, desc):
    a, b = ab
    body = []
    body.append("always @(*) begin")
    body.append("    L = val[63:32];")
    body.append("    R = val[31:0];")
    body.append(f"    for (i = 0; i < {rounds}; i = i + 1) begin")

    if kind == "alt_rev":
        # 0-based even i <-> 1-based odd round -> chi (matches C (i&1)->chi on odd)
        body.append("        // ---- odd rounds chi-F, even rounds S1-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(_chi_block(a, b))
        body.append("        end else begin")
        body.append(_s1_block(a, b))
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt713":
        body.append("        // ---- odd rounds S1-F, even rounds chi-F, (7,13) ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(_s1_block(a, b))
        body.append("        end else begin")
        body.append(_chi_block(a, b))
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt_chinolin":
        # 0-based even i <-> 1-based odd round -> S1; chi rounds: t = chi(R), tail with key
        body.append("        // ---- odd rounds S1-F(lin), even rounds chi32(R)^rk ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(_s1_block(a, b))
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
        body.append("        end else begin")
        body.append(chi_assigns("t", "R", (1, 2)))
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
        body.append("        end")
    elif kind == "alt_chioff":
        body.append("        // ---- odd rounds S1-F, even rounds chi(i+2,i+3)-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(_s1_block(a, b))
        body.append("        end else begin")
        body.append(_chi_block(a, b, (2, 3)))
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt_rkhi":
        # 0-based even i <-> 1-based odd round -> S1 with standard rk;
        # 0-based odd i <-> 1-based even round -> chi with rotating key-half.
        # C: _rk32_hi_lo_np(k, i1based) = high32 on odd, low32 on even.
        # On 1-based EVEN rounds -> low32 = rkv[31:0].
        body.append("        // ---- odd rounds S1-F std rk; even rounds chi-F rotating key-half ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(_s1_block(a, b))
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
        body.append("        end else begin")
        body.append(_chi_block(a, b))
        body.append("        r = (13 * (i + 2)) % 64;")
        body.append("        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 2) * 64'h9E3779B97F4A7C15);")
        body.append("        rk32 = rkv[31:0];  // 1-based even round -> low32")
        body.append(V_TAIL_FEISTEL)
        body.append("        end")
    elif kind == "chis1l4":
        body.append("        // ---- F = lin(chi(S1(R ^ rk))) ----")
        body.append(V_RK_STD)
        body.append("            t = R ^ rk32;")
        body.append(sbox_dnf_assigns("u", "t"))
        body.append(chi_assigns("t", "u", (1, 2)))
        body.append(f"            t = {lin_expr('t', a, b)};")
        body.append(V_TAIL_FEISTEL_NOKEY)
    elif kind == "pars1chi":
        body.append("        // ---- F = lin(S1(R^rk)) ^ lin(chi(R)) ----")
        body.append(V_RK_STD)
        body.append("            t = R ^ rk32;")
        body.append(sbox_dnf_assigns("u", "t"))
        body.append(f"            u = {lin_expr('u', a, b)};")
        body.append(chi_assigns("t", "R", (1, 2)))
        body.append(f"            t = {lin_expr('t', a, b)};")
        body.append("            t = u ^ t;")
        body.append(V_TAIL_FEISTEL_NOKEY)
    elif kind == "s1x2":
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
    elif kind in ("chi25", "chi16"):
        # 1-based chi rounds {2,5} <-> 0-based {1,4}; {1,6} <-> {0,5}
        chi_i0 = {1, 4} if kind == "chi25" else {0, 5}
        cond = " || ".join(f"i == {j}" for j in sorted(chi_i0))
        body.append(f"        // ---- chi-F on 1-based rounds "
                    f"{sorted([j + 1 for j in chi_i0])}, S1-F elsewhere ----")
        body.append(f"        if ({cond}) begin")
        body.append(_chi_block(a, b))
        body.append("        end else begin")
        body.append(_s1_block(a, b))
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "r9out":
        body.append("        // ---- r9 round: F = lin311(S1(R)) ^ rk ----")
        body.append(_s1_block(3, 11))
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "s1chi":
        body.append("        // ---- F = lin(chi(S1(R))) ^ rk ----")
        body.append(sbox_dnf_assigns("u", "R"))
        body.append(chi_assigns("t", "u", (1, 2)))
        body.append(f"            t = {lin_expr('t', a, b)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    else:
        raise ValueError(kind)

    body.append("    end")
    if kind == "r9out":
        # Invertible 64-bit final diffusion, feed-forward only (no loop).
        body.append(f"    W = {{R, L}};")
    body.append("end")
    body.append("")
    if kind == "r9out":
        body.append(f"assign out = W ^ {_rot64_expr('W', a)} ^ {_rot64_expr('W', b)};")
    else:
        body.append("assign out = {R, L};")
    body.append("")
    body.append("endmodule")
    return V_HDR.format(name=name, desc=desc) + V_DECL + "\n".join(body) + "\n"


# ---------------- model.py / meta.json ----------------
MODEL_PY = '''"""Python model wrapper for {name} (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round14/models")
from r14 import {name} as _np

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
    # chi offset spot-check: model vs brute-force bit loop (both offsets)
    xv = np.array([0x0123456789ABCDEF, 0xFFFFFFFFFFFFFFFF, 0x0,
                   0x8000000000000001], dtype=np.uint64)
    for (o0, o1), fn in [((1, 2), r14._chi32_np), ((2, 3), r14._chi32_off_np)]:
        for x in xv:
            xi = int(x)
            want = 0
            for i in range(32):
                a0 = (xi >> i) & 1
                a1 = (xi >> ((i + o0) % 32)) & 1
                a2 = (xi >> ((i + o1) % 32)) & 1
                want |= (a0 ^ ((1 - a1) & a2)) << i
            got = int(fn(np.uint64(xi)))
            assert got == want, (o0, o1, hex(xi), hex(got), hex(want))
    print("chi32 spot-check (offsets (1,2) and (2,3)): 8 vectors OK")
    # F5 final-diffusion invertibility: algebraic proof in the module docstring
    # (p(t) = 1 + t^a + t^b, p(1) = 1 mod 2, coprime with (t+1)^64); empirical
    # no-collision check on 200k random inputs for each (a,b).
    rng = np.random.default_rng(777)
    for name, (a, b) in [("r14_feist6_r9_outdiff_nw", (13, 37)),
                         ("r14_feist6_r9_outdiff2_nw", (7, 29))]:
        fn = getattr(r14, name)
        V = rng.integers(0, 2**64, size=200_000, dtype=np.uint64)
        K = np.uint64(0x123456789ABCDEF0)
        O = fn(V, K)
        assert len(np.unique(O)) == len(O), f"outdiff collision: {name}"
    print("F5 output-diffusion: no collisions on 2x200k vectors OK")
    # dedupe: pairwise-distinct model outputs across the spec set
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    outs = {}
    for name, kind, rounds, ab, desc in SPECS:
        fn = getattr(r14, name)
        o = fn(V, K).tobytes()
        assert o not in outs.values(), f"DUPLICATE model output: {name}"
        outs[name] = o
    print(f"dedupe: {len(SPECS)} specs pairwise-distinct OK")
    for name, kind, rounds, ab, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, kind, rounds, ab, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, kind, rounds, ab, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(r14, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
