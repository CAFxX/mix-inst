#!/usr/bin/env python3
"""Round 18 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round18/models/r18.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
affine r7/r8/r9 key schedule.

Families (per coordinator brief), all 6r:
  1. parsplit chi16 offsets (1,3) mod 16.
  2. parsplit chi16 offsets (0,2) mod 16.
  3. parsplit S1-8/chi-24: S1 on R[7:0] (2 nibbles), chi24 on R[31:8]
     with offsets (1,2) mod 24.
  4. truncation probe: r13 alt, round 6 (even/chi) F = chi32(R)^rk
     (no linear layer on the final diffusion round).
  5. palindromic key on r13 alt: rk_i = RK32(key,i) ^ RK32(key,7-i).
  6. asymmetric: odd rounds full S1-F; even rounds
     F = lin(3,11)((R[31:16]<<16) | chi16(R[15:0]))^rk
     (chi on low half, passthrough high half).
  7. parsplit with (5,17) rotmix.
  8. F = lin(3,11)(S1(R) ^ chi32(R))^rk — XOR of nonlinear outputs BEFORE a
     single shared linear layer.
  9. alt with chi variant on even rounds: b_i = a_i ^ (~a_{i+1} & a_{i+3}).

Structural note (premix lesson, r17): all are plain balanced Feistel with an
arbitrary F — bijective in val for fixed key regardless of F, and round
inputs change every round by construction. No novel topology.

RTL policy (rounds 8/11/12/13/17): direct boolean assigns inside ONE always
@(*) block (no Verilog functions; no module-level assign may read an
always-block-driven reg). Round-key indexing: C/Python call RK32(key,i) with
1-based i, and RK32 itself bakes in (i+1) -> rotl64(k,13*(i+1)) ^
(i+1)*GOLDEN; the 0-based Verilog loop therefore uses (i+2) (round-11
off-by-one lesson).

Usage: python3 round18/gen_r18.py   (writes fast_battery/candidates/r18_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R18 = os.path.join(EXP, "round18")
sys.path.insert(0, os.path.join(R18, "models"))
import numpy as np  # noqa: E402
import r18  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

# (name, kind, rounds, desc)
SPECS = [
    ("r18_feist6_ps_chioff13_nw", "ps_chioff13", 6,
     "6r Feistel, parsplit F=lin311(t)^rk, t[31:16]=chi16(R[31:16],1,3), t[15:0]=S1(R[15:0]), NO whitening"),
    ("r18_feist6_ps_chioff02_nw", "ps_chioff02", 6,
     "6r Feistel, parsplit F=lin311(t)^rk, t[31:16]=chi16(R[31:16],0,2), t[15:0]=S1(R[15:0]), NO whitening"),
    ("r18_feist6_ps_s18_chi24_nw", "ps_s18_chi24", 6,
     "6r Feistel, parsplit F=lin311(t)^rk, t[31:8]=chi24(R[31:8],1,2), t[7:0]=S1(R[7:0]), NO whitening"),
    ("r18_feist6_alt_notr_nw", "alt_notr", 6,
     "6r Feistel, r13 alt (odd S1-F, even chi-F) but round 6 F=chi32(R)^rk (no linear layer), NO whitening"),
    ("r18_feist6_alt_palk_nw", "alt_palk", 6,
     "6r Feistel, r13 alt with palindromic round keys rk_i=RK32(key,i)^RK32(key,7-i), NO whitening"),
    ("r18_feist6_alt_asym_nw", "alt_asym", 6,
     "6r Feistel, odd rounds S1-F=lin311(S1(R))^rk / even rounds F=lin311(t)^rk, t=(R[31:16]<<16)|chi16(R[15:0]), NO whitening"),
    ("r18_feist6_ps_517_nw", "ps_517", 6,
     "6r Feistel, parsplit F=lin517(t)^rk, t[31:16]=chi16(R[31:16]), t[15:0]=S1(R[15:0]), NO whitening"),
    ("r18_feist6_s1xorchi_nw", "s1xorchi", 6,
     "6r Feistel, F=lin311(S1(R)^chi32(R))^rk, NO whitening"),
    ("r18_feist6_alt_chioff13_nw", "alt_chioff13", 6,
     "6r Feistel, r13 alt with even-round chi variant b_i=a_i^(~a_{i+1}&a_{i+3}), NO whitening"),
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
    for n, o1, o2, fn in [(16, 1, 3, lambda x: r18._chi16_np(np.uint64(x), 1, 3)),
                          (16, 0, 2, lambda x: r18._chi16_np(np.uint64(x), 0, 2)),
                          (24, 1, 2, lambda x: r18._chi24_np(np.uint64(x), 1, 2))]:
        for _ in range(200):
            xv = int(rng.integers(0, 2 ** n))
            got = int(fn(xv))
            want = _chi_ref(xv, n, o1, o2)
            assert got == want, (n, o1, o2, hex(xv), hex(got), hex(want))
    for _ in range(200):
        xv = int(rng.integers(0, 2 ** 32))
        got = int(r18._chi32v_np(np.uint64(xv)))
        want = _chi_ref(xv, 32, 1, 3)
        assert got == want, ("chi32v", hex(xv), hex(got), hex(want))
    print("chi self-tests: chi16(1,3), chi16(0,2), chi24(1,2), chi32v — 200 vectors each OK")


def _selftest_bijection():
    # Fixed-key bijection spot check (Feistel structural sanity; would fail
    # if the round loop or output packing were broken).
    rng = np.random.default_rng(777)
    V = rng.integers(0, 2 ** 64, size=2000, dtype=np.uint64)
    K = np.uint64(0xDEADBEEFCAFEBABE)
    for name, kind, rounds, desc in SPECS:
        fn = getattr(r18, name)
        O = fn(V, K)
        assert len(set(O.tolist())) == len(V), f"bijection fail: {name}"
    print("bijection self-test: 9 candidates x 2000 vals distinct OK")


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
 * GENERATED by round18/gen_r18.py -- do not edit by hand.
 * Bit-exact vs Python model round18/models/r18.py ({name}). */
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
static uint32_t sbox8(uint32_t x, const uint8_t *T) {{
    uint32_t r = 0;
    for (int i = 0; i < 2; i++)
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
static uint32_t chi24(uint32_t x, int o1, int o2) {{
    uint32_t r = 0;
    for (int i = 0; i < 24; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + o1) % 24)) & 1u;
        uint32_t a2 = (x >> ((i + o2) % 24)) & 1u;
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
static uint32_t F_chi_notr(uint32_t R, uint32_t rk) {{
    return chi32(R) ^ rk;
}}
static uint32_t F_chi32v_311(uint32_t R, uint32_t rk) {{
    return lin_ab(chi32v(R), 3, 11) ^ rk;
}}
static uint32_t F_ps_chioff(uint32_t R, uint32_t rk, int o1, int o2) {{
    uint32_t t = (chi16(R >> 16, o1, o2) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_ps_517(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi16(R >> 16, 1, 2) << 16) | sbox16(R & 0xFFFFu, S1T);
    return lin_ab(t, 5, 17) ^ rk;
}}
static uint32_t F_ps_s18_chi24(uint32_t R, uint32_t rk) {{
    uint32_t t = (chi24(R >> 8, 1, 2) << 8) | sbox8(R & 0xFFu, S1T);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_asym_even(uint32_t R, uint32_t rk) {{
    uint32_t t = ((R & 0xFFFF0000u)) | chi16(R & 0xFFFFu, 1, 2);
    return lin_ab(t, 3, 11) ^ rk;
}}
static uint32_t F_s1xorchi(uint32_t R, uint32_t rk) {{
    return lin_ab(sbox32(R, S1T) ^ chi32(R), 3, 11) ^ rk;
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

C_MAIN_FEISTEL_NOTR = """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= 6; i++) {
        uint32_t F;
        if (i == 6)
            F = F_chi_notr(R, RK32(key, i));
        else
            F = (i & 1) ? F_s1_311(R, RK32(key, i))
                        : F_chi_311(R, RK32(key, i));
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }
    return ((uint64_t)R << 32) | L;
}
"""

C_F_LINE = {
    "ps_chioff13": ("        uint32_t F = F_ps_chioff(R, RK32(key, i), 1, 3);"),
    "ps_chioff02": ("        uint32_t F = F_ps_chioff(R, RK32(key, i), 0, 2);"),
    "ps_s18_chi24": "        uint32_t F = F_ps_s18_chi24(R, RK32(key, i));",
    "alt_palk": ("        uint32_t rk = RK32(key, i) ^ RK32(key, 7 - i);\n"
                 "        uint32_t F = (i & 1) ? F_s1_311(R, rk)\n"
                 "                           : F_chi_311(R, rk);"),
    "alt_asym": ("        uint32_t F = (i & 1) ? F_s1_311(R, RK32(key, i))\n"
                 "                           : F_asym_even(R, RK32(key, i));"),
    "ps_517": "        uint32_t F = F_ps_517(R, RK32(key, i));",
    "s1xorchi": "        uint32_t F = F_s1xorchi(R, RK32(key, i));",
    "alt_chioff13": ("        uint32_t F = (i & 1) ? F_s1_311(R, RK32(key, i))\n"
                     "                           : F_chi32v_311(R, RK32(key, i));"),
}

C_MAIN_SPECIAL = {"alt_notr"}


def gen_impl(name, kind, rounds, desc):
    body = C_COMMON.format(name=name, desc=desc)
    if kind in C_MAIN_SPECIAL:
        body += C_MAIN_FEISTEL_NOTR
    else:
        f_line = C_F_LINE[kind]
        body += C_MAIN_FEISTEL.format(rounds=rounds, f_line=f_line)
    return body


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round18/gen_r18.py -- do not edit by hand.
// Bit-exact vs Python model round18/models/r18.py ({name}).
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
reg [63:0] rkv, rkv2;
integer i, r, r2;
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

# Palindromic key: rk = RK32(key, r) ^ RK32(key, 7-r), r = i+1 (1-based 1..6),
# mirror j = 7-r = 6-i (1-based 6..1). RK32(key,j): rj=(13*(j+1))%64,
# mult (j+1)*GOLDEN = (7-i)*GOLDEN.
V_RK_PALK = """\
        r = (13 * (i + 2)) % 64;
        rkv = ((key << r) | (key >> (64 - r))) ^ ((i + 2) * 64'h9E3779B97F4A7C15);
        r2 = (13 * (7 - i)) % 64;
        rkv2 = ((key << r2) | (key >> (64 - r2))) ^ ((7 - i) * 64'h9E3779B97F4A7C15);
        rk32 = rkv[31:0] ^ rkv2[31:0];"""

V_TAIL_FEISTEL = """\
        Lt = R;
        Rt = L ^ t ^ rk32;
        L = Lt;
        R = Rt;"""


def _ps_block(o1, o2):
    # parsplit: t[31:16] = chi16(R[31:16], o1, o2), t[15:0] = S1(R[15:0])
    return (chiN_assigns("t", "R", 16, o1, o2, base=16) + "\n"
            + sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0) + "\n"
            f"            t = {lin_expr('t', 3, 11)};\n")


def gen_rtl(name, kind, rounds, desc):
    body = []
    body.append("always @(*) begin")
    body.append("    L = val[63:32];")
    body.append("    R = val[31:0];")
    body.append(f"    for (i = 0; i < {rounds}; i = i + 1) begin")

    if kind in ("ps_chioff13", "ps_chioff02"):
        o1, o2 = (1, 3) if kind == "ps_chioff13" else (0, 2)
        body.append(f"        // ---- parsplit: chi16(R[31:16],{o1},{o2}), S1(R[15:0]) ----")
        body.append(_ps_block(o1, o2))
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "ps_517":
        body.append("        // ---- parsplit: chi16(R[31:16]), S1(R[15:0]), lin(5,17) ----")
        body.append(chiN_assigns("t", "R", 16, 1, 2, base=16))
        body.append(sbox_dnf_assigns(S1, "t", "R", 4, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 5, 17)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "ps_s18_chi24":
        body.append("        // ---- parsplit: t[31:8]=chi24(R[31:8],1,2), t[7:0]=S1(R[7:0]) ----")
        body.append(chiN_assigns("t", "R", 24, 1, 2, base=8))
        body.append(sbox_dnf_assigns(S1, "t", "R", 2, dst_base=0, src_base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt_notr":
        body.append("        // ---- alt, round 6 (i==5) drops the linear layer ----")
        body.append("        if (i == 5) begin")
        body.append(chi32_assigns("t", "R"))
        body.append("        end else if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32_assigns("t", "R"))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt_palk":
        body.append("        // ---- alt with palindromic round keys ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32_assigns("t", "R"))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end")
        body.append(V_RK_PALK)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt_asym":
        body.append("        // ---- odd rounds S1-F, even rounds chi16-low/passthrough-high ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append("            t = R & 32'hFFFF0000;")
        body.append(chiN_assigns("t", "R", 16, 1, 2, base=0))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append("        end")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "s1xorchi":
        body.append("        // ---- F = lin(S1(R) ^ chi32(R)) ^ rk ----")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(chi32_assigns("t", "R"))
        body.append("            t = u ^ t;")
        body.append(f"            t = {lin_expr('t', 3, 11)};")
        body.append(V_RK_STD)
        body.append(V_TAIL_FEISTEL)
    elif kind == "alt_chioff13":
        body.append("        // ---- odd rounds S1-F, even rounds chi32v-F (offsets 1,3) ----")
        body.append("        if (i[0] == 1'b0) begin")
        body.append(sbox_dnf_assigns(S1, "u", "R", 8))
        body.append(f"            t = {lin_expr('u', 3, 11)};")
        body.append("        end else begin")
        body.append(chi32v_assigns("t", "R"))
        body.append(f"            t = {lin_expr('t', 3, 11)};")
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
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round18/models")
from r18 import {name} as _np

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
    # identical, e.g. an offset typo.)
    rng = np.random.default_rng(12345)
    V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    seen = {}
    for name, kind, rounds, desc in SPECS:
        fn = getattr(r18, name)
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
        fn = getattr(r18, name)
        g0 = f"0x{int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))):016x}"
        g1 = (f"0x{int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0))):016x}")
        with open(os.path.join(d, "meta.json"), "w") as f:
            f.write(META_JSON.format(name=name, desc=desc,
                                     golden0=g0, golden1=g1))
        print(f"emitted {name}")


if __name__ == "__main__":
    emit()
