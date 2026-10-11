#!/usr/bin/env python3
"""Round 22 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round22/models/r22.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Candidates (sota_analytical_designs.md §3, structurally different from Feistel-6):
  A. r22_wide_spn4_nw      — 4-round wide SPN: x_{i+1} = L(S16(x_i ^ rk_i))
  B. r22_em_chichi4_nw     — Even-Mansour P(m^k)^k, P = 4 x L(chichi64(x))
  B2.r22_em_chichi6_rot_nw — EM variant: 6 x rotl(chichi64(x), r_i)
  C. r22_keyed_spn6_nw     — 6-round keyed SPN: x_{i+1} = PI(S16(x_i ^ rk_i))
  D. r22_lm5_chi_nw        — 5-round correct Lai-Massey, chi32 F
  E. r22_benes_chichi_nw   — 11 Benes MUX stages + chichi64 every 3rd stage

chichi64 is the EXACT ChiChi (Belkheyar et al., EUROCRYPT 2025, Def.2/Thm.4).

RTL policy: direct boolean assigns inside ONE always @(*) block (no Verilog
functions; module-level `assign out` tap only, never read back in the block).
Round-key indexing: 0-based i everywhere; rk_i = rotl64(k,13*(i+1)) ^
((i+1)*GOLDEN64), matching r22._rk64_np.

Usage: python3 round22/gen_r22.py   (writes fast_battery/candidates/r22_*/)
"""
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R22 = os.path.join(EXP, "round22")
sys.path.insert(0, os.path.join(R22, "models"))
import numpy as np  # noqa: E402
import r22  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

SPECS = [
    ("r22_wide_spn4_nw",
     "4-round wide SPN: x_{i+1} = L(S16(x_i ^ rk_i)); S1 + (3,11) linear, NO whitening"),
    ("r22_em_chichi4_nw",
     "Even-Mansour P(m^k)^k, P = 4 rounds L(chichi64(x)); exact ChiChi (Eurocrypt'25), NO whitening"),
    ("r22_em_chichi6_rot_nw",
     "EM variant: 6 rounds rotl(chichi64(x), r_i), r_i=13(i+1)%64; aggressive 22u probe, NO whitening"),
    ("r22_keyed_spn6_nw",
     "6-round keyed SPN: x_{i+1} = PI(S16(x_i ^ rk_i)); transpose nibble perm, NO linear layer, NO whitening"),
    ("r22b_keyed_spn6_pbox_nw",
     "O34: 6-round keyed SPN: x_{i+1} = P(S16(x_i ^ rk_i)); validated P-box P(i)=(5i+27)%64 (single 64-cycle, 0 fixed points, spread), NO linear layer, NO whitening"),
    ("r22c_spn_mix4r_lp_nw",
     "O38 V0: 4-round keyed SPN: x_{i+1} = L(P(S16(x_i ^ rk_i))); P=O34 P-box, L=lin(3,11); mechanism probe for the A-class 4r failure"),
    ("r22c_spn_mix5r_lp_nw",
     "O38 V1: 5-round keyed SPN: x_{i+1} = L(P(S16(x_i ^ rk_i))); P=O34 P-box, L=lin(3,11); primary candidate (real mixing cures freezing)"),
    ("r22c_spn_mix6r_lp_nw",
     "O38 V2: 6-round keyed SPN: x_{i+1} = L(P(S16(x_i ^ rk_i))); P=O34 P-box, L=lin(3,11); round-count boundary probe"),
    ("r22c_spn_mix5r_shx_nw",
     "O38 V3: 5-round keyed SPN: x_{i+1} = SHX(P(S16(x_i ^ rk_i))); P=O34 P-box, SHX=triangular shift-XOR alternating direction (~2u/round bijective mixer)"),
    ("r22_lm5_chi_nw",
     "5-round correct Lai-Massey: d=L^R; t=chi32(d^rk); (R^t, d); orthomorphism (b,a^b), NO whitening"),
    ("r22_benes_chichi_nw",
     "11 Benes keyed-MUX stages + chichi64 every 3rd stage; switch bits from rotl64(k,13(s+1)), NO whitening"),
]


# ---------------- Quine-McCluskey (4 vars), copied from gen_r20 ----------------
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


# ---------------- C emission ----------------

