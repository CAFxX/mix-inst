#!/usr/bin/env python3
"""Generate bundles for Track 6 batch 15 (new structural axes).

Each bundle in fast_battery/candidates/<name>/ gets:
  - rtl.v:      Verilog RTL, bit-exact with the model
  - model.py:   SELF-CONTAINED Python model (no sys.path hacks)
  - impl.c:     REAL bit-exact C (never a stub)
  - meta.json:  includes rtl_top

Bit-exactness verified: model vs RTL (iverilog), model vs impl.c (gcc).
"""
import inspect
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_models_b15 as M

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


def rotl(x, r, w=64):
    r %= w
    if r == 0:
        return x
    return f"{{{x}[{w-1-r}:0], {x}[{w-1}:{w-r}]}}"


def rk(j):
    return f"({rotl('key', 13*(j+1))} ^ {RC_HEX[j % 8]})"


def rtl_head(name):
    return [f"module {name}(input [63:0] val, input [63:0] key, output [63:0] out);",
            "  wire [63:0] st0 = val ^ key;"]


def rtl_tail(cur):
    return ["  wire [63:0] key_r13 = " + rotl('key', 13) + ";",
            "  assign out = " + cur + " ^ {32'h0, key_r13[63:32]};",
            "endmodule"]


def gen_norc_rtl(name, sched):
    L = rtl_head(name)
    cur = "st0"
    for j, (a, b) in enumerate(sched):
        L.append(f"  wire [63:0] st{j+1} = {cur} ^ (({rotl(cur, a)} & {rotl(cur, b)})) ^ {rk(j)};")
        cur = f"st{j+1}"
    L += rtl_tail(cur)
    return "\n".join(L)


def gen_wide_rtl(name):
    L = rtl_head(name)
    cur = "st0"
    for j, (a, b, c, d, e) in enumerate(M.SCHED_WIDE6A):
        ra, rb, rc, rd, re = (rotl(cur, t) for t in (a, b, c, d, e))
        L.append(f"  wire [63:0] st{j+1} = {cur} ^ ((({ra} & {rb}) ^ ({rc} & {rd}) ^ {re})) ^ {rk(j)};")
        cur = f"st{j+1}"
    L += rtl_tail(cur)
    return "\n".join(L)


def gen_split_rtl(name):
    L = rtl_head(name)
    # round-key wires (declared once; part-selects need a named net)
    for j in range(12):
        L.append(f"  wire [63:0] rk{j} = {rk(j)};")
    cur = "st0"
    for s in range(3):
        L.append(f"  wire [31:0] s{s}_lo0 = {cur}[31:0];")
        L.append(f"  wire [31:0] s{s}_hi0 = {cur}[63:32];")
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = M.SPLIT_BASE[s][t]
            p = (b1 % 32, b2 % 32, b3 % 32)
            q = ((b1 + 7) % 32, (b2 + 7) % 32, (b3 + 7) % 32)
            lo, hi = f"s{s}_lo{t}", f"s{s}_hi{t}"
            nl, nh = f"s{s}_lo{t+1}", f"s{s}_hi{t+1}"
            L.append(f"  wire [31:0] {nl} = {lo} ^ (({rotl(lo, p[0], 32)} & {rotl(lo, p[1], 32)}) ^ {rotl(lo, p[2], 32)} ^ rk{j}[31:0]);")
            L.append(f"  wire [31:0] {nh} = {hi} ^ (({rotl(hi, q[0], 32)} & {rotl(hi, q[1], 32)}) ^ {rotl(hi, q[2], 32)} ^ rk{j}[31:0]);")
        r1, r2 = M.SPLIT_CROSS[s]
        L.append(f"  wire [31:0] s{s}_nlo = s{s}_lo2 ^ {rotl(f's{s}_hi2', r1, 32)} ^ rk{6+2*s}[31:0];")
        L.append(f"  wire [31:0] s{s}_nhi = s{s}_hi2 ^ {rotl(f's{s}_lo2', r2, 32)} ^ rk{7+2*s}[31:0];")
        L.append(f"  wire [63:0] st{s+1} = {{s{s}_nhi, s{s}_nlo}};")
        cur = f"st{s+1}"
    L += rtl_tail(cur)
    return "\n".join(L)


