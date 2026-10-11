#!/usr/bin/env python3
"""Round 17 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round17/models/r17.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
affine r7/r8/r9 key schedule.

Families (per coordinator brief):
  1. 5r parsplit-F (highest value): F = lin(3,11)(S1(R[15:0]) ||
     chi16(R[31:16])) ^ rk, 5 rounds.
  2. 5r alt (S1,chi): rounds 1,3,5 S1-F; rounds 2,4 chi-F.
  3. 5r alt chi-first: rounds 1,3,5 chi-F; rounds 2,4 S1-F.
  4. [re-test O4] 6r parallel S1+chi: F = lin(3,11)(S1(R^rk)) ^
     lin(3,11)(chi32(R)).
  5. [re-test O3] 6r alt, odd (S1) rounds apply S1 to low 16 bits only
     (high 16 pass through unmodified); even chi rounds unchanged.
  6. double-S1 split: 6r parsplit geometry, S1 on R[15:0] and S1rev on
     R[31:16] (S1rev = S1 composed with nibble bit-reversal).
  7. parsplit with chi16 offsets (0,1), 6r.
  8. pre-mix F: F = lin(3,11)(S1(R ^ rotl32(R,16))) ^ rk, 6r.
  9. 4r parsplit-F (S1-gated probe).
 10. 5r parsplit-F with lin(7,13).

RTL policy (rounds 8/11/12/13): direct boolean assigns inside ONE always @(*)
block (no Verilog functions; no module-level assign may read an
always-block-driven reg). Round-key indexing: C/Python call RK32(key,i) with
1-based i, and RK32 itself bakes in (i+1) -> rotl64(k,13*(i+1)) ^
(i+1)*GOLDEN; the 0-based Verilog loop therefore uses (i+2) (round-11
off-by-one lesson).

Usage: python3 round17/gen_r17.py   (writes fast_battery/candidates/r17_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R17 = os.path.join(EXP, "round17")
sys.path.insert(0, os.path.join(R17, "models"))
import numpy as np  # noqa: E402
import r17  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]
TABLES = {"s1": S1}

# (name, kind, rounds, desc)
# kinds: ps, ps713, pscoff01, alt5_s1first, alt5_chifirst, parmix,
#        altpshalf, dbs1split, premix
SPECS = [
    ("r17_feist5_parsplit_nw", "ps", 5,
     "5r Feistel, F=lin311(t)^rk, t[31:16]=chi16(R[31:16]), t[15:0]=S1(R[15:0]), NO whitening"),
    ("r17_feist5_alt_s1chi_nw", "alt5_s1first", 5,
     "5r Feistel, rounds 1,3,5 S1-F=lin311(S1(R))^rk / rounds 2,4 chi-F=lin311(chi32(R))^rk, NO whitening"),
    ("r17_feist5_alt_chifirst_nw", "alt5_chifirst", 5,
     "5r Feistel, rounds 1,3,5 chi-F / rounds 2,4 S1-F, NO whitening"),
    ("r17_feist6_parmix_nw", "parmix", 6,
     "6r Feistel, F=lin311(S1(R^rk))^lin311(chi32(R)), NO whitening"),
    ("r17_feist6_alt_pshalf_nw", "altpshalf", 6,
     "6r Feistel, odd rounds F=lin311(t)^rk with t=(R[31:16]<<16)|S1(R[15:0]) / even rounds chi-F, NO whitening"),
    ("r17_feist6_dbs1split_nw", "dbs1split", 6,
     "6r Feistel, F=lin311(t)^rk, t[15:0]=S1(R[15:0]), t[31:16]=S1rev(R[31:16]) (nibble bit-reversed S1), NO whitening"),
    ("r17_feist6_parsplit_chioff01_nw", "pscoff01", 6,
     "6r Feistel, parsplit F with chi16 offsets (0,1), NO whitening"),
    ("r17_feist6_premix_nw", "premix", 6,
     "6r Feistel, F=lin311(S1(R^rotl32(R,16)))^rk, NO whitening"),
    ("r17_feist4_parsplit_nw", "ps", 4,
     "4r Feistel, F=lin311(t)^rk, t[31:16]=chi16(R[31:16]), t[15:0]=S1(R[15:0]), NO whitening (S1-gated probe)"),
    ("r17_feist5_parsplit_713_nw", "ps713", 5,
     "5r Feistel, parsplit F with lin(7,13), NO whitening"),
]


# ---------------- Quine-McCluskey (4 vars) ----------------
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
    # Capable of failing: verifies S1's DNF against brute force.
    for bit in range(4):
        cubes = dnf_for_sbox_bit(S1, bit)
        for v in range(16):
            got = 0
            for m, b in cubes:
                if (v & ~m) == (b & ~m):
                    got = 1
                    break
            want = (S1[v] >> bit) & 1
            assert got == want, ("s1", bit, v, got, want)
    print("DNF self-test: S1 x 4 bits x 16 inputs OK")


def _selftest_s1rev():
    # Capable of failing: numpy S1REV table vs brute-force bit-reversal + S1.
    for v in range(16):
        rev = ((v & 1) << 3) | ((v & 2) << 1) | ((v & 4) >> 1) | ((v & 8) >> 3)
        want = S1[rev]
        got = int(r17.S1REV[v])
        assert got == want, (v, got, want)
    print("S1REV self-test: 16 values vs brute-force bit-reversal OK")


def _selftest_chioff01():
    # Capable of failing: numpy chi16(0,1) vs independent bit loop.
    rng = np.random.default_rng(31337)
    for _ in range(200):
        xv = int(rng.integers(0, 2 ** 16))
        want = 0
        for i in range(16):
            a0 = (xv >> i) & 1
            a1 = (xv >> ((i + 0) % 16)) & 1
            a2 = (xv >> ((i + 1) % 16)) & 1
            want |= (a0 ^ ((1 - a1) & a2)) << i
        got = int(r17._chi16_np(np.uint64(xv), 0, 1))
        assert got == want, (hex(xv), hex(got), hex(want))
    print("chi16(0,1) spot-check: 200 vectors OK")


def _cube_verilog(mask, bits, base, src, rev):
    lits = []
    for k in range(4):
        if (mask >> k) & 1:
            continue
        # input bit k lives at src[base+k]; with rev it is src[base+(3-k)]
        pos = base + (3 - k) if rev else base + k
        lits.append(f"{src}[{pos}]" if (bits >> k) & 1 else f"~{src}[{pos}]")
    if not lits:
        return "1'b1"
    return "(" + " & ".join(lits) + ")"


def sbox_dnf_assigns(sbox, dst, src, nnib, dst_base=0, src_base=0, rev=False):
    """nnib*4 assigns: dst[dst_base+..] = sbox(src[src_base+..]).
    rev=True: each nibble's input bits are bit-reversed (S1rev)."""
    lines = []
    for j in range(nnib):
        b = 4 * j
        for bit in range(4):
            cubes = dnf_for_sbox_bit(sbox, bit)
            expr = (" | ".join(_cube_verilog(m, cb, src_base + b, src, rev)
                    for m, cb in cubes)
                    if cubes else "1'b0")
            lines.append(f"            {dst}[{dst_base + b + bit}] = {expr};")
    return "\n".join(lines)


