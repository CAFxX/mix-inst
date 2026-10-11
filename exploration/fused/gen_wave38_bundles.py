#!/usr/bin/env python3
"""Wave-38 stratified S0 sample bundle generator (track 8, inc 13).

Strata (pre-registered in wave38_screen.py header): min-z / median-z /
max-z / max-align / min-align / max-distinct / min-distinct / seeded-random.
Tie-resolution (recorded in supervisor heartbeat 2026-10-11T06:47Z): strata
collide on the same keep (try39 = min-z AND max-align; try27 = min-align AND
max-distinct; try116 = 2nd max-align AND min-distinct), so the sample is 8
DISTINCT keeps covering every stratum:
  try39  min-z (z=2.580) + max-align (a=5)
  try64  median-z (z=4.072)
  try4   max-z (z=9.930)
  try27  min-align (a=0) + max-distinct (d=18)
  try116 min-distinct (d=13) + 2nd max-align (a=5)
  try49  2nd min-align (a=0) + 2nd max-distinct (d=18)
  try90  seeded-random: random.Random(0x3838).choice(keeps) (z=5.280)
  try104 2nd-lowest distinct class (d=14, z=6.239)
Schedules are read verbatim from wave38_keeps.jsonl (no transcription).
Bundle format copied from new_constructions/gen_t6_b33.py (same form:
pre-whiten x^K, 6 stages x ^= (ra&rb)^rc, post ^rotl(K,13)).
Verification: C impl vs Python model bit-exact on 2000 seeded random pairs
per bundle, fail-loud.
"""
import ctypes
import importlib.util
import json
import os
import subprocess
import sys

FUSED = os.path.dirname(os.path.abspath(__file__))
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
SAMPLE_TRIES = [39, 64, 4, 27, 116, 49, 90, 104]


def rotl_v(x, r):
    if r % 64 == 0:
        return x
    return "{%s[%d:0], %s[63:%d]}" % (x, 63 - r, x, 64 - r)


def gen_model(stages, z):
    L = ['"""Wave-38 stratified sample: 6-stage AND-rotation cascade, exact '
         'frontier form (triage z=%.3f)."""' % z]
    L.append("import numpy as np")
    L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
    L.append("STAGES = %r" % (stages,))
    L.append("def _rotl(x, r):")
    L.append("    r %= 64")
    L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
    L.append("def mix_np(V, K):")
    L.append("    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
    L.append("    x = (x ^ k) & M64")
    L.append("    for a, b, c in STAGES:")
    L.append("        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c)) & M64")
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
         "// wave-38 stratified sample 6-stage AND schedule %s (triage z=%.3f)" % (name, z),
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for a, b, c in stages:
        L.append("    x ^= (rotl64(x,%d) & rotl64(x,%d)) ^ rotl64(x,%d);" % (a, b, c))
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


def gen_rtl(name, stages, z):
    L = ["// %s: wave-38 stratified sample 6-stage AND schedule (triage z=%.3f)" % (name, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, (a, b, c) in enumerate(stages):
        prev = "x%d" % j
        L.append("    wire [63:0] x%d = %s ^ (%s & %s) ^ %s;" % (
            j + 1, prev, rotl_v(prev, a), rotl_v(prev, b), rotl_v(prev, c)))
    L.append("    assign out = x6 ^ %s;" % rotl_v("key", 13))
    L.append("endmodule")
    return "\n".join(L) + "\n"


def main():
    keeps = {}
    for line in open(os.path.join(FUSED, "wave38_keeps.jsonl")):
        k = json.loads(line)
        keeps[k["try"]] = k
    import random
    rng = random.Random(0xC0FFEE)
    pairs = [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(2000)]
    for t in SAMPLE_TRIES:
        k = keeps[t]
        assert k["try"] == t
        stages = [tuple(s) for s in k["stages"]]
        z = k["z"]
        name = "w38_t%03d" % t
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(stages, z))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages, z))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages, z))
        spec = importlib.util.spec_from_file_location("m_" + name, os.path.join(d, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        # bit-exact: compile C, compare 2000/2000 via ctypes
        so = os.path.join(d, "_check.so")
        subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", so,
                        os.path.join(d, "impl.c")], check=True)
        lib = ctypes.CDLL(so)
        lib.mix_hash.restype = ctypes.c_uint64
        lib.mix_hash.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
        for v, kk in pairs:
            got = lib.mix_hash(v, kk)
            want = m.mix(v, kk)
            assert got == want, f"{name}: C/Python mismatch v={v:#x} k={kk:#x} {got:#x} != {want:#x}"
        os.remove(so)
        goldens = []
        for v, kk in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(kk), "out": hex(m.mix(v, kk))})
        meta = {
            "name": name,
            "description": "wave-38 stratified S0 sample, screen try %d (triage z=%.3f, distinct=%d, align=%d)" % (
                t, z, k["distinct_rots"], k["cross_stage_align"]),
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        print("wrote bundle %s try=%d z=%.3f bit-exact 2000/2000" % (name, t, z), flush=True)
    print("ALL 8 BUNDLES OK")


if __name__ == "__main__":
    main()