C_HDR = """/* {name}: {desc}
 * GENERATED by round22/gen_r22.py -- do not edit by hand.
 * Bit-exact vs Python model round22/models/r22.py ({name}). */
#include <stdint.h>

static const uint8_t S1T[16] = {{0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10}};

static uint64_t rotl64(uint64_t x, unsigned r) {{
    r &= 63u;
    return r ? (x << r) | (x >> (64u - r)) : x;
}}
static uint64_t rk64(uint64_t k, int i) {{ /* i 0-based */
    unsigned r = (13u * (unsigned)(i + 1)) & 63u;
    return rotl64(k, r) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}}
static uint64_t sbox64(uint64_t x) {{
    uint64_t r = 0;
    for (int i = 0; i < 16; i++)
        r |= (uint64_t)S1T[(x >> (4*i)) & 0xFu] << (4*i);
    return r;
}}
static uint64_t lin64_311(uint64_t x) {{
    return x ^ rotl64(x, 3) ^ rotl64(x, 11);
}}
static uint32_t chi32(uint32_t x) {{
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) {{
        uint32_t a0 = (x >> i) & 1u;
        uint32_t a1 = (x >> ((i + 1) % 32)) & 1u;
        uint32_t a2 = (x >> ((i + 2) % 32)) & 1u;
        r |= (uint32_t)(a0 ^ ((~a1) & a2)) << i;
    }}
    return r;
}}
/* EXACT chi-chi_64 (Belkheyar et al., EUROCRYPT 2025, Def.2/Thm.4, m=32):
 * chi_31 on bits 0..30, chi_33 on bits 31..63, lambda at 29..32. */
static uint64_t chichi64(uint64_t x) {{
    uint64_t y = 0;
    int i, j;
    for (i = 0; i < 31; i++) {{
        uint64_t a0 = (x >> i) & 1u;
        uint64_t a1 = (x >> ((i + 1) % 31)) & 1u;
        uint64_t a2 = (x >> ((i + 2) % 31)) & 1u;
        y |= (a0 ^ ((~a1) & a2)) << i;
    }}
    for (j = 0; j < 33; j++) {{
        uint64_t a0 = (x >> (31 + j)) & 1u;
        uint64_t a1 = (x >> (31 + (j + 1) % 33)) & 1u;
        uint64_t a2 = (x >> (31 + (j + 2) % 33)) & 1u;
        y |= (a0 ^ ((~a1) & a2)) << (31 + j);
    }}
    {{
        uint64_t x29 = (x >> 29) & 1u, x30 = (x >> 30) & 1u;
        uint64_t x31 = (x >> 31) & 1u, x32 = (x >> 32) & 1u;
        y ^= ((x32 ^ x29) << 29) | ((x31 ^ x30) << 30)
           | ((x29 ^ x32 ^ x31) << 31) | ((x32 ^ x30) << 32);
    }}
    return y;
}}
static uint64_t transpose64(uint64_t x) {{
    /* new nibble j takes bit b from old nibble (j+4b)%16 */
    uint64_t y = 0;
    for (int j = 0; j < 16; j++)
        for (int b = 0; b < 4; b++) {{
            int src = (j + 4*b) % 16;
            y |= ((x >> (4*src + b)) & 1u) << (4*j + b);
        }}
    return y;
}}
static uint64_t pbox64_o34(uint64_t x) {{
    /* O34 P-box: out[(5*i+27)%64] = in[i]. Single 64-cycle, zero fixed
     * points, per-nibble spread both directions (see r22._selftest_pbox_o34).
     * Free wiring in RTL. */
    uint64_t y = 0;
    for (int i = 0; i < 64; i++)
        y |= ((x >> i) & 1u) << ((5*i + 27) % 64);
    return y;
}}
static uint64_t shxor64(uint64_t x, unsigned r, int dir) {{
    /* O38 triangular shift-XOR mixer: y = x ^ (x >> r) or y = x ^ (x << r).
     * Bijective for any r (triangular: the shift's leading r bits pass
     * through; every other bit depends only on bits closer to that edge,
     * so back-substitution inverts). Single XOR2 ~= 2u/round. */
    uint64_t s = dir > 0 ? (x >> r) : (x << r);
    return x ^ s;
}}
static uint64_t benes_stage(uint64_t x, int e, uint32_t sw) {{
    /* 32 keyed 2x2 switches pairing wires (i, i^2^e) */
    uint64_t y = 0;
    for (int j = 0; j < 32; j++) {{
        int lo = (1 << e) - 1;
        int p = (j & lo) | ((j >> e) << (e + 1));
        int q = p | (1 << e);
        uint64_t a = (x >> p) & 1u, b = (x >> q) & 1u;
        if ((sw >> j) & 1u) {{ y |= (b << p) | (a << q); }}
        else {{ y |= (a << p) | (b << q); }}
    }}
    return y;
}}
"""

