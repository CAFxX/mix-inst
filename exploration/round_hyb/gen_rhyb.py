#!/usr/bin/env python3
"""Hybridization-round candidate generator: emits impl.c, rtl.v, model.py,
meta.json for each spec in SPECS. The numpy model (round_hyb/models/rhyb.py)
is the reference; bit-exactness of the generated C/RTL is verified by xcheck
+ check_rtl.

Round tags:
  s1_311, chi_311, chi_notr, chi32v_311, chi32w_311 -- exact r20 emitters
  chi_fm11  -- exact r19 emitter (y=chi32(R)^rk; F=y^rotl32(y,11))
  ps_311, ps_notr, ps_chi16v_311, ps_chi16w_311, ps_keyin_311, ps_3rot -- NEW
     ps t = (chi16off(R>>16)<<16) | S1_16(R&0xFFFF)   [r15 parsplit geometry]
     ps_keyin: chi16((R>>16) ^ (rk>>16))
     ps_3rot: lin3(t) = t^rotl(t,3)^rotl(t,7)^rotl(t,11)  [r16's lin3]

Structural note: all are plain balanced Feistel with an arbitrary F —
bijective in val for fixed key regardless of F. No novel topology.

RTL policy: direct boolean assigns inside ONE always @(*) block (no Verilog
functions; no module-level assign may read an always-block-driven reg).
Round-key indexing: C/Python call RK32(key,i) with 1-based i, and RK32 bakes
in (i+1); the 0-based Verilog loop therefore uses (i+2) (round-11 lesson).

Usage: python3 round_hyb/gen_rhyb.py   (writes fast_battery/candidates/rh_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
RH = os.path.join(EXP, "round_hyb")
sys.path.insert(0, os.path.join(RH, "models"))
import numpy as np  # noqa: E402
import rhyb  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

SPECS = rhyb.SPECS

C_F_EXPR = {
    "s1_311": "F_s1_311(R, RK32(key, i))",
    "chi_311": "F_chi_311(R, RK32(key, i))",
    "chi_notr": "F_chi_notr(R, RK32(key, i))",
    "chi32v_311": "F_chi32v_311(R, RK32(key, i))",
    "chi32w_311": "F_chi32w_311(R, RK32(key, i))",
    "chi_fm11": "F_chi_fm11(R, RK32(key, i))",
    "ps_311": "F_ps_311(R, RK32(key, i))",
    "ps_notr": "F_ps_notr(R, RK32(key, i))",
    "ps_chi16v_311": "F_ps_chi16v_311(R, RK32(key, i))",
    "ps_chi16w_311": "F_ps_chi16w_311(R, RK32(key, i))",
    "ps_keyin_311": "F_ps_keyin_311(R, RK32(key, i))",
    "ps_3rot": "F_ps_3rot(R, RK32(key, i))",
}


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


def _cube_verilog(mask, bits, base, src):
    lits = []
    for k in range(4):
        if (mask >> k) & 1:
            continue
        pos = base + k
        lits.append(f"{src}[{pos}]" if (bits >> k) & 1 else f"~{src}[{pos}]")
    if not lits:
        return "1'b1"
    return "(" + " & ".join(lits) + ")"


def sbox_dnf_assigns(sbox, dst, src, nnib, dst_base=0, src_base=0):
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
    lines = []
    for i in range(32):
        lines.append(
            f"            {dst}[{i}] = {src}[{i}] ^ "
            f"(~{src}[{(i + 1) % 32}] & {src}[{(i + 2) % 32}]);")
    return "\n".join(lines)


def chi32v_assigns(dst, src):
    lines = []
    for i in range(32):
        lines.append(
            f"            {dst}[{i}] = {src}[{i}] ^ "
            f"(~{src}[{(i + 1) % 32}] & {src}[{(i + 3) % 32}]);")
    return "\n".join(lines)


def chi32w_assigns(dst, src):
    # chi variant: b_i = a_i ^ (~a_{i+3} & a_{i+1})
    lines = []
    for i in range(32):
        lines.append(
            f"            {dst}[{i}] = {src}[{i}] ^ "
            f"(~{src}[{(i + 3) % 32}] & {src}[{(i + 1) % 32}]);")
    return "\n".join(lines)


def chi16_assigns(dst, src, off=(1, 2), base_dst=16, base_src=16):
    """16 assigns: dst[base_dst+i] = chi16(src[base_src+i]),
    b_i = a_i ^ (~a_{(i+o0)%16} & a_{(i+o1)%16})."""
    o0, o1 = off
    lines = []
    for i in range(16):
        lines.append(
            f"            {dst}[{base_dst + i}] = {src}[{base_src + i}] ^ "
            f"(~{src}[{base_src + (i + o0) % 16}] & "
            f"{src}[{base_src + (i + o1) % 16}]);")
    return "\n".join(lines)


def _selftest_chi16_rtl():
    # Capable of failing: chi16 RTL assigns vs independent bit loops.
    rng = np.random.default_rng(987654)
    for _ in range(100):
        xv = int(rng.integers(0, 2 ** 16))
        for off, fn in (((1, 2), rhyb._chi16_np),
                        ((1, 3), rhyb._chi16_np),
                        ((3, 1), rhyb._chi16_np)):
            got = int(fn(np.uint64(xv), *off))
            want = rhyb._chi16_scalar(xv, *off)
            assert got == want, ("chi16", off, hex(xv))
    print("chi16 RTL-pattern self-test: 3 offsets x 100 vectors OK")


def _rotl_expr(reg, n):
    return f"{{{reg}[{32 - n - 1}:0], {reg}[31:{32 - n}]}}"


def lin_expr(reg, a, b):
    return f"{reg} ^ {_rotl_expr(reg, a)} ^ {_rotl_expr(reg, b)}"


def lin3_expr(reg, a, b, c):
    return (f"{reg} ^ {_rotl_expr(reg, a)} ^ {_rotl_expr(reg, b)} ^ "
            f"{_rotl_expr(reg, c)}")


# ---------------- C ----------------
C_COMMON = """/* {name}: {desc}
 * GENERATED by round_hyb/gen_rhyb.py -- do not edit by hand.
 * Bit-exact vs Python model round_hyb/models/rhyb.py ({name}). */
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
static uint32_t chi32v(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + 1) % 32)) & 1u;
        uint32_t a2 = (x >> ((i + 3) % 32)) & 1u;
        r |= (a0 ^ ((~a1) & a2)) << i;
    }}
    return r;
}}
static uint32_t chi32w(uint32_t x) {{
    /* swapped offsets: b_i = a_i ^ (~a_(i+3) & a_(i+1)) */
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a3 = (x >> ((i + 3) % 32)) & 1u;
        uint32_t a1 = (x >> ((i + 1) % 32)) & 1u;
        r |= (a0 ^ ((~a3) & a1)) << i;
    }}
    return r;
}}
static uint32_t chi16o(uint32_t x, int o0, int o1) {{
    /* 16-bit chi: b_i = a_i ^ (~a_(i+o0) & a_(i+o1)), i mod 16 */
    uint32_t r = 0;
    for (int i = 0; i < 16; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + o0) % 16)) & 1u;
        uint32_t a2 = (x >> ((i + o1) % 16)) & 1u;
        r |= (a0 ^ ((~a1) & a2)) << i;
    }}
    return r;
}}
static uint32_t chi16(uint32_t x) {{ return chi16o(x, 1, 2); }}
static uint32_t chi16v(uint32_t x) {{ return chi16o(x, 1, 3); }}
static uint32_t chi16w(uint32_t x) {{ return chi16o(x, 3, 1); }}

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
static uint32_t F_chi_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32(R), 3, 11) ^ rk;
}}
static uint32_t F_chi32v_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32v(R), 3, 11) ^ rk;
}}
static uint32_t F_chi32w_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32w(R), 3, 11) ^ rk;
}}
static uint32_t F_chi_notr(uint32_t R, uint32_t rk) {{
    return chi32(R) ^ rk;
}}
static uint32_t F_chi_fm11(uint32_t R, uint32_t rk) {{
    uint32_t y = chi32(R) ^ rk;
    return y ^ rotl32(y, 11);
}}
static uint32_t F_ps_311(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps_notr(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16) << 16) | sbox16(R & 0xFFFFu, S1T);
    return t ^ rk;
}}
static uint32_t F_ps_chi16v_311(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16v(R >> 16) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps_chi16w_311(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16w(R >> 16) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps_keyin_311(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16((R >> 16) ^ (rk >> 16)) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps_3rot(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin3(t, 3, 7, 11) ^ rk;
}}

"""

C_MAIN_TMPL = """uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= 6; i++) {{
        uint32_t F;
{f_body}
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }}
    return ((uint64_t)R << 32) | L;
}}
"""


def gen_impl(name, tags, desc):
    body = C_COMMON.format(name=name, desc=desc)
    f_lines = []
    for i, tag in enumerate(tags, start=1):
        kw = "if" if i == 1 else "else if"
        f_lines.append(f"        {kw} (i == {i}) F = {C_F_EXPR[tag]};")
    body += C_MAIN_TMPL.format(f_body="\n".join(f_lines))
    return body


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round_hyb/gen_rhyb.py -- do not edit by hand.
// Bit-exact vs Python model round_hyb/models/rhyb.py ({name}).
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
integer i, r;
"""

