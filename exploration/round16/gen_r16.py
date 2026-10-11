#!/usr/bin/env python3
"""Round 16 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round16/models/r16.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
affine r7/r8/r9 key schedule.

Families (verdict-scope re-tests per VERDICT_SCOPE.md + parsplit variants):
  F1 [re-test O1, HIGH]: crypto S-boxes in HETEROGENEOUS rounds --
      odd rounds XBOX-F = lin(3,11)(XBOX(R))^rk, even rounds chi-F.
      XBOX in {GIFT, PRESENT, SKINNY-4(corrected)}. r11 tested crypto S-boxes
      only in the homogeneous single-S-box-F slot; here only 3/6 rounds pay
      S-box cost (different economics).
  F2 [re-test O2, MEDIUM]: 3-rotation linear in chi-F rounds -- odd S1-F(3,11),
      even chi-F with lin3 = x^rotl(x,a)^rotl(x,b)^rotl(x,c), (3,7,11) and
      (7,13,19). r12 tested 3-rot lin only with S1-F.
  F3: parsplit variants (r15 parsplit: t[31:16]=chi16(R[31:16]),
      t[15:0]=S1(R[15:0]), F=lin(3,11)(t)^rk):
      rev (S1 high / chi16 low), 713 (lin(7,13)), chioff23 (chi16 offsets
      (2,3)), w24 (S1 on 24 bits + chi8 on high 8 bits), giftsplit (GIFT low /
      chi16 high).
  F4: (S1-F, parsplit-F) alternation -- odd rounds r13 S1-F, even rounds r15
      parsplit-F.
  F5 [re-test O5, LOW]: mid-key on the alt structure -- odd rounds
      F=lin(3,11)(S1(R)^rk), even rounds F=lin(3,11)(chi32(R)^rk). r13 tested
      mid-key only on the r9 (homogeneous) structure.

RTL policy (rounds 8/11/12/13): direct boolean assigns inside ONE always @(*)
block (no Verilog functions; no module-level assign may read an
always-block-driven reg). Round-key indexing: C/Python call RK32(key,i) with
1-based i, and RK32 itself bakes in (i+1) -> rotl64(k,13*(i+1)) ^
(i+1)*GOLDEN; the 0-based Verilog loop therefore uses (i+2) (round-11
off-by-one lesson).

Usage: python3 round16/gen_r16.py   (writes fast_battery/candidates/r16_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R16 = os.path.join(EXP, "round16")
sys.path.insert(0, os.path.join(R16, "models"))
import numpy as np  # noqa: E402
import r16  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]
GIFT = [1, 10, 4, 12, 6, 15, 3, 9, 2, 13, 11, 7, 5, 0, 8, 14]
PRESENT = [12, 5, 6, 11, 9, 0, 10, 13, 3, 14, 15, 8, 4, 7, 1, 2]
SKINNY4 = [12, 6, 9, 0, 1, 10, 2, 11, 3, 8, 5, 13, 4, 14, 7, 15]  # corrected r11

TABLES = {"s1": S1, "gift": GIFT, "present": PRESENT, "sk4": SKINNY4}

# (name, kind, xbox_key, extra, desc)
# kind in {xbhet, altlin3, ps, psrev, ps713, pscoff23, psw24, giftsplit,
#           alts1ps, altmidk}; extra carries lin3 (a,b,c) for altlin3.
SPECS = [
    # F1: crypto S-boxes in heterogeneous rounds [O1 re-test, HIGH]
    ("r16_feist6_gift_het_nw", "xbhet", "gift", None,
     "6r Feistel, odd rounds GIFT-F=lin311(GIFT(R))^rk / even rounds chi-F, NO whitening"),
    ("r16_feist6_present_het_nw", "xbhet", "present", None,
     "6r Feistel, odd rounds PRESENT-F=lin311(PRESENT(R))^rk / even rounds chi-F, NO whitening"),
    ("r16_feist6_sk4_het_nw", "xbhet", "sk4", None,
     "6r Feistel, odd rounds SKINNY4-F=lin311(SKINNY4(R))^rk / even rounds chi-F, NO whitening"),
    # F2: 3-rotation linear in chi-F rounds [O2 re-test, MEDIUM]
    ("r16_feist6_alt_lin3711_nw", "altlin3", "s1", (3, 7, 11),
     "6r Feistel, odd S1-F(3,11) / even chi-F with lin(3,7,11), NO whitening"),
    ("r16_feist6_alt_lin71319_nw", "altlin3", "s1", (7, 13, 19),
     "6r Feistel, odd S1-F(3,11) / even chi-F with lin(7,13,19), NO whitening"),
    # F3: parsplit variants
    ("r16_feist6_parsplit_rev_nw", "psrev", "s1", None,
     "6r Feistel, F=lin311(t)^rk, t[31:16]=S1(R[31:16]), t[15:0]=chi16(R[15:0]), NO whitening"),
    ("r16_feist6_parsplit_713_nw", "ps713", "s1", None,
     "6r Feistel, parsplit F with lin(7,13), NO whitening"),
    ("r16_feist6_parsplit_chioff23_nw", "pscoff23", "s1", None,
     "6r Feistel, parsplit F with chi16 offsets (2,3), NO whitening"),
    ("r16_feist6_parsplit_w24_nw", "psw24", "s1", None,
     "6r Feistel, F=lin311(t)^rk, t[23:0]=S1(R[23:0]), t[31:24]=chi8(R[31:24]), NO whitening"),
    ("r16_feist6_giftsplit_nw", "giftsplit", "gift", None,
     "6r Feistel, F=lin311(t)^rk, t[31:16]=chi16(R[31:16]), t[15:0]=GIFT(R[15:0]), NO whitening"),
    # F4: (S1-F, parsplit-F) alternation
    ("r16_feist6_alt_s1ps_nw", "alts1ps", "s1", None,
     "6r Feistel, odd rounds S1-F(3,11) / even rounds parsplit-F, NO whitening"),
    # F5: mid-key on the alt structure [O5 re-test, LOW]
    ("r16_feist6_alt_midk_nw", "altmidk", "s1", None,
     "6r Feistel, odd F=lin311(S1(R)^rk) / even F=lin311(chi32(R)^rk), NO whitening"),
]


# ---------------- Quine-McCluskey (4 vars), parametrized by S-box ----------------
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


_dnf_cache = {}


def dnf_for_sbox_bit(sbox, bit):
    """DNF cubes for output bit `bit` of 4-bit S-box `sbox` (list of 16)."""
    key = (tuple(sbox), bit)
    if key not in _dnf_cache:
        mt = [v for v in range(16) if (sbox[v] >> bit) & 1]
        if not mt:
            cubes = []
        elif len(mt) == 16:
            cubes = [(0xF, 0)]
        else:
            cubes = _qm_cover(mt, _qm_primes(mt))
        _dnf_cache[key] = cubes
    return _dnf_cache[key]


def _selftest_dnf():
    # Capable of failing: verifies every table's DNF against brute force.
    for tname, sbox in TABLES.items():
        for bit in range(4):
            cubes = dnf_for_sbox_bit(sbox, bit)
            for v in range(16):
                got = 0
                for m, b in cubes:
                    if (v & ~m) == (b & ~m):
                        got = 1
                        break
                want = (sbox[v] >> bit) & 1
                assert got == want, (tname, bit, v, got, want)
    print("DNF self-test: 4 tables x 4 bits x 16 inputs OK")


def _cube_verilog(mask, bits, base, src):
    lits = []
    for k in range(4):
        if (mask >> k) & 1:
            continue
        lits.append(f"{src}[{base + k}]" if (bits >> k) & 1 else f"~{src}[{base + k}]")
    if not lits:
        return "1'b1"
    return "(" + " & ".join(lits) + ")"


def sbox_dnf_assigns(sbox, dst, src, nnib, dst_base=0, src_base=0):
    """nnib*4 assigns: dst[dst_base+..] = sbox(src[src_base+..])."""
    lines = []
    for j in range(nnib):
        b = 4 * j
        for bit in range(4):
            cubes = dnf_for_sbox_bit(sbox, bit)
            expr = (" | ".join(_cube_verilog(m, cb, src_base + b, src)
                    for m, cb in cubes)
                    if cubes else "1'b0")
            lines.append(f"            {dst}[{dst_base + b + bit}] = {expr};")
    return "\n".join(lines)


def chi32_assigns(dst, src):
    """32 assigns: dst = chi32(src), b_i = a_i ^ (~a_{i+1} & a_{i+2})."""
    lines = []
    for i in range(32):
        lines.append(
            f"            {dst}[{i}] = {src}[{i}] ^ "
            f"(~{src}[{(i + 1) % 32}] & {src}[{(i + 2) % 32}]);")
    return "\n".join(lines)


def chiN_assigns(dst, src, n, o1, o2, base=0):
    """n assigns: dst[base+i] = chi(src field at base), offsets (o1,o2)."""
    lines = []
    for i in range(n):
        lines.append(
            f"            {dst}[{base + i}] = {src}[{base + i}] ^ "
            f"(~{src}[{base + (i + o1) % n}] & {src}[{base + (i + o2) % n}]);")
    return "\n".join(lines)


def _rot_expr(reg, n):
    # rotl32(reg,n) = {reg[32-n-1:0], reg[31:32-n]}
    return f"{{{reg}[{32 - n - 1}:0], {reg}[31:{32 - n}]}}"


def lin_expr(reg, a, b):
    return f"{reg} ^ {_rot_expr(reg, a)} ^ {_rot_expr(reg, b)}"


def lin3_expr(reg, a, b, c):
    return f"{reg} ^ {_rot_expr(reg, a)} ^ {_rot_expr(reg, b)} ^ {_rot_expr(reg, c)}"


# ---------------- C ----------------
C_COMMON = """/* {name}: {desc}
 * GENERATED by round16/gen_r16.py -- do not edit by hand.
 * Bit-exact vs Python model round16/models/r16.py ({name}). */
