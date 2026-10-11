"""Generator for Batch A (SPN family) models + RTL. Run once; emits
exploration/models/<name>.py and exploration/rtl/<name>.v.

S-box tables (verified 2026-10-01, see task notes):
  PRESENT: trusted per brief (also screen_lib.present_sbox_table()).
  GIFT:    eprint 2017/622 (Banik et al., CHES 2017) Table 3 + HAL thesis.
  SKINNY:  SKINNY spec / ISO/IEC 18033-7:2022 Table 6 / ToSC -- NOTE: the
           brief's table (C 6 9 0 1 A 7 B 3 E F 8 D 4 5 2) is NOT the published
           SKINNY-64 S4; the published table (C 6 9 0 1 A 2 B 3 8 5 D 4 E 7 F)
           is used here. Discrepancy flagged in report.
  AES:     FIPS-197 forward S-box (Wikipedia Rijndael S-box + corroboration).
We borrow TABLES applied to contiguous nibbles/bytes only, NOT the full
ciphers; published security bounds do not transfer.
"""
import os

EXP = "/home/hatch/workspace/mix/exploration"
M64 = (1 << 64) - 1
GOLDEN = 0x9E3779B97F4A7C15

PRESENT = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
           0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
GIFT = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9,
        0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]
SKINNY = [0xC, 0x6, 0x9, 0x0, 0x1, 0xA, 0x2, 0xB,
          0x3, 0x8, 0x5, 0xD, 0x4, 0xE, 0x7, 0xF]
AES = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]

# transcription anchors (spot transcription errors, not a substitute for the
# model asserts)
assert len(set(PRESENT)) == 16 and PRESENT[0] == 0xC and PRESENT[1] == 0x5
assert len(set(GIFT)) == 16 and GIFT[0] == 0x1 and GIFT[1] == 0xA
assert len(set(SKINNY)) == 16 and SKINNY[0] == 0xC and SKINNY[6] == 0x2
assert len(AES) == 256 and len(set(AES)) == 256
assert AES[0x00] == 0x63 and AES[0x19] == 0xD4 and AES[0xFF] == 0x16

SBOX4 = {"present": PRESENT, "gift": GIFT, "skinny": SKINNY}


def rc(i):
    return ((i + 1) * GOLDEN) & M64


def rotl_expr(sig, r):
    r %= 64
    if r == 0:
        return sig
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63 - r, sig, 64 - r)


def p_layer_concat(sig):
    # PRESENT pLayer P(b) = 16*b mod 63 (b<63), P(63)=63; out[o] = in[inv[o]]
    P = [(16 * b) % 63 for b in range(63)] + [63]
    inv = [0] * 64
    for b, o in enumerate(P):
        inv[o] = b
    return "{%s}" % ", ".join("%s[%d]" % (sig, inv[o]) for o in range(63, -1, -1))


