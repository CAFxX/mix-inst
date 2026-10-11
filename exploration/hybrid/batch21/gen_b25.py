#!/usr/bin/env python3
"""Generate bundle for Track 5 batch-25 PNL winner.

Reads hybrid/batch21/search_b25_results.json, picks the best KEEP of the
requested arm (default P7), and writes fast_battery/candidates/<name>/ with
model.py (mix scalar + mix_np vectorized -- the S1 driver requires both),
impl.c, rtl.v, meta.json. Bit-exact check: bundle mix vs an independent
pure-Python scalar reference on 2000 random vectors.
"""
import importlib.util
import json
import os
import sys

HERE = "/home/hatch/workspace/mix/exploration/hybrid/batch21"
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
M64 = (1 << 64) - 1


def rotl_py(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64


def ref_mix(stages, masks, v, k):
    x = (v ^ k) & M64
    for (a, b, c, d), mk in zip(stages, masks):
        x = (x ^ (((rotl_py(x, a) & rotl_py(x, b)) & mk) ^ rotl_py(x, c) ^ rotl_py(x, d))) & M64
    return (x ^ rotl_py(k, 13)) & M64


def rotl_v(x, r):
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model(name, stages, masks, z):
    L = ['"""%s: batch-25 PNL %d-stage partial-nonlinear-layer cascade '
         '(triage-exact DIFF z=%.2f)."""' % (name, len(stages), z)]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (stages,))
    L.append("MASKS = [%s]" % ", ".join("np.uint64(%#x)" % m for m in masks))
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for (a, b, c, d), mk in zip(STAGES, MASKS):")
    L.append("        x = (x ^ (((_rotl(x, a) & _rotl(x, b)) & mk) ^ _rotl(x, c) ^ _rotl(x, d))) & M64")
    L.append("    return ((x ^ _rotl(k, 13))) & M64")
    L.append("def mix(v, k):")
    L.append("    return int(mix_np(np.uint64(v), np.uint64(k)))")
    return "\n".join(L) + "\n"


def gen_c(name, stages, masks, z):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63;",
         "    return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "// %s: batch-25 PNL %d-stage (triage z=%.2f)" % (name, len(stages), z),
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for (a, b, c, d), mk in zip(stages, masks):
        L.append("    x ^= ((rotl64(x,%d) & rotl64(x,%d)) & 0x%016xULL) ^ rotl64(x,%d) ^ rotl64(x,%d);"
                 % (a, b, mk, c, d))
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl(name, stages, masks, z):
    L = ["// %s: batch-25 PNL %d-stage (triage z=%.2f)" % (name, len(stages), z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, ((a, b, c, d), mk) in enumerate(zip(stages, masks)):
        prev = "x%d" % j
        L.append("    wire [63:0] x%d = %s ^ (((%s) & (%s)) & 64'h%016x) ^ (%s) ^ (%s);" % (
            j + 1, prev, rotl_v(prev, a), rotl_v(prev, b), mk,
            rotl_v(prev, c), rotl_v(prev, d)))
    L.append("    assign out = x%d ^ %s;" % (len(stages), rotl_v("key", 13)))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "P7"
    res = json.load(open(os.path.join(HERE, "search_b25_results.json")))
    cands = [r for r in res if r.get("arm") == arm and r.get("keep")]
    assert cands, "no KEEP survivors in arm %s" % arm
    win = min(cands, key=lambda r: r["z"])
    stages = [tuple(s) for s in win["stages"]]
    masks = [int(m, 16) for m in win["masks"]]
    z = win["z"]
    name = "hyb25_%s_%d" % (arm.lower(), int(z * 100))
    d = os.path.join(FB, name)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, masks, z))
    open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages, masks, z))
    open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages, masks, z))
    spec = importlib.util.spec_from_file_location("m_" + name, os.path.join(d, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rng = __import__("random").Random(0xB25)
    for _ in range(2000):
        v, k = rng.getrandbits(64), rng.getrandbits(64)
        assert m.mix(v, k) == ref_mix(stages, masks, v, k), (hex(v), hex(k))
    # vectorized vs scalar agreement
    import numpy as np
    V = np.array([rng.getrandbits(64) for _ in range(1000)], dtype=np.uint64)
    K = np.array([rng.getrandbits(64) for _ in range(1000)], dtype=np.uint64)
    assert all(int(a) == ref_mix(stages, masks, int(v), int(k))
               for a, v, k in zip(m.mix_np(V, K), V, K))
    goldens = [{"val": hex(v), "key": hex(k), "out": hex(m.mix(v, k))}
               for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]]
    meta = {
        "name": name,
        "description": "batch-25 PNL %d-stage partial-nonlinear-layer (triage-exact DIFF z=%.2f, LIN proxy D=%s)" % (
            len(stages), z, win.get("lin_D")),
        "screen_keys": ["0x123456789abcdef0", "0x0"],
        "practrand_keys": ["0x123456789abcdef0", "0x0"],
        "goldens": goldens,
        "rtl_top": name,
        "triage": {"z": z, "stages": stages,
                   "masks": [hex(x) for x in masks]},
    }
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    print("wrote bundle %s bit-exact 2000/2000 scalar + 1000/1000 vector vs reference" % name,
          flush=True)


if __name__ == "__main__":
    main()
