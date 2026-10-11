#!/usr/bin/env python3
"""Generate Verilog RTL for Track 6 batch 2, bit-exact with t6_models_b2.py."""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t6_models_b2 import CANDIDATES_B2, MIX_NP_B2

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
T6 = os.path.dirname(os.path.abspath(__file__))
PORTS = "(input [63:0] val, input [63:0] key, output [63:0] out)"

RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F,
      0x78DDE6E5FD29F054, 0x2545F4914F6CDD1D, 0x9E3779B97F4A7C15 ^ 0xDEADBEEF,
      0x3C6EF372FE94F82A ^ 0x12345678, 0xDAA66D2C7DDF743F ^ 0xABCDEF01]


def gen_trivium64b():
    lines = [f"module t6_trivium64b{PORTS};", "  wire [63:0] st0 = val ^ key;"]
    n = 0; cur = "st0"
    for rnd in range(8):
        for c in range(8):
            n += 1; nxt = f"st{n}"
            lines.append(f"  wire fb{n}_a = {cur}[5] & {cur}[11];")
            lines.append(f"  wire fb{n}_b = {cur}[23] & {cur}[31];")
            lines.append(f"  wire fb{n} = fb{n}_a ^ fb{n}_b ^ {cur}[17] ^ {cur}[41] ^ {cur}[53];")
            lines.append(f"  wire [63:0] {nxt} = {{{cur}[62:0], fb{n}}};")
            cur = nxt
        n += 1; nxt = f"st{n}"
        lines.append(f"  wire [63:0] {nxt} = {cur} ^ 64'h{RC[rnd]:016x};")
        cur = nxt
    lines.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_grain64():
    lines = [f"module t6_grain64{PORTS};", "  wire [63:0] st0 = val ^ key;"]
    n = 0; cur = "st0"
    for rnd in range(6):
        for c in range(10):
            n += 1; nxt = f"st{n}"
            bit = (rnd * 10) % 64  # model: same key bit for all 10 clocks in round
            lines.append(f"  wire lfb{n} = {cur}[59] ^ {cur}[53] ^ {cur}[47] ^ {cur}[0];")
            lines.append(f"  wire h{n}_a = {cur}[11] & {cur}[29];")
            lines.append(f"  wire h{n}_b = {cur}[23] & {cur}[43];")
            lines.append(f"  wire h{n}_c = {cur}[5] & {cur}[37] & {cur}[59];")
            lines.append(f"  wire h{n} = {cur}[7] ^ {cur}[19] ^ {cur}[33] ^ {cur}[51] ^ h{n}_a ^ h{n}_b ^ h{n}_c;")
            lines.append(f"  wire [63:0] {nxt} = {{{cur}[62:0], (lfb{n} ^ h{n} ^ key[{bit}])}};")
            cur = nxt
        n += 1; nxt = f"st{n}"
        lines.append(f"  wire [63:0] {nxt} = {cur} ^ 64'h{RC[rnd]:016x};")
        cur = nxt
    lines.append(f"  assign out = {cur};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_xorshift_nl():
    lines = [f"module t6_xorshift_nl{PORTS};", "  wire [63:0] x0 = val ^ key;"]
    for rnd in range(4):
        x = f"x{rnd}"; nx = f"x{rnd+1}"
        # xorshift: x ^= x<<13; x ^= x>>7; x ^= x<<17 (use intermediate wires)
        lines.append(f"  wire [63:0] {x}_s1 = {x} ^ {{{x}[50:0], 13'h0}};")
        lines.append(f"  wire [63:0] {x}_s2 = {x}_s1 ^ {{7'h0, {x}_s1[63:7]}};")
        lines.append(f"  wire [63:0] {x}_s3 = {x}_s2 ^ {{{x}_s2[46:0], 17'h0}};")
        # nonlinear filter: x ^= (rotl(x,7) & rotl(x,23)) ^ rotl(x,41)
        # rotl64(x,7) = {x[56:0], x[63:57]}
        lines.append(f"  wire [63:0] {x}_r7 = {{{x}_s3[56:0], {x}_s3[63:57]}};")
        lines.append(f"  wire [63:0] {x}_r23 = {{{x}_s3[40:0], {x}_s3[63:41]}};")
        lines.append(f"  wire [63:0] {x}_r41 = {{{x}_s3[22:0], {x}_s3[63:23]}};")
        lines.append(f"  wire [63:0] {x}_f = {x}_s3 ^ ({x}_r7 & {x}_r23) ^ {x}_r41;")
        # key injection: x ^= RC ^ (key >> 16*rnd)
        if rnd == 0:
            kinj = "key"
        else:
            kinj = f"{{{(16*rnd)}'h0, key[63:{16*rnd}]}}"
        lines.append(f"  wire [63:0] {nx} = {x}_f ^ 64'h{RC[rnd]:016x} ^ {kinj};")
    lines.append("  assign out = x4;")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_simon_like():
    lines = [f"module t6_simon_like{PORTS};",
             "  wire [31:0] L0 = val[31:0];", "  wire [31:0] R0 = val[63:32];"]
    RC32 = [0x7F4A7C15, 0xFE94F82A, 0x7DDF743F, 0xFD29F054, 0x4F6CDD1D, 0xA1E7C2FA]
    for i in range(10):
        # model: rk = rotl32(k_low, 3*i) ^ RC32_low  (rotl FIRST, then XOR)
        r = 3 * i
        if r == 0:
            rkb = "key[31:0]"
        else:
            lines.append(f"  wire [31:0] rkr{i} = {{key[{31-r}:0], key[31:{32-r}]}};")
            rkb = f"rkr{i}"
        lines.append(f"  wire [31:0] rk{i} = {rkb} ^ 32'h{RC32[i % 6]:08x};")
        # f(R) = (rotl(R,1) & rotl(R,8)) ^ rotl(R,2)
        lines.append(f"  wire [31:0] fr{i}_1 = {{R{i}[30:0], R{i}[31]}};")  # rotl1
        lines.append(f"  wire [31:0] fr{i}_8 = {{R{i}[23:0], R{i}[31:24]}};")  # rotl8
        lines.append(f"  wire [31:0] fr{i}_2 = {{R{i}[29:0], R{i}[31:30]}};")  # rotl2
        lines.append(f"  wire [31:0] F{i} = (fr{i}_1 & fr{i}_8) ^ fr{i}_2;")
        lines.append(f"  wire [31:0] L{i+1} = R{i};")
        lines.append(f"  wire [31:0] R{i+1} = L{i} ^ F{i} ^ rk{i};")
    lines.append("  assign out = {R10, L10};")
    lines.append("endmodule")
    return "\n".join(lines)


GEN_B2 = {
    "t6_trivium64b": gen_trivium64b,
    "t6_grain64": gen_grain64,
    "t6_xorshift_nl": gen_xorshift_nl,
    "t6_simon_like": gen_simon_like,
}


def main():
    for name, gen in GEN_B2.items():
        fn, desc = CANDIDATES_B2[name]
        _nm = fn.__name__
        assert _nm.isidentifier(), (f"GEN BUG: {name} scalar fn __name__={_nm!r} not a valid identifier; "
                                            f"gen emits `return {{_nm}}(v,k)` which would be a SyntaxError (lambda?)")
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(T6, "t6_models_b2.py")) as f:
            src = f.read()
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(src + f"""
def _mix_scalar(v, k):
    return {fn.__name__}(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B2['{name}'](v, k)

def mix_np(V, K):
    return MIX_NP_B2['{name}'](V, K)
""")
        with open(os.path.join(cdir, "rtl.v"), "w") as f:
            f.write(gen() + "\n")
        with open(os.path.join(cdir, "impl.c"), "w") as f:
            f.write("/* stub */\n")
        g1 = fn(0x0, 0x123456789ABCDEF0)
        g2 = fn(0x123456789ABCDEF0, 0x0)
        meta = {"name": name, "description": desc,
                "screen_keys": ["0x123456789abcdef0", "0x0"],
                "practrand_keys": ["0x123456789abcdef0", "0x0"],
                "goldens": [
                    {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(g1)},
                    {"val": "0x123456789abcdef0", "key": "0x0", "out": hex(g2)}]}
        with open(os.path.join(cdir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print(f"created {name}: {desc}")


if __name__ == "__main__":
    main()
