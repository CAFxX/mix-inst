#!/usr/bin/env python3
"""Generate bundle for Track 5 batch-28 MU5 best KEEP (MUX-gate cascade).

Schedule harvested verbatim from hybrid/batch21/search_b28.log (the pilot
died mid-MU6 on 2026-10-11; MU5 arm completed 19/40 KEEP, script prints
only the top-10 KEEP schedules -- best is complete in the log).

MUX stage form: stages[i] = (s,a,b,d):
  x' = x ^ mux(rotl(x,s), rotl(x,a), rotl(x,b)) ^ rotl(x,d)
  mux(s,a,b) = (s&a)|(~s&b)
pre-whiten x ^= k; post-whiten x ^= rotl(k,13)  (same as search_b28.py)

Writes fast_battery/candidates/hyb28_mu5_234/ {model.py, impl.c, rtl.v,
meta.json} with C-vs-Python-style bit-exact self-checks (scalar ref vs
bundle mix 2000 vectors + mix_np vector agreement 1000 vectors), mirroring
gen_x6.py.
"""
import importlib.util
import json
import os

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
M64 = (1 << 64) - 1
NAME = "hyb28_mu5_234"
Z = 2.34
D = 20
STAGES = [(48, 8, 49, 10), (42, 41, 48, 55), (5, 45, 43, 14),
          (49, 12, 1, 63), (31, 2, 16, 39)]


def rotl_py(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64


def ref_mix(stages, v, k):
    x = (v ^ k) & M64
    for (s, a, b, d) in stages:
        m = ((rotl_py(x, s) & rotl_py(x, a)) |
             ((~rotl_py(x, s) & M64) & rotl_py(x, b))) & M64
        x = (x ^ m ^ rotl_py(x, d)) & M64
    return (x ^ rotl_py(k, 13)) & M64


def rotl_v(x, r):
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model(name, stages, z):
    L = ['"""%s: batch-28 MU5 MUX-gate 5-stage cascade (triage-exact DIFF z=%.2f, LIN proxy D=%d)."""' % (name, z, D)]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (stages,))
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def _mux(s, a, b):")
    L.append("    return ((s & a) | ((~s) & b)) & M64")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for (s, a, b, d) in STAGES:")
    L.append("        x = (x ^ _mux(_rotl(x, s), _rotl(x, a), _rotl(x, b)) ^ _rotl(x, d)) & M64")
    L.append("    return ((x ^ _rotl(k, 13))) & M64")
    L.append("def mix(v, k):")
    L.append("    return int(mix_np(np.uint64(v), np.uint64(k)))")
    return "\n".join(L) + "\n"


def gen_c(name, stages, z):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63;",
         "    return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "// %s: batch-28 MU5 MUX-gate 5-stage cascade (triage z=%.2f)" % (name, z),
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for (s, a, b, d) in stages:
        L.append("    x ^= ((rotl64(x,%d) & rotl64(x,%d)) | (~rotl64(x,%d) & rotl64(x,%d))) ^ rotl64(x,%d);"
                 % (s, a, s, b, d))
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl(name, stages, z):
    L = ["// %s: batch-28 MU5 MUX-gate 5-stage cascade (triage z=%.2f)" % (name, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, (s, a, b, d) in enumerate(stages):
        pj = "x%d" % j
        L.append("    wire [63:0] m%d = ((%s) & (%s)) | ((~(%s)) & (%s));" % (
            j, rotl_v(pj, s), rotl_v(pj, a), rotl_v(pj, s), rotl_v(pj, b)))
        L.append("    wire [63:0] x%d = %s ^ m%d ^ (%s);" % (j + 1, pj, j, rotl_v(pj, d)))
    L.append("    assign out = x%d ^ %s;" % (len(stages), rotl_v("key", 13)))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    d = os.path.join(FB, NAME)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "model.py"), "w").write(gen_model(NAME, STAGES, Z))
    open(os.path.join(d, "impl.c"), "w").write(gen_c(NAME, STAGES, Z))
    open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(NAME, STAGES, Z))
    spec = importlib.util.spec_from_file_location("m_" + NAME, os.path.join(d, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rng = __import__("random").Random(0xB28)
    for _ in range(2000):
        v, k = rng.getrandbits(64), rng.getrandbits(64)
        assert m.mix(v, k) == ref_mix(STAGES, v, k), (hex(v), hex(k))
    import numpy as np
    V = np.array([rng.getrandbits(64) for _ in range(1000)], dtype=np.uint64)
    K = np.array([rng.getrandbits(64) for _ in range(1000)], dtype=np.uint64)
    np.testing.assert_array_equal(
        m.mix_np(V, K),
        np.array([ref_mix(STAGES, int(v), int(k)) for v, k in zip(V, K)], dtype=np.uint64))
    goldens = [{"val": hex(v), "key": hex(k), "out": hex(m.mix(v, k))}
               for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]]
    meta = {
        "name": NAME,
        "description": "batch-28 MU5 5-stage MUX-gate cascade (triage-exact DIFF z=%.2f, LIN proxy D=%d, best of 19/40 KEEP)" % (Z, D),
        "screen_keys": ["0x123456789abcdef0", "0x0"],
        "practrand_keys": ["0x123456789abcdef0", "0x0"],
        "goldens": goldens,
        "rtl_top": NAME,
        "triage_z": Z,
        "stages": STAGES,
    }
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    print("wrote bundle %s triage-z=%.2f bit-exact 2000/2000 + vec 1000/1000" % (NAME, Z), flush=True)


if __name__ == "__main__":
    main()