def chi32_assigns(dst, src):
    lines = []
    for i in range(32):
        lines.append(
            f"            {dst}[{i}] = {src}[{i}] ^ "
            f"(~{src}[{(i + 1) % 32}] & {src}[{(i + 2) % 32}]);")
    return "\n".join(lines)


def chiN_assigns(dst, src, n, o1, o2, base=0):
    lines = []
    for i in range(n):
        lines.append(
            f"            {dst}[{base + i}] = {src}[{base + i}] ^ "
            f"(~{src}[{base + (i + o1) % n}] & {src}[{base + (i + o2) % n}]);")
    return "\n".join(lines)


def _rot_expr(reg, n):
    return f"{{{reg}[{32 - n - 1}:0], {reg}[31:{32 - n}]}}"


def lin_expr(reg, a, b):
    return f"{reg} ^ {_rot_expr(reg, a)} ^ {_rot_expr(reg, b)}"


# ---------------- C ----------------
C_COMMON = """/* {name}: {desc}
 * GENERATED by round17/gen_r17.py -- do not edit by hand.
 * Bit-exact vs Python model round17/models/r17.py ({name}). */
#include <stdint.h>

static const uint8_t S1T[16] = {{0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10}};

static uint32_t sbox32(uint32_t x, const uint8_t *T) {{
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)T[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}}
static uint32_t sbox16(uint32_t x, const uint8_t *T) {{
    uint32_t r = 0;
    for (int i = 0; i < 4; i++)
        r |= (uint32_t)T[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}}
static uint32_t rev4(uint32_t v) {{
    return ((v & 1u) << 3) | ((v & 2u) << 1) | ((v & 4u) >> 1) | ((v & 8u) >> 3);
}}
static uint32_t sbox16rev(uint32_t x, const uint8_t *T) {{
    /* S1rev: nibble input bits bit-reversed before the S-box */
    uint32_t r = 0;
    for (int i = 0; i < 4; i++)
        r |= (uint32_t)T[rev4((x >> (4*i)) & 0xF)] << (4*i);
    return r;
}}

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

static uint32_t F_s1_311(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, S1T), 3, 11) ^ rk;
}}
static uint32_t F_chi_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32(R), 3, 11) ^ rk;
}}
static uint32_t F_ps(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 1, 2) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps713(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 1, 2) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 7, 13) ^ rk;
}}
static uint32_t F_pscoff01(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 0, 1) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_pshalf(uint32_t R, uint32_t rk) {{
    uint32_t t = (R & 0xFFFF0000u) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_parmix(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R ^ rk, S1T), 3, 11) ^ lin_ab(chi32(R), 3, 11);
}}
static uint32_t F_dbs1split(uint32_t R, uint32_t rk) {{
    uint32_t t = (sbox16rev(R >> 16, S1T) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_premix(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R ^ rotl32(R, 16), S1T), 3, 11) ^ rk;
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
    "ps": "        uint32_t F = F_ps(R, RK32(key, i));",
    "ps713": "        uint32_t F = F_ps713(R, RK32(key, i));",
    "pscoff01": "        uint32_t F = F_pscoff01(R, RK32(key, i));",
    "alt5_s1first": ("        uint32_t F = (i & 1) ? F_s1_311(R, RK32(key, i))\n"
                     "                           : F_chi_311(R, RK32(key, i));"),
    "alt5_chifirst": ("        uint32_t F = (i & 1) ? F_chi_311(R, RK32(key, i))\n"
                      "                           : F_s1_311(R, RK32(key, i));"),
    "parmix": "        uint32_t F = F_parmix(R, RK32(key, i));",
    "altpshalf": ("        uint32_t F = (i & 1) ? F_pshalf(R, RK32(key, i))\n"
                  "                           : F_chi_311(R, RK32(key, i));"),
    "dbs1split": "        uint32_t F = F_dbs1split(R, RK32(key, i));",
    "premix": "        uint32_t F = F_premix(R, RK32(key, i));",
}


def gen_impl(name, kind, rounds, desc):
    body = C_COMMON.format(name=name, desc=desc)
    f_line = C_F_LINE[kind]
    body += C_MAIN_FEISTEL.format(rounds=rounds, f_line=f_line)
    return body


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round17/gen_r17.py -- do not edit by hand.
// Bit-exact vs Python model round17/models/r17.py ({name}).
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


def gen_rtl(name, kind, rounds, desc):
    body = []
    body.append("always @(*) begin")
    body.append("    L = val[63:32];")
    body.append("    R = val[31:0];")
    body.append(f"    for (i = 0; i < {rounds}; i = i + 1) begin")

    if kind == "ps":
        body.append("        // ---- parsplit: t[31:16]=chi16(R[31:16]), t[15:0]=S1(R[15:0]) ----")
        body.append(_ps_block())
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "ps713":
        body.append("        // ---- parsplit with lin(7,13) ----")
        body.append(chiN_assigns("t", "R", 16, 1, 2, base=16))
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 7, 13)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "pscoff01":
        body.append("        // ---- parsplit with chi16 offsets (0,1) ----")
        body.append(chiN_assigns("t", "R", 16, 0, 1, base=16))
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt5_s1first":
        # 0-based even i <-> 1-based odd round -> S1-F (matches C (i&1))
        body.append("        // ---- odd rounds S1-F, even rounds chi-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32_assigns("t", "R"))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt5_chifirst":
        body.append("        // ---- odd rounds chi-F, even rounds S1-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(chi32_assigns("t", "R"))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end else begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "parmix":
        # F = lin(S1(R^rk)) ^ lin(chi32(R)): rk XORed into R BEFORE the S-box
        body.append("        // ---- parmix: t = lin(S1(R^rk)) ^ lin(chi32(R)) ----")
        body.append(V_RK_STD)
        body.append("            D = R ^ rk32;")
        body.append(sbox_dnf_assigns(S1, "u", "D", 8))
        body.append("            D = " + lin_expr("u", 3, 11) + ";")
        body.append(chi32_assigns("t", "R"))
        body.append("            t = " + lin_expr("t", 3, 11) + ";")
        body.append("            t = D ^ t;")
        body.append(V_TAIL_FEISTEL_NOKEY)
    elif kind == "altpshalf":
        body.append("        // ---- odd rounds pshalf-F, even rounds chi-F ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append("            t = (R & 32'hFFFF0000) | {16'b0, R[15:0]};")
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32_assigns("t", "R"))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "dbs1split":
        body.append("        // ---- dbs1split: t[15:0]=S1(R[15:0]), t[31:16]=S1rev(R[31:16]) ----")
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0))
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=16, src_base=16,
                                    rev=True))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "premix":
        body.append("        // ---- premix: t = lin(S1(R ^ rotl32(R,16))) ----")
        body.append("            D = R ^ {R[15:0], R[31:16]};")
        body.append(sbox_dnf_assigns(S1, "u", "D", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
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
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round17/models")
from r17 import {name} as _np

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
    _selftest_s1rev()
    _selftest_chioff01()
    # dedupe: pairwise-distinct model outputs across the spec set
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    seen = {}
    for name, kind, rounds, desc in SPECS:
        fn = getattr(r17, name)
        o = fn(V, K).tobytes()
        assert o not in seen.values(), f"DUPLICATE model output: {name}"
        seen[name] = o
    print(f"dedupe: {len(SPECS)} specs pairwise-distinct OK")
    for name, kind, rounds, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, kind, rounds, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, kind, rounds, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(r17, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
