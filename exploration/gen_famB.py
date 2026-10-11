"""Round-2 generator, family B: 5-round pLayer SPN variants + A8 (spn4_xorlin)
rotation-pair / S-box variants. Emits exploration/models/<name>.py and
exploration/rtl/<name>.v. Does NOT touch round-1 files.

S-box tables: PRESENT and GIFT 4-bit tables as verified in gen_a.py (borrowed
TABLES applied to contiguous nibbles only; cipher security bounds do not
transfer).

Bijectivity of L(x) = x ^ ROTL(x,r) ^ ROTL(x,s) (distinct nonzero r,s): over
GF(2), L <-> 1 + x^r + x^s; evaluating at x=1 gives 1 (mod 2), so x+1 does
not divide it, and x^64+1 = (x+1)^64 has no other factor ==> bijection.
Covers (13,41), (7,19), (17,53), (11,37), (23,31).
"""
import os

EXP = "/home/hatch/workspace/mix/exploration"
M64 = (1 << 64) - 1
GOLDEN = 0x9E3779B97F4A7C15

PRESENT = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
           0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
GIFT = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9,
        0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]
assert len(set(PRESENT)) == 16 and len(set(GIFT)) == 16


def rc(i):
    return ((i + 1) * GOLDEN) & M64


def rotl_expr(sig, r):
    r %= 64
    if r == 0:
        return sig
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63 - r, sig, 64 - r)


def p_layer_concat(sig):
    P = [(16 * b) % 63 for b in range(63)] + [63]
    inv = [0] * 64
    for b, o in enumerate(P):
        inv[o] = b
    return "{%s}" % ", ".join("%s[%d]" % (sig, inv[o]) for o in range(63, -1, -1))


