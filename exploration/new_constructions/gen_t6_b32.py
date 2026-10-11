#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 32 (cross-fed dual-lane, AND-sandwich, skip-coupled)."""
import importlib.util
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b32 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

LANE_SCHEDS = {
    "t6_lane3a": (M.LANE3A_A, M.LANE3A_B, M.LANE3A_S, "LANE3A_A", "LANE3A_B", "LANE3A_S"),
    "t6_lane3b": (M.LANE3B_A, M.LANE3B_B, M.LANE3B_S, "LANE3B_A", "LANE3B_B", "LANE3B_S"),
    "t6_lane4a": (M.LANE4A_A, M.LANE4A_B, M.LANE4A_S, "LANE4A_A", "LANE4A_B", "LANE4A_S"),
}
SAND_SCHEDS = {
    "t6_sand5a": (M.SAND5A, "SAND5A"),
    "t6_sand5b": (M.SAND5B, "SAND5B"),
    "t6_sand4a": (M.SAND4A, "SAND4A"),
}
SKIP_SCHEDS = {
    "t6_skip4a": (M.SKIP4A, "SKIP4A"),
    "t6_skip5a": (M.SKIP5A, "SKIP5A"),
}


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return "{" + x + "[" + str(63 - r) + ":0], " + x + "[63:" + str(64 - r) + "]}"


def gen_rtl(name):
    if name.startswith("t6_lane"):
        sa, sb, ss, *_ = LANE_SCHEDS[name]
        L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
             "  wire [63:0] a0 = val ^ key;",
             f"  wire [63:0] b0 = {rotl('key', 29)};"]
        for j, (((pa, qa), da), ((pb, qb), db), s) in enumerate(zip(sa, sb, ss)):
            L.append(f"  wire [63:0] a{j+1} = a{j} ^ ({rotl(f'a{j}', pa)} & {rotl(f'a{j}', qa)}) ^ {rotl(f'a{j}', da)};")
            L.append(f"  wire [63:0] b{j+1} = b{j} ^ ({rotl(f'b{j}', pb)} & {rotl(f'b{j}', qb)}) ^ {rotl(f'b{j}', db)} ^ {rotl(f'a{j}', s)};")
        n = len(sa)
        L.append(f"  assign out = a{n} ^ b{n} ^ {rotl('key', 13)};")
    elif name.startswith("t6_sand"):
        sched, _ = SAND_SCHEDS[name]
        L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
             "  wire [63:0] st0 = val ^ key;"]
        for j, (a, (b, c), d) in enumerate(sched):
            L.append(f"  wire [63:0] st{j+1} = st{j} ^ {rotl(f'st{j}', a)} ^ ({rotl(f'st{j}', b)} & {rotl(f'st{j}', c)}) ^ {rotl(f'st{j}', d)};")
        L.append(f"  assign out = st{len(sched)} ^ {rotl('key', 13)};")
    else:
        sched, _ = SKIP_SCHEDS[name]
        L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
             "  wire [63:0] stm1 = 64'h0;",
             "  wire [63:0] st0 = val ^ key;"]
        for j, ((a, b), d, s) in enumerate(sched):
            prev = "stm1" if j == 0 else f"st{j-1}"
            L.append(f"  wire [63:0] st{j+1} = st{j} ^ ({rotl(f'st{j}', a)} & {rotl(f'st{j}', b)}) ^ {rotl(f'st{j}', d)} ^ {rotl(prev, s)};")
        L.append(f"  assign out = st{len(sched)} ^ {rotl('key', 13)};")
    L.append("endmodule")
    return "\n".join(L)


