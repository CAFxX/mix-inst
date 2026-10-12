#!/usr/bin/env python3
"""Generate a fast_battery candidate bundle from a batch-56 AND-form-variant KEEP.

Usage: gen_b56_bundle.py <keeps.jsonl> <form> <rank> <bundle_name>
  <form> = hetMA5N | hetMOA5
  <rank> = index into the (n_reject, z)-sorted KEEP list for that form (0 = best).
Writes fast_battery/candidates/<bundle_name>/{rtl.v,model.py,impl.c,meta.json}
with bit-exactness self-checks (C vs Python on 2000 vectors; bundle model
vs the b56 screener's apply_stage on 500 vectors).

Forms (x ^= k pre-whiten; final x ^= rotl(k,13) -- the MU5 frame):
  MUXD(s,a,b,d): x = x ^ mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)
  ANDN(p,q):     x = x ^ (rotl(x,p) & ~rotl(x,q))
  OAAND(p,q,r,s):x = x ^ ((rotl(x,p) | rotl(x,q)) & rotl(x,r)) ^ rotl(x,s)
  mux(s,a,b) = (s&a)|(~s&b). Zero-corner unit checks (bit-exact, in the
  b56 screener's selftest): ANDN degrades to x ^= ra; OAAND degrades to
  x ^= rd -- the linear masks are load-bearing, verified not assumed.
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
    elif tag == "ANDN":
        _, p, q = st
        return (x ^ (rotl(x, p) & (~rotl(x, q)))) & M64
    elif tag == "OAAND":
        _, p, q, r, s = st
        return (x ^ (((rotl(x, p) | rotl(x, q)) & rotl(x, r))) ^ rotl(x, s)) & M64
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
        elif tag == "ANDN":
            _, p, q = st
            L.append("    wire [63:0] %s_p = %s;" % (yj, rtl_rot(xj, p)))
            L.append("    wire [63:0] %s_q = %s;" % (yj, rtl_rot(xj, q)))
            L.append("    wire [63:0] %s = %s ^ (%s_p & ~%s_q);"
                     % (yj, xj, yj, yj))
        elif tag == "OAAND":
            _, p, q, r, s = st
            L.append("    wire [63:0] %s_p = %s;" % (yj, rtl_rot(xj, p)))
            L.append("    wire [63:0] %s_q = %s;" % (yj, rtl_rot(xj, q)))
            L.append("    wire [63:0] %s_r = %s;" % (yj, rtl_rot(xj, r)))
            L.append("    wire [63:0] %s_s = %s;" % (yj, rtl_rot(xj, s)))
            L.append("    wire [63:0] %s = %s ^ (((%s_p | %s_q) & %s_r) ^ %s_s);"
                     % (yj, xj, yj, yj, yj, yj))
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
        elif tag == "ANDN":
            _, p, q = st
            L.append("    x = x ^ (rotl64(x,%d) & ~rotl64(x,%d));" % (p, q))
        elif tag == "OAAND":
            _, p, q, r, s = st
            L.append("    x = x ^ (((rotl64(x,%d)|rotl64(x,%d))&rotl64(x,%d)) ^ rotl64(x,%d));"
                     % (p, q, r, s))
        else:
            raise AssertionError(tag)
    return L


def py_stages_np(and_tag):
    lines = [
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
    ]
    if and_tag == "ANDN":
        lines += [
            '        elif st[0] == "ANDN":',
            '            _, p, q = st',
            '            x = (x ^ (rotl(x, p) & (~rotl(x, q)))) & M',
        ]
    elif and_tag == "OAAND":
        lines += [
            '        elif st[0] == "OAAND":',
            '            _, p, q, r, s = st',
            '            x = (x ^ (((rotl(x, p) | rotl(x, q)) & rotl(x, r)) ^ rotl(x, s))) & M',
        ]
    else:
        raise AssertionError(and_tag)
    lines += [
        '        else:',
        '            raise AssertionError(st[0])',
        '    x = (x ^ rotl(k, 13)) & M',
        '    return x',
        'def mix(v, k):',
        '    import numpy as np',
        '    return int(mix_np(np.uint64(v), np.uint64(k)))',
    ]
    return lines


AND_TAG = {"hetMA5N": "ANDN", "hetMOA5": "OAAND"}


def main():
    kj, form, rank, name = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    assert form in AND_TAG, form
    and_tag = AND_TAG[form]
    with open(kj) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    entries = [e for e in entries if e["form"] == form]
    entries.sort(key=lambda e: (e.get("n_reject", 99), e["z"]))
    assert entries, "no %s keeps in %s" % (form, kj)
    e = entries[rank]
    stages = [tuple(s) for s in e["stages"]]
    z = e["z"]; nrej = e.get("n_reject", "?")
    and_pos = e.get("and_pos")
    assert sum(1 for s in stages if s[0] == and_tag) == 1, "not exactly one %s" % and_tag
    assert stages[1][0] == and_tag, "FAIL-LOUD: %s not fixed at stage index 1 (got %s)" % (and_tag, [s[0] for s in stages])
    # Fail-loud zero-corner + degeneracy checks on the actual keep schedule.
    for st in stages:
        if st[0] == "ANDN":
            assert st[1] != st[2], "degenerate ANDN in keep"
        elif st[0] == "OAAND":
            assert len({st[1], st[2], st[3], st[4]}) == 4, "degenerate OAAND in keep"
    x = 1 << 7
    if and_tag == "ANDN":
        st = stages[1]
        assert apply_stage(x, st) == (x ^ rotl(x, st[1])) & M64, "ANDN zero-corner fail"
    else:
        st = stages[1]
        assert apply_stage(x, st) == (x ^ rotl(x, st[4])) & M64, "OAAND zero-corner fail"
    print("selected rank %d: form=%s z=%.2f n_reject=%s andpos=%s stages=%s"
          % (rank, form, z, nrej, and_pos, stages), flush=True)
    outdir = "/home/hatch/workspace/mix/exploration/fast_battery/candidates/%s" % name
    os.makedirs(outdir, exist_ok=True)

    L = ["// %s: batch-56 %s schedule (fisher triage z=%.2f n_reject=%s, andpos=%s)"
         % (name, form, z, nrej, and_pos),
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

    mp = ['"""%s: batch-56 %s cascade (fisher triage z=%.2f n_reject=%s, andpos=%s)."""'
          % (name, form, z, nrej, and_pos),
          "STAGES = %s" % (stages,)] + py_stages_np(and_tag)
    open(os.path.join(outdir, "model.py"), "w").write("\n".join(mp) + "\n")

    cl = ["#include <stdint.h>",
          "static inline uint64_t rotl64(uint64_t x, int r) {",
          "    r &= 63;",
          "    return r ? (x << r) | (x >> (64 - r)) : x;",
          "}",
          "// batch-56 %s schedule (fisher triage z=%.2f n_reject=%s, andpos=%s);"
          % (form, z, nrej, and_pos),
          "// the linear mask (ra / rd) is load-bearing (zero-corner).",
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
            "description": "batch-56 %s %d-stage schedule (fisher triage z=%.2f n_reject=%s, andpos=%s)"
            % (form, len(stages), z, nrej, and_pos),
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
    # Cross-check the bundle model against the b56 SCREENER (apply_stage),
    # catching any transcription divergence in all forms at once.
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch56")
    import numpy as np
    import t6_b56_screen as scr
    import random
    random.seed(0xB560)
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
    print("bundle %s written (form=%s fisher triage z=%.2f n_reject=%s, andpos=%s)" % (name, form, z, nrej, and_pos),
          flush=True)


if __name__ == "__main__":
    main()