# Standard round-key block. NOTE: loop i is 0-based; C/Python call RK32(key,i)
# with 1-based i, and RK32 itself bakes in (i+1). Round r = i+1 (1-based)
# therefore needs 13*((i+1)+1) = 13*(i+2) and ((i+2)*GOLDEN) here.
# (round-11 off-by-one lesson.)
V_RK_STD = """\
        r = (13 * (i + 2)) % 64;
        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 2) * 64'h9E3779B97F4A7C15);
        rk32 = rkv[31:0];"""


def _ps_block(off=(1, 2), src="R"):
    # parsplit t: t[31:16] = chi16off(src[31:16]), t[15:0] = S1(src[15:0]).
    return (chi16_assigns("t", src, off, 16, 16) + "\n"
            + sbox_dnf_assigns(S1, "t", src, 4, dst_base=0, src_base=0) + "\n")


def _ps_keyin_block():
    # key inside chi16 half: u[15:0] = R[31:16] ^ rk32[31:16] (zero-extended);
    # t[31:16] = chi16(u[15:0]) (base_src=0), t[15:0] = S1(R[15:0]).
    return ("            u = R[31:16] ^ rk32[31:16];\n"
            + chi16_assigns("t", "u", (1, 2), 16, 0) + "\n"
            + sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0) + "\n")


