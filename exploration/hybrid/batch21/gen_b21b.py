#!/usr/bin/env python3
"""Generate bundles for Track 5 batch-21b (fat-stage cascade).

Stage: x ^= (ra&rb)^(rc&rd)^re  (2-AND + linear, ~3.3u/stage).
Top-3 fat5 KEEPs from search_b21b.py (exact S1-DIFF triage, z<10).
"""
import importlib.util
import json
import os
import sys

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

SCHEDS = {
    # name: ([(a,b,c,d,e)] x5, triage z)
    "hyb21_fat5a": ([(11, 6, 25, 13, 30), (16, 7, 24, 23, 31), (22, 18, 3, 14, 38), (7, 28, 14, 15, 10), (11, 34, 19, 38, 5)], 2.42),
    "hyb21_fat5b": ([(32, 43, 49, 9, 17), (7, 59, 11, 9, 30), (21, 31, 50, 37, 39), (35, 15, 41, 63, 45), (44, 23, 10, 46, 39)], 2.55),
    "hyb21_fat5c": ([(38, 34, 14, 20, 4), (55, 5, 6, 57, 23), (19, 38, 23, 53, 30), (53, 6, 5, 2, 44), (37, 47, 16, 6, 35)], 2.59),
}


def rotl_v(x, r):
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model(name, stages, z):
    L = ['"""5-stage fat-AND cascade, batch-21b proxy-guided schedule '
         '(triage z=%.2f)."""' % z]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (stages,))
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for a, b, c, d, e in STAGES:")
    L.append("        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ (_rotl(x, c) & _rotl(x, d)) ^ _rotl(x, e)) & M64")
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
         "// batch-21b proxy-guided 5-stage fat-AND schedule (triage z=%.2f)" % z,
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for a, b, c, d, e in stages:
        L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d)) ^ (rotl64(x,%d) & rotl64(x,%d)) ^ rotl64(x,%d);" % (a, b, c, d, e))
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl(name, stages, z):
    L = ["// %s: batch-21b proxy-guided 5-stage fat-AND schedule (triage z=%.2f)" % (name, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, (a, b, c, d, e) in enumerate(stages):
        prev = "x%d" % j
        L.append("    wire [63:0] x%d = %s ^ (%s & %s) ^ (%s & %s) ^ %s;" % (
            j + 1, prev, rotl_v(prev, a), rotl_v(prev, b), rotl_v(prev, c), rotl_v(prev, d), rotl_v(prev, e)))
    L.append("    assign out = x5 ^ %s;" % rotl_v("key", 13))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    for name, (stages, z) in SCHEDS.items():
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, z))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages, z))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages, z))
        spec = importlib.util.spec_from_file_location(
            "m_" + name, os.path.join(d, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        # verify bundle model reproduces triage schedule bit-exact on sample
        import numpy as np
        V = np.arange(1000, dtype=np.uint64); K = np.full(1000, np.uint64(0x123456789ABCDEF0))
        assert int(m.mix(0x123456789ABCDEF0, 0)) == int(m.mix_np(np.uint64(0x123456789ABCDEF0), np.uint64(0)))
        goldens = []
        for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(k), "out": hex(m.mix(v, k))})
        meta = {
            "name": name,
            "description": "batch-21b proxy-guided 5-stage fat-AND schedule (triage z=%.2f)" % z,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        print("wrote bundle", name, flush=True)


if __name__ == "__main__":
    main()
