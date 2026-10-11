#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 31 (final-form probe: chi-final + non-rotational P-box diffusion)."""
import importlib.util
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b31 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return "{" + x + "[" + str(63 - r) + ":0], " + x + "[63:" + str(64 - r) + "]}"


def chi_rtl(x):
    # bit i of result = x_i ^ (~x_{(i+1)%64} & x_{(i+2)%64})
    # {x[0], x[63:1]} has bit i = x_{(i+1)%64}; {x[1], x[0], x[63:2]} has bit i = x_{(i+2)%64}
    return f"{x} ^ (~{{{x}[0], {x}[63:1]}} & {{{x}[1], {x}[0], {x}[63:2]}})"


def pbox_rtl(x, idx):
    # out bit i = in bit idx[i]; concatenation is MSB-first
    return "{" + ", ".join(f"{x}[{idx[i]}]" for i in range(63, -1, -1)) + "}"


def gen_rtl(name):
    if name.startswith("t6_chif"):
        sched = {"t6_chif5a": M.CHF5A, "t6_chif5b": M.CHF5B,
                 "t6_chif4a": M.CHF4A}[name]
        L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
             "  wire [63:0] st0 = val ^ key;"]
        for j, (ops, d) in enumerate(sched):
            term = " & ".join(rotl(f"st{j}", a) for a in ops)
            L.append(f"  wire [63:0] st{j+1} = st{j} ^ ({term}) ^ {rotl(f'st{j}', d)};")
        n = len(sched)
        L.append(f"  wire [63:0] ch = {chi_rtl(f'st{n}')};")
        L.append(f"  assign out = ch ^ {rotl('key',13)};")
    else:
        idx = M._BITREV if name == "t6_pbox5a" else M._BYTETR
        L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
             "  wire [63:0] st0 = val ^ key;"]
        for j, (ops,) in enumerate(M.PBX5):
            term = " & ".join(rotl(f"st{j}", a) for a in ops)
            L.append(f"  wire [63:0] st{j+1} = st{j} ^ ({term}) ^ {pbox_rtl(f'st{j}', idx)};")
        L.append(f"  assign out = st{len(M.PBX5)} ^ {rotl('key',13)};")
    L.append("endmodule")
    return "\n".join(L)


def gen_c(name, desc):
    L = ["#include <stdint.h>",
         "static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}",
         "static uint64_t chi64(uint64_t x){uint64_t r1=rotl64(x,63),r2=rotl64(x,62);return x^((~r1)&r2);}",
         f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {"]
    if name.startswith("t6_chif"):
        sched = {"t6_chif5a": M.CHF5A, "t6_chif5b": M.CHF5B,
                 "t6_chif4a": M.CHF4A}[name]
        L.append("    uint64_t x = val ^ key;")
        for ops, d in sched:
            term = "&".join(f"rotl64(x,{a})" for a in ops)
            L.append(f"    x ^= ({term}) ^ rotl64(x,{d});")
        L.append("    return chi64(x) ^ rotl64(key,13);\n}")
    else:
        idx = M._BITREV if name == "t6_pbox5a" else M._BYTETR
        idx_c = "{" + ",".join(str(int(i)) for i in idx) + "}"
        L.append("    uint64_t x = val ^ key;")
        L.append(f"    static const int PB[64] = {idx_c};")
        for (ops,) in M.PBX5:
            term = "&".join(f"rotl64(x,{a})" for a in ops)
            L.append("    { uint64_t px=0; for(int i=0;i<64;i++) px |= ((x>>PB[i])&1ULL)<<i;")
            L.append(f"      x ^= ({term}) ^ px; }}")
        L.append("    return x ^ rotl64(key,13);\n}")
    return "\n".join(L) + "\n"


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B31[name][0]
    sched_src = ""
    if name.startswith("t6_chif"):
        sn = {"t6_chif5a": "CHF5A", "t6_chif5b": "CHF5B", "t6_chif4a": "CHF4A"}[name]
        sched_src = f"{sn} = {getattr(M, sn)!r}\n"
    else:
        sn = "_BITREV" if name == "t6_pbox5a" else "_BYTETR"
        sched_src = f"{sn} = {getattr(M, sn).tolist()!r}\n"
        sched_src += f"PBX5 = {M.PBX5!r}\n"
    parts = [f'"""Bit-exact Python model for {name} (batch 31)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
             sched_src]
    for h in ["_rotl64", "_chi64", "_pbox64_vec", "_andcascade", "_andcascade_pbox"]:
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


def avalanche(fn):
    import numpy as np
    V = np.uint64(0x123456789ABCDEF0)
    K = np.uint64(0x0F1E2D3C4B5A6978)  # V != K (fixed test, batch-28 lesson)
    base = int(fn(V, K))
    ds = []
    for b in range(64):
        o = int(fn(V ^ np.uint64(1 << b), K))
        ds.append(bin(base ^ o).count("1"))
    avg = sum(ds) / len(ds)
    return avg, min(ds), max(ds)


def main():
    import numpy as np
    ok = True
    IVL = "/home/hatch/tools/ivl-env/bin/iverilog"
    triage = {}
    for name, (fn, desc) in M.CANDIDATES_B31.items():
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
    for name, (fn, desc) in M.CANDIDATES_B31.items():
        d = os.path.join(FB, name)
        sp = importlib.util.spec_from_file_location("m31_" + name, f"{d}/model.py")
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
        open('/tmp/m31.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/m31", "/tmp/m31.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/m31"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
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
        open('/tmp/m31_tb.v', 'w').write("\n".join(tb))
        r = subprocess.run([IVL, "-o", "/tmp/m31_tb", f"{d}/rtl.v", "/tmp/m31_tb.v"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:300]}"); ok = False; continue
        r = subprocess.run(["/tmp/m31_tb"], capture_output=True, text=True)
        outs = r.stdout.strip().split("\n")
        good = True
        for (v, k), o in zip(vecs, outs):
            if int(o.strip(), 16) != int(fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: RTL FAIL"); good = False; ok = False; break
        if good:
            print(f"{name}: RTL OK", flush=True)

    print("=== triage: avalanche (64 single-bit flips, V!=K) ===", flush=True)
    for name, (fn, desc) in M.CANDIDATES_B31.items():
        avg, mn, mx = avalanche(fn)
        apass = avg >= 27.0
        triage[name] = apass
        print(f"{name}: avalanche avg={avg:.1f} [{mn},{mx}] "
              f"-> triage {'PASS' if apass else 'KILL'}", flush=True)

    print("=== TRIAGE SUMMARY ===", flush=True)
    for name, p in triage.items():
        print(f"  {name}: {'PASS' if p else 'KILL'}", flush=True)
    print("ALL OK" if ok else "FAILURES PRESENT", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