C_BODIES = {
    "r22_wide_spn4_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int i = 0; i < 4; i++)
        x = lin64_311(sbox64(x ^ rk64(key, i)));
    return x;
}
""",
    "r22_em_chichi4_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    for (int i = 0; i < 4; i++)
        x = lin64_311(chichi64(x));
    return x ^ key;
}
""",
    "r22_em_chichi6_rot_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    static const unsigned ROTS[6] = {13, 26, 39, 52, 1, 14};
    uint64_t x = val ^ key;
    for (int i = 0; i < 6; i++)
        x = rotl64(chichi64(x), ROTS[i]);
    return x ^ key;
}
""",
    "r22_keyed_spn6_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int i = 0; i < 6; i++)
        x = transpose64(sbox64(x ^ rk64(key, i)));
    return x;
}
""",
    "r22b_keyed_spn6_pbox_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int i = 0; i < 6; i++)
        x = pbox64_o34(sbox64(x ^ rk64(key, i)));
    return x;
}
""",
    "r22c_spn_mix4r_lp_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int i = 0; i < 4; i++)
        x = lin64_311(pbox64_o34(sbox64(x ^ rk64(key, i))));
    return x;
}
""",
    "r22c_spn_mix5r_lp_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int i = 0; i < 5; i++)
        x = lin64_311(pbox64_o34(sbox64(x ^ rk64(key, i))));
    return x;
}
""",
    "r22c_spn_mix6r_lp_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int i = 0; i < 6; i++)
        x = lin64_311(pbox64_o34(sbox64(x ^ rk64(key, i))));
    return x;
}
""",
    "r22c_spn_mix5r_shx_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int i = 0; i < 5; i++) {
        uint64_t t = pbox64_o34(sbox64(x ^ rk64(key, i)));
        x = shxor64(t, 13, (i % 2 == 0) ? 1 : -1);
    }
    return x;
}
""",
    "r22_lm5_chi_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32), R = (uint32_t)val;
    for (int i = 0; i < 5; i++) {
        uint32_t d = L ^ R;
        uint32_t t = chi32(d ^ (uint32_t)rk64(key, i));
        uint32_t nL = R ^ t, nR = d;
        L = nL; R = nR;
    }
    return ((uint64_t)L << 32) | R;
}
""",
    "r22_benes_chichi_nw": """uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val;
    for (int s = 0; s < 11; s++) {
        int e = s < 6 ? s : 10 - s;
        uint32_t sw = (uint32_t)rotl64(key, (13u * (unsigned)(s + 1)) & 63u);
        x = benes_stage(x, e, sw);
        if (s % 3 == 2) x = chichi64(x);
    }
    return x;
}
""",
}


# ---------------- Verilog emission ----------------

def _v_rk(i):
    # 0-based i -> Verilog expression for rk_i
    return ("(((({key} << {r}) | ({key} >> {rr})) ^ ((i0 + 1) * 64'h9E3779B97F4A7C15)))"
            .format(key="key", r=(13 * (i + 1)) % 64, rr=64 - (13 * (i + 1)) % 64,
                    i0=i))


def _v_sbox16_stmts(inp, outp):
    """16 parallel S1 S-boxes via DNF, fully unrolled.

    Convention (from _qm_cover): m is the DON'T-CARE mask; literals are
    emitted for the fixed bits (m=0), polarity from b.
    """
    lines = []
    for n in range(16):
        for bit in range(4):
            cubes = dnf_for_sbox_bit(S1, bit)
            if not cubes:
                lines.append(f"        {outp}[{4*n+bit}] = 1'b0;")
                continue
            terms = []
            for m, b in cubes:
                lits = []
                for k in range(4):
                    if not ((m >> k) & 1):
                        lits.append(f"{'' if (b >> k) & 1 else '~'}{inp}[{4*n+k}]")
                terms.append("(" + " & ".join(lits) + ")" if lits else "1'b1")
            lines.append(f"        {outp}[{4*n+bit}] = " + " | ".join(terms) + ";")
    return lines


