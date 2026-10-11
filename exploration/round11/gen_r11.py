#!/usr/bin/env python3
"""Round 11 candidate generator: emits impl.c, rtl.v, model.py, meta.json for
each spec in SPECS. The numpy model (round11/models/r11.py) is the reference;
bit-exactness of the generated C/RTL is verified by xcheck + check_rtl.

Template (fixed): 6r Feistel, F = S-box layer -> x^rotl32(x,a)^rotl32(x,b) ->
^rk32, NO whitening, affine key schedule.

RTL S-box policy (round-11 brief): DIRECT BOOLEAN ASSIGNS, no Verilog
functions (analyze2.py's parser breaks on function-inlined wire names), and
all round logic as blocking assignments inside ONE always @(*) block (round-8
lesson: no module-level assign may read an always-block-driven reg).
4-bit S-boxes are emitted as Quine-McCluskey-minimized DNF per output bit
(self-tested exhaustively against the table at generation time).
The 8-bit S-box uses a case statement inside the always block (DNF would be
~128 product terms per bit); a SKINNY-8 compact boolean circuit is used if
sboxes.json provides one.

Usage: python3 round11/gen_r11.py   (writes fast_battery/candidates/r11_*/)
       reads round11/sboxes.json (verified S-box tables)
"""
import json
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R11 = os.path.join(EXP, "round11")
sys.path.insert(0, os.path.join(R11, "models"))
import numpy as np  # noqa: E402
import r11  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")

with open(os.path.join(R11, "sboxes.json")) as f:
    SB = json.load(f)

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]
SBOX4 = {"s1": S1, "present4": SB["present4"], "gift4": SB["gift4"],
         "skinny4": SB["skinny4"], "piccolo4": SB["piccolo4"]}
SBOX8 = {"skinny8": SB["skinny8"]}

