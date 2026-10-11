#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 26 (andchi / split / twin4)."""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b26 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e"]


def rotl(x, r, w=64):
    r %= w
    if r == 0:
        return x
    hi = w - 1 - r
    lo = w - r
    return "{" + x + "[" + str(hi) + ":0], " + x + "[" + str(w - 1) + ":" + str(lo) + "]}"


def rk(j):
    return f"({rotl('key', 13*(j+1))} ^ {RC_HEX[j % 8]})"


def gen_rtl_andchi(name):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    for j in range(4):
        L.append(f"  wire [63:0] rk{j} = {rk(j)};")
    for j, (a, b, c) in enumerate(M.AND4_SCHED):
        L.append(f"  wire [63:0] st{j+1} = st{j} ^ ({rotl(f'st{j}',a)} & {rotl(f'st{j}',b)}) ^ {rotl(f'st{j}',c)} ^ rk{j};")
    a, b, c = M.CHI_ROTS
    L.append(f"  wire [63:0] rk4 = {rk(4)};")
    L.append(f"  wire [63:0] chip = {rotl('st4',a)};")
    L.append(f"  wire [63:0] chiq = {rotl('st4',b)};")
    L.append(f"  wire [63:0] chir = {rotl('st4',c)};")
    L.append("  wire [63:0] st5 = (chip ^ ((~chiq) & chir)) ^ rk4;")
    L.append(f"  assign out = st5 ^ {rotl('key',13)};")
    L.append("endmodule")
    return "\n".join(L)


def gen_rtl_split(name):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] x0 = val ^ key;",
         "  wire [31:0] hi0 = x0[63:32];",
         "  wire [31:0] lo0 = x0[31:0];"]
    # 32-bit rk wires (via 64-bit intermediate: icarus rejects part-select
    # on a parenthesized expression in a wire initializer)
    for j in range(12):
        L.append(f"  wire [63:0] rk64_{j} = {rk(j)};")
        L.append(f"  wire [31:0] rk32_{j} = rk64_{j}[31:0];")
    def casc(prefix, inp, jbase):
        LL = []
        prev = inp
        for j, (a, b, c) in enumerate(M.SPLIT32_SCHED):
            nxt = f"{prefix}s{j+1}"
            LL.append(f"  wire [31:0] {nxt} = {prev} ^ ({rotl(prev,a,32)} & {rotl(prev,b,32)}) ^ {rotl(prev,c,32)} ^ rk32_{jbase+j};")
            prev = nxt
        return LL, prev
    LL, hi3 = casc("hi", "hi0", 0)
    L.extend(LL)
    LL, lo3 = casc("lo", "lo0", 3)
    L.extend(LL)
    L.append(f"  wire [31:0] hix = {hi3} ^ {lo3};")
    L.append(f"  wire [31:0] lox = {lo3} ^ {rotl('hix',7,32)};")
    LL, hi6 = casc("hi2", "hix", 6)
    L.extend(LL)
    LL, lo6 = casc("lo2", "lox", 9)
    L.extend(LL)
    L.append(f"  wire [63:0] x1 = {{{hi6}, {lo6}}};")
    L.append(f"  assign out = x1 ^ {rotl('key',13)};")
    L.append("endmodule")
    return "\n".join(L)


def gen_rtl_twin(name):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    for j in range(4):
        L.append(f"  wire [63:0] rk{j} = {rk(j)};")
    for j, (a, b, c, d, e) in enumerate(M.TWIN4_SCHED):
        L.append(f"  wire [63:0] st{j+1} = st{j} ^ ({rotl(f'st{j}',a)} & {rotl(f'st{j}',b)}) ^ ({rotl(f'st{j}',c)} & {rotl(f'st{j}',d)}) ^ {rotl(f'st{j}',e)} ^ rk{j};")
    L.append(f"  assign out = st4 ^ {rotl('key',13)};")
    L.append("endmodule")
    return "\n".join(L)


GEN_RTL = {"t6_andchi5a": gen_rtl_andchi, "t6_split6a": gen_rtl_split,
           "t6_twin4a": gen_rtl_twin}


def _c_head():
    return ("#include <stdint.h>\n"
            "static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}\n"
            "static uint32_t rotl32(uint32_t x,int r){r&=31;return r?(x<<r)|(x>>(32-r)):x;}\n"
            "static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}\n")


