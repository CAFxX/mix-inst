#!/usr/bin/env python3
"""Batch-20 generator: fused maj+chi hybrid bundles from search_b20_results.json.

Stage forms (from s2proxy_b20.py; pre: x = val ^ key; no post key xor):
  fm: x ^= maj(x,ra,rb) ^ rotl(x,c) ^ chi(rd,re) ^ rotl(x,f)
      maj(x,ra,rb) = (x&ra)|(x&rb)|(ra&rb); chi(rd,re) = (~rd)&re
  dm: x ^= maj(x,ra,rb) ^ rotl(x,c) ^ maj(x,rd,re) ^ rotl(x,f)
  rf: x  = maj(x,ra,rb) ^ chi(rd,re) ^ rotl(x,f)   (replacement form)

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
RES = "/home/hatch/workspace/mix/exploration/hybrid/batch20/search_b20_results.json"

KEYS = ["0x123456789abcdef0", "0x0"]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def apply_stage_np(x, st):
    kind, a, b, c, d, e, f = st
    ra, rb, rc = rotl(x, a), rotl(x, b), rotl(x, c)
    if kind == 'fm':
        m = (x & ra) | (x & rb) | (ra & rb)
        rd, re, rf = rotl(x, d), rotl(x, e), rotl(x, f)
        ch = (~rd) & re
        return (x ^ m ^ rc ^ ch ^ rf) & M64
    if kind == 'dm':
        m1 = (x & ra) | (x & rb) | (ra & rb)
        rd, re, rf = rotl(x, d), rotl(x, e), rotl(x, f)
        m2 = (x & rd) | (x & re) | (rd & re)
        return (x ^ m1 ^ rc ^ m2 ^ rf) & M64
    if kind == 'rf':
        m = (x & ra) | (x & rb) | (ra & rb)
        rd, re, rf = rotl(x, d), rotl(x, e), rotl(x, f)
        ch = (~rd) & re
        return (m ^ ch ^ rf) & M64
    raise ValueError(st)


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
    return "%s(%s)" % (st[0], ",".join(str(v) for v in st[1:]))


def build(name, stages, hyp, proxy_z, proxy_cost):
    desc = f"batch-20 fused maj+chi [{hyp}]: " + \
        " -> ".join(stage_desc(s) for s in stages) + \
        f" (hill-climbed proxy z={proxy_z:.1f}, est={proxy_cost:.2f}u)"
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
    for st in stages:
        kind, a, b, c, dd, e, f = st
        L.append(f"    {{ uint64_t ra=rotl64(x,{a}),rb=rotl64(x,{b}),"
                 f"rc=rotl64(x,{c}),rd=rotl64(x,{dd}),re=rotl64(x,{e}),"
                 f"rf=rotl64(x,{f});")
        if kind == 'fm':
            L.append("      x ^= maj64(x,ra,rb) ^ rc ^ ((~rd)&re) ^ rf; }")
        elif kind == 'dm':
            L.append("      x ^= maj64(x,ra,rb) ^ rc ^ maj64(x,rd,re) ^ rf; }")
        else:  # rf
            L.append("      x = maj64(x,ra,rb) ^ ((~rd)&re) ^ rf; }")
    L += ["    return x;", "}"]
    open(os.path.join(d, "impl.c"), "w").write("\n".join(L) + "\n")

    # --- rtl.v ---
    V = [f"// {name}: {desc}",
         f"module {name}(",
         "    input [63:0] val,", "    input [63:0] key,",
         "    output [63:0] out", ");",
         "    wire [63:0] x0 = val ^ key;"]
    cur = "x0"
    for i, st in enumerate(stages):
        kind, a, b, c, dd, e, f = st
        V.append(f"    wire [63:0] s{i}a = {rotl_v(cur, a)};")
        V.append(f"    wire [63:0] s{i}b = {rotl_v(cur, b)};")
        V.append(f"    wire [63:0] s{i}c = {rotl_v(cur, c)};")
        V.append(f"    wire [63:0] s{i}d = {rotl_v(cur, dd)};")
        V.append(f"    wire [63:0] s{i}e = {rotl_v(cur, e)};")
        V.append(f"    wire [63:0] s{i}f = {rotl_v(cur, f)};")
        V.append(f"    wire [63:0] m1{i} = ({cur} & s{i}a) | ({cur} & s{i}b) | (s{i}a & s{i}b);")
        if kind == 'fm':
            V.append(f"    wire [63:0] ch{i} = (~s{i}d) & s{i}e;")
            V.append(f"    wire [63:0] t{i} = {cur} ^ m1{i} ^ s{i}c ^ ch{i} ^ s{i}f;")
        elif kind == 'dm':
            V.append(f"    wire [63:0] m2{i} = ({cur} & s{i}d) | ({cur} & s{i}e) | (s{i}d & s{i}e);")
            V.append(f"    wire [63:0] t{i} = {cur} ^ m1{i} ^ s{i}c ^ m2{i} ^ s{i}f;")
        else:  # rf
            V.append(f"    wire [63:0] ch{i} = (~s{i}d) & s{i}e;")
            V.append(f"    wire [63:0] t{i} = m1{i} ^ ch{i} ^ s{i}f;")
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
         "    kind, a, b, c, d, e, f = st",
         "    ra, rb, rc = _rotl(x,a), _rotl(x,b), _rotl(x,c)",
         "    rd, re, rf = _rotl(x,d), _rotl(x,e), _rotl(x,f)",
         "    m1 = _maj(x,ra,rb)",
         "    if kind == 'fm':",
         "        return (x ^ m1 ^ rc ^ ((~rd) & re) ^ rf) & M64",
         "    if kind == 'dm':",
         "        return (x ^ m1 ^ rc ^ _maj(x,rd,re) ^ rf) & M64",
         "    return (m1 ^ ((~rd) & re) ^ rf) & M64",
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
            "hyp": hyp, "proxy_z": proxy_z, "proxy_cost_u": proxy_cost,
            "stages": [list(s) for s in stages]}
    open(os.path.join(d, "meta.json"), "w").write(json.dumps(meta, indent=1) + "\n")
    return goldens


def main():
    results = json.load(open(RES))
    idx = sys.argv[1:] if len(sys.argv) > 1 else None
    names = []
    for i, r in enumerate(results):
        if idx and str(i) not in idx:
            continue
        hyp = r.get('hyp', '?')
        name = f"hyb20_{hyp}{chr(ord('a')+i)}"
        stages = [tuple(s) for s in r['stages']]
        goldens = build(name, stages, hyp, r['z'], r['cost'])
        names.append(name)
        print(f"generated {name} [{hyp}] proxy_z={r['z']:.1f} "
              f"est={r['cost']:.2f}u goldens={goldens[0]['out']}")
    print("batch-20 generation complete:", names)


if __name__ == "__main__":
    main()