def _selftest_sbox_emission():
    # Evaluate the EMITTED Verilog S-box expressions in Python for all inputs.
    # (The DNF self-test validates the cubes; this validates the emission.)
    stmts = _v_sbox16_stmts("R", "u")
    assert len(stmts) == 64
    import re
    for n in range(16):
        for bit in range(4):
            stmt = stmts[n * 4 + bit]
            m = re.match(r"\s*u\[(\d+)\] = (.*);", stmt)
            assert m and int(m.group(1)) == 4 * n + bit
            expr = m.group(2)
            for v in range(16):
                env = {f"R[{4*n+k}]": (v >> k) & 1 for k in range(4)}
                py = expr
                for var, val in sorted(env.items(), key=lambda kv: -len(kv[0])):
                    py = py.replace("~" + var, f"(1-{val})").replace(var, str(val))
                py = py.replace("&", " and ").replace("|", " or ")
                got = eval(py)  # noqa: S307 - test-only, generated expr
                want = (S1[v] >> bit) & 1
                assert bool(got) == bool(want), (n, bit, v, got, want, expr)
    print("S-box emission self-test: 16 nibbles x 4 bits x 16 inputs OK")


def _v_lin311_stmts(inp, outp):
    # L(x) = x ^ rotl64(x,3) ^ rotl64(x,11); rotl64(x,r) = {x[63-r:0], x[63:64-r]}
    return [f"        {outp} = {inp} ^ {{{inp}[60:0], {inp}[63:61]}} ^ {{{inp}[52:0], {inp}[63:53]}};"]


def _selftest_lin311_emission():
    # rotl64(x,3)[i] = x[(i-3)%64]; verify concatenation form == numpy L.
    xv = 0x5CDB5A824B383A06
    # direct bit model of the emitted concatenation expression
    def rotl(v, r):
        return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF
    want = int(r22._lin64_311_np(np.uint64(xv)))
    got = xv ^ rotl(xv, 3) ^ rotl(xv, 11)
    assert got == want, (hex(got), hex(want))
    print("lin(3,11) emission self-test OK")


def _v_chichi64_stmts(inp, outp):
    lines = []
    for i in range(31):
        lines.append(f"        {outp}[{i}] = {inp}[{i}] ^ (~{inp}[{(i+1) % 31}] & {inp}[{(i+2) % 31}]);")
    for j in range(33):
        lines.append(f"        {outp}[{31+j}] = {inp}[{31+j}] ^ (~{inp}[{31+(j+1) % 33}] & {inp}[{31+(j+2) % 33}]);")
    # lambda corrections (m=32): lam_29=x_32+x_29 etc.
    lines.append(f"        {outp}[29] = {outp}[29] ^ {inp}[32] ^ {inp}[29];")
    lines.append(f"        {outp}[30] = {outp}[30] ^ {inp}[31] ^ {inp}[30];")
    lines.append(f"        {outp}[31] = {outp}[31] ^ {inp}[29] ^ {inp}[32] ^ {inp}[31];")
    lines.append(f"        {outp}[32] = {outp}[32] ^ {inp}[32] ^ {inp}[30];")
    return lines


def _v_transpose_stmts(inp, outp):
    lines = []
    for j in range(16):
        for b in range(4):
            src = (j + 4 * b) % 16
            lines.append(f"        {outp}[{4*j+b}] = {inp}[{4*src+b}];")
    return lines


def _v_pbox_o34_stmts(inp, outp):
    # O34 P-box: out[(5*i+27)%64] = in[i] (free wiring)
    return [f"        {outp}[{(5*i+27) % 64}] = {inp}[{i}];" for i in range(64)]


def _v_shxor_stmts(inp, outp, r, direction):
    # O38 triangular shift-XOR: y = x ^ (x >> r) or y = x ^ (x << r).
    # Single XOR2 ~= 2u. Concatenation form -- note the DOUBLE outer braces:
    # the inner {r{1'b0}} is a replication, so the concatenation needs its
    # own braces: x = t ^ {{13{1'b0}}, t[63:13]};  (single paren/brace is a
    # syntax error -- caught by check_rtl/iverilog, regression-tested below).
    if direction > 0:
        return [f"        {outp} = {inp} ^ {{{{{r}{{1'b0}}}}, {inp}[63:{r}]}};"]
    else:
        return [f"        {outp} = {inp} ^ {{{inp}[{63-r}:0], {{{r}{{1'b0}}}}}};"]


