#!/usr/bin/env python3
"""Generate Verilog RTL for Track 6 candidates, bit-exact with t6_models.py.
Also creates impl.c (bit-exact C) and meta.json, then runs S0 via run_synth.py.
"""
import os, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t6_models import CANDIDATES

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
EXP = "/home/hatch/workspace/mix/exploration"
T6 = os.path.dirname(os.path.abspath(__file__))

RC_HEX = ["64'h9E3779B97F4A7C15", "64'h3C6EF372FE94F82A",
          "64'hDAA66D2C7DDF743F", "64'h78DDE6E5FD29F054",
          "64'h2545F4914F6CDD1D", "64'h9E3779B97F4A7C15"]


def rotl(w, x, r):
    r %= w
    if r == 0:
        return x
    return f"{{{x}[{w-1-r}:0], {x}[{w-1}:{w-r}]}}"


# Port convention for check_rtl: (val, key, out)
PORTS = "(input [63:0] val, input [63:0] key, output [63:0] out)"


def gen_narrow_arx():
    lines = [f"module t6_narrow_arx{PORTS};",
             "  wire [15:0] L0_0 = val[15:0],  L1_0 = val[31:16],  L2_0 = val[47:32],  L3_0 = val[63:48];",
             "  wire [15:0] K0 = key[15:0], K1 = key[31:16], K2 = key[47:32], K3 = key[63:48];"]
    for rnd in range(4):
        s = rnd
        lines.append(f"  // round {rnd}")
        for i, (Ln, Kn) in enumerate([("L0", "K0"), ("L1", "K1"), ("L2", "K2"), ("L3", "K3")]):
            rcval = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054][rnd]
            lane_c = (rcval >> (16 * i)) & 0xFFFF
            kr_rot = rotl(16, Kn, 3 + rnd)
            prev = f"{Ln}_{s}"
            # intermediate sum wire (can't bit-select an expression)
            sumw = f"{Ln}_{s+1}_sum"
            lines.append(f"  wire [15:0] {sumw} = {prev} + {kr_rot} + 16'h{lane_c:04x};")
            lines.append(f"  wire [15:0] {Ln}_{s+1}_arx = {rotl(16, sumw, 7)};")
        lines.append(f"  wire [15:0] L0_{s+1} = L0_{s+1}_arx ^ {rotl(16, f'L1_{s+1}_arx', 5)};")
        lines.append(f"  wire [15:0] L2_{s+1} = L2_{s+1}_arx ^ {rotl(16, f'L3_{s+1}_arx', 11)};")
        lines.append(f"  wire [15:0] L1_{s+1} = L1_{s+1}_arx ^ {rotl(16, f'L2_{s+1}', 3)};")
        lines.append(f"  wire [15:0] L3_{s+1} = L3_{s+1}_arx ^ {rotl(16, f'L0_{s+1}', 9)};")
    lines.append("  assign out = {L3_4, L2_4, L1_4, L0_4};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_trivium64():
    # 64-bit shift register, 6 macro-rounds x 8 clocks, unrolled combinationally.
    lines = [f"module t6_trivium64{PORTS};",
             "  wire [63:0] st0 = val ^ key;"]
    n = 0
    cur = "st0"
    RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F,
          0x78DDE6E5FD29F054, 0x2545F4914F6CDD1D, 0x9E3779B97F4A7C15 ^ 0xDEADBEEF]
    for rnd in range(6):
        for c in range(8):
            n += 1
            nxt = f"st{n}"
            lines.append(f"  wire fb{n} = {cur}[8] ^ ({cur}[8] & {cur}[13]) ^ {cur}[29] ^ {cur}[47];")
            lines.append(f"  wire [63:0] {nxt} = {{{cur}[62:0], fb{n}}};")
            cur = nxt
        n += 1
        nxt = f"st{n}"
        lines.append(f"  wire [63:0] {nxt} = {cur} ^ 64'h{RC[rnd]:016x};")
        cur = nxt
    # post-whiten: model does s ^ (k >> 32); zero-extend to 64 bits
    lines.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_feistel_arx():
    lines = [f"module t6_feistel_arx{PORTS};",
             "  wire [31:0] L0 = val[31:0];",
             "  wire [31:0] R0 = val[63:32];"]
    RC32 = [0x7F4A7C15, 0xFE94F82A, 0x7DDF743F, 0xFD29F054, 0x4F6CDD1D, 0xA1E7C2FA]
    for i in range(8):
        off = 8 * (i % 8)
        # model: (kk >> off) & 0xFFFFFFFF — zero-padded, not wrapped
        if off + 32 <= 64:
            kslice = f"key[{off+31}:{off}]"
        else:
            valid = 64 - off
            kslice = f"{{{32-valid}'h0, key[63:{off}]}}"
        lines.append(f"  wire [31:0] rk{i}_b = ({kslice} ^ 32'h{RC32[i % 6]:08x});")
        rk = rotl(32, f"rk{i}_b", 3 * i)
        lines.append(f"  wire [31:0] rk{i} = {rk};")
        # F(R, rk) with intermediate wires (no bit-select on expressions)
        lines.append(f"  wire [31:0] Fy{i}_1 = R{i} + rk{i};")
        lines.append(f"  wire [31:0] Fy{i}_2 = {rotl(32, f'Fy{i}_1', 7)};")
        lines.append(f"  wire [31:0] Fy{i}_3 = Fy{i}_2 ^ (Fy{i}_2 >> 11);")
        lines.append(f"  wire [31:0] Fy{i}_4 = Fy{i}_3 + {rotl(32, f'rk{i}', 13)};")
        lines.append(f"  wire [31:0] F{i} = {rotl(32, f'Fy{i}_4', 5)};")
        lines.append(f"  wire [31:0] L{i+1} = R{i};")
        lines.append(f"  wire [31:0] R{i+1} = L{i} ^ F{i};")
    lines.append("  assign out = {R8, L8};")
    lines.append("endmodule")
    return "\n".join(lines)


