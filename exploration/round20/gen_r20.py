#!/usr/bin/env python3
"""Round 20 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round20/models/r20.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Frontier entering round 20: r19_feist6_alt_notr_chioff13_nw (37.4u, BIC 0.142),
r18_feist6_alt_notr_nw (37.9u, BIC 0.172). Both 6r alt-notr (odd S1 rounds,
even chi rounds, round 6 F=chi32(R)^rk truncated).

Families (all 6r Feistel, no whitening, affine r7/r8/r9 key schedule),
round tags: s1_311, chi_311, s1_notr, chi_notr, s1_713, chi_713,
chi32v_311, chi32v_notr, chi32v_517, s1_517, chi_keyin_notr, chi_fm16, chi32w_311.
  A. BIC-fix probes (notr + cheap final mixing on round 6's F output):
     fm03:  F_6 = (chi32(R)^rk) ^ rotl32(chi32(R)^rk, 3)
     fm07:  same with rotl 7
     fm11:  same with rotl 11
     fm311: F_6 = rotl32(chi32(R),3) ^ rotl32(chi32(R),11) ^ rk
  B. truncation axis:
     notr5:  r13 alt with round 5's linear ALSO dropped (F_5 = S1(R)^rk)
     ps_notr: parsplit-F with round 6's linear dropped
     r9_notr: r9 structure with round 6's linear dropped (F_6 = S1(R)^rk)
     chioff13: notr + chi offsets (1,3) on rounds 2,4
     notr_517: notr with (5,17) rotmix on the 5 surviving linears

Structural note: all are plain balanced Feistel with an arbitrary F —
bijective in val for fixed key regardless of F. No novel topology.

RTL policy: direct boolean assigns inside ONE always @(*) block (no Verilog
functions; no module-level assign may read an always-block-driven reg).
Round-key indexing: C/Python call RK32(key,i) with 1-based i, and RK32 bakes
in (i+1); the 0-based Verilog loop therefore uses (i+2) (round-11 lesson).

Usage: python3 round20/gen_r20.py   (writes fast_battery/candidates/r19_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R20 = os.path.join(EXP, "round20")
sys.path.insert(0, os.path.join(R20, "models"))
import numpy as np  # noqa: E402
import r20  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

# (name, [6 round tags], desc)
SPECS = [
    ("r20_feist6_alt_notr_s1final_nw",
     ["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "s1_notr"],
     "6r alt-notr with round 6 F = S1(R)^rk (S1 final, no linear), NO whitening"),
    ("r20_feist6_alt_notr_chioff13all_nw",
     ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "chi32v_notr"],
     "6r alt-notr + chi offsets (1,3) on rounds 2,4 AND truncated round 6, NO whitening"),
    ("r20_feist6_alt_notr_chioff13_517_nw",
     ["s1_517", "chi32v_517", "s1_517", "chi32v_517", "s1_517", "chi_notr"],
     "6r alt-notr + chi offsets (1,3) on rounds 2,4 with (5,17) rotmix on the 5 surviving linears, NO whitening"),
    ("r20_feist6_alt_notr_keyin_nw",
     ["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_keyin_notr"],
     "6r alt-notr with round 6 F = chi32(R ^ rk32) (key inside chi input), NO whitening"),
    ("r20_feist6_alt_notr_drop4_nw",
     ["s1_311", "chi_311", "s1_311", "chi_notr", "s1_311", "chi_notr"],
     "6r alt-notr with round 4's (chi) linear ALSO dropped (F_4=chi32(R)^rk), NO whitening — S1-gated probe"),
    ("r20_feist6_alt_notr_713_nw",
     ["s1_713", "chi_713", "s1_713", "chi_713", "s1_713", "chi_notr"],
     "6r alt-notr with (7,13) rotmix on the 5 surviving linears, NO whitening"),
    ("r20_feist6_alt_notr_fm16_nw",
     ["s1_311", "chi_311", "s1_311", "chi_311", "s1_311", "chi_fm16"],
     "6r alt-notr + final mixing F_6=(chi32(R)^rk)^rotl32(chi32(R)^rk,16), NO whitening"),
    ("r20_feist6_alt_notr_chioff31_nw",
     ["s1_311", "chi32w_311", "s1_311", "chi32w_311", "s1_311", "chi_notr"],
     "6r alt-notr + chi variant b_i=a_i^(~a_{i+3}&a_{i+1}) on rounds 2,4, NO whitening"),
    ("r20_feist6_alt_chioff13_nw",
     ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "chi32v_311"],
     "6r FULL alt (WITH round-6 linear) + chi offsets (1,3) on rounds 2,4,6, NO whitening"),
]

C_F_EXPR = {
    "s1_311": "F_s1_311(R, RK32(key, i))",
    "chi_311": "F_chi_311(R, RK32(key, i))",
    "chi_notr": "F_chi_notr(R, RK32(key, i))",
    "s1_notr": "F_s1_notr(R, RK32(key, i))",
    "s1_713": "F_s1_713(R, RK32(key, i))",
    "chi_713": "F_chi_713(R, RK32(key, i))",
    "s1_517": "F_s1_517(R, RK32(key, i))",
    "chi32v_311": "F_chi32v_311(R, RK32(key, i))",
    "chi32v_notr": "F_chi32v_notr(R, RK32(key, i))",
    "chi32v_517": "F_chi32v_517(R, RK32(key, i))",
    "chi_keyin_notr": "F_chi_keyin_notr(R, RK32(key, i))",
    "chi_fm16": "F_chi_fm16(R, RK32(key, i))",
    "chi32w_311": "F_chi32w_311(R, RK32(key, i))",
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


def _chi_ref(xv, n, o1, o2):
    want = 0
    for i in range(n):
        a0 = (xv >> i) & 1
        a1 = (xv >> ((i + o1) % n)) & 1
        a2 = (xv >> ((i + o2) % n)) & 1
        want |= (a0 ^ ((1 - a1) & a2)) << i
    return want


def _selftest_chis():
    # Capable of failing: numpy chi variants vs independent bit loops.
    rng = np.random.default_rng(424242)
    for _ in range(200):
        xv = int(rng.integers(0, 2 ** 32))
        assert int(r20._chi32_np(np.uint64(xv))) == _chi_ref(xv, 32, 1, 2), \
            ("chi32", hex(xv))
        assert int(r20._chi32v_np(np.uint64(xv))) == _chi_ref(xv, 32, 1, 3), \
            ("chi32v", hex(xv))
        assert int(r20._chi32w_np(np.uint64(xv))) == _chi_ref(xv, 32, 3, 1), \
            ("chi32w", hex(xv))
    print("chi self-tests: chi32, chi32v, chi32w — 200 vectors each OK")


def _selftest_bijection():
    # Fixed-key bijection spot check (Feistel structural sanity; would fail
    # if the round loop or output packing were broken).
    rng = np.random.default_rng(777)
    V = rng.integers(0, 2 ** 64, size=2000, dtype=np.uint64)
    K = np.uint64(0xDEADBEEFCAFEBABE)
    for name, tags, desc in SPECS:
        fn = getattr(r20, name)
        O = fn(V, K)
        assert len(set(O.tolist())) == len(V), f"bijection fail: {name}"
    print(f"bijection self-test: {len(SPECS)} candidates x 2000 vals distinct OK")


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
    # chi16 offsets (1,2)
    lines = []
    for i in range(16):
        lines.append(
            f"            {dst}[{base + i}] = {src}[{base + i}] ^ "
            f"(~{src}[{base + (i + 1) % 16}] & {src}[{base + (i + 2) % 16}]);")
    return "\n".join(lines)


def _rotl_expr(reg, n):
    return f"{{{reg}[{32 - n - 1}:0], {reg}[31:{32 - n}]}}"


def lin_expr(reg, a, b):
    return f"{reg} ^ {_rotl_expr(reg, a)} ^ {_rotl_expr(reg, b)}"


# ---------------- C ----------------
C_COMMON = """/* {name}: {desc}
 * GENERATED by round20/gen_r20.py -- do not edit by hand.
 * Bit-exact vs Python model round20/models/r20.py ({name}). */
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

