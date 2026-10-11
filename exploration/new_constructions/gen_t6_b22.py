#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 22 (higher-degree AND cascade)."""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b22 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e"]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    hi = 63 - r
    lo = 64 - r
    return "{" + x + "[" + str(hi) + ":0], " + x + "[63:" + str(lo) + "]}"


def rk(j):
    return f"({rotl('key', 13*(j+1))} ^ {RC_HEX[j % 8]})"


def gen_rtl(name):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    if name == "t6_and3_6a":
        sched, ns = M.AND3_SCHED6, 6
        for j in range(ns):
            L.append(f"  wire [63:0] rk{j} = {rk(j)};")
        cur = "st0"
        for j in range(ns):
            a, b, c, d = sched[j]
            L.append(f"  wire [63:0] st{j+1} = {cur} ^ ({rotl(cur,a)} & {rotl(cur,b)} & {rotl(cur,c)}) ^ {rotl(cur,d)} ^ rk{j};")
            cur = f"st{j+1}"
    elif name == "t6_and3_5a":
        sched, ns = M.AND3_SCHED5, 5
        for j in range(ns):
            L.append(f"  wire [63:0] rk{j} = {rk(j)};")
        cur = "st0"
        for j in range(ns):
            a, b, c, d = sched[j]
            L.append(f"  wire [63:0] st{j+1} = {cur} ^ ({rotl(cur,a)} & {rotl(cur,b)} & {rotl(cur,c)}) ^ {rotl(cur,d)} ^ rk{j};")
            cur = f"st{j+1}"
    elif name == "t6_and4_6a":
        sched, ns = M.AND4_SCHED6, 6
        for j in range(ns):
            L.append(f"  wire [63:0] rk{j} = {rk(j)};")
        cur = "st0"
        for j in range(ns):
            a, b, c, d, e = sched[j]
            L.append(f"  wire [63:0] st{j+1} = {cur} ^ ({rotl(cur,a)} & {rotl(cur,b)} & {rotl(cur,c)} & {rotl(cur,d)}) ^ {rotl(cur,e)} ^ rk{j};")
            cur = f"st{j+1}"
    L.append(f"  wire [63:0] key_r13 = {rotl('key', 13)};")
    L.append(f"  assign out = st{ns} ^ (key_r13 >> 32);")
    L.append("endmodule")
    return "\n".join(L)


def _c_head():
    return ("#include <stdint.h>\n"
            "static uint64_t rotl64(uint64_t x, int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}\n"
            "static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2C7DDF743FULL^0xABCDEF01ULL};return rotl64(k,13*(j+1))^RC[j%8];}\n")


C_HEAD = _c_head()


def gen_c(name, desc):
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    if name in ("t6_and3_6a",):
        sched = M.AND3_SCHED6
    elif name in ("t6_and3_5a",):
        sched = M.AND3_SCHED5
    else:
        sched = M.AND4_SCHED6
    is_quad = (name == "t6_and4_6a")
    for j, s in enumerate(sched):
        if is_quad:
            a, b, c, d, e = s
            L.append(f"    x ^= (rotl64(x,{a}) & rotl64(x,{b}) & rotl64(x,{c}) & rotl64(x,{d})) ^ rotl64(x,{e}) ^ rk(key,{j});")
        else:
            a, b, c, d = s
            L.append(f"    x ^= (rotl64(x,{a}) & rotl64(x,{b}) & rotl64(x,{c})) ^ rotl64(x,{d}) ^ rk(key,{j});")
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;\n}")
    return "\n".join(L) + "\n"


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B22[name][0]
    parts = [f'"""Bit-exact Python model for {name} (batch 22)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
             "RC64 = [%s]" % ", ".join("np.uint64(0x%X)" % int(v) for v in M.RC64),
             "AND3_SCHED6 = %r" % (M.AND3_SCHED6,),
             "AND3_SCHED5 = %r" % (M.AND3_SCHED5,),
             "AND4_SCHED6 = %r" % (M.AND4_SCHED6,),
             ""]
    for h in ["_rotl64", "_rk"]:
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
    for name, (fn, desc) in M.CANDIDATES_B22.items():
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
    ok = True
    IVL = "/home/hatch/tools/ivl-env/bin/iverilog"
    for name, (fn, desc) in M.CANDIDATES_B22.items():
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
            print(f"{name}: model OK", flush=True)
        open('/tmp/b22.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/b22", "/tmp/b22.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/b22"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
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
        open('/tmp/b22_tb.v', 'w').write("\n".join(tb))
        r = subprocess.run([IVL, "-o", "/tmp/b22_tb", f"{d}/rtl.v", "/tmp/b22_tb.v"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:200]}"); ok = False; continue
        r = subprocess.run(["/tmp/b22_tb"], capture_output=True, text=True)
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