def gen_laidassey():
    lines = [f"module t6_laidassey{PORTS};",
             "  wire [31:0] L0 = val[31:0];",
             "  wire [31:0] R0 = val[63:32];"]
    RC32 = [0x7F4A7C15, 0xFE94F82A, 0x7DDF743F, 0xFD29F054, 0x4F6CDD1D, 0xA1E7C2FA]

    def H(d_expr, rk_expr, tag):
        lines.append(f"  wire [31:0] H{tag}_1 = {d_expr} + {rk_expr};")
        lines.append(f"  wire [31:0] H{tag}_2 = {rotl(32, f'H{tag}_1', 9)};")
        lines.append(f"  wire [31:0] H{tag}_3 = H{tag}_2 ^ (H{tag}_2 >> 7);")
        lines.append(f"  wire [31:0] H{tag} = H{tag}_3 + {rotl(32, f'H{tag}_3', 4)};")
        return f"H{tag}"

    for i in range(6):
        lines.append(f"  wire [31:0] rk{i}_b = (key[31:0] ^ 32'h{RC32[i]:08x});")
        lines.append(f"  wire [31:0] rk{i} = {rotl(32, f'rk{i}_b', 5 * i)};")
        d = H(f"(L{i} ^ R{i})", f"rk{i}", f"{i}")
        lines.append(f"  wire [31:0] Lp{i} = L{i} ^ {d};")
        lines.append(f"  wire [31:0] Rp{i} = R{i} ^ {d};")
        if i < 5:
            lines.append(f"  wire [31:0] L{i+1} = Rp{i};")
            lines.append(f"  wire [31:0] R{i+1} = Lp{i};")
        else:
            lines.append(f"  wire [31:0] L{i+1} = Lp{i};")
            lines.append(f"  wire [31:0] R{i+1} = Rp{i};")
    lines.append("  wire [31:0] key_hi = key[63:32];")
    lines.append(f"  wire [31:0] rkf = {rotl(32, 'key_hi', 11)};")
    df = H("(L6 ^ R6)", "rkf", "f")
    lines.append("  wire [31:0] Lf = L6 ^ Hf;")
    lines.append("  wire [31:0] Rf = R6 ^ Hf;")
    lines.append("  assign out = {Rf, Lf};")
    lines.append("endmodule")
    return "\n".join(lines)


GEN = {
    "t6_narrow_arx": gen_narrow_arx,
    "t6_trivium64": gen_trivium64,
    "t6_feistel_arx": gen_feistel_arx,
    "t6_laidassey": gen_laidassey,
}

# Minimal impl.c template (bit-exact C, for S2/S3 later)
C_TEMPLATE = """\
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
uint64_t mix(uint64_t v, uint64_t k);
int main(int argc, char** argv) {
    // placeholder: real impl generated per-candidate if it survives S0
    return 0;
}
uint64_t mix(uint64_t v, uint64_t k) { (void)v; (void)k; return 0; }
"""


def main():
    import importlib.util
    for name, gen in GEN.items():
        fn, desc = CANDIDATES[name]
        _nm = fn.__name__
        assert _nm.isidentifier(), (f"GEN BUG: {name} scalar fn __name__={_nm!r} not a valid identifier; "
                                            f"gen emits `return {{_nm}}(v,k)` which would be a SyntaxError (lambda?)")
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        # model.py (copy full source + mix/mix_np entry points)
        with open(os.path.join(T6, "t6_models.py")) as f:
            src = f.read()
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(src + f"""
def _mix_scalar(v, k):
    return {fn.__name__}(v, k)

def mix(v, k):
    # dispatch: scalar -> scalar fn, array -> vectorized
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP['{name}'](v, k)

def mix_np(V, K):
    return MIX_NP['{name}'](V, K)
""")
        # rtl.v
        with open(os.path.join(cdir, "rtl.v"), "w") as f:
            f.write(gen() + "\n")
        # impl.c stub
        with open(os.path.join(cdir, "impl.c"), "w") as f:
            f.write(C_TEMPLATE)
        # meta.json with goldens
        import json
        g1 = fn(0x0, 0x123456789ABCDEF0)
        g2 = fn(0x123456789ABCDEF0, 0x0)
        meta = {
            "name": name, "description": desc,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": [
                {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(g1)},
                {"val": "0x123456789abcdef0", "key": "0x0", "out": hex(g2)},
            ],
        }
        with open(os.path.join(cdir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print(f"created {name}: {desc}")


if __name__ == "__main__":
    main()
