#!/usr/bin/env python3
"""Batch-11 hybrid generator (Track 5, 2026-10-09 respawn).

Two co-design directions (batch-5B/5C were LOST in a restart; redesigned here):

DIR 1 — final diffusion layer (hyb11_and{5,6}_finalPL):
  Batch-6/8 proved P-box BETWEEN al_and6a stages hurts (disrupts the triplet
  sequence co-design). NEVER TESTED: P-box AFTER all stages, i.e. a final
  diffusion layer that does not touch inter-stage co-design.
  Hypothesis: a strong final (P-box + L) layer compensates for the 6th AND
  stage -> 5 stages + final layer ties/beats 20.1u.
  Structure: x=v^k; N stages al_and6a triplets x^=(ra&rb)^rc;
             x=P37(x); x=L513(x); o=x^rotl(k,13)
  P=(37,1): metric top pick FOR al_and6a's schedule (score 43, batch-6).

DIR 2 — SPN skeleton with cascade nonlinear layer (5B/5C reconstruction):
  Proven SPN core from batch-3: 4 rounds, rk[i]=rotl(k,13*(i+1))^RC[i],
  RC = golden-ratio multiples, round = NL -> P-box -> lin(5,13).
  5B (AND as S-box replacement): NL = 64-bit AND stage x^=(ra&rb)^rc, (1,2,13).
     (A 4-bit y=x^quadratic AND-S-box was prototyped and ABANDONED: the full
      literal-AND space yields ddt=16 structurally -- single-bit input
      differences propagate with probability 1. Documented, not buried.)
  5C (chi-SPN): NL = 64-bit chi stage x^=(~ra&rb)^rc, (1,2,13).
  P-box: (27,1) = SPN-co-designed pick (batch-3, S2-clean); (43,1) = chi/AND
  metric top pick (batch-5) for the chi variant as co-design comparison.

Generates impl.c, rtl.v, model.py (self-contained, bit-exact), meta.json
(with rtl_top -- lesson from batch-4 incident; mix+mix_np -- lesson from r5).
"""
import json
import os
import subprocess
import sys

import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
OUT = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

AND6A = [(1, 2, 13), (7, 19, 5), (3, 11, 29),
         (17, 31, 7), (11, 23, 37), (19, 41, 23)]
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
      0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054]
KEYS = ["0x123456789abcdef0", "0x0"]

# (name, kind, params, desc)
SPECS = [
    ("hyb11_and5_finalPL", "finalPL", dict(nstages=5, pa=37, pb=1),
     "5-stage al_and6a triplets + final P(37,1)+L(5,13): can final diffusion replace stage 6?"),
    ("hyb11_and6_finalPL", "finalPL", dict(nstages=6, pa=37, pb=1),
     "6-stage al_and6a triplets + final P(37,1)+L(5,13) (control: final layer on frontier design)"),
    ("hyb11b_andSPN_p27", "spnNL", dict(nl="and", pa=27, pb=1),
     "4-round SPN, AND-stage NL (1,2,13), P(27,1), L(5,13) -- 5B reconstruction"),
    ("hyb11c_chiSPN_p27", "spnNL", dict(nl="chi", pa=27, pb=1),
     "4-round SPN, chi-stage NL (1,2,13), P(27,1), L(5,13) -- 5C reconstruction, SPN pick"),
    ("hyb11c_chiSPN_p43", "spnNL", dict(nl="chi", pa=43, pb=1),
     "4-round SPN, chi-stage NL (1,2,13), P(43,1), L(5,13) -- 5C reconstruction, chi-metric pick"),
]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def pbox_apply(x, a, b):
    y = np.uint64(0)
    for i in range(64):
        if (x >> np.uint64(i)) & np.uint64(1):
            y |= np.uint64(1) << np.uint64((a * i + b) % 64)
    return y & M64


def lin513(x):
    return (x ^ rotl(x, 5) ^ rotl(x, 13)) & M64


def and_stage(x, sched):
    for (a, b, c) in sched:
        ra, rb, rc = rotl(x, a), rotl(x, b), rotl(x, c)
        x = (x ^ (ra & rb) ^ rc) & M64
    return x


def chi_stage(x, sched):
    for (a, b, c) in sched:
        ra, rb, rc = rotl(x, a), rotl(x, b), rotl(x, c)
        x = (x ^ ((~ra) & rb) ^ rc) & M64
    return x


def model_hash(val, key, kind, p):
    x = np.uint64(val) ^ np.uint64(key)
    k = np.uint64(key)
    if kind == "finalPL":
        x = and_stage(x, AND6A[:p["nstages"]])
        x = pbox_apply(x, p["pa"], p["pb"])
        x = lin513(x)
        return int((x ^ rotl(k, 13)) & M64)
    # spnNL
    for i in range(4):
        rk = rotl(k, 13 * (i + 1)) ^ np.uint64(RC[i])
        x = x ^ rk
        if p["nl"] == "and":
            x = and_stage(x, [(1, 2, 13)])
        else:
            x = chi_stage(x, [(1, 2, 13)])
        x = pbox_apply(x, p["pa"], p["pb"])
        x = lin513(x)
    return int(x & M64)