def gen_round_assigns(tag):
    """Verilog assigns computing F into t (tail XORs rk32 via the tail rule),
    except tags that bake rk into t themselves (chi_fm11: y^rotl(y,11))."""
    if tag == "s1_311":
        return (sbox_dnf_assigns(S1, "u", "R", 8) + "\n"
                f"            t = {lin_expr('u', 3, 11)};")
    if tag == "chi_311":
        return (chi32_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 3, 11)};")
    if tag == "chi32v_311":
        return (chi32v_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 3, 11)};")
    if tag == "chi32w_311":
        return (chi32w_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 3, 11)};")
    if tag == "chi_notr":
        return chi32_assigns("t", "R")
    if tag == "chi_fm11":
        # t = (u ^ rk32) ^ rotl((u ^ rk32), 11); u = chi32(R)
        return (chi32_assigns("u", "R") + "\n"
                "            t = u ^ rk32;\n"
                f"            t = t ^ {_rotl_expr('t', 11)};")
    if tag == "ps_311":
        return (_ps_block((1, 2))
                + f"            t = {lin_expr('t', 3, 11)};\n")
    if tag == "ps_notr":
        return _ps_block((1, 2))
    if tag == "ps_chi16v_311":
        return (_ps_block((1, 3))
                + f"            t = {lin_expr('t', 3, 11)};\n")
    if tag == "ps_chi16w_311":
        return (_ps_block((3, 1))
                + f"            t = {lin_expr('t', 3, 11)};\n")
    if tag == "ps_keyin_311":
        return (_ps_keyin_block()
                + f"            t = {lin_expr('t', 3, 11)};\n")
    if tag == "ps_3rot":
        return (_ps_block((1, 2))
                + f"            t = {lin3_expr('t', 3, 7, 11)};\n")
    raise ValueError(tag)


