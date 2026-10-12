#!/usr/bin/env python3
"""Generate a fast_battery candidate bundle from a batch-58 muxD4f KEEP.

Usage: gen_b58_bundle.py <keeps.jsonl> <rank> <bundle_name>
  <rank> = index into the (n_reject, z)-sorted MUXD-keep list (0 = best).
Writes fast_battery/candidates/<bundle_name>/{rtl.v,model.py,impl.c,meta.json}
with bit-exactness self-checks (C vs Python on 2000 vectors; bundle model
vs the b57 screener's apply_stage on 500 vectors).

Form (x ^= k pre-whiten; final x ^= rotl(k,13) -- the MU5 frame):
  MUXD(s,a,b,d): x = x ^ mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)
  mux(s,a,b) = (s&a)|(~s&b). s,a,b pairwise distinct per draw constraints
  (b51 cut #10 degeneracy proof); fail-loud re-checked here.
"""
import json
import os
import subprocess
import sys

M64 = 0xFFFFFFFFFFFFFFFF


def rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x & M64


def mux(s, a, b):
    return ((s & a) | ((~s) & b)) & M64


def apply_stage(x, st):
    tag = st[0]
    assert tag == "MUXD", tag
    _, s, a, b, d = st
    return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b)) ^ rotl(x, d)) & M64


def mix_py(v, k, stages):
    x = (v ^ k) & M64
    for st in stages:
        x = apply_stage(x, st)
    return (x ^ rotl(k, 13)) & M64


def rtl_rot(x, r):
    if r == 0:
        return x
    return "{%s[%d:0],%s[63:%d]}" % (x, 64 - r - 1, x, 64 - r)


def vlog_stages(stages):
    L = []
    for j, st in enumerate(stages):
        xj = "x%d" % j
        yj = "x%d" % (j + 1)
        assert st[0] == "MUXD", st
        _, s, a, b, d = st
        L.append("    wire [63:0] %s_s = %s;" % (yj, rtl_rot(xj, s)))
        L.append("    wire [63:0] %s_a = %s;" % (yj, rtl_rot(xj, a)))
        L.append("    wire [63:0] %s_b = %s;" % (yj, rtl_rot(xj, b)))
        L.append("    wire [63:0] %s_d = %s;" % (yj, rtl_rot(xj, d)))
        L.append("    wire [63:0] %s_m = (%s_s & %s_a) | (~%s_s & %s_b);"
                 % ((yj,) * 5))
        L.append("    wire [63:0] %s = %s ^ %s_m ^ %s_d;"
                 % (yj, xj, yj, yj))
    return L


def c_stages(stages):
    L = []
    for st in stages:
        assert st[0] == "MUXD", st
        _, s, a, b, d = st
        L.append(
            "    x = x ^ (((rotl64(x,%d)&rotl64(x,%d))|"
            "((~rotl64(x,%d))&rotl64(x,%d))) ^ rotl64(x,%d));"
            % (s, a, s, b, d))
    return L


def py_stages_np():
    return [
        'def mix_np(V, K):',
        '    import numpy as np',
        '    M = np.uint64(0xFFFFFFFFFFFFFFFF)',
        '    def rotl(x, r):',
        '        r %= 64',
        '        return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M if r else x',
        '    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)',
        '    x = (x ^ k) & M',
        '    for st in STAGES:',
        '        assert st[0] == "MUXD"',
        '        _, s, a, b, d = st',
        '        g = ((rotl(x, s) & rotl(x, a)) | ((~rotl(x, s)) & rotl(x, b))) & M',
        '        x = (x ^ g ^ rotl(x, d)) & M',
        '    x = (x ^ rotl(k, 13)) & M',
        '    return x',
        'def mix(v, k):',
        '    import numpy as np',
        '    return int(mix_np(np.uint64(v), np.uint64(k)))',
    ]


