#!/usr/bin/env python3
"""Generate bundles for Track 5 batch-21d (1-AND+2-linear cascade).

Stage: x ^= (ra&rb)^rc^rd. Top-2 from search_b21d.py (exact S1-DIFF, 56/100 KEEP).
"""
import importlib.util
import json
import os

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

SCHEDS = {
    "hyb21_lin2a": ([(11, 63, 18, 52), (25, 8, 20, 51), (5, 31, 14, 34), (50, 6, 1, 54), (14, 1, 62, 39)], 2.38),
    "hyb21_lin2b": ([(29, 54, 38, 39), (10, 4, 46, 6), (37, 5, 57, 49), (10, 29, 35, 33), (30, 17, 44, 50)], 2.48),
}

def rotl_v(x, r):
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)

def gen_model(name, stages, z):
    L = ['"""5-stage 1-AND+2-linear cascade, batch-21d proxy-guided schedule '
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
    L.append("    for a, b, c, d in STAGES:")
    L.append("        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c) ^ _rotl(x, d)) & M64")
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
         "// batch-21d proxy-guided 5-stage 1-AND+2-linear schedule (triage z=%.2f)" % z,
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for a, b, c, d in stages:
        L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d)) ^ rotl64(x,%d) ^ rotl64(x,%d);" % (a, b, c, d))
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"

def gen_rtl(name, stages, z):
    L = ["// %s: batch-21d proxy-guided 5-stage 1-AND+2-linear schedule (triage z=%.2f)" % (name, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, (a, b, c, d) in enumerate(stages):
        prev = "x%d" % j
        L.append("    wire [63:0] x%d = %s ^ (%s & %s) ^ %s ^ %s;" % (
            j + 1, prev, rotl_v(prev, a), rotl_v(prev, b), rotl_v(prev, c), rotl_v(prev, d)))
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
        spec = importlib.util.spec_from_file_location("m_" + name, os.path.join(d, "model.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        import numpy as np
        V = np.arange(500, dtype=np.uint64); K = np.full(500, np.uint64(0x123456789ABCDEF0))
        assert all(int(x) == m.mix(int(v), int(k)) for x, v, k in zip(m.mix_np(V, K), V, K)), "mix_np != mix"
        goldens = []
        for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(k), "out": hex(m.mix(v, k))})
        meta = {
            "name": name,
            "description": "batch-21d proxy-guided 5-stage 1-AND+2-linear schedule (triage z=%.2f)" % z,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        print("wrote bundle", name, flush=True)

if __name__ == "__main__":
    main()