#include <stdint.h>

static const uint8_t S1T[16] = {{0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10}};
static const uint8_t XBT[16] = {{{xbox_init}}};

static uint32_t sbox32(uint32_t x, const uint8_t *T) {{
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)T[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}}
static uint32_t sbox24(uint32_t x, const uint8_t *T) {{
    uint32_t r = 0;
    for (int i = 0; i < 6; i++)
        r |= (uint32_t)T[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}}
static uint32_t sbox16(uint32_t x, const uint8_t *T) {{
    uint32_t r = 0;
    for (int i = 0; i < 4; i++)
        r |= (uint32_t)T[(x >> (4*i)) & 0xF] << (4*i);
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
static uint32_t chi16(uint32_t x, int o1, int o2) {{
    uint32_t r = 0;
    for (int i = 0; i < 16; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + o1) % 16)) & 1u;
        uint32_t a2 = (x >> ((i + o2) % 16)) & 1u;
        r |= (a0 ^ ((~a1) & a2)) << i;
    }}
    return r;
}}
static uint32_t chi8(uint32_t x, int o1, int o2) {{
    uint32_t r = 0;
    for (int i = 0; i < 8; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + o1) % 8)) & 1u;
        uint32_t a2 = (x >> ((i + o2) % 8)) & 1u;
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
static uint32_t lin3(uint32_t x, int a, int b, int c) {{
    return x ^ rotl32(x, a) ^ rotl32(x, b) ^ rotl32(x, c);
}}