def rotl_v(sig, r):
    if r % 64 == 0:
        return sig
    r %= 64
    return "{%s[%d:0], %s[63:%d]}" % (sig, 64 - 1 - r, sig, 64 - r)


def pbox_v(sig, a, b, out):
    ainv = pow(a, -1, 64)
    terms = []
    for j in range(63, -1, -1):
        i = (ainv * (j - b)) % 64
        terms.append("%s[%d]" % (sig, i))
    return "wire [63:0] %s = {%s};" % (out, ", ".join(terms))


def nl_v(cur, op, i):
    a, b, c = 1, 2, 13
    V = []
    V.append("    wire [63:0] n" + str(i) + "a = " + rotl_v(cur, a) + ";")
    V.append("    wire [63:0] n" + str(i) + "b = " + rotl_v(cur, b) + ";")
    V.append("    wire [63:0] n" + str(i) + "c = " + rotl_v(cur, c) + ";")
    na, nb, nc = "n%da" % i, "n%db" % i, "n%dc" % i
    if op == "and":
        V.append("    wire [63:0] n%d = %s ^ (%s & %s) ^ %s;" % (i, cur, na, nb, nc))
    else:
        V.append("    wire [63:0] n%d = %s ^ ((~%s) & %s) ^ %s;" % (i, cur, na, nb, nc))
    return V, "n%d" % i


