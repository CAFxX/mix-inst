#!/usr/bin/env python3
"""Batch-19 generator: maj+chi hybrid bundles from search_mc_results.json.

Stage forms (proven lineages):
  maj(a,b,c): x ^= maj(x, rotl(x,a), rotl(x,b)) ^ rotl(x,c)   [fz22_maj5d form]
  chi(a,b,c): x ^= ((~rotl(x,a)) & rotl(x,b)) ^ rotl(x,c)     [al_chi8 form]
Pre: x = val ^ key. No post key xor (maj5d form).

Emits per candidate into fast_battery/candidates/<name>:
  impl.c, rtl.v, model.py (mix/mix_np/mix_hash aliases -- S1 driver REQUIRES
  module attribute `mix`), meta.json.
"""
import json
import os
import sys

import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
OUT = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
RES = "/home/hatch/workspace/mix/exploration/hybrid/batch19/search_mc_results.json"

KEYS = ["0x123456789abcdef0", "0x0"]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def apply_stage_np(x, st):
    kind, a, b, c = st
    ra, rb, rc = rotl(x, a), rotl(x, b), rotl(x, c)
    if kind == 'maj':
        m = (x & ra) | (x & rb) | (ra & rb)
        return (x ^ m ^ rc) & M64
    else:  # chi
        return (x ^ ((~ra) & rb) ^ rc) & M64


def model_hash(stages, val, key):
    x = np.uint64(val) ^ np.uint64(key)
    for st in stages:
        x = apply_stage_np(x, st)
    return int(x)


def rotl_v(sig, r):
    r %= 64
    if r == 0:
        return sig
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63 - r, sig, 64 - r)


def stage_desc(st):
    return f"{st[0]}({st[1]},{st[2]},{st[3]})"


def build(name, stages, pattern, proxy_z, proxy_cost):
    desc = f"batch-19 maj+chi hybrid [{pattern}]: " + \
        " -> ".join(stage_desc(s) for s in stages) + \
        f" (proxy z={proxy_z:.1f}, est={proxy_cost:.2f}u)"
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)

    # --- impl.c ---
    L = [f"// {name}: {desc}",
         "#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "static inline uint64_t maj64(uint64_t a, uint64_t b, uint64_t c) {",
         "    return (a & b) | (b & c) | (a & c); }",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for (kind, a, b, c) in stages:
        L.append(f"    {{ uint64_t ra=rotl64(x,{a}),rb=rotl64(x,{b}),rc=rotl64(x,{c});")
        if kind == 'maj':
            L.append("      x ^= maj64(x,ra,rb) ^ rc; }")
        else:
            L.append("      x ^= ((~ra)&rb) ^ rc; }")
    L += ["    return x;", "}"]
    open(os.path.join(d, "impl.c"), "w").write("\n".join(L) + "\n")

    # --- rtl.v ---
    V = [f"// {name}: {desc}",
         f"module {name}(",
         "    input [63:0] val,", "    input [63:0] key,",
         "    output [63:0] out", ");",
         "    wire [63:0] x0 = val ^ key;"]
    cur = "x0"
    for i, (kind, a, b, c) in enumerate(stages):
        V.append(f"    wire [63:0] s{i}a = {rotl_v(cur, a)};")
        V.append(f"    wire [63:0] s{i}b = {rotl_v(cur, b)};")
        V.append(f"    wire [63:0] s{i}c = {rotl_v(cur, c)};")
        if kind == 'maj':
            V.append(f"    wire [63:0] m{i} = ({cur} & s{i}a) | ({cur} & s{i}b) | (s{i}a & s{i}b);")
            V.append(f"    wire [63:0] t{i} = {cur} ^ m{i} ^ s{i}c;")
        else:
            V.append(f"    wire [63:0] m{i} = (~s{i}a) & s{i}b;")
            V.append(f"    wire [63:0] t{i} = {cur} ^ m{i} ^ s{i}c;")
        cur = f"t{i}"
    V += [f"    assign out = {cur};", "endmodule"]
    open(os.path.join(d, "rtl.v"), "w").write("\n".join(V) + "\n")

    # --- model.py ---
    P = [f'"""{name}: {desc}."""',
         "import numpy as np", "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
         "STAGES = %r" % (list(stages),), "",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64",
         "",
         "def _maj(a,b,c): return (a & b) | (b & c) | (a & c)",
         "",
         "def _stage(x, st):",
         "    kind, a, b, c = st",
         "    ra, rb, rc = _rotl(x,a), _rotl(x,b), _rotl(x,c)",
         "    if kind == 'maj':",
         "        return (x ^ _maj(x,ra,rb) ^ rc) & M64",
         "    return (x ^ ((~ra) & rb) ^ rc) & M64",
         "",
         "def _mix_core(x):",
         "    for st in STAGES:",
         "        x = _stage(x, st)",
         "    return x & M64",
         "",
         "def mix_hash(val, key):",
         "    return int(_mix_core(np.uint64(val) ^ np.uint64(key)))",
         "",
         "def mix_np(V, K):",
         "    V = np.asarray(V, dtype=np.uint64)",
         "    K = np.asarray(K, dtype=np.uint64)",
         "    return _mix_core(V ^ K)",
         "",
         "def mix(v, k):", "    return mix_hash(v, k)"]
    open(os.path.join(d, "model.py"), "w").write("\n".join(P) + "\n")

    goldens = []
    for vk, kk in [("0x0", KEYS[0]), (KEYS[0], "0x0")]:
        out = model_hash(stages, int(vk, 16), int(kk, 16))
        goldens.append({"val": vk, "key": kk, "out": hex(out)})
    meta = {"name": name, "description": desc, "screen_keys": KEYS,
            "practrand_keys": KEYS, "goldens": goldens, "rtl_top": name,
            "pattern": pattern, "proxy_z": proxy_z, "proxy_cost_u": proxy_cost,
            "stages": [list(s) for s in stages]}
    open(os.path.join(d, "meta.json"), "w").write(json.dumps(meta, indent=1) + "\n")
    return goldens


def main():
    results = json.load(open(RES))
    names = []
    for i, r in enumerate(results):
        name = f"hyb19_mc{chr(ord('A')+i)}"
        stages = [tuple(s) for s in r['stages']]
        goldens = build(name, stages, r['pattern'], r['z'], r['cost'])
        names.append(name)
        print(f"generated {name} [{r['pattern']}] proxy_z={r['z']:.1f} "
              f"est={r['cost']:.2f}u goldens={goldens[0]['out']}")
    print("batch-19 generation complete:", names)


if __name__ == "__main__":
    main()
