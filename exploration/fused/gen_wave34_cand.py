#!/usr/bin/env python3
"""gen_wave34_cand.py VARIANT NAME "s11,s12,...;s21,s22,...;..."

Emits fast_battery candidate bundle (impl.c, model.py, rtl.v, meta.json)
for a wave-34 two-state hit. Stage tuples come from wave34_probe HIT lines.
V0/V1/V3: 6 rots/stage (a,b,c,d,e,f). V2: 8 rots/stage (a,b,c,d,e,f,g,h).

Bit-exactness is enforced downstream by the battery's own xcheck (stage 0a).
"""
import os, sys, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave34_probe import make_mix, M64

FB = "/home/hatch/workspace/mix/exploration/fast_battery"

def rotl64(x, r):
    r &= 63
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64

def rtl_rotl(sig, r):
    r %= 64
    if r == 0:
        return sig
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63 - r, sig, 64 - r)

def gen(name, variant, stages):
    d = os.path.join(FB, "candidates", name)
    os.makedirs(d, exist_ok=True)
    ns = len(stages)
    # ---- impl.c ----
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, unsigned r){",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t v, uint64_t k){",
         "    uint64_t x = v ^ k;",
         "    uint64_t y = rotl64(v, 11) ^ rotl64(k, 29);",
         "    uint64_t xn, yn;"]
    for j, st in enumerate(stages):
        if variant in ("V0", "V1", "V3"):
            a, b, c, dd, e, f = st
            if variant == "V0":
                L.append("    xn = x ^ (rotl64(x,%d) & rotl64(y,%d)) ^ rotl64(y,%d);" % (a, b, c))
                L.append("    yn = y ^ (rotl64(y,%d) & rotl64(x,%d)) ^ rotl64(x,%d);" % (dd, e, f))
            else:
                L.append("    xn = x ^ (rotl64(x,%d) & rotl64(y,%d));" % (a, b))
                L.append("    yn = y ^ (rotl64(y,%d) & rotl64(x,%d));" % (dd, e))
        else:
            a, b, c, dd, e, f, g, h = st
            L.append("    xn = x ^ (rotl64(x,%d) & rotl64(x,%d)) ^ (rotl64(x,%d) & rotl64(y,%d));" % (a, b, c, dd))
            L.append("    yn = y ^ (rotl64(y,%d) & rotl64(y,%d)) ^ (rotl64(x,%d) & rotl64(y,%d));" % (e, f, g, h))
        L.append("    x = xn; y = yn;")
    L.append("    return x ^ rotl64(y, 17); }")
    open(os.path.join(d, "impl.c"), "w").write("\n".join(L) + "\n")
    # ---- model.py ----
    mix_fn = make_mix(variant, stages)
    mp = ["import numpy as np", "import sys",
          "sys.path.insert(0, '/home/hatch/workspace/mix/exploration/fused')",
          "from wave34_probe import make_mix",
          "STAGES = %r" % (stages,),
          "VARIANT = %r" % variant,
          "_fn = make_mix(VARIANT, STAGES)",
          "def mix(v, k):",
          "    return int(_fn(np.uint64(v), np.uint64(k)))",
          "def mix_np(V, K):",
          "    return _fn(np.asarray(V, dtype=np.uint64), np.asarray(K, dtype=np.uint64))",
          "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)"]
    open(os.path.join(d, "model.py"), "w").write("\n".join(mp) + "\n")
    # ---- rtl.v ----
    R = ["module %s(input [63:0] val, input [63:0] key, output [63:0] out);" % name,
         "  wire [63:0] x0 = val ^ key;",
         "  wire [63:0] y0 = %s ^ %s;" % (rtl_rotl("val", 11), rtl_rotl("key", 29))]
    for j, st in enumerate(stages):
        px, py = "x%d" % j, "y%d" % j
        nx, ny = "x%d" % (j + 1), "y%d" % (j + 1)
        if variant in ("V0", "V1", "V3"):
            a, b, c, dd, e, f = st
            andx = "(%s & %s)" % (rtl_rotl(px, a), rtl_rotl(py, b))
            andy = "(%s & %s)" % (rtl_rotl(py, dd), rtl_rotl(px, e))
            if variant == "V0":
                R.append("  wire [63:0] %s = %s ^ %s ^ %s;" % (nx, px, andx, rtl_rotl(py, c)))
                R.append("  wire [63:0] %s = %s ^ %s ^ %s;" % (ny, py, andy, rtl_rotl(px, f)))
            else:
                R.append("  wire [63:0] %s = %s ^ %s;" % (nx, px, andx))
                R.append("  wire [63:0] %s = %s ^ %s;" % (ny, py, andy))
        else:
            a, b, c, dd, e, f, g, h = st
            andx1 = "(%s & %s)" % (rtl_rotl(px, a), rtl_rotl(px, b))
            andx2 = "(%s & %s)" % (rtl_rotl(px, c), rtl_rotl(py, dd))
            andy1 = "(%s & %s)" % (rtl_rotl(py, e), rtl_rotl(py, f))
            andy2 = "(%s & %s)" % (rtl_rotl(px, g), rtl_rotl(py, h))
            R.append("  wire [63:0] %s = %s ^ %s ^ %s;" % (nx, px, andx1, andx2))
            R.append("  wire [63:0] %s = %s ^ %s ^ %s;" % (ny, py, andy1, andy2))
    R.append("  assign out = x%d ^ %s;" % (ns, rtl_rotl("y%d" % ns, 17)))
    R.append("endmodule")
    open(os.path.join(d, "rtl.v"), "w").write("\n".join(R) + "\n")
    # ---- meta.json ----
    goldens = []
    for v, k in [(0x123456789ABCDEF0, 0x0FEDCBA987654321),
                 (0x0000000000000001, 0xFFFFFFFFFFFFFFFF)]:
        goldens.append({"in": hex(v), "key": hex(k),
                        "out": hex(int(mix_fn(np.uint64(v), np.uint64(k))))})
    meta = {"name": name, "rtl_top": name,
            "description": "wave-34 two-state %s %d-stage (track-8)" % (variant, ns),
            "goldens": goldens}
    open(os.path.join(d, "meta.json"), "w").write(json.dumps(meta, indent=1) + "\n")
    print("wrote candidate %s (%s, %d stages) -> %s" % (name, variant, ns, d))

if __name__ == "__main__":
    variant, name, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    stages = [tuple(int(r) for r in s.split(",")) for s in spec.split(";")]
    gen(name, variant, stages)
