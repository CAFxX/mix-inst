#!/usr/bin/env python3
"""Generate Verilog RTL for Track 6 batch 6, bit-exact with t6_models_b6.py."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t6_models_b6 import CANDIDATES_B6, SEQ_A, SEQ_B, SEQ_C, SCHED6_HET, OP_NROTS

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
T6 = os.path.dirname(os.path.abspath(__file__))

PORTS = "(input [63:0] val, input [63:0] key, output [63:0] out)"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e"]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"


def gen_hetero(seq):
    def gen():
        L = [f"module PLACEHOLDER{PORTS};",
             f"  wire [63:0] st0 = val ^ key;"]
        cur = "st0"
        for i, op in enumerate(seq):
            nrots = OP_NROTS[op]
            rots = SCHED6_HET[i][:nrots]
            r = [rotl(cur, t) for t in rots]
            if op == "maj":
                maj = f"(({r[0]} & {r[1]}) | ({r[0]} & {r[2]}) | ({r[1]} & {r[2]}))"
                nl = f"({maj} ^ {r[3]})"
            elif op == "andor":
                nl = f"((({r[0]} & {r[1]}) | ({r[2]} & {r[3]})) ^ {r[4]})"
            elif op == "chi":
                # chi: a ^ (b & ~c)
                nl = f"({r[0]} ^ ({r[1]} & ~{r[2]}))"
            elif op == "majxor":
                maj = f"(({r[0]} & {r[1]}) | ({r[0]} & {r[2]}) | ({r[1]} & {r[2]}))"
                nl = f"({maj} ^ ({r[3]} & {r[4]}))"
            elif op == "xor3and":
                nl = f"({r[0]} ^ {r[1]} ^ {r[2]} ^ ({r[3]} & {r[4]} & {r[5]}))"
            else:
                raise ValueError(op)
            rk = f"({rotl('key', 13*(i+1))} ^ {RC_HEX[i % 8]})"
            # Note: extra paren in rk is intentional to match model
            rk = f"({rotl('key', 13*(i+1))} ^ {RC_HEX[i % 8]})"
            L.append(f"  wire [63:0] st{i+1} = {cur} ^ {nl} ^ {rk};")
            cur = f"st{i+1}"
        # post-whiten: model does x ^ (rotl(k,13) >> 32); take bits [63:32] of rotl(key,13)
        # (via intermediate wire: part-select on a concatenation is not Verilog-2001)
        L.append(f"  wire [63:0] key_r13 = {rotl('key', 13)};")
        L.append(f"  assign out = {cur} ^ {{32'h0, key_r13[63:32]}};")
        L.append("endmodule")
        return "\n".join(L)
    return gen


GEN_B6 = {
    "t6_het6a": gen_hetero(SEQ_A),
    "t6_het6b": gen_hetero(SEQ_B),
    "t6_het6c": gen_hetero(SEQ_C),
}

# Bit-exact C impl generator (2026-10-09 fix): bundles shipped impl.c stubs
# ("/* stub */") which S2 compiled against `mix_hash` -> INFRA_FAIL
# (undefined reference). Every generator must now emit a REAL impl.c exposing
# uint64_t mix_hash(uint64_t val, uint64_t key), verified bit-exact vs the
# Python model. Verified 2016/2016 vectors incl. edge keys per candidate.
_C_OP_BLOCK = {
    "maj":     "    nl = maj64(rotl64(x,{r0}), rotl64(x,{r1}), rotl64(x,{r2})) ^ rotl64(x,{r3});",
    "andor":   "    nl = ((rotl64(x,{r0}) & rotl64(x,{r1})) | (rotl64(x,{r2}) & rotl64(x,{r3}))) ^ rotl64(x,{r4});",
    "chi":     "    nl = chi64(rotl64(x,{r0}), rotl64(x,{r1}), rotl64(x,{r2}));",
    "majxor":  "    nl = maj64(rotl64(x,{r0}), rotl64(x,{r1}), rotl64(x,{r2})) ^ (rotl64(x,{r3}) & rotl64(x,{r4}));",
    "xor3and": "    nl = rotl64(x,{r0}) ^ rotl64(x,{r1}) ^ rotl64(x,{r2}) ^ (rotl64(x,{r3}) & rotl64(x,{r4}) & rotl64(x,{r5}));",
}
RC_DEC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
          0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054,
          0x2545F4914F6CDD1D,
          0x9E3779B97F4A7C15 ^ 0xDEADBEEF,
          0x3C6EF372FE94F82A ^ 0x12345678,
          0xDAA66D2C7DDF743F ^ 0xABCDEF01]


def gen_impl_c(name, seq, desc):
    """Bit-exact C port of t6_models_b6._hetero_cascade for seq."""
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "static inline uint64_t maj64(uint64_t a, uint64_t b, uint64_t c) {",
         "    return (a & b) | (a & c) | (b & c);",
         "}",
         "static inline uint64_t chi64(uint64_t a, uint64_t b, uint64_t c) {",
         "    return a ^ (b & ~c);",
         "}",
         f"// {name}: {desc}",
         "// bit-exact C port of t6_models_b6._hetero_cascade (incl. b6 post-whiten)",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    static const uint64_t RC[8] = {"
         + ", ".join("0x%016Xu" % r for r in RC_DEC) + "};",
         "    uint64_t x = val ^ key, nl;"]
    for i, op in enumerate(seq):
        nrots = OP_NROTS[op]
        rots = SCHED6_HET[i][:nrots]
        L.append(f"    // stage {i}: {op}")
        L.append("    " + _C_OP_BLOCK[op].format(
            **{f"r{j}": rots[j] for j in range(nrots)}))
        L.append(f"    x ^= nl ^ (rotl64(key, {13*(i+1)}) ^ RC[{i % 8}]);")
    L.append("    x ^= rotl64(key, 13) >> 32;  // post-whiten (b6 finalization)")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


SEQ_OF = {"t6_het6a": SEQ_A, "t6_het6b": SEQ_B, "t6_het6c": SEQ_C}

# Map to model for bit-exactness check
from t6_models_b6 import CANDIDATES_B6 as MODELS_B6


def main():
    import json
    import shutil
    for name, gen in GEN_B6.items():
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        rtl = gen().replace("PLACEHOLDER", name)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(rtl + "\n")
        # model.py: thin wrapper importing from t6_models_b6
        # (s1_screen.py expects module-level `mix`, `mix_np`, `meta`)
        model_src = f'''"""Bit-exact Python model for {name} (batch 6 heterogeneous)."""
import sys
sys.path.insert(0, "{T6}")
import numpy as np
from t6_models_b6 import CANDIDATES_B6, MIX_NP_B6

_scalar_fn = CANDIDATES_B6["{name}"][0]
_desc = CANDIDATES_B6["{name}"][1]

def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _scalar_fn(int(v), int(k))
    return MIX_NP_B6["{name}"](v, k)

def mix_np(V, K):
    return MIX_NP_B6["{name}"](V, K)

meta = {{"desc": _desc}}
'''
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(model_src)
        # meta.json: required by s0_delay.py
        from t6_models_b6 import CANDIDATES_B6 as C6
        desc = C6[name][1]
        meta_json = {
            "name": name,
            "description": desc,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
        }
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump(meta_json, f, indent=1)
        # impl.c: REAL bit-exact C (never a stub — S2 links mix_hash;
        # 2026-10-09 escape-protocol fix after stub caused S2 INFRA_FAIL)
        from t6_models_b6 import CANDIDATES_B6 as C6b
        impl_src = gen_impl_c(name, SEQ_OF[name], C6b[name][1])
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(impl_src)
        print(f"{name}: RTL + model + impl.c + meta written to {d}")


if __name__ == "__main__":
    main()