def build(name, kind, p, desc):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)

    # ---- impl.c ----
    L = []
    L.append("// %s: %s (generated by hybrid/codesign/gen_batch11.py)" % (name, desc))
    L.append("#include <stdint.h>")
    L.append("static inline uint64_t rotl64(uint64_t x, int r) {")
    L.append("    r &= 63;")
    L.append("    return r ? (x << r) | (x >> (64 - r)) : x;")
    L.append("}")
    L.append("static inline uint64_t pbox64(uint64_t x) { /* P(i)=(%d*i+%d)%%64 */"
             % (p["pa"], p["pb"]))
    L.append("    uint64_t y = 0;")
    for i in range(64):
        j = (p["pa"] * i + p["pb"]) % 64
        L.append("    y |= ((x >> %d) & 1ULL) << %d;" % (i, j))
    L.append("    return y;")
    L.append("}")
    L.append("static inline uint64_t lin513(uint64_t x) {")
    L.append("    return x ^ rotl64(x, 5) ^ rotl64(x, 13);")
    L.append("}")
    L.append("uint64_t mix_hash(uint64_t val, uint64_t key) {")
    L.append("    uint64_t x = val ^ key;")
    if kind == "finalPL":
        for i, (a, b, c) in enumerate(AND6A[:p["nstages"]]):
            L.append("    { /* AND stage %d: (%d,%d,%d) */" % (i, a, b, c))
            L.append("        uint64_t ra = rotl64(x, %d), rb = rotl64(x, %d), rc = rotl64(x, %d);"
                     % (a, b, c))
            L.append("        x ^= (ra & rb) ^ rc;")
            L.append("    }")
        L.append("    x = pbox64(x);")
        L.append("    x = lin513(x);")
        L.append("    x ^= rotl64(key, 13);")
    else:
        op = "and" if p["nl"] == "and" else "chi"
        nl_expr = "(ra & rb) ^ rc" if op == "and" else "((~ra) & rb) ^ rc"
        for i in range(4):
            L.append("    { /* SPN round %d, %s NL */" % (i, op))
            L.append("        uint64_t rk = rotl64(key, %d) ^ 0x%016xULL;" % (13 * (i + 1), RC[i]))
            L.append("        x ^= rk;")
            L.append("        uint64_t ra = rotl64(x, 1), rb = rotl64(x, 2), rc = rotl64(x, 13);")
            L.append("        x ^= %s;" % nl_expr)
            L.append("        x = pbox64(x);")
            L.append("        x = lin513(x);")
            L.append("    }")
    L.append("    return x;")
    L.append("}")
    open(os.path.join(d, "impl.c"), "w").write("\n".join(L) + "\n")

    # ---- rtl.v ----
    V = []
    V.append("// %s: %s (generated by hybrid/codesign/gen_batch11.py)" % (name, desc))
    V.append("module %s(" % name)
    V.append("    input [63:0] val,")
    V.append("    input [63:0] key,")
    V.append("    output [63:0] out")
    V.append(");")
    V.append("    wire [63:0] x0 = val ^ key;")
    cur = "x0"
    if kind == "finalPL":
        for i, (a, b, c) in enumerate(AND6A[:p["nstages"]]):
            V.append("    wire [63:0] s%da = %s;" % (i, rotl_v(cur, a)))
            V.append("    wire [63:0] s%db = %s;" % (i, rotl_v(cur, b)))
            V.append("    wire [63:0] s%dc = %s;" % (i, rotl_v(cur, c)))
            V.append("    wire [63:0] t%d = %s ^ (s%da & s%db) ^ s%dc;" % (i, cur, i, i, i))
            cur = "t%d" % i
        V.append("    " + pbox_v(cur, p["pa"], p["pb"], "pf"))
        V.append("    wire [63:0] lf = pf ^ %s ^ %s;" % (rotl_v("pf", 5), rotl_v("pf", 13)))
        V.append("    wire [63:0] kr = {key[50:0], key[63:51]};")
        V.append("    assign out = lf ^ kr;")
    else:
        for i in range(4):
            r = (13 * (i + 1)) % 64
            V.append("    wire [63:0] rk%d = %s ^ 64'h%016x;" % (i, rotl_v("key", r), RC[i]))
            V.append("    wire [63:0] xr%d = %s ^ rk%d;" % (i, cur, i))
            nv, cur = nl_v("xr%d" % i, p["nl"], i)
            V.extend(nv)
            V.append("    " + pbox_v(cur, p["pa"], p["pb"], "p%d" % i))
            V.append("    wire [63:0] l%d = p%d ^ %s ^ %s;"
                     % (i, i, rotl_v("p%d" % i, 5), rotl_v("p%d" % i, 13)))
            cur = "l%d" % i
        V.append("    assign out = %s;" % cur)
    V.append("endmodule")
    open(os.path.join(d, "rtl.v"), "w").write("\n".join(V) + "\n")

    # ---- model.py ----
    P = []
    P.append('"""%s: %s. Self-contained bit-exact model."""' % (name, desc))
    P.append("import numpy as np")
    P.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    P.append("PA, PB = %d, %d" % (p["pa"], p["pb"]))
    P.append("")
    P.append("def _rotl(x, r):")
    P.append("    r %= 64")
    P.append("    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64")
    P.append("")
    P.append("def _pbox(x):")
    P.append("    y = np.uint64(0)")
    for i in range(64):
        j = (p["pa"] * i + p["pb"]) % 64
        P.append("    y |= ((x >> np.uint64(%d)) & np.uint64(1)) << np.uint64(%d)" % (i, j))
    P.append("    return y & M64")
    P.append("")
    P.append("def _lin(x):")
    P.append("    return (x ^ _rotl(x, 5) ^ _rotl(x, 13)) & M64")
    P.append("")
    P.append("def _nl(x, op):")
    P.append("    ra, rb, rc = _rotl(x, 1), _rotl(x, 2), _rotl(x, 13)")
    P.append("    if op == 'and':")
    P.append("        return (x ^ (ra & rb) ^ rc) & M64")
    P.append("    return (x ^ ((~ra) & rb) ^ rc) & M64")
    P.append("")
    P.append("def _mix_core(x, k):")
    if kind == "finalPL":
        P.append("    # %d AND stages (al_and6a triplets)" % p["nstages"])
        for (a, b, c) in AND6A[:p["nstages"]]:
            P.append("    ra, rb, rc = _rotl(x, %d), _rotl(x, %d), _rotl(x, %d)" % (a, b, c))
            P.append("    x = (x ^ (ra & rb) ^ rc) & M64")
        P.append("    x = _lin(_pbox(x))")
        P.append("    return (x ^ _rotl(k, 13)) & M64")
    else:
        P.append("    RC = [%s]" % ", ".join(str(r) for r in RC))
        P.append("    for i in range(4):")
        P.append("        x = (x ^ _rotl(k, 13 * (i + 1)) ^ np.uint64(RC[i])) & M64")
        P.append("        x = _nl(x, '%s')" % p["nl"])
        P.append("        x = _lin(_pbox(x))")
        P.append("    return x & M64")
    P.append("")
    P.append("def mix_hash(val, key):")
    P.append("    return int(_mix_core(np.uint64(val) ^ np.uint64(key), np.uint64(key)))")
    P.append("")
    P.append("def mix_np(V, K):")
    P.append("    V = np.asarray(V, dtype=np.uint64)")
    P.append("    K = np.asarray(K, dtype=np.uint64)")
    P.append("    return _mix_core(V ^ K, K)")
    P.append("")
    P.append("def mix(v, k):")
    P.append("    return mix_hash(v, k)")
    open(os.path.join(d, "model.py"), "w").write("\n".join(P) + "\n")

    # ---- meta.json ----
    goldens = []
    for vk, kk in [("0x0", KEYS[0]), (KEYS[0], "0x0")]:
        out = model_hash(int(vk, 16), int(kk, 16), kind, p)
        goldens.append({"val": vk, "key": kk, "out": hex(out)})
    meta = {
        "name": name,
        "description": desc,
        "rtl_top": name,
        "screen_keys": KEYS,
        "practrand_keys": KEYS,
        "goldens": goldens,
    }
    open(os.path.join(d, "meta.json"), "w").write(json.dumps(meta, indent=1) + "\n")
    print("generated %s: goldens %s, %s" % (name, goldens[0]["out"], goldens[1]["out"]))


if __name__ == "__main__":
    for spec in SPECS:
        build(*spec)
    print("batch-11 generation complete")