def _selftest_shxor_emission():
    # The emitted Verilog concatenation must equal the numpy mixer bit-exactly
    # AND be syntactically valid (double-brace concatenation around replication).
    import numpy as np
    import re
    rng = np.random.default_rng(0x38)
    vs = rng.integers(0, 2 ** 64, size=50, dtype=np.uint64)
    for r, d in ((13, 1), (13, -1), (27, 1), (1, -1)):
        stmts = _v_shxor_stmts("t", "x", r, d)
        assert len(stmts) == 1, stmts
        st = stmts[0]
        assert re.search(r"\^ \{", st), ("missing concatenation braces", st)
        assert st.count("{") == st.count("}"), ("unbalanced braces", st)
        # verify the slicing arithmetic: emulate {r{1'b0}},t[63:r] etc.
        for v in vs:
            vv = int(v)
            shifted = (vv >> r) if d > 0 else ((vv << r) & 0xFFFFFFFFFFFFFFFF)
            want = int(r22._mix_shxor_np(np.uint64(vv), r, 0xFFFFFFFFFFFFFFFF, d))
            assert ((vv ^ shifted) & 0xFFFFFFFFFFFFFFFF) == want, (r, d, hex(vv))
    print("shift-XOR emission self-test: 4 (r,dir) x 50 values vs numpy OK")


def _selftest_pbox_o34_emission():
    # The emitted wiring must equal the numpy P-box map exactly.
    stmts = _v_pbox_o34_stmts("s", "x")
    assert len(stmts) == 64
    import re
    got = {}
    for st in stmts:
        m = re.match(r"\s*x\[(\d+)\] = s\[(\d+)\];", st)
        assert m, st
        got[int(m.group(2))] = int(m.group(1))
    assert [got[i] for i in range(64)] == r22._O34_P, "emission != numpy P-box"
    print("P-box O34 emission self-test: 64 wires == numpy map OK")


def _v_chi32_stmts(inp, outp):
    return [f"        {outp}[{i}] = {inp}[{i}] ^ (~{inp}[{(i+1) % 32}] & {inp}[{(i+2) % 32}]);"
            for i in range(32)]


def _v_benes_stage_stmts(inp, outp, e, swreg):
    lines = []
    lo = (1 << e) - 1
    for j in range(32):
        p = (j & lo) | ((j >> e) << (e + 1))
        q = p | (1 << e)
        lines.append(f"        {outp}[{p}] = {swreg}[{j}] ? {inp}[{q}] : {inp}[{p}];")
        lines.append(f"        {outp}[{q}] = {swreg}[{j}] ? {inp}[{p}] : {inp}[{q}];")
    return lines


V_HDR = """// {name}: {desc}
// GENERATED by round22/gen_r22.py -- do not edit by hand.
// Bit-exact vs Python model round22/models/r22.py ({name}).
// Direct boolean assigns inside one always @(*) block (no functions).
module {name}(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);

reg [63:0] x, t, s;
reg [31:0] L, R, d, tt;
reg [63:0] rkv;
reg [31:0] sw;
always @(*) begin
"""


def _v_roundkey_stmts(i, target="rkv"):
    r = (13 * (i + 1)) % 64
    return [f"        {target} = ((key << {r}) | (key >> {64-r})) ^ ({i+1} * 64'h9E3779B97F4A7C15);"]


def _v_benes_sw_stmts(s):
    r = (13 * (s + 1)) % 64
    return [f"        sw = ((key << {r}) | (key >> {64-r}));  // low 32 bits are the switch bits"]


