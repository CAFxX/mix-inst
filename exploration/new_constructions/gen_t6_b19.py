#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 19 (parallel dual-cascade)."""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b19 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e"]
RC_DEC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
          0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054,
          0x2545F4914F6CDD1D,
          0x9E3779B97F4A7C15 ^ 0xDEADBEEF,
          0x3C6EF372FE94F82A ^ 0x12345678,
          0xDAA66D2C7DDF743F ^ 0xABCDEF01]

SCHED = {"t6_par5a": M.SCHED_A, "t6_par5b": M.SCHED_B}


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"


def rk(key, j):
    return f"({rotl(key, 13*(j+1))} ^ {RC_HEX[j % 8]})"


def gen_rtl(name):
    sched = SCHED[name]
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] vk = val ^ key;"]
    # cascade A: x=val, key=key
    L.append("  wire [63:0] a0 = val;")
    cur = "a0"
    for j, (a, b, c) in enumerate(sched):
        L.append(f"  wire [63:0] a{j+1} = {cur} ^ (({rotl(cur, a)} & {rotl(cur, b)}) ^ {rotl(cur, c)}) ^ {rk('key', j)};")
        cur = f"a{j+1}"
    # cascade B: x=key, key=val (cross-keyed)
    L.append("  wire [63:0] b0 = key;")
    cur = "b0"
    for j, (a, b, c) in enumerate(sched):
        L.append(f"  wire [63:0] b{j+1} = {cur} ^ (({rotl(cur, a)} & {rotl(cur, b)}) ^ {rotl(cur, c)}) ^ {rk('val', j)};")
        cur = f"b{j+1}"
    L.append(f"  wire [63:0] rkC = ({rotl('vk', 77)} ^ {RC_HEX[7]});")
    L.append(f"  wire [63:0] cmb = a5 ^ b5 ^ (a5 & b5) ^ rkC;")
    L.append(f"  wire [63:0] key_r13 = {rotl('vk', 13)};")
    L.append(f"  assign out = cmb ^ {{32'h0, key_r13[63:32]}};")
    L.append("endmodule")
    return "\n".join(L)


C_HEAD = """#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint64_t RC[8] = {%s};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j %% 8]; }
""" % ", ".join("0x%016Xu" % v for v in RC_DEC)


def gen_c(name, desc):
    sched = SCHED[name]
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t a = val, b = key;"]
    for j, (a, b, c) in enumerate(sched):
        L.append(f"    a ^= ((rotl64(a,{a}) & rotl64(a,{b})) ^ rotl64(a,{c})) ^ rk(key,{j});")
    for j, (a, b, c) in enumerate(sched):
        L.append(f"    b ^= ((rotl64(b,{a}) & rotl64(b,{b})) ^ rotl64(b,{c})) ^ rk(val,{j});")
    L.append("    uint64_t rkC = rotl64(val ^ key, 77) ^ RC[7];")
    L.append("    uint64_t out = a ^ b ^ (a & b) ^ rkC;")
    L.append("    out ^= rotl64(val ^ key, 13) >> 32;")
    L.append("    return out;\n}")
    return "\n".join(L) + "\n"


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B19[name][0]
    parts = [f'"""Bit-exact Python model for {name} (batch 19)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
             "RC64 = [%s]" % ", ".join("np.uint64(0x%X)" % int(v) for v in M.RC64),
             "SCHED_A = %r" % (M.SCHED_A,),
             "SCHED_B = %r" % (M.SCHED_B,),
             ""]
    for h in ["_rotl64", "_rk", "_cascade", "_par5"]:
        parts.append(inspect.getsource(getattr(M, h)))
    parts.append(inspect.getsource(fn))
    parts.append("")
    parts.append("def mix(v, k):")
    parts.append(f"    if np.ndim(v) == 0 and np.ndim(k) == 0:")
    parts.append(f"        return int({fn.__name__}(np.uint64(v), np.uint64(k)))")
    parts.append(f"    return {fn.__name__}(np.asanyarray(v, dtype=np.uint64), np.asanyarray(k, dtype=np.uint64))")
    parts.append("")
    parts.append("def mix_np(V, K):")
    parts.append(f"    return {fn.__name__}(np.asanyarray(V, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))")
    parts.append("")
    parts.append(f"meta = {{'desc': {desc!r}}}")
    return "\n".join(parts) + "\n"


def main():
    import numpy as np
    for name, (fn, desc) in M.CANDIDATES_B19.items():
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name) + "\n")
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(self_contained_model(name, desc))
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump({"name": name, "rtl_top": name, "description": desc,
                       "screen_keys": ["0x123456789abcdef0", "0x0"],
                       "practrand_keys": ["0x123456789abcdef0", "0x0"]},
                      f, indent=1)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_c(name, desc))
        print(f"{name}: bundle written")

    print("=== checks ===")
    ok = True
    IVL = "/home/hatch/tools/ivl-env/bin/iverilog"
    for name, (fn, desc) in M.CANDIDATES_B19.items():
        d = os.path.join(FB, name)
        mu = __import__("importlib.util", fromlist=["util"])
        sp = mu.spec_from_file_location("m_" + name, f"{d}/model.py")
        m = mu.module_from_spec(sp)
        sp.loader.exec_module(m)
        rng = np.random.default_rng(42)
        for _ in range(200):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            if int(m.mix(np.uint64(v), np.uint64(k))) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: MODEL FAIL"); ok = False; break
        else:
            print(f"{name}: model OK")
        open('/tmp/b19.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/b19", "/tmp/b19.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/b19"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
                           capture_output=True, text=True)
        for (v, k), o in zip(vecs, r.stdout.strip().split("\n")):
            if int(o, 16) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: C FAIL"); ok = False; break
        else:
            print(f"{name}: impl.c OK")
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(20)]
        tb = ['`timescale 1ns/1ps', 'module tb;', '  reg [63:0] val,key;',
              '  wire [63:0] out;', f'  {name} dut(.val(val),.key(key),.out(out));',
              '  initial begin']
        for v, k in vecs:
            e = int(fn(np.uint64(v), np.uint64(k)))
            tb.append(f"    val=64'h{v:016x};key=64'h{k:016x};#10;")
            tb.append(f"    if(out!==64'h{e:016x})$display(\"MISMATCH\");")
        tb += ['    $display("TB DONE");', '    $finish;', '  end', 'endmodule']
        open('/tmp/b19tb.v', 'w').write('\n'.join(tb))
        r = subprocess.run([IVL, '-o', '/tmp/b19tb', f'{d}/rtl.v', '/tmp/b19tb.v'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:200]}"); ok = False; continue
        r = subprocess.run(['/tmp/b19tb'], capture_output=True, text=True, timeout=120)
        good = "TB DONE" in r.stdout and "MISMATCH" not in r.stdout
        print(f"{name}: RTL {'OK' if good else 'FAIL'}")
        if not good:
            ok = False
    print("ALL OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
