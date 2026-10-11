#!/usr/bin/env python3
"""Generate bundles for Track 5 batch-25 X6 (XOR-fed chain, 6-stage) winners.

Reads hybrid/batch21/search_b25_results.json, picks the TOP-N KEEPs of arm
X6 by triage z, and writes fast_battery/candidates/<name>/ with model.py
(mix scalar + mix_np vectorized -- the S1 driver requires both), impl.c,
rtl.v, meta.json.

XFC stage form: stages[i] = (a,b,s,e,c)
  i=0: u = rot(x,a) & rot(x,b); x = x ^ u ^ rot(x,c)
  i>0: u = rot(x,a) & (rot(u,s) ^ rot(x,e)); x = x ^ u ^ rot(x,c)
  pre-whiten x ^= k; post-whiten x ^= rotl(k,13)

Bit-exact check: bundle mix vs an independent pure-Python scalar reference
on 2000 random vectors, plus mix_np scalar/vector agreement.
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


def ref_mix(stages, v, k):
    x = (v ^ k) & M64
    a, b, s, e, c = stages[0]
    u = (rotl_py(x, a) & rotl_py(x, b)) & M64
    x = (x ^ u ^ rotl_py(x, c)) & M64
    for (a, b, s, e, c) in stages[1:]:
        u = (rotl_py(x, a) & ((rotl_py(u, s) ^ rotl_py(x, e)) & M64)) & M64
        x = (x ^ u ^ rotl_py(x, c)) & M64
    return (x ^ rotl_py(k, 13)) & M64


def rotl_v(x, r):
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model(name, stages, z):
    L = ['"""%s: batch-25 X6 XOR-fed-chain 6-stage cascade (triage-exact DIFF z=%.2f)."""' % (name, z)]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (stages,))
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    a, b, s, e, c = STAGES[0]")
    L.append("    u = (_rotl(x, a) & _rotl(x, b)) & M64")
    L.append("    x = (x ^ u ^ _rotl(x, c)) & M64")
    L.append("    for (a, b, s, e, c) in STAGES[1:]:")
    L.append("        u = (_rotl(x, a) & ((_rotl(u, s) ^ _rotl(x, e)) & M64)) & M64")
    L.append("        x = (x ^ u ^ _rotl(x, c)) & M64")
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
         "// %s: batch-25 X6 6-stage XOR-fed chain (triage z=%.2f)" % (name, z),
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;",
         "    uint64_t u;"]
    a, b, s, e, c = stages[0]
    L.append("    u = rotl64(x,%d) & rotl64(x,%d);" % (a, b))
    L.append("    x ^= u ^ rotl64(x,%d);" % c)
    for (a, b, s, e, c) in stages[1:]:
        L.append("    u = rotl64(x,%d) & (rotl64(u,%d) ^ rotl64(x,%d));" % (a, s, e))
        L.append("    x ^= u ^ rotl64(x,%d);" % c)
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl(name, stages, z):
    L = ["// %s: batch-25 X6 6-stage XOR-fed chain (triage z=%.2f)" % (name, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;",
         ]
    a, b, s, e, c = stages[0]
    L.append("    wire [63:0] u0 = (%s) & (%s);" % (rotl_v("x0", a), rotl_v("x0", b)))
    L.append("    wire [63:0] x1 = x0 ^ u0 ^ (%s);" % rotl_v("x0", c))
    for j, (a, b, s, e, c) in enumerate(stages[1:], start=1):
        pj, uj = "x%d" % j, "u%d" % (j - 1)
        L.append("    wire [63:0] u%d = (%s) & ((%s) ^ (%s));" % (
            j, rotl_v(pj, a), rotl_v(uj, s), rotl_v(pj, e)))
        L.append("    wire [63:0] x%d = %s ^ u%d ^ (%s);" % (j + 1, pj, j, rotl_v(pj, c)))
    L.append("    assign out = x%d ^ %s;" % (len(stages), rotl_v("key", 13)))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    res = json.load(open(os.path.join(HERE, "search_b25_results.json")))
    cands = sorted([r for r in res if r.get("arm") == "X6" and r.get("keep")],
                   key=lambda r: r["z"])[:n]
    assert cands, "no X6 KEEP survivors"
    names = []
    for rank, win in enumerate(cands):
        stages = [tuple(s) for s in win["stages"]]
        assert len(stages) == 6 and all(len(s) == 5 for s in stages)
        z = win["z"]
        name = "hyb25_x6_%d" % int(z * 100)
        d = os.path.join(FB, name)
        if os.path.exists(d) and rank > 0:
            name = "hyb25_x6_%d_%d" % (int(z * 100), rank)
            d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, z))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages, z))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages, z))
        spec = importlib.util.spec_from_file_location("m_" + name, os.path.join(d, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        rng = __import__("random").Random(0xB25 + rank)
        for _ in range(2000):
            v, k = rng.getrandbits(64), rng.getrandbits(64)
            assert m.mix(v, k) == ref_mix(stages, v, k), (hex(v), hex(k))
        import numpy as np
        V = np.array([rng.getrandbits(64) for _ in range(1000)], dtype=np.uint64)
        K = np.array([rng.getrandbits(64) for _ in range(1000)], dtype=np.uint64)
        np.testing.assert_array_equal(
            m.mix_np(V, K),
            np.array([ref_mix(stages, int(v), int(k)) for v, k in zip(V, K)], dtype=np.uint64))
        goldens = [{"val": hex(v), "key": hex(k), "out": hex(m.mix(v, k))}
                   for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]]
        meta = {
            "name": name,
            "description": "batch-25 X6 6-stage XOR-fed chain (triage-exact DIFF z=%.2f, rank %d)" % (z, rank),
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
            "triage_z": z,
            "triage_killkey": hex(win["killkey"]) if win.get("killkey") else None,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        print("wrote bundle %s triage-z=%.2f bit-exact 2000/2000 + vec 1000/1000" % (name, z), flush=True)
        names.append(name)
    open(os.path.join(HERE, "x6_escalation_names.json"), "w").write(json.dumps(names, indent=1))


if __name__ == "__main__":
    main()
