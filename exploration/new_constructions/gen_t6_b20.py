#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 20 (AND + S-box hybrid)."""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b20 as M

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

SB0_CASE = ("      4'h0: sb0 = 4'hc; 4'h1: sb0 = 4'ha; 4'h2: sb0 = 4'hd; 4'h3: sb0 = 4'h3;\n"
            "      4'h4: sb0 = 4'he; 4'h5: sb0 = 4'hb; 4'h6: sb0 = 4'hf; 4'h7: sb0 = 4'h7;\n"
            "      4'h8: sb0 = 4'h8; 4'h9: sb0 = 4'h9; 4'ha: sb0 = 4'h1; 4'hb: sb0 = 4'h5;\n"
            "      4'hc: sb0 = 4'h0; 4'hd: sb0 = 4'h2; 4'he: sb0 = 4'h4; 4'hf: sb0 = 4'h6;")


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"


def rk(j):
    return f"({rotl('key', 13*(j+1))} ^ {RC_HEX[j % 8]})"


def gen_rtl(name):
    first_sbox = (name == "t6_hyb5f")
    L = [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
         "  wire [63:0] st0 = val ^ key;"]
    for j in range(5):
        L.append(f"  wire [63:0] rk{j} = {rk(j)};")
    L.append("  function [3:0] sb0(input [3:0] n);")
    L.append("    begin")
    L.append("      case (n)")
    L.append(SB0_CASE)
    L.append("      endcase")
    L.append("    end")
    L.append("  endfunction")
    cur, idx = "st0", 0
    order = ["sb", "a", "a", "a", "a"] if first_sbox else ["a", "a", "a", "a", "sb"]
    for pos, kind in enumerate(order):
        j = 0 if first_sbox and pos == 0 else (pos - 1 if first_sbox else pos)
        # rk index: sbox uses its position; AND uses AND_SCHED index
        if kind == "sb":
            rkj = 0 if first_sbox else 4
            kx, sb, pb = f"kx{pos}", f"sx{pos}", f"px{pos}"
            L.append(f"  wire [63:0] {kx} = {cur} ^ rk{rkj};")
            L.append(f"  wire [63:0] {sb};")
            L.append(f"  genvar g{pos};")
            L.append(f"  generate for (g{pos}=0; g{pos}<16; g{pos}=g{pos}+1) begin : sbl{pos}")
            L.append(f"    assign {sb}[4*g{pos}+3:4*g{pos}] = sb0({kx}[4*g{pos}+3:4*g{pos}]);")
            L.append("  end endgenerate")
            assigns = " ".join(f"assign {pb}[{M.PBOX[i]}] = {sb}[{i}];" for i in range(64))
            L.append(f"  wire [63:0] {pb};")
            L.append(f"  {assigns}")
            L.append(f"  wire [63:0] st{pos+1} = {pb};")
        else:
            aj = pos - 1 if first_sbox else pos
            a, b, c = M.AND_SCHED[aj]
            rkj = pos if first_sbox else pos
            # AND_SCHED index and rk index aligned for simplicity
            L.append(f"  wire [63:0] st{pos+1} = {cur} ^ (({rotl(cur, a)} & {rotl(cur, b)}) ^ {rotl(cur, c)}) ^ rk{rkj};")
        cur = f"st{pos+1}"
    L.append(f"  wire [63:0] key_r13 = {rotl('key', 13)};")
    L.append(f"  assign out = {cur} ^ {{32'h0, key_r13[63:32]}};")
    L.append("endmodule")
    return "\n".join(L)


C_HEAD = """#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint64_t RC[8] = {%s};
static const uint8_t SB0[16] = {0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6};
static const uint8_t PB[64] = {%s};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j %% 8]; }
""" % (", ".join("0x%016Xu" % v for v in RC_DEC),
       ",".join(str(p) for p in M.PBOX))


def gen_c(name, desc):
    first_sbox = (name == "t6_hyb5f")
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key, y, z;"]
    order = ["sb", "a", "a", "a", "a"] if first_sbox else ["a", "a", "a", "a", "sb"]
    ai = 0
    for pos, kind in enumerate(order):
        if kind == "sb":
            rkj = 0 if first_sbox else 4
            L.append(f"    x ^= rk(key,{rkj}); y = 0;")
            L.append("    for (int i = 0; i < 16; i++) y |= (uint64_t)SB0[(x >> (4*i)) & 0xF] << (4*i);")
            L.append("    z = 0; for (int i = 0; i < 64; i++) z |= ((y >> i) & 1ULL) << PB[i];")
            L.append("    x = z;")
        else:
            a, b, c = M.AND_SCHED[ai]
            rkj = pos
            L.append(f"    x ^= ((rotl64(x,{a}) & rotl64(x,{b})) ^ rotl64(x,{c})) ^ rk(key,{rkj});")
            ai += 1
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;\n}")
    return "\n".join(L) + "\n"


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B20[name][0]
    parts = [f'"""Bit-exact Python model for {name} (batch 20)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
             "RC64 = [%s]" % ", ".join("np.uint64(0x%X)" % int(v) for v in M.RC64),
             "SBOX_MIDORI0 = np.array([0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6], dtype=np.uint64)",
             "PBOX = %r" % (M.PBOX,),
             "AND_SCHED = %r" % (M.AND_SCHED,),
             ""]
    for h in ["_rotl64", "_rk", "_sbox16", "_pbox", "_and_stage", "_sbox_stage"]:
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
    for name, (fn, desc) in M.CANDIDATES_B20.items():
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
    for name, (fn, desc) in M.CANDIDATES_B20.items():
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
        open('/tmp/b20.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/b20", "/tmp/b20.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/b20"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
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
        open('/tmp/b20tb.v', 'w').write('\n'.join(tb))
        r = subprocess.run([IVL, '-o', '/tmp/b20tb', f'{d}/rtl.v', '/tmp/b20tb.v'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:200]}"); ok = False; continue
        r = subprocess.run(['/tmp/b20tb'], capture_output=True, text=True, timeout=120)
        good = "TB DONE" in r.stdout and "MISMATCH" not in r.stdout
        print(f"{name}: RTL {'OK' if good else 'FAIL'}")
        if not good:
            ok = False
    print("ALL OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
