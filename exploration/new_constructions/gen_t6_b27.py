#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 27 (dual-AND cascade)."""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b27 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e"]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return "{" + x + "[" + str(63 - r) + ":0], " + x + "[63:" + str(64 - r) + "]}"


def rk(j):
    return f"({rotl('key', 13*(j+1))} ^ {RC_HEX[j % 8]})"


SCHEDS = {"t6_dual5a": M.DUAL5_SCHED_A, "t6_dual5b": M.DUAL5_SCHED_B,
          "t6_dual4a": M.DUAL4_SCHED}


def gen_rtl(name):
    sched = SCHEDS[name]
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    for j in range(len(sched)):
        L.append(f"  wire [63:0] rk{j} = {rk(j)};")
    for j, (a, b, c, d) in enumerate(sched):
        L.append(f"  wire [63:0] st{j+1} = st{j} ^ ({rotl(f'st{j}',a)} & {rotl(f'st{j}',b)}) ^ ({rotl(f'st{j}',c)} & {rotl(f'st{j}',d)}) ^ rk{j};")
    L.append(f"  assign out = st{len(sched)} ^ {rotl('key',13)};")
    L.append("endmodule")
    return "\n".join(L)


def gen_c(name, desc):
    sched = SCHEDS[name]
    L = ["#include <stdint.h>",
         "static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}",
         "static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}",
         f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for j, (a, b, c, d) in enumerate(sched):
        L.append(f"    x ^= (rotl64(x,{a})&rotl64(x,{b})) ^ (rotl64(x,{c})&rotl64(x,{d})) ^ rk(key,{j});")
    L.append("    return x ^ rotl64(key,13);\n}")
    return "\n".join(L) + "\n"


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B27[name][0]
    sched_name = {"t6_dual5a": "DUAL5_SCHED_A", "t6_dual5b": "DUAL5_SCHED_B",
                  "t6_dual4a": "DUAL4_SCHED"}[name]
    parts = [f'"""Bit-exact Python model for {name} (batch 27)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
             "def _u64(hi, lo):",
             "    return (np.uint64(hi) << np.uint64(32)) | np.uint64(lo)",
             "RC64 = [_u64(0x9E3779B9, 0x7F4A7C15), _u64(0x3C6EF372, 0xFE94F82A),",
             "        _u64(0xDAA66D2C, 0x7DDF743F), _u64(0x78DDE6E5, 0xFD29F054),",
             "        _u64(0x2545F491, 0x4F6CDD1D),",
             "        _u64(0x9E3779B9, 0x7F4A7C15) ^ np.uint64(0xDEADBEEF),",
             "        _u64(0x3C6EF372, 0xFE94F82A) ^ np.uint64(0x12345678),",
             "        _u64(0xDAA66D2C, 0xDD6129B3E)]",
             f"{sched_name} = {getattr(M, sched_name)!r}", ""]
    for h in ["_rotl64", "_rk", "_dual"]:
        parts.append(inspect.getsource(getattr(M, h)))
    parts.append(inspect.getsource(fn))
    parts.append("")
    parts.append("def mix(v, k):")
    parts.append("    if np.ndim(v) == 0 and np.ndim(k) == 0:")
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
    ok = True
    IVL = "/home/hatch/tools/ivl-env/bin/iverilog"
    for name, (fn, desc) in M.CANDIDATES_B27.items():
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
        print(f"{name}: bundle written", flush=True)

    print("=== checks ===", flush=True)
    for name, (fn, desc) in M.CANDIDATES_B27.items():
        d = os.path.join(FB, name)
        mu = __import__("importlib.util", fromlist=["util"])
        sp = mu.spec_from_file_location("m27_" + name, f"{d}/model.py")
        m = mu.module_from_spec(sp)
        sp.loader.exec_module(m)
        rng = np.random.default_rng(42)
        for _ in range(200):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            if int(m.mix(np.uint64(v), np.uint64(k))) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: MODEL FAIL"); ok = False; break
        else:
            print(f"{name}: model OK", flush=True)
        open('/tmp/m27.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/m27", "/tmp/m27.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/m27"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
                           capture_output=True, text=True)
        for (v, k), o in zip(vecs, r.stdout.strip().split("\n")):
            if int(o, 16) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: C FAIL"); ok = False; break
        else:
            print(f"{name}: impl.c OK", flush=True)
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(20)]
        tb = ['`timescale 1ns/1ps', 'module tb;', '  reg [63:0] val,key;',
              '  wire [63:0] out;', f'  {name} dut(.val(val),.key(key),.out(out));',
              '  integer i;', '  initial begin']
        for v, k in vecs:
            tb.append(f'    val = 64\'h{v:016x}; key = 64\'h{k:016x}; #10;')
            tb.append(f'    $display("%016h", out);')
        tb += ['  end', 'endmodule']
        open('/tmp/m27_tb.v', 'w').write("\n".join(tb))
        r = subprocess.run([IVL, "-o", "/tmp/m27_tb", f"{d}/rtl.v", "/tmp/m27_tb.v"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:300]}"); ok = False; continue
        r = subprocess.run(["/tmp/m27_tb"], capture_output=True, text=True)
        outs = r.stdout.strip().split("\n")
        good = True
        for (v, k), o in zip(vecs, outs):
            if int(o.strip(), 16) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: RTL FAIL"); good = False; ok = False; break
        if good:
            print(f"{name}: RTL OK", flush=True)
    print("ALL OK" if ok else "FAILURES PRESENT", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
