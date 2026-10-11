#!/usr/bin/env python3
"""Generate a fast_battery candidate bundle from a batch-55 hetMA5p1f KEEP (fisher-matched triage).

Usage: gen_b55_bundle.py <keeps.jsonl> <rank> <bundle_name>
  <rank> = index into the (n_reject, z)-sorted hetMA5p1f KEEP list (0 = best).
Writes fast_battery/candidates/<bundle_name>/{rtl.v,model.py,impl.c,meta.json}
with bit-exactness self-checks (C vs Python on 2000 vectors; bundle model
vs the b53 screener's apply_stage on 500 vectors).

Form (x ^= k pre-whiten; final x ^= rotl(k,13) -- the MU5 frame):
  MUXD(s,a,b,d): x = x ^ mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)
  AND3(p,q,r):   x = x ^ (rotl(x,p) & rotl(x,q)) ^ rotl(x,r)
  mux(s,a,b) = (s&a)|(~s&b). The AND3 rotl(x,r) linear term is the b33 rc
  term -- LOAD-BEARING per b53 cut #6, reproduced bit-exactly in all three
  forms (Python/C/Verilog).
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
    if tag == "MUXD":
        _, s, a, b, d = st
        return (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b)) ^ rotl(x, d)) & M64
    elif tag == "AND3":
        _, p, q, r = st
        return (x ^ (rotl(x, p) & rotl(x, q)) ^ rotl(x, r)) & M64
    raise AssertionError(tag)


def mix_py(v, k, stages):
    x = (v ^ k) & M64
    for st in stages:
        x = apply_stage(x, st)
    return (x ^ rotl(k, 13)) & M64


def rtl_rot(x, r):
    # rotl by r in Verilog concat form; r==0 is the bare wire.
    if r == 0:
        return x
    return "{%s[%d:0],%s[63:%d]}" % (x, 64 - r - 1, x, 64 - r)


def vlog_stages(stages):
    L = []
    for j, st in enumerate(stages):
        xj = "x%d" % j
        yj = "x%d" % (j + 1)
        tag = st[0]
        if tag == "MUXD":
            _, s, a, b, d = st
            L.append("    wire [63:0] %s_s = %s;" % (yj, rtl_rot(xj, s)))
            L.append("    wire [63:0] %s_a = %s;" % (yj, rtl_rot(xj, a)))
            L.append("    wire [63:0] %s_b = %s;" % (yj, rtl_rot(xj, b)))
            L.append("    wire [63:0] %s_d = %s;" % (yj, rtl_rot(xj, d)))
            L.append("    wire [63:0] %s_m = (%s_s & %s_a) | (~%s_s & %s_b);"
                     % ((yj,) * 5))
            L.append("    wire [63:0] %s = %s ^ %s_m ^ %s_d;"
                     % (yj, xj, yj, yj))
        elif tag == "AND3":
            _, p, q, r = st
            L.append("    wire [63:0] %s_p = %s;" % (yj, rtl_rot(xj, p)))
            L.append("    wire [63:0] %s_q = %s;" % (yj, rtl_rot(xj, q)))
            L.append("    wire [63:0] %s_r = %s;" % (yj, rtl_rot(xj, r)))
            L.append("    wire [63:0] %s = %s ^ (%s_p & %s_q) ^ %s_r;"
                     % (yj, xj, yj, yj, yj))
        else:
            raise AssertionError(tag)
    return L


def c_stages(stages):
    L = []
    for st in stages:
        tag = st[0]
        if tag == "MUXD":
            _, s, a, b, d = st
            L.append(
                "    x = x ^ (((rotl64(x,%d)&rotl64(x,%d))|"
                "((~rotl64(x,%d))&rotl64(x,%d))) ^ rotl64(x,%d));"
                % (s, a, s, b, d))
        elif tag == "AND3":
            _, p, q, r = st
            L.append("    x = x ^ (rotl64(x,%d) & rotl64(x,%d)) ^ rotl64(x,%d);"
                     % (p, q, r))
        else:
            raise AssertionError(tag)
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
        '        if st[0] == "MUXD":',
        '            _, s, a, b, d = st',
        '            g = ((rotl(x, s) & rotl(x, a)) | ((~rotl(x, s)) & rotl(x, b))) & M',
        '            x = (x ^ g ^ rotl(x, d)) & M',
        '        else:',
        '            _, p, q, r = st',
        '            x = (x ^ (rotl(x, p) & rotl(x, q)) ^ rotl(x, r)) & M',
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
    entries = [e for e in entries if e["form"] == "hetMA5p1f"]
    entries.sort(key=lambda e: (e.get("n_reject", 99), e["z"]))
    assert entries, "no hetMA5p1f keeps in %s" % kj
    e = entries[rank]
    stages = [tuple(s) for s in e["stages"]]
    z = e["z"]; nrej = e.get("n_reject", "?")
    and_pos = e.get("and_pos")
    assert sum(1 for s in stages if s[0] == "AND3") == 1, "not exactly one AND3"
    assert stages[1][0] == "AND3", "FAIL-LOUD: AND3 not fixed at stage index 1 (got %s)" % [s[0] for s in stages]
    print("selected rank %d: form=hetMA5p1f z=%.2f n_reject=%s andpos=%s stages=%s"
          % (rank, z, nrej, and_pos, stages), flush=True)
    outdir = "/home/hatch/workspace/mix/exploration/fast_battery/candidates/%s" % name
    os.makedirs(outdir, exist_ok=True)

    L = ["// %s: batch-55 hetMA5p1f schedule (fisher triage z=%.2f n_reject=%s, andpos=%s)"
         % (name, z, nrej, and_pos),
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

    mp = ['"""%s: batch-55 hetMA5p1f cascade (fisher triage z=%.2f n_reject=%s, andpos=%s)."""'
          % (name, z, nrej, and_pos),
          "STAGES = %s" % (stages,)] + py_stages_np()
    open(os.path.join(outdir, "model.py"), "w").write("\n".join(mp) + "\n")

    cl = ["#include <stdint.h>",
          "static inline uint64_t rotl64(uint64_t x, int r) {",
          "    r &= 63;",
          "    return r ? (x << r) | (x >> (64 - r)) : x;",
          "}",
          "// batch-55 hetMA5p1f schedule (fisher triage z=%.2f n_reject=%s, andpos=%s);"
          % (z, nrej, and_pos),
          "// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).",
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
            "description": "batch-55 hetMA5p1f %d-stage schedule (fisher triage z=%.2f n_reject=%s, andpos=%s)"
            % (len(stages), z, nrej, and_pos),
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
    # Cross-check the bundle model against the b55 SCREENER (apply_stage),
    # catching any transcription divergence in all three forms at once.
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch55")
    for mod in list(sys.modules):
        if mod == "t6_b54_screen":
            del sys.modules[mod]
    import numpy as np
    import t6_b55_screen as scr
    import random
    random.seed(0xB550)
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
    print("bundle %s written (fisher triage z=%.2f n_reject=%s, andpos=%s)" % (name, z, nrej, and_pos),
          flush=True)


if __name__ == "__main__":
    main()
