#!/usr/bin/env python3
"""Generate a fast_battery bundle for a wave-35 KEEP hit.

Usage: gen_wave35_bundle.py <template> <hits.json> <index> <name>
Writes fast_battery/candidates/<name>/{model.py,impl.c,rtl.v,meta.json}.
Bit-exactness vs the triage model must be verified separately (2000/2000).
"""
import json
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave35_lib import SB0  # noqa: F401  (validates import path)

SB0_LIST = [12, 10, 13, 3, 14, 11, 15, 7, 8, 9, 1, 5, 0, 2, 4, 6]
SB0_HEX = "cad3ebf789150246"

CAND_DIR = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"


def rotl_expr(x, r):
    r %= 64
    if r == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen(template, sched, inter_rot, name):
    n_and = len(sched)
    # ---- model.py ----
    stages_py = ", ".join("(%d, %d, %d)" % s for s in sched)
    model = '''"""Wave-35 two-state: AND-cascade + Midori-Sb0 S-box layer (template %s)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SB0 = np.array([%s], dtype=np.uint64)
AND_SCHED = [%s]
INTER_ROT = %d
def _rotl(x, r):
    r %%= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def _splayer64(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SB0[((x >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)] << np.uint64(4*i)
    return y & M64
_PBOX = [(9*i) %% 64 for i in range(64)]
def _splayer(x):
    x = np.asarray(x, dtype=np.uint64)
    xs = _splayer64(x)
    y = np.zeros_like(xs)
    for i in range(64):
        y |= ((xs >> np.uint64(i)) & np.uint64(1)) << np.uint64(_PBOX[i])
    return y & M64
def mix_np(V, K):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    ai = iter(AND_SCHED)
''' % (template, ", ".join(map(str, SB0_LIST)), stages_py, inter_rot)
    body = {
        "A": """    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = _splayer(x)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
""",
        "B": """    x = _splayer(x)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
""",
        "C": """    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = _splayer(x); x = _rotl(x, INTER_ROT)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = _splayer(x)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
""",
        "E": """    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = _splayer(x)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
""",
        "F": """    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    x = _splayer(x)
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
    a,b,c = next(ai); x = (x ^ (_rotl(x,a) & _rotl(x,b)) ^ _rotl(x,c)) & M64
""",
    }[template]
    model += body + """    x = (x ^ _rotl(k, 13)) & M64
    return x & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
"""
    # ---- impl.c ----
    impl = '''#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint8_t SB0[16] = {%s};
static inline uint64_t sbox64(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= (uint64_t)SB0[(x >> (4*i)) & 0xF] << (4*i);
    return y;
}
static inline uint64_t splayer64(uint64_t x) {
    uint64_t xs = sbox64(x), y = 0;
    for (int i = 0; i < 64; i++)
        y |= ((xs >> i) & 1u) << ((9*i) & 63);
    return y;
}
// wave-35 two-state (template %s): AND-cascade + Midori-Sb0 S-box layer
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
''' % (", ".join("0x%x" % v for v in SB0_LIST), template)
    ai = iter(sched)
    def and_c(a, b, c):
        return "    x ^= (rotl64(x,%d) & rotl64(x,%d)) ^ rotl64(x,%d);\n" % (a, b, c)
    if template == "A":
        impl += and_c(*next(ai)) + and_c(*next(ai))
        impl += "    x = splayer64(x);\n"
        impl += and_c(*next(ai)) + and_c(*next(ai))
    elif template == "B":
        impl += "    x = splayer64(x);\n"
        impl += and_c(*next(ai)) + and_c(*next(ai)) + and_c(*next(ai))
    elif template == "E":
        impl += and_c(*next(ai)) + and_c(*next(ai)) + and_c(*next(ai)) + and_c(*next(ai))
        impl += "    x = splayer64(x);\n"
        impl += and_c(*next(ai))
    elif template == "F":
        impl += and_c(*next(ai)) + and_c(*next(ai))
        impl += "    x = splayer64(x);\n"
        impl += and_c(*next(ai)) + and_c(*next(ai)) + and_c(*next(ai))
    else:
        impl += and_c(*next(ai))
        impl += "    x = splayer64(x);\n    x = rotl64(x, %d);\n" % inter_rot
        impl += and_c(*next(ai))
        impl += "    x = splayer64(x);\n"
        impl += and_c(*next(ai))
    impl += """    x ^= rotl64(key, 13);
    return x;
}
"""
    # ---- rtl.v ----
    case_lines = "\n".join(
        "        4'h%x: sb0 = 4'h%s;" % (i, SB0_HEX[i]) for i in range(16))
    rtl = '''// %s: wave-35 two-state (template %s) AND-cascade + Midori-Sb0 S-box layer
module %s(
    input  [63:0] val,
    input  [63:0] key,
    output [63:0] out
);
    function [3:0] sb0;
        input [3:0] n;
        case (n)
%s
            default: sb0 = 4'h0;
        endcase
    endfunction
    wire [63:0] x0 = val ^ key;
''' % (name, template, name, case_lines)
    n = 0
    ai = iter(sched)
    def and_v(xn, a, b, c):
        return ("    wire [63:0] x%d = x%d ^ (%s & %s) ^ %s;\n"
                % (n + 1, n, rotl_expr("x%d" % n, a), rotl_expr("x%d" % n, b),
                   rotl_expr("x%d" % n, c)))
    def splayer_wires():
        # Flat S-player: 16x sb0 + (9i)%64 P-box as explicit wiring.
        # (Function-with-loop form hangs yosys AST simplifier.)
        global_n = n
        lines = []
        lines.append("    wire [63:0] x%d_sb;\n" % (global_n + 1))
        for i in range(16):
            lines.append("    assign x%d_sb[%d:%d] = sb0(x%d[%d:%d]);\n"
                         % (global_n + 1, 4*i+3, 4*i, global_n, 4*i+3, 4*i))
        lines.append("    wire [63:0] x%d;\n" % (global_n + 1))
        for i in range(64):
            lines.append("    assign x%d[%d] = x%d_sb[%d];\n"
                         % (global_n + 1, (9*i) % 64, global_n + 1, i))
        return "".join(lines)
    if template == "A":
        for _ in range(2):
            a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
        rtl += splayer_wires(); n += 1
        for _ in range(2):
            a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
    elif template == "B":
        rtl += splayer_wires(); n += 1
        for _ in range(3):
            a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
    elif template == "E":
        for _ in range(4):
            a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
        rtl += splayer_wires(); n += 1
        a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
    elif template == "F":
        for _ in range(2):
            a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
        rtl += splayer_wires(); n += 1
        for _ in range(3):
            a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
    else:
        a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
        rtl += splayer_wires(); n += 1
        rtl += "    wire [63:0] x%d = %s;\n" % (n + 1, rotl_expr("x%d" % n, inter_rot)); n += 1
        a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
        rtl += splayer_wires(); n += 1
        a, b, c = next(ai); rtl += and_v("x%d" % n, a, b, c); n += 1
    rtl += "    assign out = x%d ^ %s;\nendmodule\n" % (n, rotl_expr("key", 13))
    # ---- meta.json ----
    meta = {
        "name": name,
        "description": "wave-35 two-state template %s: AND-cascade + Midori-Sb0 S-box layer" % template,
        "screen_keys": ["0x123456789abcdef0", "0x0"],
        "practrand_keys": ["0x123456789abcdef0", "0x0"],
        "goldens": [],
        "rtl_top": name,
    }
    import os
    d = os.path.join(CAND_DIR, name)
    os.makedirs(d, exist_ok=True)
    for fn, content in (("model.py", model), ("impl.c", impl), ("rtl.v", rtl)):
        with open(os.path.join(d, fn), "w") as f:
            f.write(content)
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("bundle written: %s/{model.py,impl.c,rtl.v,meta.json}" % d)


def main():
    template, hits_json, index, name = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    with open(hits_json) as f:
        hits = json.load(f)
    h = sorted(hits, key=lambda h: h["z"])[index]
    gen(template, [tuple(s) for s in h["sched"]], h["inter_rot"], name)


if __name__ == "__main__":
    main()
