#!/usr/bin/env python3
"""Generate a fast_battery candidate bundle from a batch-41 KEEP entry.

Usage: gen_b41_bundle.py <keeps.jsonl> <rank> <bundle_name>
  <rank> = index into the z-sorted KEEP list (0 = best).
Writes fast_battery/candidates/<bundle_name>/{rtl.v,model.py,impl.c,meta.json}
with a bit-exactness self-check (C vs Python on 2000 vectors).
Forms: nandM  x ^= ~(ra & rb) ^ rc ;  norM  x ^= ~(ra | rb) ^ rc
"""
import json
import os
import subprocess
import sys

M64 = 0xFFFFFFFFFFFFFFFF


def rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64


def stage_py(x, form, a, b, c):
    if form == "nandM":
        return (x ^ ((~(rotl(x, a) & rotl(x, b))) & M64) ^ rotl(x, c)) & M64
    if form == "norM":
        return (x ^ ((~(rotl(x, a) | rotl(x, b))) & M64) ^ rotl(x, c)) & M64
    raise ValueError(form)


def mix_py(v, k, stages, form):
    x = (v ^ k) & M64
    for a, b, c in stages:
        x = stage_py(x, form, a, b, c)
    return (x ^ rotl(k, 13)) & M64


def rtl_rot(x, r):
    return "{%s[%d:0], %s[63:%d]}" % (x, r - 1, x, 64 - r) if r else x


def rtl_stage(xj, form, a, b, c):
    op = "&" if form == "nandM" else "|"
    return "~((%s) %s (%s))" % (rtl_rot(xj, a), op, rtl_rot(xj, b))


def np_stage(form):
    if form == "nandM":
        return "x = (x ^ ((~(_rotl(x, a) & _rotl(x, b))) & M64) ^ _rotl(x, c)) & M64"
    return "x = (x ^ ((~(_rotl(x, a) | _rotl(x, b))) & M64) ^ _rotl(x, c)) & M64"


def c_stage(form, a, b, c):
    if form == "nandM":
        return "    x ^= (~(rotl64(x,%d) & rotl64(x,%d))) ^ rotl64(x,%d);" % (a, b, c)
    return "    x ^= (~(rotl64(x,%d) | rotl64(x,%d))) ^ rotl64(x,%d);" % (a, b, c)


def main():
    kj, rank, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(kj) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    entries.sort(key=lambda e: e["z"])
    e = entries[rank]
    form = e["form"]
    stages = [tuple(s) for s in e["stages"]]
    z = e["z"]
    print("selected rank %d: form=%s z=%.2f stages=%s" % (rank, form, z, stages))
    outdir = "/home/hatch/workspace/mix/exploration/fast_battery/candidates/%s" % name
    os.makedirs(outdir, exist_ok=True)

    L = ["// %s: batch-41 %s schedule (triage z=%.2f)" % (name, form, z),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    for j, (a, b, c) in enumerate(stages):
        xj = "x%d" % j
        L.append("    wire [63:0] x%d = %s ^ (%s) ^ %s;"
                 % (j + 1, xj, rtl_stage(xj, form, a, b, c), rtl_rot(xj, c)))
    n = len(stages)
    L.append("    assign out = x%d ^ %s;" % (n, rtl_rot("key", 13)))
    L.append("endmodule")
    open(os.path.join(outdir, "rtl.v"), "w").write("\n".join(L) + "\n")

    mp = ['"""%s: batch-41 %s cascade (triage z=%.2f)."""' % (name, form, z),
          "import numpy as np",
          "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
          "STAGES = %s" % (stages,),
          "def _rotl(x, r):",
          "    r %= 64",
          "    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x",
          "def mix_np(V, K):",
          "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)",
          "    x = (x ^ k) & M64",
          "    for a, b, c in STAGES:",
          "        " + np_stage(form),
          "    x = (x ^ _rotl(k, 13)) & M64",
          "    return x & M64",
          "def mix(v, k):",
          "    return int(mix_np(np.uint64(v), np.uint64(k)))"]
    open(os.path.join(outdir, "model.py"), "w").write("\n".join(mp) + "\n")

    cl = ["#include <stdint.h>",
          "static inline uint64_t rotl64(uint64_t x, int r) {",
          "    r &= 63;",
          "    return r ? (x << r) | (x >> (64 - r)) : x;",
          "}",
          "// batch-41 %s schedule (triage z=%.2f)" % (form, z),
          "uint64_t mix_hash(uint64_t val, uint64_t key) {",
          "    uint64_t x = val ^ key;"]
    for a, b, c in stages:
        cl.append(c_stage(form, a, b, c))
    cl += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    open(os.path.join(outdir, "impl.c"), "w").write("\n".join(cl) + "\n")

    goldens = []
    for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
        goldens.append({"val": hex(v), "key": hex(k),
                        "out": hex(mix_py(v, k, stages, form))})
    meta = {"name": name,
            "description": "batch-41 %s 6-stage schedule (triage z=%.2f)" % (form, z),
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name}
    open(os.path.join(outdir, "meta.json"), "w").write(json.dumps(meta, indent=1))

    chk = os.path.join(outdir, "check_exact.c")
    open(chk, "w").write(
        '#include <stdio.h>\n#include <stdint.h>\n#include "impl.c"\n'
        'int main(void){uint64_t s=0x123456789abcdefULL;\n'
        'for(int i=0;i<2000;i++){s=s*6364136223846793005ULL+1442695040888963407ULL;\n'
        'uint64_t v=s;s=s*6364136223846793005ULL+1442695040888963407ULL;uint64_t k=s;\n'
        'printf("%llx %llx %llx\\n",(unsigned long long)v,(unsigned long long)k,\n'
        '       (unsigned long long)mix_hash(v,k));}return 0;}\n')
    subprocess.run(["gcc", "-O2", "-o", os.path.join(outdir, "check_exact"), chk],
                   check=True, cwd=outdir)
    out = subprocess.run([os.path.join(outdir, "check_exact")], capture_output=True,
                         text=True, check=True).stdout.strip().split("\n")
    sys.path.insert(0, outdir)
    import model
    bad = 0
    for line in out:
        v, k, o = [int(t, 16) for t in line.split()]
        if model.mix(v, k) != o:
            bad += 1
    print("bit-exact C-vs-Python: %d/2000 %s" % (2000 - bad, "OK" if bad == 0 else "FAIL"))
    if bad:
        sys.exit(4)
    print("bundle %s written (form=%s triage z=%.2f)" % (name, form, z))


if __name__ == "__main__":
    main()