static uint32_t F_s1_311(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, S1T), 3, 11) ^ rk;
}}
static uint32_t F_xb_311(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, XBT), 3, 11) ^ rk;
}}
static uint32_t F_chi_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32(R), 3, 11) ^ rk;
}}
static uint32_t F_chi_lin3(uint32_t R, uint32_t rk, int a, int b, int c) {{
    return lin3(chi32(R), a, b, c) ^ rk;
}}
static uint32_t F_ps(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 1, 2) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_psrev(uint32_t R, uint32_t rk) {{
    uint32_t t = (sbox16(R >> 16, S1T) << 16) | chi16(R & 0xFFFFu, 1, 2);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps713(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 1, 2) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 7, 13) ^ rk;
}}
static uint32_t F_pscoff23(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 2, 3) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_psw24(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi8(R >> 24, 1, 2) << 24) | sbox24(R & 0xFFFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_giftsplit(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 1, 2) << 16) | sbox16(R & 0xFFFFu, XBT);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_midk_s1(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, S1T) ^ rk, 3, 11);
}}
static uint32_t F_midk_chi(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32(R) ^ rk, 3, 11);
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

C_F_LINE = {
    "xbhet": ("        uint32_t F = (i & 1) ? F_xb_311(R, RK32(key, i))\n"
              "                           : F_chi_311(R, RK32(key, i));"),
    "altlin3": ("        uint32_t F = (i & 1) ? F_s1_311(R, RK32(key, i))\n"
                "                           : F_chi_lin3(R, RK32(key, i), {a2}, {b2}, {c2});"),
    "ps": "        uint32_t F = F_ps(R, RK32(key, i));",
    "psrev": "        uint32_t F = F_psrev(R, RK32(key, i));",
    "ps713": "        uint32_t F = F_ps713(R, RK32(key, i));",
    "pscoff23": "        uint32_t F = F_pscoff23(R, RK32(key, i));",
    "psw24": "        uint32_t F = F_psw24(R, RK32(key, i));",
    "giftsplit": "        uint32_t F = F_giftsplit(R, RK32(key, i));",
    "alts1ps": ("        uint32_t F = (i & 1) ? F_s1_311(R, RK32(key, i))\n"
                "                           : F_ps(R, RK32(key, i));"),
    "altmidk": ("        uint32_t F = (i & 1) ? F_midk_s1(R, RK32(key, i))\n"
                "                           : F_midk_chi(R, RK32(key, i));"),
}


