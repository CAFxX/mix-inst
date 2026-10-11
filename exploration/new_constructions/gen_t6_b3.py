#!/usr/bin/env python3
"""Generate Verilog RTL for Track 6 batch 3."""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t6_models_b3 import CANDIDATES_B3, MIX_NP_B3

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
T6 = os.path.dirname(os.path.abspath(__file__))
PORTS = "(input [63:0] val, input [63:0] key, output [63:0] out)"
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F,
      0x78DDE6E5FD29F054, 0x2545F4914F6CDD1D, 0x9E3779B97F4A7C15 ^ 0xDEADBEEF]


def gen_ca30():
    # 16 steps of Rule 30 on 64-bit ring. Each bit: nb[i] = s[i-1] ^ (s[i] | s[i+1])
    lines = [f"module t6_ca30{PORTS};", "  wire [63:0] st0 = val ^ key;"]
    cur = "st0"
    for rnd in range(16):
        nxt = f"st{rnd+1}"
        # unroll 64 bits: nb[i] = cur[(i-1)%64] ^ (cur[i] | cur[(i+1)%64])
        terms = []
        for i in range(64):
            l = (i - 1) % 64; r = (i + 1) % 64
            terms.append(f"({cur}[{l}] ^ ({cur}[{i}] | {cur}[{r}]))")
        # build as concatenation: {nb63, nb62, ..., nb0}
        concat = "{" + ", ".join(reversed(terms)) + "}"
        if rnd % 4 == 3:
            lines.append(f"  wire [63:0] {nxt}_raw = {concat};")
            lines.append(f"  wire [63:0] {nxt} = {nxt}_raw ^ 64'h{RC[rnd//4]:016x};")
        else:
            lines.append(f"  wire [63:0] {nxt} = {concat};")
        cur = nxt
    lines.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_ca_mix():
    lines = [f"module t6_ca_mix{PORTS};", "  wire [63:0] st0 = val ^ key;"]
    cur = "st0"
    rules = [30, 150, 90]
    for rnd in range(12):
        rule = rules[rnd % 3]
        nxt = f"st{rnd+1}"
        terms = []
        for i in range(64):
            l = (i - 1) % 64; r = (i + 1) % 64
            if rule == 30:
                terms.append(f"({cur}[{l}] ^ ({cur}[{i}] | {cur}[{r}]))")
            elif rule == 150:
                terms.append(f"({cur}[{l}] ^ {cur}[{i}] ^ {cur}[{r}])")
            else:
                terms.append(f"({cur}[{l}] ^ {cur}[{r}])")
        concat = "{" + ", ".join(reversed(terms)) + "}"
        if rnd % 3 == 2:
            lines.append(f"  wire [63:0] {nxt}_raw = {concat};")
            lines.append(f"  wire [63:0] {nxt} = {nxt}_raw ^ 64'h{RC[rnd//3]:016x};")
        else:
            lines.append(f"  wire [63:0] {nxt} = {concat};")
        cur = nxt
    lines.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_ascon5():
    lines = [f"module t6_ascon5{PORTS};", "  wire [63:0] x0 = val ^ key;"]
    cur = "x0"
    for rnd in range(8):
        nxt = f"x{rnd+1}"
        # 21 triplets of chi: o0=b0^(~b1&b2), o1=b1^(~b2&b0), o2=b2^(~b0&b1)
        chibits = []
        for t in range(21):
            b = 3 * t
            chibits.append(f"({cur}[{b}] ^ (~{cur}[{b+1}] & {cur}[{b+2}]))")  # o0
            chibits.append(f"({cur}[{b+1}] ^ (~{cur}[{b+2}] & {cur}[{b}]))")  # o1
            chibits.append(f"({cur}[{b+2}] ^ (~{cur}[{b}] & {cur}[{b+1}]))")  # o2
        # bit 63 passthrough; concat {b63, o62..o0}
        concat = "{" + f"{cur}[63], " + ", ".join(reversed(chibits)) + "}"
        lines.append(f"  wire [63:0] {nxt}_s = {concat};")
        # linear: y ^= rotl(y,19) ^ rotl(y,37)
        lines.append(f"  wire [63:0] {nxt}_l1 = {{{nxt}_s[44:0], {nxt}_s[63:45]}};")  # rotl19
        lines.append(f"  wire [63:0] {nxt}_l2 = {{{nxt}_s[26:0], {nxt}_s[63:27]}};")  # rotl37
        lines.append(f"  wire [63:0] {nxt} = {nxt}_s ^ {nxt}_l1 ^ {nxt}_l2 ^ 64'h{RC[rnd%6]:016x};")
        cur = nxt
    lines.append(f"  assign out = {cur};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_gimli():
    lines = [f"module t6_gimli{PORTS};",
             "  wire [31:0] a0 = val[31:0] ^ key[31:0];",
             "  wire [31:0] b0 = val[63:32] ^ key[63:32];"]
    for rnd in range(6):
        a = f"a{rnd}"; b = f"b{rnd}"; na = f"a{rnd+1}"; nb = f"b{rnd+1}"
        # c = rotl(a,16)
        lines.append(f"  wire [31:0] c{rnd} = {{{a}[15:0], {a}[31:16]}};")
        # SP-box
        lines.append(f"  wire [31:0] {na}_t1 = {a} ^ (c{rnd} << 1) ^ (( {b} & c{rnd}) << 2);")
        # careful: <<2 on 32-bit drops top bits; model does & 0xFFFFFFFF after
        # Verilog << on 32-bit wire keeps 32 bits (drops overflow). Matches.
        lines.append(f"  wire [31:0] {nb}_t1 = {b} ^ {a} ^ (({a} & c{rnd}) << 1);")
        # round constant on a
        rc = (RC[rnd] & 0xFFFFFFFF) ^ ((rnd * 0x9E3779B9) & 0xFFFFFFFF)
        if rnd % 2 == 1:
            # model: a,b = na,nb; then a,b = b,a; then a ^= rc
            # => final a = nb^rc, b = na
            lines.append(f"  wire [31:0] {na} = {nb}_t1 ^ 32'h{rc:08x};")
            lines.append(f"  wire [31:0] {nb} = {na}_t1;")
        else:
            lines.append(f"  wire [31:0] {na} = {na}_t1 ^ 32'h{rc:08x};")
            lines.append(f"  wire [31:0] {nb} = {nb}_t1;")
    lines.append("  assign out = {b6, a6};")
    lines.append("endmodule")
    return "\n".join(lines)


GEN_B3 = {
    "t6_ca30": gen_ca30,
    "t6_ca_mix": gen_ca_mix,
    "t6_ascon5": gen_ascon5,
    "t6_gimli": gen_gimli,
}


def main():
    for name, gen in GEN_B3.items():
        fn, desc = CANDIDATES_B3[name]
        _nm = fn.__name__
        assert _nm.isidentifier(), (f"GEN BUG: {name} scalar fn __name__={_nm!r} not a valid identifier; "
                                            f"gen emits `return {{_nm}}(v,k)` which would be a SyntaxError (lambda?)")
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(T6, "t6_models_b3.py")) as f:
            src = f.read()
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(src + f"""
def _mix_scalar(v, k):
    return {fn.__name__}(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B3['{name}'](v, k)

def mix_np(V, K):
    return MIX_NP_B3['{name}'](V, K)
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