static uint32_t F_s1_311(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, S1T), 3, 11) ^ rk;
}}
static uint32_t F_chi_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32(R), 3, 11) ^ rk;
}}
static uint32_t F_chi32v_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32v(R), 3, 11) ^ rk;
}}
static uint32_t F_chi_notr(uint32_t R, uint32_t rk) {{
    return chi32(R) ^ rk;
}}
static uint32_t F_s1_notr(uint32_t R, uint32_t rk) {{
    return sbox32(R, S1T) ^ rk;
}}
static uint32_t F_chi_fm03(uint32_t R, uint32_t rk) {{
    uint32_t y = chi32(R) ^ rk;
    return y ^ rotl32(y, 3);
}}
static uint32_t F_chi_fm07(uint32_t R, uint32_t rk) {{
    uint32_t y = chi32(R) ^ rk;
    return y ^ rotl32(y, 7);
}}
static uint32_t F_chi_fm11(uint32_t R, uint32_t rk) {{
    uint32_t y = chi32(R) ^ rk;
    return y ^ rotl32(y, 11);
}}
static uint32_t F_chi_fm311(uint32_t R, uint32_t rk) {{
    uint32_t c = chi32(R);
    return rotl32(c, 3) ^ rotl32(c, 11) ^ rk;
}}
static uint32_t F_ps_311(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps_notr(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16) << 16) | sbox16(R & 0xFFFFu, S1T);
    return t ^ rk;
}}
static uint32_t F_s1_517(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, S1T), 5, 17) ^ rk;
}}
static uint32_t F_chi_517(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32(R), 5, 17) ^ rk;
}}
static uint32_t F_s1_713(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, S1T), 7, 13) ^ rk;
}}
static uint32_t F_chi_713(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32(R), 7, 13) ^ rk;
}}
static uint32_t F_chi32v_517(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32v(R), 5, 17) ^ rk;
}}
static uint32_t F_chi32v_notr(uint32_t R, uint32_t rk) {{
    return chi32v(R) ^ rk;
}}
static uint32_t F_chi_keyin_notr(uint32_t R, uint32_t rk) {{
    return chi32(R ^ rk);
}}
static uint32_t F_chi_fm16(uint32_t R, uint32_t rk) {{
    uint32_t y = chi32(R) ^ rk;
    return y ^ rotl32(y, 16);
}}
static uint32_t F_chi32w_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32w(R), 3, 11) ^ rk;
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
// GENERATED by round20/gen_r20.py -- do not edit by hand.
// Bit-exact vs Python model round20/models/r20.py ({name}).
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