# (name, kind, sbox, a, b, desc)
# kind: "s4" | "s8" | "s4mix"(even=s1, odd=present4)
SPECS = [
    ("r11_feist6_present311_nw", "s4", "present4", 3, 11,
     "6r Feistel, F=PRESENT-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_present713_nw", "s4", "present4", 7, 13,
     "6r Feistel, F=PRESENT-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_gift311_nw", "s4", "gift4", 3, 11,
     "6r Feistel, F=GIFT-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_gift713_nw", "s4", "gift4", 7, 13,
     "6r Feistel, F=GIFT-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_sk4311_nw", "s4", "skinny4", 3, 11,
     "6r Feistel, F=SKINNY4-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_sk4713_nw", "s4", "skinny4", 7, 13,
     "6r Feistel, F=SKINNY4-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_piccolo311_nw", "s4", "piccolo4", 3, 11,
     "6r Feistel, F=Piccolo-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_piccolo713_nw", "s4", "piccolo4", 7, 13,
     "6r Feistel, F=Piccolo-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_sk8311_nw", "s8", "skinny8", 3, 11,
     "6r Feistel, F=4xSKINNY8-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_s1mix311_nw", "s4mix", ("s1", "present4"), 3, 11,
     "6r Feistel, F=alternating S1/PRESENT per nibble+lin(3,11), NO whitening"),
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


def dnf_for_bit(sbox, bit):
    """Minimized DNF cubes [(mask, bits)] for output bit `bit` of 4-bit sbox."""
    mt = [v for v in range(16) if (sbox[v] >> bit) & 1]
    if not mt:
        return []
    if len(mt) == 16:
        return [(0xF, 0)]
    return _qm_cover(mt, _qm_primes(mt))


def _selftest_dnf():
    for name, sb in SBOX4.items():
        for bit in range(4):
            cubes = dnf_for_bit(sb, bit)
            for v in range(16):
                got = 0
                for m, b in cubes:
                    if (v & ~m) == (b & ~m):
                        got = 1
                        break
                want = (sb[v] >> bit) & 1
                assert got == want, (name, bit, v, got, want)
    print("DNF self-test: all S-boxes x 4 bits x 16 inputs OK")


def _cube_verilog(mask, bits, base):
    """One product term over R[base+0..3]; mask=don't-care positions."""
    lits = []
    for k in range(4):
        if (mask >> k) & 1:
            continue
        lits.append(f"R[{base + k}]" if (bits >> k) & 1 else f"~R[{base + k}]")
    if not lits:
        return "1'b1"
    return "(" + " & ".join(lits) + ")"


def sbox_dnf_assigns(sbox, base):
    """32 Verilog blocking assigns t[base..base+31] = DNF(R[base..])."""
    lines = []
    for j in range(8):
        b = base + 4 * j
        for bit in range(4):
            cubes = dnf_for_bit(sbox, bit)
            if not cubes:
                expr = "1'b0"
            else:
                expr = " | ".join(_cube_verilog(m, cb, b) for m, cb in cubes)
            lines.append(f"            t[{b + bit}] = {expr};")
    return "\n".join(lines)


# ---------------- C ----------------
C_HDR = """/* {name}: {desc}
 * GENERATED by round11/gen_r11.py -- do not edit by hand.
 * Bit-exact vs Python model round11/models/r11.py ({pyfn}). */
#include <stdint.h>

{sbox_c}

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

static uint32_t lin_ab(uint32_t x) {{
    return x ^ rotl32(x, {a}) ^ rotl32(x, {b});
}}

static uint32_t F_f(uint32_t R, uint32_t rk32) {{
    uint32_t t = sbox_layer32(R);
    t = lin_ab(t);
    return t ^ rk32;
}}

uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint32_t L = (uint32_t)(val >> 32);
    uint32_t R = (uint32_t)val;
    for (int i = 1; i <= 6; i++) {{
        uint32_t F = F_f(R, RK32(key, i));
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }}
    return ((uint64_t)R << 32) | L;
}}
"""

C_SBOX4 = "static const uint8_t SBOX[16] = {{{}}};".format
C_SBOX8 = "static const uint8_t SBOX8[256] = {{{}}};".format

C_LAYER4 = """
static uint32_t sbox_layer32(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)SBOX[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}"""

C_LAYER4MIX = """
static const uint8_t SBOX_E[16] = {%s};
static const uint8_t SBOX_O[16] = {%s};
static uint32_t sbox_layer32(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)((i & 1) ? SBOX_O[(x >> (4*i)) & 0xF]
                                : SBOX_E[(x >> (4*i)) & 0xF]) << (4*i);
    return r;
}"""

C_LAYER8 = """
static uint32_t sbox_layer32(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 4; i++)
        r |= (uint32_t)SBOX8[(x >> (8*i)) & 0xFF] << (8*i);
    return r;
}"""


def gen_impl(name, kind, sbox, a, b, desc):
    if kind == "s4":
        sbox_c = C_SBOX4(",".join(str(v) for v in SBOX4[sbox]))
        layer_c = C_LAYER4
    elif kind == "s4mix":
        se, so = sbox
        sbox_c = ""
        layer_c = C_LAYER4MIX % (",".join(str(v) for v in SBOX4[se]),
                                 ",".join(str(v) for v in SBOX4[so]))
    elif kind == "s8":
        sbox_c = C_SBOX8(",".join(str(v) for v in SBOX8[sbox]))
        layer_c = C_LAYER8
    else:
        raise ValueError(kind)
    return C_HDR.format(name=name, desc=desc, pyfn=name, a=a, b=b,
                        sbox_c=sbox_c, sbox_layer_c=layer_c)


# ---------------- Verilog ----------------
V_HDR = """// {name}: {desc}
// GENERATED by round11/gen_r11.py -- do not edit by hand.
// Bit-exact vs Python model round11/models/r11.py ({pyfn}).
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
    for (i = 0; i < 6; i = i + 1) begin
        // ---- S-box layer: R -> t (direct boolean assigns) ----
{sbox_assigns}
// ---- lin({a},{b}): t ^= rotl32(t,{a}) ^ rotl32(t,{b}) ----
        t = t ^ {{t[{rahi}:0], t[31:{ralo}]}} ^ {{t[{rbhi}:0], t[31:{rblo}]}};
// ---- round key: low32(rotl64(key,13*(i+1)) ^ (i+1)*GOLDEN64) ----
        // NOTE: loop i is 0-based; C/Python call RK32(key, i) with 1-based i,
        // so here we use (i+2) to match round (i+1)'s 13*(i+2)/((i+2)*GOLDEN).
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


def gen_rtl_s4(name, sbox_key, a, b, desc):
    assigns = sbox_dnf_assigns(SBOX4[sbox_key], 0)
    rahi, ralo = _rot_parts(a)
    rbhi, rblo = _rot_parts(b)
    body = V_MAIN_TMPL.format(sbox_assigns=assigns, a=a, b=b,
                              rahi=rahi, ralo=ralo, rbhi=rbhi, rblo=rblo)
    return (V_HDR.format(name=name, desc=desc, pyfn=name) + V_DECL + body)


def gen_rtl_s4mix(name, sbox_pair, a, b, desc):
    se, so = sbox_pair
    parts = []
    for j in range(8):
        sb = SBOX4[se] if j % 2 == 0 else SBOX4[so]
        parts.append(sbox_dnf_assigns(sb, 4 * j))
    assigns = "\n".join(parts)
    rahi, ralo = _rot_parts(a)
    rbhi, rblo = _rot_parts(b)
    body = V_MAIN_TMPL.format(sbox_assigns=assigns, a=a, b=b,
                              rahi=rahi, ralo=ralo, rbhi=rbhi, rblo=rblo)
    return (V_HDR.format(name=name, desc=desc, pyfn=name) + V_DECL + body)


def gen_rtl_s8(name, sbox8_key, a, b, desc):
    sb8 = SBOX8[sbox8_key]
    cases = []
    for j in range(4):
        cl = [f"            case (R[{8*j+7}:{8*j}])"]
        for v in range(256):
            cl.append(f"                8'h{v:02X}: t[{8*j+7}:{8*j}] = 8'h{sb8[v]:02X};")
        cl.append("            endcase")
        cases.append("\n".join(cl))
    assigns = "\n".join(cases)
    rahi, ralo = _rot_parts(a)
    rbhi, rblo = _rot_parts(b)
    body = V_MAIN_TMPL.format(sbox_assigns=assigns, a=a, b=b,
                              rahi=rahi, ralo=ralo, rbhi=rbhi, rblo=rblo)
    return (V_HDR.format(name=name, desc=desc, pyfn=name) + V_DECL + body)


def gen_rtl(name, kind, sbox, a, b, desc):
    if kind == "s4":
        return gen_rtl_s4(name, sbox, a, b, desc)
    if kind == "s4mix":
        return gen_rtl_s4mix(name, sbox, a, b, desc)
    if kind == "s8":
        return gen_rtl_s8(name, sbox, a, b, desc)
    raise ValueError(kind)


MODEL_WRAPPER = '''"""Python model wrapper for {name} (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round11/models")
from r11 import {pyfn} as _np


def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
'''


def main():
    _selftest_dnf()
    r11fns = {n: fn for n, fn, _ in r11.CANDIDATES_R11}
    for name, kind, sbox, a, b, desc in SPECS:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "impl.c"), "w").write(
            gen_impl(name, kind, sbox, a, b, desc))
        open(os.path.join(d, "rtl.v"), "w").write(
            gen_rtl(name, kind, sbox, a, b, desc))
        open(os.path.join(d, "model.py"), "w").write(
            MODEL_WRAPPER.format(name=name, pyfn=name))
        fn = r11fns[name]
        g1 = int(fn(np.uint64(0), np.uint64(0x123456789ABCDEF0)))
        g2 = int(fn(np.uint64(0), np.uint64(0)))
        meta = {
            "name": name,
            "description": desc,
            "composition": desc,
            "rtl_top": name,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": [
                {"val": "0x0", "key": "0x123456789abcdef0",
                 "out": "0x%016x" % g1},
                {"val": "0x0", "key": "0x0", "out": "0x%016x" % g2},
            ],
        }
        open(os.path.join(d, "meta.json"), "w").write(json.dumps(meta, indent=1))
        print(f"generated {name}")


if __name__ == "__main__":
    main()