def hx(v, w):
    return "%d'h%0*x" % (w, w // 4, v)


def pylist(lst):
    return ", ".join("0x%X" % v for v in lst)


def sop_terms(sig, base, table, bit):
    terms = []
    for v in range(16):
        if (table[v] >> bit) & 1:
            lits = []
            for j in range(4):
                nm = "%s[%d]" % (sig, base + j)
                lits.append(nm if (v >> j) & 1 else "(~%s)" % nm)
            terms.append("(" + "&".join(lits) + ")")
    return terms


RTL_HEAD = """// {name}: {desc}
// S-box inline as assign-based SOP (minterm expansion from the verified table;
// ABC minimizes). NOTE: function+case infers $rom cells which this flow
// (yosys -> abc -fast) cannot map, and a separate S-box module leaves
// hierarchical net names in dead concat assigns that the analyzer cannot
// parse; inline SOP keeps every net name a plain identifier.
module {name}(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
{body}
endmodule
"""


def rk_expr(i, ks):
    parts = [rotl_expr("key", 13 * (i + 1))]
    if ks == "ks2":
        parts.append(rotl_expr("key", 37 * (i + 1)))
    parts.append(hx(rc(i), 64))
    return " ^ ".join(parts)


def round_body(rounds, ks, lin, table, rot_off=None, lrotx=None):
    # lin: "player" (+optional free whole-state ROTL(rot_off) between S-box and
    # pLayer) or "xorlin" (x ^ ROTL(x,r) ^ ROTL(x,s) with lrotx=(r,s)).
    L = ["  wire [63:0] s0 = val ^ key;"]
    for i in range(rounds):
        sx = "sx%d" % i
        L.append("  wire [63:0] %s = s%d ^ %s;" % (sx, i, rk_expr(i, ks)))
        sbnames = []
        for b in range(16):
            sb = "sb%d_%d" % (i, b)
            sbnames.append(sb)
            L.append("  wire [3:0] %s;" % sb)
            for bit in range(4):
                terms = sop_terms(sx, 4 * b, table, bit)
                rhs = " | ".join(terms) if terms else "1'b0"
                L.append("  assign %s[%d] = %s;" % (sb, bit, rhs))
        sy = "sy%d" % i
        L.append("  wire [63:0] %s = {%s};" % (sy, ", ".join(sbnames[::-1])))
        if lin == "player":
            if rot_off:
                sr = "sr%d" % i
                L.append("  wire [63:0] %s = %s;" % (sr, rotl_expr(sy, rot_off)))
                L.append("  wire [63:0] s%d = %s;" % (i + 1, p_layer_concat(sr)))
            else:
                L.append("  wire [63:0] s%d = %s;" % (i + 1, p_layer_concat(sy)))
        else:
            r, s = lrotx
            L.append("  wire [63:0] s%d = %s ^ %s ^ %s;" % (
                i + 1, sy, rotl_expr(sy, r), rotl_expr(sy, s)))
    L.append("  assign out = s%d ^ %s;" % (rounds, rk_expr(rounds, ks)))
    return "\n".join(L)


# ---------------------------------------------------------------- models

MODEL_SPN = '''"""{name}: {desc}

Bijectivity (fixed key): xor round key (bijection), 16x bijective 4-bit
S-box (16 distinct outputs asserted){rotbij}, PRESENT pLayer bit-permutation
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
        {rotsc}
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
        x = {rotnp}
    return x ^ _rk_np(k, _ROUNDS)


if __name__ == "__main__":
    check_model_equiv(mix_{name}_scalar, mix_{name}_np, "{name}")
    bijectivity_spotcheck(mix_{name}_np, "{name}")
'''

MODEL_XORLIN = '''"""{name}: {desc}

Bijectivity (fixed key): xor round key (bijection), 16x bijective 4-bit
S-box (16 distinct outputs asserted), bijective 3-term xor-linear layer
L(x) = x ^ ROTL(x,{lr}) ^ ROTL(x,{ls}) -- over GF(2), L <-> 1+x^{lr}+x^{ls};
(1+x^{lr}+x^{ls})(1) = 1 != 0 mod 2 so x+1 does not divide it, and
x^64+1 = (x+1)^64 has no other factor ==> L is a permutation of 2^64 --
final xor whitening (bijection); composition of bijections => permutation of
2^64. The S-box TABLE is borrowed only, applied to contiguous nibbles --
NOT the full cipher; published security bounds do not transfer.
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
_ROUNDS = {rounds}


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _rotl64_scalar(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_scalar(key, i):
    return _rotl64_scalar(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)


def mix_{name}_scalar(val, key):
    val &= M64
    key &= M64
    x = val ^ key
    for i in range(_ROUNDS):
        x ^= _rk_scalar(key, i)
        y = 0
        for s in range(16):
            y |= _SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
        x = (y ^ _rotl64_scalar(y, {lr}) ^ _rotl64_scalar(y, {ls})) & M64
    return (x ^ _rk_scalar(key, _ROUNDS)) & M64


def _L64_np(x):
    return x ^ rotl64_np(x, U64({lr})) ^ rotl64_np(x, U64({ls}))


def mix_{name}_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(_ROUNDS):
        x = _L64_np(sbox16_np(x ^ _rk_np(k, i), _SBOX_NP))
    return x ^ _rk_np(k, _ROUNDS)


if __name__ == "__main__":
    check_model_equiv(mix_{name}_scalar, mix_{name}_np, "{name}")
    bijectivity_spotcheck(mix_{name}_np, "{name}")
'''


def emit_spn(name, rounds, sbox, ks, rot_off=None):
    table = PRESENT if sbox == "present" else GIFT
    sboxname = sbox.upper()
    if ks == "ks2":
        ksdesc = "rk[i] = ROTL64(key,13*(i+1)) ^ ROTL64(key,37*(i+1)) ^ RC[i]"
        rknp = "rotl64_np(k, U64(13 * (i + 1))) ^ rotl64_np(k, U64(37 * (i + 1)))"
        rksc = "_rotl64_scalar(key, 13 * (i + 1)) ^ _rotl64_scalar(key, 37 * (i + 1))"
    else:
        ksdesc = "rk[i] = ROTL64(key,13*(i+1)) ^ RC[i]"
        rknp = "rotl64_np(k, U64(13 * (i + 1)))"
        rksc = "_rotl64_scalar(key, 13 * (i + 1))"
    rotpart = (" + free whole-state ROTL(%d) between S-box and pLayer" % rot_off
               if rot_off else "")
    desc = ("%d-round SPN, %s 4-bit S-box + PRESENT pLayer%s; x = val ^ key, %s, "
            "RC[i]=(i+1)*0x9E3779B97F4A7C15; round: x = pLayer(SBOX16(x ^ rk[i]))%s; "
            "out = x ^ rk[%d]" % (rounds, sboxname, rotpart, ksdesc,
                                  " (S-box output ROTL%d before pLayer)" % rot_off
                                  if rot_off else "", rounds))
    rotbij = (", whole-state ROTL(%d) (bijection)" % rot_off if rot_off else "")
    if rot_off:
        rotsc = "y = _rotl64_scalar(y, %d)" % rot_off
        rotnp = ("present_perm_np(rotl64_np(sbox16_np(x ^ _rk_np(k, i), "
                 "_SBOX_NP), U64(%d)))" % rot_off)
    else:
        rotsc = "pass  # no extra rotation"
        rotnp = "present_perm_np(sbox16_np(x ^ _rk_np(k, i), _SBOX_NP))"
    src = MODEL_SPN.format(name=name, desc=desc, rotbij=rotbij,
                           sboxlist=pylist(table), rounds=rounds,
                           rknp=rknp, rksc=rksc, rotsc=rotsc, rotnp=rotnp)
    open(EXP + "/models/%s.py" % name, "w").write(src)
    rtl = RTL_HEAD.format(name=name, desc=desc,
                          body=round_body(rounds, ks, "player", table,
                                          rot_off=rot_off))
    open(EXP + "/rtl/%s.v" % name, "w").write(rtl)
    print("wrote", name)


def emit_xorlin(name, sbox, lr, ls):
    table = PRESENT if sbox == "present" else GIFT
    desc = ("4 rounds of (xor rk, 16x %s 4-bit S-box, bijective 3-term "
            "xor-linear L(x)=x^ROTL(x,%d)^ROTL(x,%d) applied to the state) + "
            "whitening; key schedule rk[i] = ROTL64(key,13*(i+1)) ^ RC[i]" %
            (sbox.upper(), lr, ls))
    src = MODEL_XORLIN.format(name=name, desc=desc, sboxlist=pylist(table),
                              rounds=4, lr=lr, ls=ls)
    open(EXP + "/models/%s.py" % name, "w").write(src)
    rtl = RTL_HEAD.format(name=name, desc=desc,
                          body=round_body(4, "default", "xorlin", table,
                                          lrotx=(lr, ls)))
    open(EXP + "/rtl/%s.v" % name, "w").write(rtl)
    print("wrote", name)


def main():
    os.makedirs(EXP + "/models", exist_ok=True)
    os.makedirs(EXP + "/rtl", exist_ok=True)
    # 5-round pLayer SPN variants
    emit_spn("spn5_present", 5, "present", "default")
    emit_spn("spn5_gift", 5, "gift", "default")
    emit_spn("spn5_present_rot", 5, "present", "default", rot_off=7)
    emit_spn("spn5_present_rot11", 5, "present", "default", rot_off=11)
    emit_spn("spn5_present_ks2", 5, "present", "ks2")
    # A8 variants (rotation-pair / S-box lottery)
    emit_xorlin("spn4_xorlin_719", "present", 7, 19)
    emit_xorlin("spn4_xorlin_1753", "present", 17, 53)
    emit_xorlin("spn4_xorlin_gift", "gift", 13, 41)
    emit_xorlin("spn4_xorlin_1137", "present", 11, 37)


if __name__ == "__main__":
    main()