def gen_c(name, desc):
    H = _c_head()
    if name == "t6_andchi5a":
        L = [H, f"// {name}: {desc}",
             "uint64_t mix_hash(uint64_t val, uint64_t key) {",
             "    uint64_t x = val ^ key;"]
        for j, (a, b, c) in enumerate(M.AND4_SCHED):
            L.append(f"    x ^= (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c}) ^ rk(key,{j});")
        a, b, c = M.CHI_ROTS
        L.append(f"    {{ uint64_t p=rotl64(x,{a}), q=rotl64(x,{b}), r=rotl64(x,{c});")
        L.append(f"      x = (p ^ ((~q) & r)) ^ rk(key,4); }}")
        L.append("    return x ^ rotl64(key,13);\n}")
    elif name == "t6_split6a":
        L = [H, f"// {name}: {desc}",
             "uint64_t mix_hash(uint64_t val, uint64_t key) {",
             "    uint64_t x = val ^ key;",
             "    uint32_t hi = (uint32_t)(x >> 32), lo = (uint32_t)x;",
             "    int j;",
             "    static const int S[3][3]={{1,2,9},{5,6,17},{3,4,25}};"]
        L.append("    for (j=0;j<3;j++) hi ^= (rotl32(hi,S[j][0])&rotl32(hi,S[j][1]))^rotl32(hi,S[j][2])^(uint32_t)rk(key,j);")
        L.append("    for (j=0;j<3;j++) lo ^= (rotl32(lo,S[j][0])&rotl32(lo,S[j][1]))^rotl32(lo,S[j][2])^(uint32_t)rk(key,3+j);")
        L.append("    hi ^= lo; lo ^= rotl32(hi,7);")
        L.append("    for (j=0;j<3;j++) hi ^= (rotl32(hi,S[j][0])&rotl32(hi,S[j][1]))^rotl32(hi,S[j][2])^(uint32_t)rk(key,6+j);")
        L.append("    for (j=0;j<3;j++) lo ^= (rotl32(lo,S[j][0])&rotl32(lo,S[j][1]))^rotl32(lo,S[j][2])^(uint32_t)rk(key,9+j);")
        L.append("    x = ((uint64_t)hi << 32) | lo;")
        L.append("    return x ^ rotl64(key,13);\n}")
    elif name == "t6_twin4a":
        L = [H, f"// {name}: {desc}",
             "uint64_t mix_hash(uint64_t val, uint64_t key) {",
             "    uint64_t x = val ^ key;"]
        for j, (a, b, c, d, e) in enumerate(M.TWIN4_SCHED):
            L.append(f"    x ^= (rotl64(x,{a})&rotl64(x,{b})) ^ (rotl64(x,{c})&rotl64(x,{d})) ^ rotl64(x,{e}) ^ rk(key,{j});")
        L.append("    return x ^ rotl64(key,13);\n}")
    return "\n".join(L) + "\n"


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B26[name][0]
    parts = [f'"""Bit-exact Python model for {name} (batch 26)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
             "M32 = np.uint64(0xFFFFFFFF)",
             "RC64 = [%s]" % ", ".join("np.uint64(0x%X)" % int(v) for v in M.RC64),
             ""]
    # schedules used by this candidate
    if name == "t6_andchi5a":
        parts.append("AND4_SCHED = %r" % (M.AND4_SCHED,))
        parts.append("CHI_ROTS = %r" % (M.CHI_ROTS,))
        helpers = ["_rotl64", "_rk", "_chi_layer"]
    elif name == "t6_split6a":
        parts.append("SPLIT32_SCHED = %r" % (M.SPLIT32_SCHED,))
        helpers = ["_rotl64", "_rotl32", "_rk", "_casc32"]
    else:
        parts.append("TWIN4_SCHED = %r" % (M.TWIN4_SCHED,))
        helpers = ["_rotl64", "_rk"]
    parts.append("")
    for h in helpers:
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
    for name, (fn, desc) in M.CANDIDATES_B26.items():
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(GEN_RTL[name](name) + "\n")
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
    for name, (fn, desc) in M.CANDIDATES_B26.items():
        d = os.path.join(FB, name)
        mu = __import__("importlib.util", fromlist=["util"])
        sp = mu.spec_from_file_location("m26_" + name, f"{d}/model.py")
        m = mu.module_from_spec(sp)
        sp.loader.exec_module(m)
        rng = np.random.default_rng(42)
        # model vs reference
        for _ in range(200):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            if int(m.mix(np.uint64(v), np.uint64(k))) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: MODEL FAIL"); ok = False; break
        else:
            print(f"{name}: model OK", flush=True)
        # impl.c vs reference
        open('/tmp/m26.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/m26", "/tmp/m26.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/m26"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
                           capture_output=True, text=True)
        for (v, k), o in zip(vecs, r.stdout.strip().split("\n")):
            if int(o, 16) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: C FAIL"); ok = False; break
        else:
            print(f"{name}: impl.c OK", flush=True)
        # RTL vs reference
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(20)]
        tb = ['`timescale 1ns/1ps', 'module tb;', '  reg [63:0] val,key;',
              '  wire [63:0] out;', f'  {name} dut(.val(val),.key(key),.out(out));',
              '  integer i;', '  initial begin']
        for v, k in vecs:
            tb.append(f'    val = 64\'h{v:016x}; key = 64\'h{k:016x}; #10;')
            tb.append(f'    $display("%016h", out);')
        tb += ['  end', 'endmodule']
        open('/tmp/m26_tb.v', 'w').write("\n".join(tb))
        r = subprocess.run([IVL, "-o", "/tmp/m26_tb", f"{d}/rtl.v", "/tmp/m26_tb.v"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:300]}"); ok = False; continue
        r = subprocess.run(["/tmp/m26_tb"], capture_output=True, text=True)
        outs = r.stdout.strip().split("\n")
        good = True
        for (v, k), o in zip(vecs, outs):
            if int(o.strip(), 16) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: RTL FAIL got {o.strip()}"); good = False; ok = False; break
        if good:
            print(f"{name}: RTL OK", flush=True)
    print("ALL OK" if ok else "FAILURES PRESENT", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
