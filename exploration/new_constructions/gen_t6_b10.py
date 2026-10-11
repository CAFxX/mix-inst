#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 10 (5-stage AND-cascade).

Bundle hygiene: self-contained model.py, meta.json WITH rtl_top, REAL impl.c.
"""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b10 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"


def gen_rtl(name, stages):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] x0 = val ^ key;"]
    cur = "x0"
    for i, (a, b, c) in enumerate(stages):
        ra, rb, rc = rotl(cur, a), rotl(cur, b), rotl(cur, c)
        L.append(f"  wire [63:0] x{i+1} = {cur} ^ ({ra} & {rb}) ^ {rc};")
        cur = f"x{i+1}"
    L.append(f"  assign out = {cur} ^ {rotl('key', 13)};")
    L.append("endmodule")
    return "\n".join(L)


def gen_c(name, desc, stages):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for (a, b, c) in stages:
        L.append(f"    x ^= (rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c});")
    L.append("    x ^= rotl64(key, 13);")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


BUNDLES = {
    "t6_and5a": M.STAGES_A,
    "t6_and5b": M.STAGES_B,
}


def self_contained_model(name, desc, stages):
    parts = [f'"""Bit-exact Python model for {name} (batch 10)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)"]
    parts.append(inspect.getsource(M._rotl64))
    parts.append(inspect.getsource(M._and5_cascade))
    parts.append(inspect.getsource(M._vec))
    parts.append(f"STAGES = {stages!r}")
    parts.append("")
    parts.append("def _scalar(v, k):")
    parts.append("    return _and5_cascade(v, k, STAGES)")
    parts.append("_mix_np = _vec(_scalar)")
    parts.append("")
    parts.append("def mix(v, k):")
    parts.append("    if np.ndim(v) == 0 and np.ndim(k) == 0:")
    parts.append("        return _scalar(int(v), int(k))")
    parts.append("    return _mix_np(v, k)")
    parts.append("def mix_np(V, K):")
    parts.append("    return _mix_np(V, K)")
    parts.append(f"meta = {{'desc': {desc!r}}}")
    return "\n".join(parts) + "\n"


def main():
    import numpy as np
    for name, stages in BUNDLES.items():
        desc = M.CANDIDATES_B10[name][1]
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, stages) + "\n")
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(self_contained_model(name, desc, stages))
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump({"name": name, "rtl_top": name, "description": desc,
                       "screen_keys": ["0x123456789abcdef0", "0x0"],
                       "practrand_keys": ["0x123456789abcdef0", "0x0"]},
                      f, indent=1)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_c(name, desc, stages))
        print(f"{name}: bundle written")

    print("\n=== bit-exact checks ===")
    ok = True
    IVL = '/home/hatch/tools/ivl-env/bin/iverilog'
    for name, stages in BUNDLES.items():
        d = os.path.join(FB, name)
        mu = __import__("importlib.util", fromlist=["util"])
        spec = mu.spec_from_file_location("m_" + name, os.path.join(d, "model.py"))
        m = mu.module_from_spec(spec); spec.loader.exec_module(m)
        ref_fn = M.CANDIDATES_B10[name][0]
        import numpy as np
        rng = np.random.default_rng(42)
        for _ in range(200):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            if int(m.mix(np.uint64(v), np.uint64(k))) != int(ref_fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: MODEL MISMATCH"); ok = False; break
        else:
            print(f"{name}: model OK")
        # impl.c
        open('/tmp/b10_t.c','w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc","-O2","-o","/tmp/b10_t","/tmp/b10_t.c",f"{d}/impl.c"],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: GCC FAIL"); ok=False; continue
        vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(200)]
        r=subprocess.run(["/tmp/b10_t"],input="\n".join(f"{v:x} {k:x}" for v,k in vecs),capture_output=True,text=True)
        for (v,k),o in zip(vecs,r.stdout.strip().split("\n")):
            if int(o,16)!=int(ref_fn(np.uint64(v),np.uint64(k))): print(f"{name}: C MISMATCH"); ok=False; break
        else: print(f"{name}: impl.c OK")
        # RTL
        fn = ref_fn
        vecs=[(int(rng.integers(0,2**64,dtype=np.uint64)),int(rng.integers(0,2**64,dtype=np.uint64))) for _ in range(20)]
        tb=['`timescale 1ns/1ps','module tb;','  reg [63:0] val, key;','  wire [63:0] out;',f'  {name} dut(.val(val),.key(key),.out(out));','  initial begin']
        for v,k in vecs:
            exp=int(fn(np.uint64(v),np.uint64(k)))
            tb.append(f"    val=64'h{v:016x};key=64'h{k:016x};#10;")
            tb.append(f"    if(out!==64'h{exp:016x})$display(\"MISMATCH\");")
        tb+=['    $display("TB DONE");','    $finish;','  end','endmodule']
        open('/tmp/b10_tb.v','w').write('\n'.join(tb))
        r=subprocess.run([IVL,'-o','/tmp/b10_tb',f'{d}/rtl.v','/tmp/b10_tb.v'],capture_output=True,text=True)
        if r.returncode!=0: print(f"{name}: IVL FAIL"); ok=False; continue
        r=subprocess.run(['/tmp/b10_tb'],capture_output=True,text=True,timeout=60)
        mm="MISMATCH" in r.stdout; dd="TB DONE" in r.stdout
        print(f"{name}: RTL {'OK' if dd and not mm else 'MISMATCH!'}")
        if mm or not dd: ok=False
    print("ALL OK" if ok else "FAILURES")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