V_TAIL_FEISTEL = """\
        Lt = R;
        Rt = L ^ t ^ rk32;
        L = Lt;
        R = Rt;"""


def _ps_block():
    # parsplit t = chi16(R[31:16]) || S1(R[15:0])  (offsets 1,2)
    return (chi16_assigns("t", "R", base=16) + "\n"
            + sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0) + "\n")


def gen_round_assigns(tag):
    """Verilog assigns computing F into t (tail XORs rk32 via V_TAIL_FEISTEL),
    except tags that bake rk into t themselves (fm03/07/11/16)."""
    if tag == "s1_311":
        return (sbox_dnf_assigns(S1, "u", "R", 8) + "\n"
                f"            t = {lin_expr('u', 3, 11)};")
    if tag == "chi_311":
        return (chi32_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 3, 11)};")
    if tag == "chi32v_311":
        return (chi32v_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 3, 11)};")
    if tag == "chi_notr":
        return chi32_assigns("t", "R")
    if tag == "s1_notr":
        return sbox_dnf_assigns(S1, "t", "R", 8)
    if tag in ("chi_fm03", "chi_fm07", "chi_fm11", "chi_fm16"):
        m = {"chi_fm03": 3, "chi_fm07": 7, "chi_fm11": 11, "chi_fm16": 16}[tag]
        # t = (u ^ rk32) ^ rotl((u ^ rk32), m); u = chi32(R)
        return (chi32_assigns("u", "R") + "\n"
                "            t = u ^ rk32;\n"
                f"            t = t ^ {_rotl_expr('t', m)};")
    if tag == "chi_fm311":
        # t = rotl(chi,3) ^ rotl(chi,11) ^ rk32; u = chi32(R)
        return (chi32_assigns("u", "R") + "\n"
                f"            t = {_rotl_expr('u', 3)} ^ {_rotl_expr('u', 11)} ^ rk32;")
    if tag == "ps_311":
        return (_ps_block()
                + f"            t = {lin_expr('t', 3, 11)};\n")
    if tag == "ps_notr":
        return _ps_block()
    if tag == "s1_517":
        return (sbox_dnf_assigns(S1, "u", "R", 8) + "\n"
                f"            t = {lin_expr('u', 5, 17)};")
    if tag == "chi_517":
        return (chi32_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 5, 17)};")
    if tag == "s1_713":
        return (sbox_dnf_assigns(S1, "u", "R", 8) + "\n"
                f"            t = {lin_expr('u', 7, 13)};")
    if tag == "chi_713":
        return (chi32_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 7, 13)};")
    if tag == "chi32v_517":
        return (chi32v_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 5, 17)};")
    if tag == "chi32v_notr":
        return chi32v_assigns("t", "R")
    if tag == "chi32w_311":
        return (chi32w_assigns("t", "R") + "\n"
                f"            t = {lin_expr('t', 3, 11)};")
    if tag == "chi_keyin_notr":
        # t = chi32(R ^ rk32); u is free scratch within this round branch.
        return ("            u = R ^ rk32;\n"
                + chi32_assigns("t", "u"))
    raise ValueError(tag)


