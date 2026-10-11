#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 33 (proxy-guided 6-stage AND rotation
schedules). KEEP from t6_b33_screen.py pilot (exact S1-DIFF triage, z<10)."""
import importlib.util
import json
import os
import sys

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

SCHEDS = {
    # name: ([(a,b,c)] x6, triage z)
    "t6_b33a": ([(37, 43, 51), (12, 11, 63), (28, 33, 27), (63, 2, 57), (4, 14, 1), (18, 17, 40)], 2.6),
    "t6_b33b": ([(58, 53, 21), (52, 17, 18), (25, 23, 40), (54, 55, 13), (42, 33, 61), (53, 57, 29)], 3.0),
    "t6_b33c": ([(25, 45, 42), (44, 14, 26), (51, 54, 34), (41, 53, 51), (54, 40, 6), (12, 15, 11)], 3.3),
    "t6_b33d": ([(38, 34, 15), (47, 35, 33), (47, 2, 23), (16, 11, 60), (19, 5, 44), (18, 42, 41)], 3.4),
    "t6_b33e": ([(57, 43, 8), (41, 50, 24), (52, 3, 22), (36, 32, 21), (41, 56, 10), (54, 56, 22)], 5.7),
    "t6_b33f": ([(25, 44, 8), (27, 40, 37), (63, 5, 39), (11, 22, 6), (29, 7, 21), (12, 3, 44)], 6.9),
    "t6_b33g": ([(21, 46, 53), (29, 16, 38), (57, 4, 18), (5, 59, 5), (12, 41, 31), (23, 11, 51)], 8.3),
}


def rotl_v(x, r):
    # Verilog rotl expression for 64-bit wire x
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model(name, stages, z):
    L = ['"""6-stage AND-rotation cascade, batch-33 proxy-guided schedule '
         '(triage z=%.1f)."""' % z]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (stages,))
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for a, b, c in STAGES:")
    L.append("        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c)) & M64")
    L.append("    x = (x ^ _rotl(k, 13)) & M64")
    L.append("    return x & M64")
    L.append("def mix(v, k):")
    L.append("    return int(mix_np(np.uint64(v), np.uint64(k)))")
    return "\n".join(L) + "\n"


def gen_c(name, stages, z):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63;",
         "    return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "// batch-33 proxy-guided 6-stage AND schedule (triage z=%.1f)" % z,
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for a, b, c in stages:
        L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d)) ^ rotl64(x,%d);" % (a, b, c))
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl(name, stages, z):
    L = ["// %s: batch-33 proxy-guided 6-stage AND schedule (triage z=%.1f)" % (name, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, (a, b, c) in enumerate(stages):
        prev = "x%d" % j
        L.append("    wire [63:0] x%d = %s ^ (%s & %s) ^ %s;" % (
            j + 1, prev, rotl_v(prev, a), rotl_v(prev, b), rotl_v(prev, c)))
    L.append("    assign out = x6 ^ %s;" % rotl_v("key", 13))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    for name, (stages, z) in SCHEDS.items():
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, z))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages, z))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages, z))
        # goldens from the model
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
            "description": "batch-33 proxy-guided 6-stage AND schedule (triage z=%.1f)" % z,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        print("wrote bundle", name, flush=True)


if __name__ == "__main__":
    main()
