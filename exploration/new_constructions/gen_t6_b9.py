#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 9 (hetero x^= simple ops).

Bundle hygiene (2026-10-09 lessons): self-contained model.py (inspect.getsource,
no sys.path), meta.json WITH rtl_top, REAL bit-exact impl.c (no stubs).
"""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b9 as M

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"


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


def _rtl_op(op, r):
    if op == "ANDXOR":
        return f"(({r[0]} & {r[1]}) ^ {r[2]})"
    elif op == "ORXOR":
        return f"(({r[0]} | {r[1]}) ^ {r[2]})"
    elif op == "MAJ":
        return (f"(({r[0]} & {r[1]}) | ({r[0]} & {r[2]}) "
                f"| ({r[1]} & {r[2]}))")


def gen_rtl(name, seq, sched):
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    cur = "st0"
    for i, op in enumerate(seq):
        r = [rotl(cur, t) for t in sched[i]]
        nl = _rtl_op(op, r)
        rk = f"({rotl('key', 13*(i+1))} ^ {RC_HEX[i % 8]})"
        L.append(f"  wire [63:0] st{i+1} = {cur} ^ {nl} ^ {rk};")
        cur = f"st{i+1}"
    L.append(f"  wire [63:0] key_r13 = {rotl('key', 13)};")
    L.append(f"  assign out = {cur} ^ {{32'h0, key_r13[63:32]}};")
    L.append("endmodule")
    return "\n".join(L)


def _c_op(op, r):
    if op == "ANDXOR":
        return f"    nl = (rotl64(x,{r[0]}) & rotl64(x,{r[1]})) ^ rotl64(x,{r[2]});"
    elif op == "ORXOR":
        return f"    nl = (rotl64(x,{r[0]}) | rotl64(x,{r[1]})) ^ rotl64(x,{r[2]});"
    elif op == "MAJ":
        return (f"    nl = maj64(rotl64(x,{r[0]}), rotl64(x,{r[1]}), "
                f"rotl64(x,{r[2]}));")


def gen_c(name, desc, seq, sched):
    L = ["#include <stdint.h>",
         "static inline uint64_t rotl64(uint64_t x, int r) {",
         "    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;",
         "}",
         "static inline uint64_t maj64(uint64_t a, uint64_t b, uint64_t c) {",
         "    return (a & b) | (a & c) | (b & c);",
         "}",
         f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    static const uint64_t RC[8] = {"
         + ", ".join("0x%016Xu" % v for v in RC_DEC) + "};",
         "    uint64_t x = val ^ key, nl;"]
    for i, op in enumerate(seq):
        L.append(f"    // stage {i}: {op}")
        L.append(_c_op(op, sched[i]))
        L.append(f"    x ^= nl ^ (rotl64(key, {13*(i+1)}) ^ RC[{i % 8}]);")
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;")
    L.append("}")
    return "\n".join(L) + "\n"


BUNDLES = {
    "t6_hx5a": (M.SEQ_HX5, M.SCHED_HX),
    "t6_hx6a": (M.SEQ_HX6, M.SCHED_HX),
    "t6_hx5b": (M.SEQ_HX5, M.SCHED_HXB),
    "t6_hx6b": (M.SEQ_HX6, M.SCHED_HXB),
}


def self_contained_model(name, desc, seq, sched):
    parts = [f'"""Bit-exact Python model for {name} (batch 9)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)"]
    rc_src = inspect.getsource(M).split("RC64 = [")[1].split("]")[0]
    parts.append("RC64 = [" + rc_src + "]")
    parts.append("")
    for fn_name in ["_rotl64", "_andxor", "_orxor", "_maj3"]:
        parts.append(inspect.getsource(getattr(M, fn_name)))
    parts.append("OP_FN = {'ANDXOR': _andxor, 'ORXOR': _orxor, 'MAJ': _maj3}")
    parts.append(inspect.getsource(M._hetero_xor_cascade))
    parts.append(inspect.getsource(M._vec))
    parts.append(f"SEQ = {seq!r}")
    parts.append(f"SCHED = {sched!r}")
    parts.append("")
    parts.append("def _scalar(v, k):")
    parts.append("    return _hetero_xor_cascade(v, k, SEQ, SCHED)")
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
    for name, (seq, sched) in BUNDLES.items():
        desc = M.CANDIDATES_B9[name][1]
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, seq, sched) + "\n")
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(self_contained_model(name, desc, seq, sched))
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump({"name": name, "rtl_top": name, "description": desc,
                       "screen_keys": ["0x123456789abcdef0", "0x0"],
                       "practrand_keys": ["0x123456789abcdef0", "0x0"]},
                      f, indent=1)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_c(name, desc, seq, sched))
        print(f"{name}: bundle written")

    print("\n=== bit-exact checks ===")
    ok = True
    for name in BUNDLES:
        d = os.path.join(FB, name)
        mu = __import__("importlib.util", fromlist=["util"])
        spec = mu.spec_from_file_location("m_" + name,
                                          os.path.join(d, "model.py"))
        m = mu.module_from_spec(spec)
        spec.loader.exec_module(m)
        ref_fn = M.CANDIDATES_B9[name][0]
        import numpy as np
        rng = np.random.default_rng(42)
        for trial in range(200):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            if int(m.mix(np.uint64(v), np.uint64(k))) != int(ref_fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: MODEL MISMATCH"); ok = False; break
        else:
            print(f"{name}: model.py OK (200v)")
        # impl.c
        with open("/tmp/b9_test.c", "w") as f:
            f.write('#include <stdio.h>\n#include <stdint.h>\n'
                    'uint64_t mix_hash(uint64_t, uint64_t);\n'
                    'int main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)'
                    '{printf("%016lx\\n",mix_hash(v,k));}return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/b9_test", "/tmp/b9_test.c",
                            os.path.join(d, "impl.c")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: COMPILE FAIL"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/b9_test"],
                           input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
                           capture_output=True, text=True)
        for (v, k), o in zip(vecs, r.stdout.strip().split("\n")):
            if int(o, 16) != int(ref_fn(np.uint64(v), np.uint64(k))):
                print(f"{name}: IMPL.C MISMATCH"); ok = False; break
        else:
            print(f"{name}: impl.c OK (200v)")
    # RTL via iverilog
    IVL = '/home/hatch/tools/ivl-env/bin/iverilog'
    for name in BUNDLES:
        d = os.path.join(FB, name)
        fn = M.CANDIDATES_B9[name][0]
        rng = np.random.default_rng(7)
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(20)]
        tb = ['`timescale 1ns/1ps', 'module tb;',
              '  reg [63:0] val, key;', '  wire [63:0] out;',
              f'  {name} dut(.val(val), .key(key), .out(out));',
              '  initial begin']
        for v, k in vecs:
            exp = int(fn(np.uint64(v), np.uint64(k)))
            tb.append(f'    val = 64\'h{v:016x}; key = 64\'h{k:016x}; #10;')
            tb.append(f'    if (out !== 64\'h{exp:016x}) $display("MISMATCH");')
        tb += ['    $display("TB DONE");', '    $finish;', '  end', 'endmodule']
        open('/tmp/b9_tb.v', 'w').write('\n'.join(tb))
        r = subprocess.run([IVL, '-o', '/tmp/b9_tb', f'{d}/rtl.v', '/tmp/b9_tb.v'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f'{name}: IVERILOG FAIL'); ok = False; continue
        r = subprocess.run(['/tmp/b9_tb'], capture_output=True, text=True, timeout=60)
        print(f'{name}: RTL {"OK (20v)" if "TB DONE" in r.stdout and "MISMATCH" not in r.stdout else "MISMATCH!"}')
        if "MISMATCH" in r.stdout: ok = False
    print("ALL OK" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
