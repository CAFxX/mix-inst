#!/usr/bin/env python3
"""Round 15 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round15/models/r15.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): balanced Feistel, 32-bit halves, {R,L} output, NO whitening
(except alt_wh which whitens the input with the key), affine r7/r8/r9 key
schedule. All r15 designs are Feistel-based (fixed-key bijectivity
structural); whitening is an XOR with a fixed-key constant -> bijection.

Families (exploit the r13 heterogeneity breakthrough; everything in the
EXHAUSTED list in the task brief is out):
  F1: alt rotation-heterogeneity (6r):
      alt_s713_c311: odd rounds S1-F (7,13), even rounds chi-F (3,11)
      alt_s311_c713: odd rounds S1-F (3,11), even rounds chi-F (7,13)
      alt_2rot: S1/chi alt; rotmix pair alternates every two rounds:
                {1,2} (3,11), {3,4} (7,13), {5,6} (3,11)
                (the task's "(c)" collapsed to (b) under the natural reading,
                so this is the genuinely distinct rotation-block variant)
  F2: alt + input whitening (6r):
      alt_wh: W = val ^ key, then r13 alt (odd S1 / even chi, (3,11))
  F3: mixed single/double-F rounds:
      mix5_db3: 5r, round 3 double-F (s1x2, keys 3,4);
                singles [s1, chi, chi, s1] on rounds 1,2,4,5
      mix6_db4: 6r, round 4 double-F (keys 4,5);
                singles [s1, chi, s1, s1, chi]
      mix5_db24: 5r, double-F on rounds 2 (keys 2,3) and 4 (keys 5,6);
                singles [s1, chi, s1]
      mix6_db34: 6r, double-F on rounds 3 (keys 3,4) and 4 (keys 5,6);
                singles [s1, chi, s1, chi]
      (mixed rounds are unrolled in C and Verilog from the same per-round
      spec; key index j is 1-based C sense: RK32 bakes (j+1))
  F4: parallel-split F (6r):
      parsplit: t[15:0] = S1(R[15:0]) (4 nibbles),
                t[31:16] = chi16(R[31:16]) (offsets (1,2) mod 16);
                F = lin(3,11)(t) ^ rk
  F5: key-diffusion variants on the r13 alt structure (6r):
      alt_rkdiff: rk' = RK32(key,i) ^ rotl32(RK32(key,i+1), 8)
      alt_rksbox: rk = sbox_layer32(RK32(key, i))
  F6: alt with chi offsets (2,3) (6r):
      alt_chioff023: odd rounds S1-F (3,11), even rounds chi-F with
                b_i = a_i ^ (~a_{i+2} & a_{i+3})

RTL policy (rounds 8/11/12/13/14): direct boolean assigns inside ONE always
@(*) block (no Verilog functions; no module-level assign may read an
always-block-driven reg and feed it BACK inside the block -- feed-forward
reads like `assign out = {R,L}` are the established safe pattern). Round-key
indexing: C/Python call RK32(key, j) with 1-based j and the function itself
bakes in (j+1) -> rotl64(k,13*(j+1)) ^ (j+1)*GOLDEN; the 0-based Verilog loop
therefore uses (i+2) (round-11 off-by-one lesson). Mixed rounds are unrolled
with explicit per-round key constants via _rk_v(j).

Usage: python3 round15/gen_r15.py   (writes fast_battery/candidates/r15_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R15 = os.path.join(EXP, "round15")
sys.path.insert(0, os.path.join(R15, "models"))
import numpy as np  # noqa: E402
import r15  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

# (name, kind, rounds, params, desc)
SPECS = [
    # F1: alt rotation-heterogeneity, 6r
    ("r15_feist6_alt_s713_c311_nw", "alt_s713_c311", 6, None,
     "6r Feistel, odd rounds S1-F (7,13) / even rounds chi-F (3,11), NO whitening"),
    ("r15_feist6_alt_s311_c713_nw", "alt_s311_c713", 6, None,
     "6r Feistel, odd rounds S1-F (3,11) / even rounds chi-F (7,13), NO whitening"),
    ("r15_feist6_alt_2rot_nw", "alt_2rot", 6, None,
     "6r Feistel, S1/chi alt; rotmix pair per round-block: {1,2}(3,11) {3,4}(7,13) {5,6}(3,11), NO whitening"),
    # F2: alt + input whitening, 6r
    ("r15_feist6_alt_wh_nw", "alt_wh", 6, None,
     "6r Feistel, input whitening W=val^key, then odd S1-F / even chi-F (3,11)"),
    # F3: mixed single/double-F rounds
    ("r15_feist5_db3_nw", "mixed", 5,
     {"fsched": ["s1", "chi", "s1x2", "chi", "s1"],
      "kidx": [[1], [2], [3, 4], [5], [6]]},
     "5r Feistel, round 3 double-F (s1x2, keys 3,4); singles [s1,chi,chi,s1], NO whitening"),
    ("r15_feist6_db4_nw", "mixed", 6,
     {"fsched": ["s1", "chi", "s1", "s1x2", "s1", "chi"],
      "kidx": [[1], [2], [3], [4, 5], [6], [7]]},
     "6r Feistel, round 4 double-F (s1x2, keys 4,5); singles [s1,chi,s1,s1,chi], NO whitening"),
    ("r15_feist5_db24_nw", "mixed", 5,
     {"fsched": ["s1", "s1x2", "chi", "s1x2", "s1"],
      "kidx": [[1], [2, 3], [4], [5, 6], [7]]},
     "5r Feistel, rounds 2,4 double-F (s1x2); singles [s1,chi,s1], NO whitening"),
    ("r15_feist6_db34_nw", "mixed", 6,
     {"fsched": ["s1", "chi", "s1x2", "s1x2", "s1", "chi"],
      "kidx": [[1], [2], [3, 4], [5, 6], [7], [8]]},
     "6r Feistel, rounds 3,4 double-F (s1x2); singles [s1,chi,s1,chi], NO whitening"),
    # F4: parallel-split F, 6r
    ("r15_feist6_parsplit_nw", "parsplit", 6, None,
     "6r Feistel, F=lin311(S1(R[15:0])||chi16(R[31:16]))^rk, NO whitening"),
    # F5: key-diffusion variants on r13 alt, 6r
    ("r15_feist6_alt_rkdiff_nw", "alt_rkdiff", 6, None,
     "6r Feistel, odd S1-F / even chi-F (3,11); rk=RK32(i)^rotl32(RK32(i+1),8), NO whitening"),
    ("r15_feist6_alt_rksbox_nw", "alt_rksbox", 6, None,
     "6r Feistel, odd S1-F / even chi-F (3,11); rk=sbox_layer32(RK32(i)), NO whitening"),
    # F6: alt with chi offsets (2,3), 6r
    ("r15_feist6_alt_chioff023_nw", "alt_chioff023", 6, None,
     "6r Feistel, odd rounds S1-F (3,11) / even rounds chi(2,3)-F, NO whitening"),
]


# ---------------- Quine-McCluskey (4 vars), as in gen_r13.py/gen_r14.py ----------------
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


def sbox_dnf_assigns(dst, src, nibbles=8):
    """DNF assigns: dst = S1(src) over `nibbles` 4-bit nibbles."""
    lines = []
    for j in range(nibbles):
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


def chi16_assigns(dst, src, base):
    """16 assigns: dst[base+i] = chi16(src[base+i]),
    b_i = a_i ^ (~a_{(i+1)%16} & a_{(i+2)%16})."""
    lines = []
    for i in range(16):
        lines.append(
            f"            {dst}[{base + i}] = {src}[{base + i}] ^ "
            f"(~{src}[{base + (i + 1) % 16}] & {src}[{base + (i + 2) % 16}]);")
    return "\n".join(lines)


def _rot_expr(reg, n):
    # rotl32(reg,n) = {reg[32-n-1:0], reg[31:32-n]}
    return f"{{{reg}[{32 - n - 1}:0], {reg}[31:{32 - n}]}}"


def lin_expr(reg, a, b):
    return f"{reg} ^ {_rot_expr(reg, a)} ^ {_rot_expr(reg, b)}"


def _rk_v(j):
    """Verilog statements computing rkv from a 1-based C key index j.
    C: RK64(key,j) = rotl64(key,13*(j+1)) ^ (j+1)*GOLDEN (j 1-based)."""
    shift = (13 * (j + 1)) % 64
    mult = j + 1
    if shift == 0:
        return f"        rkv = key ^ ({mult} * 64'h9E3779B97F4A7C15);"
    return (f"        r = {shift};\n"
            f"        rkv = ((key << r) | (key >> (64 - r))) ^ "
            f"({mult} * 64'h9E3779B97F4A7C15);")


# ---------------- C ----------------
C_COMMON = """/* {name}: {desc}
 * GENERATED by round15/gen_r15.py -- do not edit by hand.
 * Bit-exact vs Python model round15/models/r15.py ({name}). */