def gen_quad_rtl(name):
    L = rtl_head(name)
    for j in range(14):
        L.append(f"  wire [63:0] rk{j} = {rk(j)};")
    cur = "st0"
    for s in range(3):
        for i in range(4):
            L.append(f"  wire [15:0] s{s}_l{i}_0 = {cur}[{16*i+15}:{16*i}];")
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = M.QUAD_BASE[s][t]
            for i in range(4):
                p1, p2, p3 = (b1 + 5 * i) % 16, (b2 + 5 * i) % 16, (b3 + 5 * i) % 16
                ln, lo = f"s{s}_l{i}_{t+1}", f"s{s}_l{i}_{t}"
                L.append(f"  wire [15:0] {ln} = {lo} ^ (({rotl(lo, p1, 16)} & {rotl(lo, p2, 16)}) ^ {rotl(lo, p3, 16)} ^ rk{j}[15:0]);")
        c1, c2 = M.QUAD_CROSS[s]
        nl = []
        for i in range(4):
            a, b = f"s{s}_l{(i+1) % 4}_2", f"s{s}_l{(i+2) % 4}_2"
            nl.append(f"s{s}_n{i}")
            L.append(f"  wire [15:0] s{s}_n{i} = s{s}_l{i}_2 ^ {rotl(a, c1, 16)} ^ {rotl(b, c2, 16)} ^ rk{6+2*s+i}[15:0];")
        L.append(f"  wire [63:0] st{s+1} = {{{', '.join(reversed(nl))}}};")
        cur = f"st{s+1}"
    L += rtl_tail(cur)
    return "\n".join(L)


SB0_CASE = ("      4'h0: sb0 = 4'hc; 4'h1: sb0 = 4'ha; 4'h2: sb0 = 4'hd; 4'h3: sb0 = 4'h3;\n"
            "      4'h4: sb0 = 4'he; 4'h5: sb0 = 4'hb; 4'h6: sb0 = 4'hf; 4'h7: sb0 = 4'h7;\n"
            "      4'h8: sb0 = 4'h8; 4'h9: sb0 = 4'h9; 4'ha: sb0 = 4'h1; 4'hb: sb0 = 4'h5;\n"
            "      4'hc: sb0 = 4'h0; 4'hd: sb0 = 4'h2; 4'he: sb0 = 4'h4; 4'hf: sb0 = 4'h6;")


def gen_sboxrot_rtl(name):
    L = rtl_head(name)
    for j in range(6):
        L.append(f"  wire [63:0] rk{j} = {rk(j)};")
    L.append("  function [3:0] sb0(input [3:0] n);")
    L.append("    begin")
    L.append("      case (n)")
    L.append(SB0_CASE)
    L.append("      endcase")
    L.append("    end")
    L.append("  endfunction")
    cur = "st0"
    for j in range(6):
        kx = f"kx{j}"
        sb = f"sx{j}"
        L.append(f"  wire [63:0] {kx} = {cur} ^ rk{j};")
        L.append(f"  wire [63:0] {sb};")
        L.append(f"  genvar g{j};")
        L.append(f"  generate for (g{j}=0; g{j}<16; g{j}=g{j}+1) begin : sbl{j}")
        L.append(f"    assign {sb}[4*g{j}+3:4*g{j}] = sb0({kx}[4*g{j}+3:4*g{j}]);")
        L.append("  end endgenerate")
        L.append(f"  wire [63:0] st{j+1} = {rotl(sb, M.SBOX_ROTS[j])};")
        cur = f"st{j+1}"
    L += rtl_tail(cur)
    return "\n".join(L)


C_HEAD = """#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31; return r ? (x << r) | (x >> (32 - r)) : x;
}
static inline uint16_t rotl16(uint16_t x, int r) {
    r &= 15; return r ? (uint16_t)(((uint32_t)x << r) | ((uint32_t)x >> (16 - r))) : x;
}
static const uint64_t RC[8] = {%s};
static const uint8_t SB0[16] = {0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j %% 8]; }
""" % ", ".join("0x%016Xu" % v for v in RC_DEC)


def gen_norc_c(name, desc, sched):
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for j, (a, b) in enumerate(sched):
        L.append(f"    x ^= (rotl64(x,{a}) & rotl64(x,{b})) ^ rk(key,{j});")
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;\n}")
    return "\n".join(L) + "\n"


def gen_wide_c(name, desc):
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;"]
    for j, (a, b, c, d, e) in enumerate(M.SCHED_WIDE6A):
        L.append(f"    x ^= ((rotl64(x,{a}) & rotl64(x,{b})) ^ (rotl64(x,{c}) & rotl64(x,{d})) ^ rotl64(x,{e})) ^ rk(key,{j});")
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;\n}")
    return "\n".join(L) + "\n"