def gen_impl(name, kind, xbox, extra, desc):
    xbox_init = ",".join(str(v) for v in TABLES[xbox])
    body = C_COMMON.format(name=name, desc=desc, xbox_init=xbox_init)
    f_line = C_F_LINE[kind]
    if kind == "altlin3":
        a2, b2, c2 = extra
        f_line = f_line.format(a2=a2, b2=b2, c2=c2)
    body += C_MAIN_FEISTEL.format(rounds=6, f_line=f_line)
    return body


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round16/gen_r16.py -- do not edit by hand.
// Bit-exact vs Python model round16/models/r16.py ({name}).
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


def _ps_block():
    # parsplit: t[31:16] = chi16(R[31:16]), t[15:0] = S1(R[15:0])
    return (chiN_assigns("t", "R", 16, 1, 2, base=16) + "\n"
            + sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0) + "\n"
            f"            t = {lin_expr('t', 3, 11)};\n")


def gen_rtl(name, kind, xbox, extra, desc):
    sbox = TABLES[xbox]
    body = []
    body.append("always @(*) begin")
    body.append("    L = val[63:32];")
    body.append("    R = val[31:0];")
    body.append("    for (i = 0; i < 6; i = i + 1) begin")

    if kind == "xbhet":
        # 0-based even i <-> 1-based odd round -> XBOX-F (matches C (i&1))
        body.append("        // ---- odd rounds XBOX-F, even rounds chi-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(sbox, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32_assigns("t", "R"))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "altlin3":
        a2, b2, c2 = extra
        body.append("        // ---- odd rounds S1-F(3,11), even rounds chi-F lin3 ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32_assigns("t", "R"))
        body.append(f"            t = {lin3_expr('t', a2, b2, c2)};")
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "ps":
        body.append("        // ---- parsplit: t[31:16]=chi16(R[31:16]), t[15:0]=S1(R[15:0]) ----")
        body.append(_ps_block())
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "psrev":
        body.append("        // ---- parsplit-rev: t[31:16]=S1(R[31:16]), t[15:0]=chi16(R[15:0]) ----")
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=16, src_base=16))
        body.append(chiN_assigns("t", "R", 16, 1, 2, base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "ps713":
        body.append("        // ---- parsplit with lin(7,13) ----")
        body.append(chiN_assigns("t", "R", 16, 1, 2, base=16))
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 7, 13)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "pscoff23":
        body.append("        // ---- parsplit with chi16 offsets (2,3) ----")
        body.append(chiN_assigns("t", "R", 16, 2, 3, base=16))
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "psw24":
        body.append("        // ---- parsplit-w24: t[23:0]=S1(R[23:0]), t[31:24]=chi8(R[31:24]) ----")
        body.append(chiN_assigns("t", "R", 8, 1, 2, base=24))
        body.append(sbox_dnf_assigns(S1, "t", "R", 6, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "giftsplit":
        body.append("        // ---- giftsplit: t[31:16]=chi16(R[31:16]), t[15:0]=GIFT(R[15:0]) ----")
        body.append(chiN_assigns("t", "R", 16, 1, 2, base=16))
        body.append(sbox_dnf_assigns(sbox, "t", "R", 4, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alts1ps":
        body.append("        // ---- odd rounds S1-F, even rounds parsplit-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(_ps_block())
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "altmidk":
        # mid-key: rk needed BEFORE the nonlinear layer
        body.append("        // ---- odd F=lin(S1(R)^rk), even F=lin(chi32(R)^rk) ----")
        body.append(V_RK_STD)
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append("            u = u ^ rk32;")
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32_assigns("t", "R"))
        body.append("            t = t ^ rk32;")
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end")
        body.append(V_TAIL_FEISTEL_NOKEY)
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
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round16/models")
from r16 import {name} as _np

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


def _selftest_chi():
    # Independent brute-force bit loops vs the numpy chi16/chi8 (capable of
    # failing: would fail on an offset or masking bug).
    rng = np.random.default_rng(777)
    for (n, o1, o2) in ((16, 1, 2), (16, 2, 3), (8, 1, 2)):
        for _ in range(200):
            xv = int(rng.integers(0, 2 ** n))
            want = 0
            for i in range(n):
                a0 = (xv >> i) & 1
                a1 = (xv >> ((i + o1) % n)) & 1
                a2 = (xv >> ((i + o2) % n)) & 1
                want |= (a0 ^ ((1 - a1) & a2)) << i
            got = int(r16._chi16_np(np.uint64(xv), o1, o2)) if n == 16 else \
                int(r16._chi8_np(np.uint64(xv), o1, o2))
            assert got == want, (n, o1, o2, hex(xv), hex(got), hex(want))
    print("chi16/chi8 spot-check: 3 offset-pairs x 200 vectors OK")


def _selftest_lin3():
    # Independent pure-Python shift-or vs numpy lin3 (capable of failing).
    rng = np.random.default_rng(4242)
    for (a, b, c) in ((3, 7, 11), (7, 13, 19)):
        for _ in range(200):
            xv = int(rng.integers(0, 2 ** 32))
            want = xv
            for r in (a, b, c):
                want ^= ((xv << r) | (xv >> (32 - r))) & 0xFFFFFFFF
            want &= 0xFFFFFFFF
            got = int(r16._lin3_np(np.uint64(xv), a, b, c))
            assert got == want, (a, b, c, hex(xv), hex(got), hex(want))
    print("lin3 spot-check: 2 triples x 200 vectors OK")


def emit():
    _selftest_dnf()
    _selftest_chi()
    _selftest_lin3()
    # dedupe: pairwise-distinct model outputs across the spec set
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    seen = {}
    for name, kind, xbox, extra, desc in SPECS:
        fn = getattr(r16, name)
        o = fn(V, K).tobytes()
        assert o not in seen.values(), f"DUPLICATE model output: {name}"
        seen[name] = o
    print(f"dedupe: {len(SPECS)} specs pairwise-distinct OK")
    for name, kind, xbox, extra, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, kind, xbox, extra, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, kind, xbox, extra, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(r16, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