def gen_rtl(name, tags, desc):
    # chi_fm* tags bake rk32 into t (y = chi^rk before the extra rotation).
    # V_RK_STD runs BEFORE the round if-chain, and the tail skips ^rk32 on
    # those rounds (r20 keyin-class lesson: any tag whose t already
    # incorporates rk needs the tail skip).
    body = []
    body.append("always @(*) begin")
    body.append("    L = val[63:32];")
    body.append("    R = val[31:0];")
    body.append("    for (i = 0; i < 6; i = i + 1) begin")
    body.append("        " + V_RK_STD.replace("\n", "\n        "))
    for ri, tag in enumerate(tags):
        kw = "if" if ri == 0 else "else if"
        body.append(f"        {kw} (i == {ri}) begin")
        for line in gen_round_assigns(tag).split("\n"):
            body.append(line)
        body.append("        end")
    body.append("        Lt = R;")
    fm_rounds = [ri for ri, tag in enumerate(tags)
                 if tag.startswith("chi_fm")]
    if fm_rounds:
        cond = " || ".join(f"i == {ri}" for ri in fm_rounds)
        body.append(f"        if ({cond}) Rt = L ^ t;")
        body.append("        else Rt = L ^ t ^ rk32;")
    else:
        body.append("        Rt = L ^ t ^ rk32;")
    body.append("        L = Lt;")
    body.append("        R = Rt;")
    body.append("    end")
    body.append("end")
    body.append("")
    body.append("assign out = {R, L};")
    body.append("")
    body.append("endmodule")
    return V_HDR.format(name=name, desc=desc) + V_DECL + "\n".join(body) + "\n"


# ---------------- wide kinds ----------------
# C helpers shared by the wide constructions (appended after C_COMMON).
C_WIDE_HELPERS = """
static uint64_t sbox64(uint64_t x, const uint8_t *T) {
    uint64_t r = 0;
    for (int i = 0; i < 16; i++)
        r |= (uint64_t)T[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}
static uint64_t RK64new(uint64_t k, int i) {
    /* new 64-bit schedule: rotl64(k,7*i) ^ (i*GOLDEN64), i 1-based */
    return rotl64(k, 7*i) ^ ((uint64_t)i * 0x9E3779B97F4A7C15ULL);
}
static uint64_t lin64(uint64_t x) { return x ^ rotl64(x, 3) ^ rotl64(x, 11); }
static uint32_t F_wide(uint32_t R, uint32_t rk) {
    uint64_t X = ((uint64_t)R << 32) | rk;
    X = sbox64(X, S1T);
    X = lin64(X);
    return (uint32_t)(X >> 32) ^ (uint32_t)X ^ rk;
}
"""


def gen_impl_wide(name, kind, param, desc):
    body = C_COMMON.format(name=name, desc=desc) + C_WIDE_HELPERS
    if kind == "spn":
        nr = param
        body += f"""
uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint64_t X = val;
    for (int i = 1; i <= {nr}; i++) {{
        X ^= RK64new(key, i);
        X = sbox64(X, S1T);
        X = lin64(X);
    }}
    X ^= RK64new(key, {nr + 1});
    return X;
}}
"""
    elif kind == "lm":
        fexpr = {"ps_311": "F_ps_311(D, RK32(key, i))",
                 "chi_311": "F_chi_311(D, RK32(key, i))"}[param]
        body += f"""
uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= 6; i++) {{
        uint32_t D = L ^ R;
        uint32_t T = {fexpr};
        uint32_t nL = R ^ T, nR = D;
        L = nL; R = nR;
    }}
    return ((uint64_t)L << 32) | R;
}}
"""
    elif kind == "wide128":
        nr = param
        body += f"""
uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint64_t L = val ^ RK64new(key, 101);
    uint64_t R = rotl64(val, 13) ^ RK64new(key, 102);
    for (int i = 1; i <= {nr}; i++) {{
        uint64_t F = lin64(sbox64(R, S1T)) ^ RK64new(key, i);
        uint64_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }}
    return L ^ R;
}}
"""
    elif kind == "wideF":
        body += """
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= 5; i++) {
        uint32_t F = F_wide(R, RK32(key, i));
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }
    return ((uint64_t)R << 32) | L;
}
"""
    else:
        raise ValueError(kind)
    return body