#include <stdint.h>

static const uint8_t S1[16] = {{0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10}};

static uint32_t sbox_layer32(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)S1[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}}

static uint32_t sbox_layer16(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 4; i++)
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

/* chi16: 16-bit chi, offsets (1,2) mod 16. */
static uint32_t chi16(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 16; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + 1) % 16)) & 1u;
        uint32_t a2 = (x >> ((i + 2) % 16)) & 1u;
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
static uint32_t F_chi(uint32_t R, uint32_t rk, int a, int b, int o0, int o1) {{
    return lin_ab(chi32(R, o0, o1), a, b) ^ rk;
}}
static uint32_t F_parsplit(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16) << 16) | sbox_layer16(R & 0xFFFF);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_s1x2(uint32_t R, uint32_t rkA, uint32_t rkB, int a, int b) {{
    uint32_t t = lin_ab(sbox_layer32(R ^ rkA), a, b) ^ rkB;
    return lin_ab(sbox_layer32(t), a, b);
}}

"""

C_LOOP_STD = """uint64_t mix_hash(uint64_t val, uint64_t key) {{
{prelude}    for (int i = 1; i <= {rounds}; i++) {{
{f_line}
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }}
    return ((uint64_t)R << 32) | L;
}}
"""

C_PRELUDE_STD = """    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
"""
C_PRELUDE_WH = """    uint32_t L = (uint32_t)(val >> 32) ^ (uint32_t)(key >> 32);
    uint32_t R = (uint32_t)val ^ (uint32_t)key;
