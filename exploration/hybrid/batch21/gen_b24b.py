#!/usr/bin/env python3
"""Generate bundle for Track 5 batch-24b (hyb24_het6a): guided heterogeneous
6-stage AND cascade. Stage types: 'front' = x ^= (ra&rb)^rc (frontier form),
'nolin' = x ^= (ra&rb) (no-lin, cheap density). Triage-exact DIFF z=7.16.

NOTE: the winning schedule has 2 degenerate stages (S0 a==b -> AND collapses
to linear x^ra^rc; S5 a==b -> x^ra). The model/C/RTL below reproduce the
schedule literally, so bit-exactness is unaffected; the clean-axis re-run
(b24c, mutate excluding a==b) is a separate lead.
"""
import importlib.util
import json
import os

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

# (type, a, b, c) x6 from search_b24b_results.json (k4, best z=7.16)
STAGES = [('front', 17, 17, 26), ('front', 41, 56, 40), ('front', 55, 36, 4),
          ('front', 22, 4, 37), ('nolin', 52, 47, 22), ('nolin', 55, 55, 47)]
Z = 7.16
NAME = "hyb24_het6a"


def rotl_v(x, r):
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model():
    L = ['"""6-stage heterogeneous AND cascade, batch-24b guided schedule '
         '(triage-exact DIFF z=%.2f)."""' % Z]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (STAGES,))
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for typ, a, b, c in STAGES:")
    L.append("        if typ == 'front':")
    L.append("            x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c)) & M64")
    L.append("        else:")
    L.append("            x = (x ^ (_rotl(x, a) & _rotl(x, b))) & M64")
    L.append("    x = (x ^ _rotl(k, 13)) & M64")
    L.append("    return x & M64")
    L.append("def mix(v, k):")
    L.append("    return int(mix_np(np.uint64(v), np.uint64(k)))")
    return "\n".join(L) + "\n"


def gen_c():
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63;",
         "    return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "// batch-24b guided 6-stage heterogeneous AND schedule (triage z=%.2f)" % Z,
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for typ, a, b, c in STAGES:
        if typ == 'front':
            L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d)) ^ rotl64(x,%d);" % (a, b, c))
        else:
            L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d));" % (a, b))
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl():
    L = ["// %s: batch-24b guided 6-stage heterogeneous AND schedule (triage z=%.2f)" % (NAME, Z),
         "module %s(" % NAME,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, (typ, a, b, c) in enumerate(STAGES):
        prev = "x%d" % j
        if typ == 'front':
            L.append("    wire [63:0] x%d = %s ^ (%s & %s) ^ %s;" % (
                j + 1, prev, rotl_v(prev, a), rotl_v(prev, b), rotl_v(prev, c)))
        else:
            L.append("    wire [63:0] x%d = %s ^ (%s & %s);" % (
                j + 1, prev, rotl_v(prev, a), rotl_v(prev, b)))
    L.append("    assign out = x6 ^ %s;" % rotl_v("key", 13))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    d = os.path.join(FB, NAME)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "model.py"), "w").write(gen_model())
    open(os.path.join(d, "impl.c"), "w").write(gen_c())
    open(os.path.join(d, "rtl.v"), "w").write(gen_rtl())
    spec = importlib.util.spec_from_file_location("m_" + NAME, os.path.join(d, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    # cross-check against the original triage model on random vectors
    src = importlib.util.spec_from_file_location(
        "src_model", "/home/hatch/workspace/mix/exploration/hybrid/batch21/gen_hyb24_het6a_model.py")
    sm = importlib.util.module_from_spec(src)
    src.loader.exec_module(sm)
    rng = __import__("random").Random(0x24b)
    for _ in range(2000):
        v, k = rng.getrandbits(64), rng.getrandbits(64)
        assert m.mix(v, k) == sm.mix(v, k), (v, k)
    goldens = []
    for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
        goldens.append({"val": hex(v), "key": hex(k), "out": hex(m.mix(v, k))})
    meta = {
        "name": NAME,
        "description": "batch-24b guided 6-stage heterogeneous AND cascade (triage-exact DIFF z=%.2f)" % Z,
        "screen_keys": ["0x123456789abcdef0", "0x0"],
        "practrand_keys": ["0x123456789abcdef0", "0x0"],
        "goldens": goldens,
        "rtl_top": NAME,
        "caveat": "winning schedule has 2 degenerate stages (S0 a==b, S5 a==b); clean-axis b24c re-run is a separate lead",
    }
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    print("wrote bundle", NAME, "bit-exact vs triage model 2000/2000", flush=True)


if __name__ == "__main__":
    main()