def gen_rtl(name, tags, desc):
    # fm03/07/11/16 and chi_keyin_notr bake rk32 into t (they need rk inside
    # the round branch, e.g. y = chi^rk before the extra rotation, or
    # t = chi32(R^rk32)). V_RK_STD therefore runs BEFORE the round if-chain,
    # and the tail skips ^rk32 on those rounds.
    body = []
    body.append("always @(*) begin")
    body.append("    L = val[63:32];")
    body.append("    R = val[31:0];")
    body.append("    for (i = 0; i < 6; i = i + 1) begin")
    body.append("        " + V_RK_STD.replace("\n", "\n        "))
    for ri, tag in enumerate(tags):
        # previous branch's "end" already closed its begin, so chain with
        # plain "else if" (an extra "end" here would unbalance the block).
        kw = "if" if ri == 0 else "else if"
        body.append(f"        {kw} (i == {ri}) begin")
        for line in gen_round_assigns(tag).split("\n"):
            body.append(line)
        body.append("        end")
    body.append("        Lt = R;")
    fm_rounds = [ri for ri, tag in enumerate(tags)
                 if tag.startswith("chi_fm") or tag == "chi_keyin_notr"]
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


# ---------------- model.py / meta.json ----------------
MODEL_PY = '''"""Python model wrapper for {name} (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round20/models")
from r20 import {name} as _np

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
    _selftest_chis()
    _selftest_bijection()
    # dedupe: pairwise-distinct model outputs across the spec set.
    # (Capable of failing: would trip if two specs were accidentally
    # identical, e.g. a round-tag typo.)
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    seen = {}
    for name, tags, desc in SPECS:
        fn = getattr(r20, name)
        o = fn(V, K).tobytes()
        assert o not in seen.values(), f"DUPLICATE model output: {name}"
        seen[name] = o
    print(f"dedupe: {len(SPECS)} specs pairwise-distinct OK")
    for name, tags, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_impl(name, tags, desc))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, tags, desc))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(MODEL_PY.format(name=name))
        fn = getattr(r20, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