def gen_split_c(name, desc):
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;", "    uint32_t lo, hi;"]
    for s in range(3):
        L.append(f"    lo = (uint32_t)x; hi = (uint32_t)(x >> 32);  // super-stage {s}")
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = M.SPLIT_BASE[s][t]
            p = (b1 % 32, b2 % 32, b3 % 32)
            q = ((b1 + 7) % 32, (b2 + 7) % 32, (b3 + 7) % 32)
            L.append(f"    lo ^= (rotl32(lo,{p[0]}) & rotl32(lo,{p[1]})) ^ rotl32(lo,{p[2]}) ^ (uint32_t)rk(key,{j});")
            L.append(f"    hi ^= (rotl32(hi,{q[0]}) & rotl32(hi,{q[1]})) ^ rotl32(hi,{q[2]}) ^ (uint32_t)rk(key,{j});")
        r1, r2 = M.SPLIT_CROSS[s]
        L.append(f"    x = ((uint64_t)(lo ^ rotl32(hi,{r1}) ^ (uint32_t)rk(key,{6+2*s}))) | (((uint64_t)(hi ^ rotl32(lo,{r2}) ^ (uint32_t)rk(key,{7+2*s}))) << 32);")
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;\n}")
    return "\n".join(L) + "\n"


def gen_quad_c(name, desc):
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key;", "    uint16_t l[4], n[4];"]
    for s in range(3):
        L.append(f"    l[0]=(uint16_t)x; l[1]=(uint16_t)(x>>16); l[2]=(uint16_t)(x>>32); l[3]=(uint16_t)(x>>48);")
        for t in range(2):
            j = 2 * s + t
            b1, b2, b3 = M.QUAD_BASE[s][t]
            for i in range(4):
                p1, p2, p3 = (b1 + 5 * i) % 16, (b2 + 5 * i) % 16, (b3 + 5 * i) % 16
                L.append(f"    l[{i}] ^= (rotl16(l[{i}],{p1}) & rotl16(l[{i}],{p2})) ^ rotl16(l[{i}],{p3}) ^ (uint16_t)rk(key,{j});")
        c1, c2 = M.QUAD_CROSS[s]
        for i in range(4):
            L.append(f"    n[{i}] = l[{i}] ^ rotl16(l[{(i+1) % 4}],{c1}) ^ rotl16(l[{(i+2) % 4}],{c2}) ^ (uint16_t)rk(key,{6+2*s+i});")
        L.append("    x = (uint64_t)n[0] | ((uint64_t)n[1] << 16) | ((uint64_t)n[2] << 32) | ((uint64_t)n[3] << 48);")
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;\n}")
    return "\n".join(L) + "\n"


def gen_sboxrot_c(name, desc):
    L = [C_HEAD, f"// {name}: {desc}",
         "uint64_t mix_hash(uint64_t val, uint64_t key) {",
         "    uint64_t x = val ^ key, y;"]
    for j in range(6):
        L.append(f"    x ^= rk(key,{j}); y = 0;")
        L.append("    for (int i = 0; i < 16; i++) y |= (uint64_t)SB0[(x >> (4*i)) & 0xF] << (4*i);")
        L.append(f"    x = rotl64(y, {M.SBOX_ROTS[j]});")
    L.append("    x ^= rotl64(key, 13) >> 32;")
    L.append("    return x;\n}")
    return "\n".join(L) + "\n"


SCHED_OF = {
    "t6_norc6a": "SCHED_NORC6A", "t6_norc6b": "SCHED_NORC6B",
    "t6_norc7a": "SCHED_NORC7A", "t6_norc5a": "SCHED_NORC5A",
}
NEEDS = {
    "t6_norc6a": ["_norc_cascade", "SCHED_NORC6A"],
    "t6_norc6b": ["_norc_cascade", "SCHED_NORC6B"],
    "t6_norc7a": ["_norc_cascade", "SCHED_NORC7A"],
    "t6_norc5a": ["_norc_cascade", "SCHED_NORC5A"],
    "t6_wide6a": ["SCHED_WIDE6A"],
    "t6_split3a": ["_rotl32", "SPLIT_BASE", "SPLIT_CROSS"],
    "t6_quad3a": ["_rotl16", "QUAD_BASE", "QUAD_CROSS"],
    "t6_sboxrot6": ["_sbox_nibbles", "SBOX_ROTS"],
}
FAMILY = {
    "t6_norc6a": "norc", "t6_norc6b": "norc", "t6_norc7a": "norc",
    "t6_norc5a": "norc", "t6_wide6a": "wide", "t6_split3a": "split",
    "t6_quad3a": "quad", "t6_sboxrot6": "sboxrot",
}


