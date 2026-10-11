#!/usr/bin/env python3
"""Generate fast_battery bundles for wave-14 W3 KEEPs (GF-diffused word-AND).

Selection (recorded in RESUME.md): best-z member of each structural class
(stages,total ANDs) among the 99 screen KEEPs, so every cost class is
represented by its strongest member:
  al_w3a (3st,3AND) zmax 2.52 -- best overall
  al_w3b (2st,4AND) zmax 2.54 -- best 2-stage (fewest GF layers)
  al_w3c (2st,4AND) zmax 2.63 -- second P constant, 2-stage
  al_w3d (2st,2AND) zmax 7.00 -- minimal-nonlinearity probe (still KEEP<10)
Class (3st,6AND) NOT bundled: same stage count as (3,3), strictly more
ANDs, best z 2.71 worse than 2.52 -- cost-dominated by al_w3a's class.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

# name: (stages, P, z_seq, z_rnd) -- stages = list of [(a,b),...] per stage
CANDS = {
    "al_w3a": ([[(52, 26)], [(19, 44)], [(9, 54)]],
               0xBF58476D1CE4E5B9, 2.52, 2.48),
    "al_w3b": ([[(47, 35), (55, 47)], [(13, 3), (31, 26)]],
               0x9E3779B97F4A7C15, 2.54, 2.52),
    "al_w3c": ([[(59, 43), (24, 38)], [(28, 49), (17, 15)]],
               0x94D049BB133111EB, 2.63, 2.40),
    "al_w3d": ([[(32, 33)], [(54, 58)]],
               0x94D049BB133111EB, 7.00, None),
}


def gf_mul_scalar(a, C):
    res = 0
    p = a
    c = C
    while c:
        if c & 1:
            res ^= p
        hi = (p >> 63) & 1
        p = ((p << 1) & 0xFFFFFFFFFFFFFFFF) ^ (0x1B if hi else 0)
        c >>= 1
    return res


def gf_matrix_cols(C):
    """cols[j] = gf_mul(1<<j, C); out bit i = XOR of x_j for cols[j] bit i."""
    return [gf_mul_scalar(1 << j, C) for j in range(64)]


def rotl_v(x, r):
    r %= 64
    if r == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model(name, stages, P, zs, zr):
    L = ['"""Wave-14 W3 GF(2^64)-diffused word-AND (screen z_seq=%.2f)."""'
         % zs]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (stages,))
    L.append("P = 0x%016X" % P)
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def _gf(a, C):")
    L.append("    res = np.zeros(a.shape, dtype=np.uint64); p = a.copy(); c = int(C)")
    L.append("    while c:")
    L.append("        if c & 1: res ^= p")
    L.append("        hi = (p >> np.uint64(63)) & np.uint64(1)")
    L.append("        p = ((p << np.uint64(1)) & M64) ^ (hi * np.uint64(0x1B))")
    L.append("        c >>= 1")
    L.append("    return res")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for ands in STAGES:")
    L.append("        for a, b in ands:")
    L.append("            x = (x ^ (_rotl(x, a) & _rotl(x, b))) & M64")
    L.append("        x = _gf(x, P)")
    L.append("    x = (x ^ _rotl(k, 13)) & M64")
    L.append("    return x & M64")
    L.append("def mix(v, k):")
    L.append("    return int(mix_np(np.uint64(v), np.uint64(k)))")
    return "\n".join(L) + "\n"


def gen_c(name, stages, P, zs):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63;",
         "    return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "static uint64_t gf_mul(uint64_t a, uint64_t C) {",
         "    uint64_t res = 0, p = a;",
         "    while (C) {",
         "        if (C & 1) res ^= p;",
         "        uint64_t hi = p >> 63;",
         "        p = (p << 1) ^ (hi ? 0x1BULL : 0ULL);",
         "        C >>= 1;",
         "    }",
         "    return res;",
         "}",
         "// wave-14 W3 GF-diffused word-AND (screen z_seq=%.2f)" % zs,
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for ands in stages:
        for a, b in ands:
            L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d));" % (a, b))
        L.append("    x = gf_mul(x, 0x%016XULL);" % P)
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl(name, stages, P, zs):
    cols = gf_matrix_cols(P)
    # rows[i] = list of input bits feeding output bit i
    rows = [[] for _ in range(64)]
    for j, col in enumerate(cols):
        for i in range(64):
            if (col >> i) & 1:
                rows[i].append(j)
    L = ["// %s: wave-14 W3 GF-diffused word-AND (screen z_seq=%.2f)"
         % (name, zs),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");"]
    prev = "x0"
    L.append("    wire [63:0] x0 = val ^ key;")
    n = 0
    for si, ands in enumerate(stages):
        cur = prev
        for ai, (a, b) in enumerate(ands):
            nxt = "s%d_%d" % (si, ai)
            L.append("    wire [63:0] %s = %s ^ (%s & %s);"
                     % (nxt, cur, rotl_v(cur, a), rotl_v(cur, b)))
            cur = nxt
        g = "g%d" % si
        L.append("    wire [63:0] %s;" % g)
        for i in range(64):
            terms = " ^ ".join("%s[%d]" % (cur, j) for j in rows[i])
            L.append("    assign %s[%d] = %s;" % (g, i, terms))
        prev = g
        n = si + 1
    L.append("    assign out = %s ^ %s;" % (prev, rotl_v("key", 13)))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    only = sys.argv[1:] or list(CANDS)
    for name in only:
        stages, P, zs, zr = CANDS[name]
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(
            gen_model(name, stages, P, zs, zr))
        open(os.path.join(d, "impl.c"), "w").write(
            gen_c(name, stages, P, zs))
        open(os.path.join(d, "rtl.v"), "w").write(
            gen_rtl(name, stages, P, zs))
        spec = importlib.util.spec_from_file_location(
            "m_" + name, os.path.join(d, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        goldens = []
        for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(k),
                            "out": hex(m.mix(v, k))})
        meta = {
            "name": name,
            "description": "wave-14 W3 GF-diffused word-AND, %d stages, "
                           "P=0x%016x (screen z_seq=%.2f z_rnd=%s)"
                           % (len(stages), P, zs, zr),
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        print("wrote bundle", name, flush=True)


if __name__ == "__main__":
    main()