def hx(v, w):
    return "%d'h%0*x" % (w, w // 4, v)


# ---------------------------------------------------------------- models

MODEL_SPN = '''"""{name}: {rounds}-round SPN, {sboxname} 4-bit S-box + PRESENT pLayer.

x = val ^ key
rk[i] = {ksdesc}
round: x = pLayer(SBOX16(x ^ rk[i]))
out = x ^ rk[{rounds}]

Bijectivity (fixed key): xor round key (bijection), 16x bijective 4-bit
S-box (16 distinct outputs asserted), PRESENT pLayer bit-permutation
(bijection), final xor whitening (bijection); composition of bijections =>
permutation of 2^64. The S-box TABLE is borrowed only, applied to contiguous
nibbles -- NOT the full cipher; published security bounds do not transfer.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, rotl64_np, sbox16_np, present_perm_np,
                        check_model_equiv, bijectivity_spotcheck)

M64 = (1 << 64) - 1
_SBOX = [{sboxlist}]
assert len(set(_SBOX)) == 16, "S-box table must be a permutation"
_SBOX_NP = np.array(_SBOX, dtype=np.uint64)
_ROUNDS = {rounds}


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return {rknp} ^ _rc(i)


def _rotl64_scalar(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_scalar(key, i):
    return {rksc} ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)


def mix_{name}_scalar(val, key):
    val &= M64
    key &= M64
    P = [(16 * b) % 63 for b in range(63)] + [63]
    x = val ^ key
    for i in range(_ROUNDS):
        x ^= _rk_scalar(key, i)
        y = 0
        for s in range(16):
            y |= _SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
        z = 0
        for b in range(64):
            if (y >> b) & 1:
                z |= 1 << P[b]
        x = z
    return (x ^ _rk_scalar(key, _ROUNDS)) & M64


def mix_{name}_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(_ROUNDS):
        x = present_perm_np(sbox16_np(x ^ _rk_np(k, i), _SBOX_NP))
    return x ^ _rk_np(k, _ROUNDS)


if __name__ == "__main__":
    check_model_equiv(mix_{name}_scalar, mix_{name}_np, "{name}")
    bijectivity_spotcheck(mix_{name}_np, "{name}")
'''

MODEL_AES8 = '''"""spn2_aes8: 2 rounds of (xor rk, 8x AES 8-bit S-box, bijective 3-term
xor-linear layer L), plus whitening.

x = val ^ key
rk[i] = ROTL64(key, 13*(i+1)) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15
round: x ^= rk[i]; x = AES8(x); x = L(x),  L(x) = x ^ ROTL64(x,13) ^ ROTL64(x,41)
out = x ^ rk[2]

NOTE on the task's "x^=L(x)" notation: with the 3-term L as defined, x^L(x)
algebraically collapses to the NON-bijective 2-term ROTL(x,13)^ROTL(x,41)
(the x cancels; kernel = rotation-by-28-invariant words, 16 elements, 16-to-1).
The brief (which governs) allows only proven-bijective blocks, so the round's
linear step is the proven bijective 3-term map L applied to the state --
the same function under every bijective reading of the spec. One-line proof:
over GF(2), L <-> 1+x^13+x^41; (1+x^13+x^41)(1)=1 != 0 so x+1 does not divide
it, and x^64+1 = (x+1)^64 has no other factor ==> L is a permutation of 2^64.

Bijectivity (fixed key): xor rk (bij) + 8x bijective AES S-box (256 distinct
outputs asserted; FIPS-197 table) + bijective L (proven above) + final xor
whitening (bij); composition of bijections => permutation of 2^64. Only the
AES S-box TABLE is borrowed (applied to contiguous bytes), not the AES round
structure; AES security bounds do not transfer.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, rotl64_np, check_model_equiv, bijectivity_spotcheck)

M64 = (1 << 64) - 1
_AES = [{aeslist}]
assert len(_AES) == 256 and len(set(_AES)) == 256, "AES S-box must be a permutation"
_AES_NP = np.array(_AES, dtype=np.uint64)
_ROUNDS = 2


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _rotl64_scalar(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_scalar(key, i):
    return _rotl64_scalar(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _aes8_scalar(x):
    y = 0
    for b in range(8):
        y |= _AES[(x >> (8 * b)) & 0xFF] << (8 * b)
    return y


def _L64_scalar(x):
    return (x ^ _rotl64_scalar(x, 13) ^ _rotl64_scalar(x, 41)) & M64


def mix_spn2_aes8_scalar(val, key):
    val &= M64
    key &= M64
    x = val ^ key
    for i in range(_ROUNDS):
        x = _L64_scalar(_aes8_scalar(x ^ _rk_scalar(key, i)))
    return (x ^ _rk_scalar(key, _ROUNDS)) & M64


def _aes8_np(x):
    shp = np.shape(x)
    xf = np.asarray(x, dtype=np.uint64).reshape(-1)
    y = np.zeros_like(xf)
    for b in range(8):
        y |= _AES_NP[((xf >> U64(8 * b)) & U64(0xFF)).astype(np.int64)] << U64(8 * b)
    return y.reshape(shp)


def _L64_np(x):
    return x ^ rotl64_np(x, U64(13)) ^ rotl64_np(x, U64(41))


def mix_spn2_aes8_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(_ROUNDS):
        x = _L64_np(_aes8_np(x ^ _rk_np(k, i)))
    return x ^ _rk_np(k, _ROUNDS)


if __name__ == "__main__":
    check_model_equiv(mix_spn2_aes8_scalar, mix_spn2_aes8_np, "spn2_aes8")
    bijectivity_spotcheck(mix_spn2_aes8_np, "spn2_aes8")
'''

MODEL_XORLIN = '''"""spn4_xorlin: 4 rounds of (xor rk, 16x PRESENT 4-bit S-box, bijective
3-term xor-linear layer L), plus whitening.

x = val ^ key
rk[i] = ROTL64(key, 13*(i+1)) ^ RC[i], RC[i] = (i+1)*0x9E3779B97F4A7C15
round: x ^= rk[i]; x = PRESENT16(x); x = L(x),
       L(x) = x ^ ROTL64(x,13) ^ ROTL64(x,41)
out = x ^ rk[4]

Same notation note as spn2_aes8: the task's "x^=L(x)" with the 3-term L would
collapse to the non-bijective 2-term ROTL(x,13)^ROTL(x,41); the brief governs,
so the round's linear step is the proven bijective 3-term map L applied to
the state. Proof: over GF(2), L <-> 1+x^13+x^41; (1+x^13+x^41)(1)=1 != 0 so
x+1 does not divide it, and x^64+1=(x+1)^64 has no other factor ==> bijection.

Bijectivity (fixed key): xor rk (bij) + 16x bijective PRESENT S-box (16
distinct asserted) + bijective L (proven above) + final xor whitening (bij);
composition of bijections => permutation of 2^64. Only the PRESENT S-box
TABLE is borrowed (contiguous nibbles), not the cipher.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, rotl64_np, sbox16_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
_SBOX = [{sboxlist}]
assert len(set(_SBOX)) == 16, "S-box table must be a permutation"
_SBOX_NP = np.array(_SBOX, dtype=np.uint64)
_ROUNDS = 4


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _rotl64_scalar(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_scalar(key, i):
    return _rotl64_scalar(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)


def mix_spn4_xorlin_scalar(val, key):
    val &= M64
    key &= M64
    x = val ^ key
    for i in range(_ROUNDS):
        x ^= _rk_scalar(key, i)
        y = 0
        for s in range(16):
            y |= _SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
        x = (y ^ _rotl64_scalar(y, 13) ^ _rotl64_scalar(y, 41)) & M64
    return (x ^ _rk_scalar(key, _ROUNDS)) & M64


def _L64_np(x):
    return x ^ rotl64_np(x, U64(13)) ^ rotl64_np(x, U64(41))


def mix_spn4_xorlin_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(_ROUNDS):
        x = _L64_np(sbox16_np(x ^ _rk_np(k, i), _SBOX_NP))
    return x ^ _rk_np(k, _ROUNDS)


if __name__ == "__main__":
    check_model_equiv(mix_spn4_xorlin_scalar, mix_spn4_xorlin_np, "spn4_xorlin")
    bijectivity_spotcheck(mix_spn4_xorlin_np, "spn4_xorlin")
'''

# ---------------------------------------------------------------- RTL

RTL_HEAD = """// {name}: {desc}
// S-box inline as assign-based SOP (minterm expansion from the verified table;
// ABC minimizes). NOTE: function+case infers $rom cells which this flow
// (yosys -> abc -fast) cannot map, and a separate S-box module leaves
// hierarchical net names (\\u_r0n15.y) in dead concat assigns that the
// analyzer cannot parse; inline SOP keeps every net name a plain identifier,
// mirroring the proven mix_spn12.v baseline (QM-minimized SOP) structurally.
module {name}(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
{body}
endmodule
"""


def sop_terms(sig, base, w, table, bit):
    # Product terms for output `bit` of the S-box applied to sig[base+w-1:base].
    terms = []
    for v in range(1 << w):
        if (table[v] >> bit) & 1:
            lits = []
            for j in range(w):
                nm = "%s[%d]" % (sig, base + j)
                lits.append(nm if (v >> j) & 1 else "(~%s)" % nm)
            terms.append("(" + "&".join(lits) + ")")
    return terms


def _sympy_verilog(expr, sig, base):
    # Convert sympy Or(And(...)) over x0..x7 (x_j = bit j) to Verilog.
    from sympy.logic.boolalg import Or, And, Not
    def lit(a):
        # sympy SOPform: x0 is the MSB. x_j <-> sig[base + (7-j)].
        neg = isinstance(a, Not)
        s = a.args[0] if neg else a
        j = int(s.name[1:])
        nm = "%s[%d]" % (sig, base + (7 - j))
        return ("(~%s)" % nm) if neg else nm
    def term(a):
        if isinstance(a, And):
            return "(" + "&".join(lit(x) for x in a.args) + ")"
        return "(" + lit(a) + ")"
    if isinstance(expr, Or):
        return " | ".join(term(a) for a in expr.args)
    return term(expr)


_AES_SOP8 = None
def _aes_sop8():
    # Minimized SOP per output bit (~45 cubes vs 128 minterms); computed once.
    global _AES_SOP8
    if _AES_SOP8 is None:
        from sympy.logic.boolalg import SOPform
        from sympy import symbols
        xs = symbols('x0:8')
        _AES_SOP8 = []
        for bit in range(8):
            # sympy minterm m <-> (x0..x7) = bits 7..0 of m; with x_j = v[7-j]
            # this is exactly v, so no bit reversal.
            mt = [v for v in range(256) if (AES[v] >> bit) & 1]
            _AES_SOP8.append(SOPform(xs, mt))
    return _AES_SOP8


def sbox8_sop(sig, base, table):
    # 8-bit S-box as sympy-minimized SOP (correct by construction from the
    # verified table; ABC further optimizes). Replaces the ternary mux chain,
    # which yosys/ABC mapped to a 256-deep mux tree (330 unit-delays).
    assert table == AES
    exprs = _aes_sop8()
    return ["assign %s[%d] = %s;" % ("SB", bit, _sympy_verilog(exprs[bit], sig, base))
            for bit in range(8)]


def round_body(rounds, ks, w, lin, table):
    # lin: "player" (PRESENT pLayer) or "lin3" (x^ROTL(x,13)^ROTL(x,41)).
    # Rounds fully unrolled; key schedule inlined (baseline style); S-box SOP
    # inlined per nibble/byte so all net names stay plain identifiers.
    nb = 64 // w
    L = ["  wire [63:0] s0 = val ^ key;"]
    for i in range(rounds):
        sx = "sx%d" % i
        L.append("  wire [63:0] %s = s%d ^ %s;" % (sx, i, rk_expr(i, ks)))
        sbnames = []
        for b in range(nb):
            sb = "sb%d_%d" % (i, b)
            sbnames.append(sb)
            if w == 8:
                L.append("  wire [7:0] %s;" % sb)
                for stmt in sbox8_sop(sx, w * b, table):
                    L.append("  " + stmt.replace("SB", sb))
            else:
                L.append("  wire [%d:0] %s;" % (w - 1, sb))
                for bit in range(w):
                    terms = sop_terms(sx, w * b, w, table, bit)
                    rhs = " | ".join(terms) if terms else "1'b0"
                    L.append("  assign %s[%d] = %s;" % (sb, bit, rhs))
        sy = "sy%d" % i
        L.append("  wire [63:0] %s = {%s};" % (sy, ", ".join(sbnames[::-1])))
        if lin == "player":
            L.append("  wire [63:0] s%d = %s;" % (i + 1, p_layer_concat(sy)))
        else:
            L.append("  wire [63:0] s%d = %s ^ %s ^ %s;" % (
                i + 1, sy, rotl_expr(sy, 13), rotl_expr(sy, 41)))
    L.append("  assign out = s%d ^ %s;" % (rounds, rk_expr(rounds, ks)))
    return "\n".join(L)



def rk_expr(i, ks):
    # Inlined round-key expression (NOT a standalone wire): the baseline
    # mix_spn12.v uses this style, and it keeps yosys from emitting
    # `assign {concat} = {concat};` alias statements in the mapped netlist,
    # which analyze2.py cannot parse (LHS-concat width ERROR -- reported).
    parts = [rotl_expr("key", 13 * (i + 1))]
    if ks == "ks2":
        parts.append(rotl_expr("key", 29 * (i + 1)))
    parts.append(hx(rc(i), 64))
    return " ^ ".join(parts)


def pylist(lst):
    return ", ".join("0x%X" % v for v in lst)


def main():
    os.makedirs(EXP + "/models", exist_ok=True)
    os.makedirs(EXP + "/rtl", exist_ok=True)

    spn_specs = [
        ("spn7_present", 7, "present", "default", "PRESENT"),
        ("spn6_present", 6, "present", "default", "PRESENT"),
        ("spn7_gift", 7, "gift", "default", "GIFT"),
        ("spn6_gift", 6, "gift", "default", "GIFT"),
        ("spn7_skinny", 7, "skinny", "default", "SKINNY"),
        ("spn7_present_ks2", 7, "present", "ks2", "PRESENT"),
    ]
    for name, rounds, sbox, ks, sboxname in spn_specs:
        ksdesc = ("ROTL64(key,13*(i+1)) ^ RC[i]" if ks == "default"
                  else "ROTL64(key,13*(i+1)) ^ ROTL64(key,29*(i+1)) ^ RC[i]")
        rknp = ("rotl64_np(k, U64(13 * (i + 1)))" if ks == "default"
                else "rotl64_np(k, U64(13 * (i + 1))) ^ rotl64_np(k, U64(29 * (i + 1)))")
        rksc = ("_rotl64_scalar(key, 13 * (i + 1))" if ks == "default"
                else "_rotl64_scalar(key, 13 * (i + 1)) ^ _rotl64_scalar(key, 29 * (i + 1))")
        src = MODEL_SPN.format(name=name, rounds=rounds, sboxname=sboxname,
                               ksdesc=ksdesc, sboxlist=pylist(SBOX4[sbox]),
                               rknp=rknp, rksc=rksc)
        open(EXP + "/models/%s.py" % name, "w").write(src)
        desc = ("%d-round SPN, %s 4-bit S-box + PRESENT pLayer; key schedule " % (rounds, sboxname) +
                ("rk[i] = ROTL64(key,13*(i+1)) ^ RC[i]" if ks == "default"
                 else "rk[i] = ROTL64(key,13*(i+1)) ^ ROTL64(key,29*(i+1)) ^ RC[i]"))
        rtl = RTL_HEAD.format(
            name=name, desc=desc,
            body=round_body(rounds, ks, 4, "player", SBOX4[sbox]))
        open(EXP + "/rtl/%s.v" % name, "w").write(rtl)
        print("wrote", name)

    src = MODEL_AES8.format(aeslist=pylist(AES))
    open(EXP + "/models/spn2_aes8.py", "w").write(src)
    rtl = RTL_HEAD.format(
        name="spn2_aes8",
        desc=("2 rounds of (xor rk, 8x AES 8-bit S-box, bijective 3-term xor-linear " +
              "L(x)=x^ROTL(x,13)^ROTL(x,41) applied to the state) + whitening; " +
              "key schedule rk[i] = ROTL64(key,13*(i+1)) ^ RC[i]"),
        body=round_body(2, "default", 8, "lin3", AES))
    open(EXP + "/rtl/spn2_aes8.v", "w").write(rtl)
    print("wrote spn2_aes8")

    src = MODEL_XORLIN.format(sboxlist=pylist(PRESENT))
    open(EXP + "/models/spn4_xorlin.py", "w").write(src)
    rtl = RTL_HEAD.format(
        name="spn4_xorlin",
        desc=("4 rounds of (xor rk, 16x PRESENT 4-bit S-box, bijective 3-term xor-linear " +
              "L(x)=x^ROTL(x,13)^ROTL(x,41) applied to the state) + whitening; " +
              "key schedule rk[i] = ROTL64(key,13*(i+1)) ^ RC[i]"),
        body=round_body(4, "default", 4, "lin3", PRESENT))
    open(EXP + "/rtl/spn4_xorlin.v", "w").write(rtl)
    print("wrote spn4_xorlin")


if __name__ == "__main__":
    main()