def main():
    kj, rank, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(kj) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    entries = [e for e in entries if e["form"] == "muxD4f"]
    entries.sort(key=lambda e: (e.get("n_reject", 99), e["z"]))
    assert entries, "no muxD4f keeps in %s" % kj
    e = entries[rank]
    stages = [tuple(s) for s in e["stages"]]
    z = e["z"]; nrej = e.get("n_reject", "?")
    # Fail-loud: MUXD-only, 4 stages, pairwise-distinct s/a/b (b51 cut #10).
    assert len(stages) == 4 and all(s[0] == "MUXD" for s in stages), stages
    for st in stages:
        _, s, a, b, d = st
        assert len({s, a, b}) == 3, "degenerate MUXD stage in keep: %s" % (st,)
    assert not e.get("is_324", False), "324-rediscovery is not a challenger"
    print("selected rank %d: form=muxD4f z=%.2f n_reject=%s stages=%s"
          % (rank, z, nrej, stages), flush=True)
    outdir = "/home/hatch/workspace/mix/exploration/fast_battery/candidates/%s" % name
    os.makedirs(outdir, exist_ok=True)

    L = ["// %s: batch-58 muxD4f schedule (fisher triage z=%.2f n_reject=%s)"
         % (name, z, nrej),
         "module %s(" % name,
         "    input  [63:0] val,",
         "    input  [63:0] key,",
         "    output [63:0] out",
         ");",
         "    wire [63:0] x0 = val ^ key;"]
    L += vlog_stages(stages)
    L.append("    wire [63:0] k13 = %s;" % rtl_rot("key", 13))
    L.append("    assign out = x%d ^ k13;" % len(stages))
    L.append("endmodule")
    open(os.path.join(outdir, "rtl.v"), "w").write("\n".join(L) + "\n")

    mp = ['"""%s: batch-58 muxD4f cascade (fisher triage z=%.2f n_reject=%s)."""'
          % (name, z, nrej),
          "STAGES = %s" % (stages,)] + py_stages_np()
    open(os.path.join(outdir, "model.py"), "w").write("\n".join(mp) + "\n")

    cl = ["#include <stdint.h>",
          "static inline uint64_t rotl64(uint64_t x, int r) {",
          "    r &= 63;",
          "    return r ? (x << r) | (x >> (64 - r)) : x;",
          "}",
          "// batch-58 muxD4f schedule (fisher triage z=%.2f n_reject=%s);"
          % (z, nrej),
          "uint64_t mix_hash(uint64_t val, uint64_t key) {",
          "    uint64_t x = val ^ key;"]
    cl += c_stages(stages)
    cl += ["    x ^= rotl64(key, 13);", "    return x;", "}"]
    open(os.path.join(outdir, "impl.c"), "w").write("\n".join(cl) + "\n")

    goldens = []
    for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
        goldens.append({"val": hex(v), "key": hex(k),
                        "out": hex(mix_py(v, k, stages))})
    meta = {"name": name,
            "description": "batch-58 muxD4f 4-stage schedule (fisher triage z=%.2f n_reject=%s)"
            % (z, nrej),
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
    for mod in list(sys.modules):
        if mod == "model":
            del sys.modules[mod]
    import model
    bad = 0
    for line in out:
        v, k, o = [int(t, 16) for t in line.split()]
        if model.mix(v, k) != o:
            bad += 1
            if bad < 3:
                print("C-PY MISMATCH v=%x k=%x C=%x py=%x" % (v, k, o, model.mix(v, k)))
    print("bit-exact C-vs-Python: %d/2000 %s" % (2000 - bad, "OK" if bad == 0 else "FAIL"),
          flush=True)
    if bad:
        sys.exit(4)
    # Cross-check the bundle model against the b57 SCREENER (apply_stage).
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch57")
    import numpy as np
    import t6_b57_screen as scr
    import random
    random.seed(0xB570)
    bad2 = 0
    for _ in range(500):
        v = random.getrandbits(64)
        k = random.getrandbits(64)
        xx = np.uint64((v ^ k) & 0xFFFFFFFFFFFFFFFF)
        for st in stages:
            xx = scr.apply_stage(xx, st)
        ref = int((xx ^ scr.rotl(np.uint64(k), 13)) & np.uint64(0xFFFFFFFFFFFFFFFF))
        if model.mix(v, k) != ref:
            bad2 += 1
            if bad2 < 3:
                print("SCREENER-MISMATCH v=%x k=%x" % (v, k))
    print("screener-vs-bundle: %d/500 %s" % (500 - bad2, "OK" if bad2 == 0 else "FAIL"),
          flush=True)
    if bad2:
        sys.exit(5)
    print("bundle %s written (form=muxD4f fisher triage z=%.2f n_reject=%s)"
          % (name, z, nrej), flush=True)


if __name__ == "__main__":
    main()