def gen_c(name, desc):
    L = ["#include <stdint.h>",
         "static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}",
         f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {"]
    if name.startswith("t6_lane"):
        sa, sb, ss, *_ = LANE_SCHEDS[name]
        L.append("    uint64_t a = val ^ key, b = rotl64(key,29);")
        for ((pa, qa), da), ((pb, qb), db), s in zip(sa, sb, ss):
            L.append(f"    {{ uint64_t an = a ^ (rotl64(a,{pa})&rotl64(a,{qa})) ^ rotl64(a,{da});")
            L.append(f"      uint64_t bn = b ^ (rotl64(b,{pb})&rotl64(b,{qb})) ^ rotl64(b,{db}) ^ rotl64(a,{s});")
            L.append("      a = an; b = bn; }")
        L.append("    return a ^ b ^ rotl64(key,13);\n}")
    elif name.startswith("t6_sand"):
        sched, _ = SAND_SCHEDS[name]
        L.append("    uint64_t x = val ^ key;")
        for a, (b, c), d in sched:
            L.append(f"    x ^= rotl64(x,{a}) ^ (rotl64(x,{b})&rotl64(x,{c})) ^ rotl64(x,{d});")
        L.append("    return x ^ rotl64(key,13);\n}")
    else:
        sched, _ = SKIP_SCHEDS[name]
        L.append("    uint64_t x = val ^ key, xm1 = 0;")
        for (a, b), d, s in sched:
            L.append(f"    {{ uint64_t xn = x ^ (rotl64(x,{a})&rotl64(x,{b})) ^ rotl64(x,{d}) ^ rotl64(xm1,{s});")
            L.append("      xm1 = x; x = xn; }")
        L.append("    return x ^ rotl64(key,13);\n}")
    return "\n".join(L) + "\n"


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B32[name][0]
    if name.startswith("t6_lane"):
        _, _, _, sna, snb, sns = LANE_SCHEDS[name]
        sched_src = "".join(f"{sn} = {getattr(M, sn)!r}\n" for sn in (sna, snb, sns))
        helpers = ["_rotl64", "_lanes"]
    elif name.startswith("t6_sand"):
        _, sn = SAND_SCHEDS[name]
        sched_src = f"{sn} = {getattr(M, sn)!r}\n"
        helpers = ["_rotl64", "_sandwich"]
    else:
        _, sn = SKIP_SCHEDS[name]
        sched_src = f"{sn} = {getattr(M, sn)!r}\n"
        helpers = ["_rotl64", "_skipcascade"]
    parts = [f'"""Bit-exact Python model for {name} (batch 32)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)", sched_src]
    for h in helpers:
        parts.append(inspect.getsource(getattr(M, h)))
    parts.append(inspect.getsource(fn))
    parts.append("")
    parts.append("def mix(v, k):")
    parts.append("    if np.ndim(v) == 0 and np.ndim(k) == 0:")
    parts.append(f"        return int({fn.__name__}(np.uint64(v), np.uint64(k)))")
    parts.append(f"    return {fn.__name__}(np.asanyarray(v, dtype=np.uint64), np.asanyarray(K, dtype=np.uint64))".replace("K)", "k)"))
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
    for name, (fn, desc) in M.CANDIDATES_B32.items():
        if name == "t6_lane3a":
            continue  # triage-killed (av 24.3)
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name) + "\n")
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(self_contained_model(name, desc))
        g1 = int(fn(np.uint64(0x0), np.uint64(0x123456789ABCDEF0)))
        g2 = int(fn(np.uint64(0x123456789ABCDEF0), np.uint64(0x0)))
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump({"name": name, "rtl_top": name, "description": desc,
                       "screen_keys": ["0x123456789abcdef0", "0x0"],
                       "practrand_keys": ["0x123456789abcdef0", "0x0"],
                       "goldens": [
                           {"val": "0x0", "key": "0x123456789abcdef0",
                            "out": f"0x{g1:016x}"},
                           {"val": "0x123456789abcdef0", "key": "0x0",
                            "out": f"0x{g2:016x}"}]},
                      f, indent=1)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_c(name, desc))
        print(f"{name}: bundle written", flush=True)

    print("=== bit-exactness checks ===", flush=True)
    for name, (fn, desc) in M.CANDIDATES_B32.items():
        if name == "t6_lane3a":
            continue
        d = os.path.join(FB, name)
        sp = importlib.util.spec_from_file_location("m32_" + name, f"{d}/model.py")
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        rng = np.random.default_rng(42)
        for _ in range(200):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            if int(m.mix(np.uint64(v), np.uint64(k))) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: MODEL FAIL"); ok = False; break
        else:
            print(f"{name}: model OK", flush=True)
        open('/tmp/m32.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/m32", "/tmp/m32.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/m32"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
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
            tb.append('    $display("%016h", out);')
        tb += ['  end', 'endmodule']
        open('/tmp/m32_tb.v', 'w').write("\n".join(tb))
        r = subprocess.run([IVL, "-o", "/tmp/m32_tb", f"{d}/rtl.v", "/tmp/m32_tb.v"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:300]}"); ok = False; continue
        r = subprocess.run(["/tmp/m32_tb"], capture_output=True, text=True)
        outs = r.stdout.strip().split("\n")
        good = True
        for (v, k), o in zip(vecs, outs):
            if int(o, 16) != int(fn(np.uint64(v), np.uint64(k))):
                good = False; break
        print(f"{name}: RTL {'OK' if good else 'FAIL'}", flush=True)
        if not good:
            ok = False
    print("ALL OK" if ok else "FAILURES PRESENT")


if __name__ == "__main__":
    main()