"""

C_F_LINE = {
    "alt_s713_c311": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), 7, 13)\n"
                      "                           : F_chi(R, RK32(key, i), 3, 11, 1, 2);"),
    "alt_s311_c713": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), 3, 11)\n"
                      "                           : F_chi(R, RK32(key, i), 7, 13, 1, 2);"),
    "alt_2rot": ("        int pa = ((((i - 1) / 2) & 1) == 0) ? 3 : 7;\n"
                 "        int pb = ((((i - 1) / 2) & 1) == 0) ? 11 : 13;\n"
                 "        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), pa, pb)\n"
                 "                           : F_chi(R, RK32(key, i), pa, pb, 1, 2);"),
    "alt_wh": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), 3, 11)\n"
               "                           : F_chi(R, RK32(key, i), 3, 11, 1, 2);"),
    "parsplit": "        uint32_t F = F_parsplit(R, RK32(key, i));",
    "alt_rkdiff": ("        uint32_t rk = RK32(key, i) ^ rotl32(RK32(key, i + 1), 8);\n"
                   "        uint32_t F = (i & 1) ? F_s1(R, rk, 3, 11)\n"
                   "                           : F_chi(R, rk, 3, 11, 1, 2);"),
    "alt_rksbox": ("        uint32_t rk = sbox_layer32(RK32(key, i));\n"
                   "        uint32_t F = (i & 1) ? F_s1(R, rk, 3, 11)\n"
                   "                           : F_chi(R, rk, 3, 11, 1, 2);"),
    "alt_chioff023": ("        uint32_t F = (i & 1) ? F_s1(R, RK32(key, i), 3, 11)\n"
                      "                           : F_chi(R, RK32(key, i), 3, 11, 2, 3);"),
}


def gen_impl(name, kind, rounds, params, desc):
    body = C_COMMON.format(name=name, desc=desc)
    if kind == "mixed":
        fsched = params["fsched"]
        kidx = params["kidx"]
        assert len(fsched) == rounds and len(kidx) == rounds
        lines = [C_PRELUDE_STD.rstrip("\n")]
        for r in range(1, rounds + 1):
            f = fsched[r - 1]
            ks = kidx[r - 1]
            lines.append(f"    /* round {r}: {f}, keys {ks} */")
            if f == "s1":
                lines.append(f"    {{ uint32_t F = F_s1(R, RK32(key, {ks[0]}), 3, 11);")
            elif f == "chi":
                lines.append(f"    {{ uint32_t F = F_chi(R, RK32(key, {ks[0]}), 3, 11, 1, 2);")
            elif f == "s1x2":
                lines.append(f"    {{ uint32_t F = F_s1x2(R, RK32(key, {ks[0]}), RK32(key, {ks[1]}), 3, 11);")
            else:
                raise ValueError(f)
            lines.append("      uint32_t nL = R, nR = L ^ F; L = nL; R = nR; }")
        body += ("uint64_t mix_hash(uint64_t val, uint64_t key) {\n" +
                 "\n".join(lines) + "\n"
                 "    return ((uint64_t)R << 32) | L;\n}\n")
    else:
        prelude = C_PRELUDE_WH if kind == "alt_wh" else C_PRELUDE_STD
        f_line = C_F_LINE[kind]
        body += C_LOOP_STD.format(prelude=prelude, rounds=rounds, f_line=f_line)
    return body

# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round15/gen_r15.py -- do not edit by hand.
// Bit-exact vs Python model round15/models/r15.py ({name}).
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

# Standard round-key block. NOTE: loop i is 0-based; C/Python call RK32(key,j)
# with 1-based j, and RK32 itself bakes in (j+1). Round r = i+1 (1-based)
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


def _parsplit_block():
    lines = [sbox_dnf_assigns("u", "R", nibbles=4),
             chi16_assigns("u", "R", 16),
             f"            t = {lin_expr('u', 3, 11)};"]
    return "\n".join(lines) + "\n"


def gen_rtl(name, kind, rounds, params, desc):
    body = []
    body.append("always @(*) begin")
    if kind == "alt_wh":
        body.append("    L = val[63:32] ^ key[63:32];  // input whitening")
        body.append("    R = val[31:0] ^ key[31:0];")
    else:
        body.append("    L = val[63:32];")
        body.append("    R = val[31:0];")

    if kind == "mixed":
        # Unrolled rounds from the shared per-round spec.
        fsched = params["fsched"]
        kidx = params["kidx"]
        for r1 in range(1, rounds + 1):
            f = fsched[r1 - 1]
            ks = kidx[r1 - 1]
            body.append(f"    // ---- round {r1}: {f}, keys {ks} ----")
            if f in ("s1", "chi"):
                body.append(_rk_v(ks[0]).rstrip("\n"))
                body.append("        rk32 = rkv[31:0];")
                body.append(_s1_block(3, 11) if f == "s1"
                            else _chi_block(3, 11))
                body.append(V_TAIL_FEISTEL)
            elif f == "s1x2":
                jA, jB = ks
                body.append(_rk_v(jA).rstrip("\n"))
                body.append("        t = R ^ rkv[31:0];")
                body.append(sbox_dnf_assigns("u", "t"))
                body.append(f"            t = {lin_expr('u', 3, 11)};")
                body.append(_rk_v(jB).rstrip("\n"))
                body.append("        t = t ^ rkv[31:0];")
                body.append(sbox_dnf_assigns("u", "t"))
                body.append(f"            t = {lin_expr('u', 3, 11)};")
                body.append(V_TAIL_FEISTEL_NOKEY)
            else:
                raise ValueError(f)
    else:
        body.append(f"    for (i = 0; i < {rounds}; i = i + 1) begin")

        if kind == "alt_s713_c311":
            body.append("        // ---- odd rounds S1-F (7,13), even rounds chi-F (3,11) ----")
            body.append("        if (i[0] == 1'b0) begin")
            body.append(_s1_block(7, 13))
            body.append("        end else begin")
            body.append(_chi_block(3, 11))
            body.append("        end")
            body.append(V_RK_STD)
            body.append(V_TAIL_FEISTEL)
        elif kind == "alt_s311_c713":
            body.append("        // ---- odd rounds S1-F (3,11), even rounds chi-F (7,13) ----")
            body.append("        if (i[0] == 1'b0) begin")
            body.append(_s1_block(3, 11))
            body.append("        end else begin")
            body.append(_chi_block(7, 13))
            body.append("        end")
            body.append(V_RK_STD)
            body.append(V_TAIL_FEISTEL)
        elif kind == "alt_2rot":
            # 0-based i0: rounds 1,2 -> (3,11); 3,4 -> (7,13); 5,6 -> (3,11)
            # i0>>1 & 1: 0,0,1,1,0,0 -> matches ((i1-1)//2)%2 in the model.
            body.append("        // ---- S1/chi alt; rotmix pair: {1,2}(3,11) {3,4}(7,13) {5,6}(3,11) ----")
            body.append("        if (i[0] == 1'b0) begin")
            body.append(sbox_dnf_assigns("u", "R"))
            body.append("            if (((i >> 1) & 1'b1) == 1'b0)")
            body.append(f"                t = {lin_expr('u', 3, 11)};")
            body.append("            else")
            body.append(f"                t = {lin_expr('u', 7, 13)};")
            body.append("        end else begin")
            body.append(chi_assigns("t", "R", (1, 2)))
            body.append("            if (((i >> 1) & 1'b1) == 1'b0)")
            body.append(f"                t = {lin_expr('t', 3, 11)};")
            body.append("            else")
            body.append(f"                t = {lin_expr('t', 7, 13)};")
            body.append("        end")
            body.append(V_RK_STD)
            body.append(V_TAIL_FEISTEL)
        elif kind == "alt_wh":
            body.append("        // ---- odd rounds S1-F, even rounds chi-F, (3,11) ----")
            body.append("        if (i[0] == 1'b0) begin")
            body.append(_s1_block(3, 11))
            body.append("        end else begin")
            body.append(_chi_block(3, 11))
            body.append("        end")
            body.append(V_RK_STD)
            body.append(V_TAIL_FEISTEL)
        elif kind == "parsplit":
            body.append("        // ---- F = lin311(S1(R[15:0]) || chi16(R[31:16])) ^ rk ----")
            body.append(_parsplit_block())
            body.append(V_RK_STD)
            body.append(V_TAIL_FEISTEL)
        elif kind == "alt_rkdiff":
            # 0-based i0: round r=i0+1; j1=r -> bake (i0+2); j2=r+1 -> bake (i0+3)
            body.append("        // ---- rk = RK32(i) ^ rotl32(RK32(i+1),8) ----")
            body.append("        if (i[0] == 1'b0) begin")
            body.append(_s1_block(3, 11))
            body.append("        end else begin")
            body.append(_chi_block(3, 11))
            body.append("        end")
            body.append("        r = (13 * (i + 2)) % 64;")
            body.append("        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 2) * 64'h9E3779B97F4A7C15);")
            body.append("        r = (13 * (i + 3)) % 64;")
            body.append("        W = ((key << r) | (key >> (64 - r))) ^ ((i + 3) * 64'h9E3779B97F4A7C15);")
            body.append("        rk32 = rkv[31:0] ^ {W[23:0], W[31:24]};")
            body.append(V_TAIL_FEISTEL)
        elif kind == "alt_rksbox":
            body.append("        // ---- rk = sbox_layer32(RK32(i)) ----")
            body.append("        if (i[0] == 1'b0) begin")
            body.append(_s1_block(3, 11))
            body.append("        end else begin")
            body.append(_chi_block(3, 11))
            body.append("        end")
            body.append(V_RK_STD)
            body.append(sbox_dnf_assigns("rk32", "rkv"))
            body.append(V_TAIL_FEISTEL)
        elif kind == "alt_chioff023":
            body.append("        // ---- odd rounds S1-F (3,11), even rounds chi(2,3)-F ----")
            body.append("        if (i[0] == 1'b0) begin")
            body.append(_s1_block(3, 11))
            body.append("        end else begin")
            body.append(_chi_block(3, 11, (2, 3)))
            body.append("        end")
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
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round15/models")
from r15 import {name} as _np

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
    # chi offset spot-check: model vs brute-force bit loop (all offsets)
    xv = np.array([0x0123456789ABCDEF, 0xFFFFFFFFFFFFFFFF, 0x0,
                   0x8000000000000001], dtype=np.uint64)
    for (o0, o1), fn in [((1, 2), r15._chi32_np), ((2, 3), r15._chi32_off23_np)]:
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
    # chi16 spot-check vs brute force
    xv16 = [0x0000, 0xFFFF, 0x1234, 0x8001, 0xAAAA]
    for x in xv16:
        want = 0
        for i in range(16):
            a0 = (x >> i) & 1
            a1 = (x >> ((i + 1) % 16)) & 1
            a2 = (x >> ((i + 2) % 16)) & 1
            want |= (a0 ^ ((1 - a1) & a2)) << i
        got = int(r15._chi16_np(np.uint64(x)))
        assert got == want, (hex(x), hex(got), hex(want))
    print("chi16 spot-check: 5 vectors OK")
    # parsplit layout spot-check: _F_parsplit vs manual composition
    rng = np.random.default_rng(4242)
    Rv = rng.integers(0, 2**32, size=8, dtype=np.uint64)
    for rv in Rv:
        rvi = int(rv)
        t = 0
        for j in range(4):
            t |= int(S1[(rvi >> (4 * j)) & 0xF]) << (4 * j)
        hi = (rvi >> 16) & 0xFFFF
        ch = 0
        for i in range(16):
            a0 = (hi >> i) & 1
            a1 = (hi >> ((i + 1) % 16)) & 1
            a2 = (hi >> ((i + 2) % 16)) & 1
            ch |= (a0 ^ ((1 - a1) & a2)) << i
        t |= ch << 16
        # lin(3,11)
        lin = (t ^ ((t << 3) | (t >> 29)) ^ ((t << 11) | (t >> 21))) & 0xFFFFFFFF
        got = int(r15._F_parsplit(np.uint64(rv), np.uint64(0)))
        assert got == lin, (hex(rv), hex(got), hex(lin))
    print("parsplit layout spot-check: 8 vectors OK")
    # key-index derivation spot-check: _rk_v(1..8) vs numpy _rk64_std_np
    for j in range(1, 9):
        shift = (13 * (j + 1)) % 64
        mult = j + 1
        kv = np.uint64(0x123456789ABCDEF0)
        want = int(r15._rk64_std_np(kv, j))
        got = ((int(kv) << shift) | (int(kv) >> (64 - shift))) & 0xFFFFFFFFFFFFFFFF \
            if shift else int(kv)
        got = (got ^ (mult * 0x9E3779B97F4A7C15)) & 0xFFFFFFFFFFFFFFFF
        assert got == want, (j, hex(got), hex(want))
    print("key-index derivation spot-check (j=1..8): OK")
    # dedupe: pairwise-distinct model outputs across the spec set
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    outs = {}
    for name, kind, rounds, params, desc in SPECS:
        fn = getattr(r15, name)
        o = fn(V, K).tobytes()
        assert o not in outs.values(), f"DUPLICATE model output: {name}"
        outs[name] = o
    print(f"dedupe: {len(SPECS)} specs pairwise-distinct OK")
    for name, kind, rounds, params, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, kind, rounds, params, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, kind, rounds, params, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(r15, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