def self_contained_model(name, desc):
    fn = M.CANDIDATES_B15[name][0]
    parts = [f'"""Bit-exact Python model for {name} (batch 15)."""',
             "import numpy as np", "",
             "M64 = np.uint64(0xFFFFFFFFFFFFFFFF)",
             "M32 = np.uint64(0xFFFFFFFF)",
             "M16 = np.uint64(0xFFFF)",
             "RC64 = [%s]" % ", ".join("np.uint64(0x%X)" % int(v) for v in M.RC64),
             "SBOX_MIDORI0 = np.array([0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6], dtype=np.uint64)",
             ""]
    for h in ["_rotl64", "_rk", "_postwhite"]:
        parts.append(inspect.getsource(getattr(M, h)))
    for need in NEEDS[name]:
        obj = getattr(M, need)
        if callable(obj):
            parts.append(inspect.getsource(obj))
        else:
            parts.append(f"{need} = {obj!r}")
    parts.append(inspect.getsource(fn))
    parts.append("")
    parts.append(f"def mix(v, k):")
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
    for name, (fn, desc) in M.CANDIDATES_B15.items():
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        fam = FAMILY[name]
        if fam == "norc":
            rtl = gen_norc_rtl(name, getattr(M, SCHED_OF[name]))
            impl_src = gen_norc_c(name, desc, getattr(M, SCHED_OF[name]))
        elif fam == "wide":
            rtl = gen_wide_rtl(name); impl_src = gen_wide_c(name, desc)
        elif fam == "split":
            rtl = gen_split_rtl(name); impl_src = gen_split_c(name, desc)
        elif fam == "quad":
            rtl = gen_quad_rtl(name); impl_src = gen_quad_c(name, desc)
        elif fam == "sboxrot":
            rtl = gen_sboxrot_rtl(name); impl_src = gen_sboxrot_c(name, desc)
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(rtl + "\n")
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(self_contained_model(name, desc))
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump({"name": name, "rtl_top": name, "description": desc,
                       "screen_keys": ["0x123456789abcdef0", "0x0"],
                       "practrand_keys": ["0x123456789abcdef0", "0x0"]},
                      f, indent=1)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(impl_src)
        print(f"{name}: bundle written")

    print("=== checks ===")
    ok = True
    IVL = "/home/hatch/tools/ivl-env/bin/iverilog"
    for name, (fn, desc) in M.CANDIDATES_B15.items():
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
        open('/tmp/b15.c', 'w').write('#include <stdio.h>\n#include <stdint.h>\nuint64_t mix_hash(uint64_t,uint64_t);\nint main(){uint64_t v,k;while(scanf("%lx %lx",&v,&k)==2)printf("%016lx\\n",mix_hash(v,k));return 0;}')
        r = subprocess.run(["gcc", "-O2", "-o", "/tmp/b15", "/tmp/b15.c", f"{d}/impl.c"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: GCC FAIL {r.stderr[:200]}"); ok = False; continue
        vecs = [(int(rng.integers(0, 2**64, dtype=np.uint64)),
                 int(rng.integers(0, 2**64, dtype=np.uint64))) for _ in range(200)]
        r = subprocess.run(["/tmp/b15"], input="\n".join(f"{v:x} {k:x}" for v, k in vecs),
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
        open('/tmp/b15tb.v', 'w').write('\n'.join(tb))
        r = subprocess.run([IVL, '-o', '/tmp/b15tb', f'{d}/rtl.v', '/tmp/b15tb.v'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: IVL COMPILE FAIL {r.stderr[:200]}"); ok = False; continue
        r = subprocess.run(['/tmp/b15tb'], capture_output=True, text=True, timeout=120)
        good = "TB DONE" in r.stdout and "MISMATCH" not in r.stdout
        print(f"{name}: RTL {'OK' if good else 'FAIL'}")
        if not good:
            print(r.stdout[-500:]); ok = False
    print("ALL OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