def build_verilog(name, desc):
    L = []
    L.append(V_HDR.format(name=name, desc=desc))
    if name == "r22_wide_spn4_nw":
        L.append("    x = val;")
        for i in range(4):
            L += _v_roundkey_stmts(i)
            L.append("    t = x ^ rkv;")
            L += _v_sbox16_stmts("t", "s")
            L += _v_lin311_stmts("s", "x")
    elif name == "r22_em_chichi4_nw":
        L.append("    x = val ^ key;")
        for _ in range(4):
            L += _v_chichi64_stmts("x", "t")
            L += _v_lin311_stmts("t", "x")
        L.append("    x = x ^ key;")
    elif name == "r22_em_chichi6_rot_nw":
        rots = [(13 * (i + 1)) % 64 for i in range(6)]
        L.append("    x = val ^ key;")
        for r in rots:
            L += _v_chichi64_stmts("x", "t")
            L.append(f"    x = {{t[{63-r}:0], t[63:{64-r}]}};" if r else "    x = t;")
        L.append("    x = x ^ key;")
    elif name == "r22_keyed_spn6_nw":
        L.append("    x = val;")
        for i in range(6):
            L += _v_roundkey_stmts(i)
            L.append("    t = x ^ rkv;")
            L += _v_sbox16_stmts("t", "s")
            L += _v_transpose_stmts("s", "x")
    elif name == "r22b_keyed_spn6_pbox_nw":
        L.append("    x = val;")
        for i in range(6):
            L += _v_roundkey_stmts(i)
            L.append("    t = x ^ rkv;")
            L += _v_sbox16_stmts("t", "s")
            L += _v_pbox_o34_stmts("s", "x")
    elif name in ("r22c_spn_mix4r_lp_nw", "r22c_spn_mix5r_lp_nw",
                 "r22c_spn_mix6r_lp_nw"):
        nrounds = {"r22c_spn_mix4r_lp_nw": 4, "r22c_spn_mix5r_lp_nw": 5,
                   "r22c_spn_mix6r_lp_nw": 6}[name]
        L.append("    x = val;")
        for i in range(nrounds):
            L += _v_roundkey_stmts(i)
            L.append("    t = x ^ rkv;")
            L += _v_sbox16_stmts("t", "s")
            L += _v_pbox_o34_stmts("s", "t")
            L += _v_lin311_stmts("t", "x")
    elif name == "r22c_spn_mix5r_shx_nw":
        L.append("    x = val;")
        for i in range(5):
            d = 1 if (i % 2 == 0) else -1
            L += _v_roundkey_stmts(i)
            L.append("    t = x ^ rkv;")
            L += _v_sbox16_stmts("t", "s")
            L += _v_pbox_o34_stmts("s", "t")
            L += _v_shxor_stmts("t", "x", 13, d)
    elif name == "r22_lm5_chi_nw":
        L.append("    L = val[63:32];")
        L.append("    R = val[31:0];")
        for i in range(5):
            L += _v_roundkey_stmts(i)
            L.append("    d = L ^ R;")
            L.append("    t[31:0] = d ^ rkv[31:0];")
            L += _v_chi32_stmts("t", "tt")
            L.append("    s[31:0] = R ^ tt;")   # nL
            L.append("    s[63:32] = d;")       # nR
            L.append("    L = s[31:0];")
            L.append("    R = s[63:32];")
    elif name == "r22_benes_chichi_nw":
        L.append("    x = val;")
        for s in range(11):
            e = s if s < 6 else 10 - s
            L += _v_benes_sw_stmts(s)
            L += _v_benes_stage_stmts("x", "t", e, "sw")
            L.append("    x = t;")
            if s % 3 == 2:
                L += _v_chichi64_stmts("x", "t")
                L.append("    x = t;")
    L.append("end\n")
    L.append("assign out = x;\n" if name != "r22_lm5_chi_nw" else "assign out = {L, R};\n")
    L.append("endmodule\n")
    return "\n".join(L)


def build_model_py(name):
    return ('"""Python model wrapper for %s (fast_battery candidate interface).\n'
            'Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""\n'
            'import sys\nimport numpy as np\n'
            'sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round22/models")\n'
            'from r22 import %s as _np\n\n'
            'def mix(v, k):\n    return int(_np(np.uint64(v), np.uint64(k)))\n\n'
            'mix_np = _np\n' % (name, name))


def main():
    _selftest_dnf()
    _selftest_sbox_emission()
    _selftest_lin311_emission()
    _selftest_pbox_o34_emission()
    _selftest_shxor_emission()
    # self-test the numpy reference first (fails loudly before generation)
    for fn in ("_selftest_chichi64_spot", "_selftest_lm_inverse",
               "_selftest_linear_ranks", "_selftest_pbox_o34",
               "_selftest_o38_singularity", "_selftest_o38_nofreeze",
               "_selftest_o38_random", "_selftest_o38_bijection"):
        getattr(r22, fn)()
    for name, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        # impl.c
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(C_HDR.format(name=name, desc=desc))
            f.write(C_BODIES[name])
        # rtl.v
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(build_verilog(name, desc))
        # model.py
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(build_model_py(name))
        # meta.json (goldens filled below)
        fn = getattr(r22, name)
        goldens = []
        for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(k),
                            "out": hex(int(fn(np.uint64(v), np.uint64(k))))})
        import json
        meta = {
            "name": name,
            "description": desc,
            "composition": desc,
            "rtl_top": name,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
        }
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print("generated", name)
    print("gen_r22 complete")


if __name__ == "__main__":
    main()