W_V_DECL = """
reg [31:0] L, R;
reg [31:0] Lt, Rt;
reg [31:0] t, u;
reg [31:0] rk32;
reg [31:0] D;
reg [63:0] X, X2;
reg [63:0] L64, R64, F64;
reg [63:0] rkv;
integer i, r;
"""

# New 64-bit round-key schedule in the 0-based Verilog loop:
# C: RK64new(key, j) = rotl64(key, 7*j) ^ (j*GOLDEN64), j 1-based = i+1.
V_RK64NEW_LOOP = """\
        r = (7 * (i + 1)) % 64;
        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 1) * 64'h9E3779B97F4A7C15);"""


def _rotl64_expr(reg, n):
    if n == 0:
        return reg
    return f"{{{reg}[{64 - n - 1}:0], {reg}[63:{64 - n}]}}"


def lin64_expr(reg):
    return f"{reg} ^ {_rotl64_expr(reg, 3)} ^ {_rotl64_expr(reg, 11)}"


def _lm_T_assigns(ftag):
    # T into t, reading D (Lai-Massey F input). Includes the ^rk32 that the
    # model/C F_ps_311 / F_chi_311 apply (dropped in first draft — caught by
    # check_rtl 300/300 before any synthesis numbers were trusted).
    if ftag == "ps_311":
        return (_ps_block((1, 2), src="D")
                + f"            t = {lin_expr('t', 3, 11)} ^ rk32;\n")
    if ftag == "chi_311":
        return (chi32_assigns("t", "D") + "\n"
                f"            t = {lin_expr('t', 3, 11)} ^ rk32;")
    raise ValueError(ftag)


def gen_rtl_wide(name, kind, param, desc):
    hdr = V_HDR.format(name=name, desc=desc)
    body = []
    if kind == "spn":
        nr = param
        body.append("always @(*) begin")
        body.append("    X = val;")
        body.append(f"    for (i = 0; i < {nr}; i = i + 1) begin")
        body.append("        " + V_RK64NEW_LOOP.replace("\n", "\n        "))
        body.append("        X = X ^ rkv;")
        body.append(sbox_dnf_assigns(S1, "X2", "X", 16))
        body.append(f"        X = {lin64_expr('X2')};")
        body.append("    end")
        j = nr + 1
        body.append(f"    r = (7 * {j}) % 64;")
        body.append(f"    rkv = ((key << r) | (key >> (64 - r))) ^ "
                    f"({j} * 64'h9E3779B97F4A7C15);")
        body.append("    X = X ^ rkv;")
        body.append("end")
        body.append("")
        body.append("assign out = X;")
    elif kind == "lm":
        body.append("always @(*) begin")
        body.append("    L = val[63:32];")
        body.append("    R = val[31:0];")
        body.append("    for (i = 0; i < 6; i = i + 1) begin")
        body.append("        " + V_RK_STD.replace("\n", "\n        "))
        body.append("        D = L ^ R;")
        for line in _lm_T_assigns(param).split("\n"):
            body.append(line)
        body.append("        Lt = R ^ t;")
        body.append("        Rt = D;")
        body.append("        L = Lt;")
        body.append("        R = Rt;")
        body.append("    end")
        body.append("end")
        body.append("")
        body.append("assign out = {L, R};")
    elif kind == "wide128":
        nr = param
        body.append("always @(*) begin")
        body.append("    r = (7 * 101) % 64;")
        body.append("    rkv = ((key << r) | (key >> (64 - r))) ^ "
                    "(101 * 64'h9E3779B97F4A7C15);")
        body.append("    L64 = val ^ rkv;")
        body.append("    r = (7 * 102) % 64;")
        body.append("    rkv = ((key << r) | (key >> (64 - r))) ^ "
                    "(102 * 64'h9E3779B97F4A7C15);")
        body.append("    R64 = {val[50:0], val[63:51]} ^ rkv;")
        body.append(f"    for (i = 0; i < {nr}; i = i + 1) begin")
        body.append("        " + V_RK64NEW_LOOP.replace("\n", "\n        "))
        body.append(sbox_dnf_assigns(S1, "X2", "R64", 16))
        body.append(f"        F64 = {lin64_expr('X2')} ^ rkv;")
        body.append("        X = R64;")
        body.append("        R64 = L64 ^ F64;")
        body.append("        L64 = X;")
        body.append("    end")
        body.append("end")
        body.append("")
        body.append("assign out = L64 ^ R64;")
    elif kind == "wideF":
        body.append("always @(*) begin")
        body.append("    L = val[63:32];")
        body.append("    R = val[31:0];")
        body.append("    for (i = 0; i < 5; i = i + 1) begin")
        body.append("        " + V_RK_STD.replace("\n", "\n        "))
        body.append("        X = {R, rk32};")
        body.append(sbox_dnf_assigns(S1, "X2", "X", 16))
        body.append(f"        X2 = {lin64_expr('X2')};")
        body.append("        t = X2[63:32] ^ X2[31:0] ^ rk32;")
        body.append("        Lt = R;")
        body.append("        Rt = L ^ t;")
        body.append("        L = Lt;")
        body.append("        R = Rt;")
        body.append("    end")
        body.append("end")
        body.append("")
        body.append("assign out = {R, L};")
    else:
        raise ValueError(kind)
    body.append("")
    body.append("endmodule")
    return hdr + W_V_DECL + "\n".join(body) + "\n"


