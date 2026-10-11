#!/usr/bin/env python3
"""Batch-10 hybrid generator: XOR-AND restructured stage.

Restructure for parallelism:
  Old: x ^= (ra & rb) ^ rc  = AND(1u) -> XOR(1u) -> XOR(1u) = 3u/stage
  New: x ^= ra ^ (rb & rc)  = [XOR(ra) || AND(rb,rc)](1u) -> XOR(1u) = 2u/stage

6 stages x 2u = 12u + overhead. Target ~15u.

Uses al_and6a triplets (a,b,c) mapped to (ra, rb&rc) structure.
"""
import json
import os

import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
OUT = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

TRIPLETS = [(1, 2, 13), (7, 19, 5), (3, 11, 29),
            (17, 31, 7), (11, 23, 37), (19, 41, 23)]

KEYS = ["0x123456789abcdef0", "0x0"]
NAME = "hyb10_xorand_6"
DESC = "6-stage XOR-AND: x ^= ra ^ (rb & rc) (parallel structure)"


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def model_hash(val, key):
    x = np.uint64(val) ^ np.uint64(key)
    k = np.uint64(key)
    for (a, b, c) in TRIPLETS:
        ra, rb, rc = rotl(x, a), rotl(x, b), rotl(x, c)
        x = (x ^ ra ^ (rb & rc)) & M64
    x = (x ^ rotl(k, 13)) & M64
    return int(x)


def rotl_v(sig, r):
    if r % 64 == 0:
        return sig
    r %= 64
    return "{%s[%d:0], %s[63:%d]}" % (sig, 64 - 1 - r, sig, 64 - r)


def build():
    d = os.path.join(OUT, NAME)
    os.makedirs(d, exist_ok=True)

    L = [f"// {NAME}: {DESC}",
         "#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for i, (a, b, c) in enumerate(TRIPLETS):
        L.append(f"    {{ uint64_t ra=rotl64(x,{a}),rb=rotl64(x,{b}),rc=rotl64(x,{c});")
        L.append("      x ^= ra ^ (rb & rc); }")
    L += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    open(os.path.join(d, "impl.c"), "w").write("\n".join(L) + "\n")

    V = [f"// {NAME}: {DESC}",
         f"module {NAME}(",
         "    input [63:0] val,", "    input [63:0] key,",
         "    output [63:0] out", ");",
         "    wire [63:0] x0 = val ^ key;"]
    cur = "x0"
    for i, (a, b, c) in enumerate(TRIPLETS):
        V.append(f"    wire [63:0] s{i}a = {rotl_v(cur, a)};")
        V.append(f"    wire [63:0] s{i}b = {rotl_v(cur, b)};")
        V.append(f"    wire [63:0] s{i}c = {rotl_v(cur, c)};")
        V.append(f"    wire [63:0] t{i} = {cur} ^ s{i}a ^ (s{i}b & s{i}c);")
        cur = f"t{i}"
    V += ["    wire [63:0] kr = {key[50:0], key[63:51]};",
          f"    assign out = {cur} ^ kr;",
          "endmodule"]
    open(os.path.join(d, "rtl.v"), "w").write("\n".join(V) + "\n")

    P = [f'"""{NAME}: {DESC}."""',
         "import numpy as np", "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)", "",
         "def _rotl(x, r):",
         "    r %= 64",
         "    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64",
         "",
         "def _mix_core(x, k):"]
    for (a, b, c) in TRIPLETS:
        P.append(f"    ra,rb,rc = _rotl(x,{a}),_rotl(x,{b}),_rotl(x,{c})")
        P.append("    x = (x ^ ra ^ (rb & rc)) & M64")
    P += ["    return (x ^ _rotl(k, 13)) & M64", "",
          "def mix_hash(val, key):",
          "    return int(_mix_core(np.uint64(val) ^ np.uint64(key), np.uint64(key)))",
          "",
          "def mix_np(V, K):",
          "    V = np.asarray(V, dtype=np.uint64)",
          "    K = np.asarray(K, dtype=np.uint64)",
          "    return _mix_core(V ^ K, K)",
          "",
          "def mix(v, k):", "    return mix_hash(v, k)"]
    open(os.path.join(d, "model.py"), "w").write("\n".join(P) + "\n")

    goldens = []
    for vk, kk in [("0x0", KEYS[0]), (KEYS[0], "0x0")]:
        out = model_hash(int(vk, 16), int(kk, 16))
        goldens.append({"val": vk, "key": kk, "out": hex(out)})
    meta = {"name": NAME, "description": DESC, "screen_keys": KEYS,
            "practrand_keys": KEYS, "goldens": goldens, "rtl_top": NAME}
    open(os.path.join(d, "meta.json"), "w").write(json.dumps(meta, indent=1) + "\n")
    print(f"generated {NAME}: goldens {goldens[0]['out']}, {goldens[1]['out']}")


if __name__ == "__main__":
    build()
    print("batch-10 generation complete")