# ---------------- rh2 emitters ----------------
C_RH2_HELPERS = """
static uint32_t F_ps_3rot_odd(uint32_t R, uint32_t rk) {
    uint32_t t = F_ps_t(R, 1, 2);
    uint32_t l = t ^ rotl32(t, 3) ^ rotl32(t, 7);
    return l ^ rk;
}
static uint64_t lin64_fast(uint64_t x) { return x ^ rotl64(x, 17) ^ rotl64(x, 41); }
"""


def gen_impl_rh2(name, kind, desc):
    body = C_COMMON.format(name=name, desc=desc) + C_WIDE_HELPERS + C_RH2_HELPERS
    if kind == "feistel_odd3rot":
        body += """
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= 6; i++) {
        uint32_t F = F_ps_3rot_odd(R, RK32(key, i));
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }
    return ((uint64_t)R << 32) | L;
}
"""
    elif kind == "spn_fast":
        body += """
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t X = val;
    for (int i = 1; i <= 4; i++) {
        X ^= RK64new(key, i);
        X = sbox64(X, S1T);
        X = lin64_fast(X);
    }
    X ^= RK64new(key, 5);
    return X;
}
"""
    elif kind == "wide128_nocomp":
        body += """
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t L = val ^ RK64new(key, 101);
    uint64_t R = rotl64(val, 13) ^ RK64new(key, 102);
    for (int i = 1; i <= 5; i++) {
        uint64_t F = lin64(sbox64(R, S1T)) ^ RK64new(key, i);
        uint64_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }
    return L;
}
"""
    elif kind == "lm5":
        body += """
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= 5; i++) {
        uint32_t D = L ^ R;
        uint32_t T = F_chi_311(D, RK32(key, i));
        uint32_t nL = R ^ T, nR = D;
        L = nL; R = nR;
    }
    return ((uint64_t)L << 32) | R;
}
"""
    else:
        raise ValueError(kind)
    return body


def gen_rtl_rh2(name, kind, desc):
    hdr = V_HDR.format(name=name, desc=desc)
    body = []
    if kind == "feistel_odd3rot":
        body.append("always @(*) begin")
        body.append("    L = val[63:32];")
        body.append("    R = val[31:0];")
        body.append("    for (i = 0; i < 6; i = i + 1) begin")
        body.append("        " + V_RK_STD.replace("\n", "\n        "))
        body.append(_ps_block((1, 2)))
        body.append("            t = t ^ {t[28:0], t[31:29]} ^ {t[24:0], t[31:25]} ^ rk32;")
        body.append("        Lt = R;")
        body.append("        Rt = L ^ t;")
        body.append("        L = Lt;")
        body.append("        R = Rt;")
        body.append("    end")
        body.append("end")
        body.append("")
        body.append("assign out = {R, L};")
    elif kind == "spn_fast":
        body.append("always @(*) begin")
        body.append("    X = val;")
        body.append("    for (i = 0; i < 4; i = i + 1) begin")
        body.append("        " + V_RK64NEW_LOOP.replace("\n", "\n        "))
        body.append("        X = X ^ rkv;")
        body.append(sbox_dnf_assigns(S1, "X2", "X", 16))
        body.append("        X = X2 ^ {X2[46:0], X2[63:47]} ^ {X2[22:0], X2[63:23]};")
        body.append("    end")
        body.append("    r = (7 * 5) % 64;")
        body.append("    rkv = ((key << r) | (key >> (64 - r))) ^ (5 * 64'h9E3779B97F4A7C15);")
        body.append("    X = X ^ rkv;")
        body.append("end")
        body.append("")
        body.append("assign out = X;")
    elif kind == "wide128_nocomp":
        body.append("always @(*) begin")
        body.append("    r = (7 * 101) % 64;")
        body.append("    rkv = ((key << r) | (key >> (64 - r))) ^ "
                    "(101 * 64'h9E3779B97F4A7C15);")
        body.append("    L64 = val ^ rkv;")
        body.append("    r = (7 * 102) % 64;")
        body.append("    rkv = ((key << r) | (key >> (64 - r))) ^ "
                    "(102 * 64'h9E3779B97F4A7C15);")
        body.append("    R64 = {val[50:0], val[63:51]} ^ rkv;")
        body.append("    for (i = 0; i < 5; i = i + 1) begin")
        body.append("        " + V_RK64NEW_LOOP.replace("\n", "\n        "))
        body.append(sbox_dnf_assigns(S1, "X2", "R64", 16))
        body.append(f"        F64 = {lin64_expr('X2')} ^ rkv;")
        body.append("        X = R64;")
        body.append("        R64 = L64 ^ F64;")
        body.append("        L64 = X;")
        body.append("    end")
        body.append("end")
        body.append("")
        body.append("assign out = L64;")
    elif kind == "lm5":
        body.append("always @(*) begin")
        body.append("    L = val[63:32];")
        body.append("    R = val[31:0];")
        body.append("    for (i = 0; i < 5; i = i + 1) begin")
        body.append("        " + V_RK_STD.replace("\n", "\n        "))
        body.append("        D = L ^ R;")
        for line in _lm_T_assigns("chi_311").split("\n"):
            body.append(line)
        body.append("        Lt = R ^ t;")
        body.append("        Rt = D;")
        body.append("        L = Lt;")
        body.append("        R = Rt;")
        body.append("    end")
        body.append("end")
        body.append("")
        body.append("assign out = {L, R};")
    else:
        raise ValueError(kind)
    body.append("")
    body.append("endmodule")
    return hdr + W_V_DECL + "\n".join(body) + "\n"


# ---------------- model.py / meta.json ----------------
MODEL_PY = '''"""Python model wrapper for {name} (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round_hyb/models")
from rhyb import {name} as _np

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
    _selftest_chi16_rtl()
    rhyb.selftest()
    # dedupe: pairwise-distinct model outputs across the full 17-spec set.
    # (Capable of failing: would trip if two specs were accidentally
    # identical, e.g. a round-tag typo.)
    rng = np.random.default_rng(20261003)
    V = rng.integers(0, 2**64, size=300, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    seen = {}
    all_specs = ([(n, t, d) for n, t, d in SPECS]
                 + [(n, None, d) for n, _, _, d in rhyb.WIDE_SPECS]
                 + [(n, None, d) for n, _, d in rhyb.RH2_SPECS])
    for name, tags, desc in all_specs:
        fn = getattr(rhyb, name)
        o = fn(V, K).tobytes()
        assert o not in seen.values(), f"DUPLICATE model output: {name}"
        seen[name] = o
    print(f"dedupe: {len(all_specs)} specs pairwise-distinct OK (300 vectors)")
    for name, tags, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, tags, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, tags, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(rhyb, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")
    for name, kind, param, desc in rhyb.WIDE_SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl_wide(name, kind, param, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl_wide(name, kind, param, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(rhyb, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name} [{kind}]")
    # rh2 follow-ups
    for name, kind, desc in rhyb.RH2_SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl_rh2(name, kind, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl_rh2(name, kind, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(rhyb, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name} [rh2:{kind}]")


if __name__ == "__main__":
    emit()
