#!/usr/bin/env python3
"""Generate Verilog RTL for Track 6 batch 4, bit-exact with t6_models_b4.py.
Also creates model.py, impl.c stub, meta.json with goldens.
"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t6_models_b4 import CANDIDATES_B4, SBOX_RASC2_0, SBOX_MIDORI0

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
T6 = os.path.dirname(os.path.abspath(__file__))

PORTS = "(input [63:0] val, input [63:0] key, output [63:0] out)"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e",
          # cycle to match model RC64[rnd % 8]
          "64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054"]


def rotl(w, x, r):
    r %= w
    if r == 0:
        return x
    return f"{{{x}[{w-1-r}:0], {x}[{w-1}:{w-r}]}}"


def sbox4_lines(prefix, inp, sbox, n=16):
    """Emit 16 parallel 4-bit S-box lookups as case statements in an always block.
    Returns (decl_lines, always_block). Drives wires {prefix}_sb[63:0]."""
    decl = [f"  reg [63:0] {prefix}_sb_r;",
            f"  wire [63:0] {prefix}_sb = {prefix}_sb_r;"]
    body = [f"  always @(*) begin",
            f"    {prefix}_sb_r = 64'h0;"]
    for i in range(n):
        body.append(f"    case ({inp}[{4*i+3}:{4*i}])")
        for v in range(16):
            body.append(f"      4'h{v:x}: {prefix}_sb_r[{4*i+3}:{4*i}] = 4'h{int(sbox[v]):x};")
        body.append(f"    endcase")
    body.append(f"  end")
    return decl + body


def theta_lines(prefix, inp):
    """Keccak-theta-style parity diffusion. Drives wire {prefix}_th[63:0]."""
    L = [f"  // theta parity diffusion on 8x8 bit matrix"]
    # row parities: XOR of 8 bits each
    for i in range(8):
        terms = " ^ ".join(f"{inp}[{8*i+j}]" for j in range(8))
        L.append(f"  wire {prefix}_par{i} = {terms};")
    L.append(f"  wire [63:0] {prefix}_th;")
    for i in range(8):
        d = f"({prefix}_par{(i+1)%8} ^ {prefix}_par{(i+2)%8})"
        for j in range(8):
            L.append(f"  assign {prefix}_th[{8*i+j}] = {inp}[{8*i+j}] ^ {d};")
    return L


def midori_mc_lines(prefix, inp):
    """Midori MixColumn on 4x4 nibble matrix. Drives wire {prefix}_mc[63:0]."""
    L = [f"  // Midori MixColumn"]
    L.append(f"  wire [63:0] {prefix}_mc;")
    for c in range(4):
        n0, n1, n2, n3 = (f"{inp}[{4*(c+4*k)+3}:{4*(c+4*k)}]" for k in range(4))
        L.append(f"  assign {prefix}_mc[{4*c+3}:{4*c}] = {n1} ^ {n2} ^ {n3};")
        L.append(f"  assign {prefix}_mc[{4*(c+4)+3}:{4*(c+4)}] = {n0} ^ {n2} ^ {n3};")
        L.append(f"  assign {prefix}_mc[{4*(c+8)+3}:{4*(c+8)}] = {n0} ^ {n1} ^ {n3};")
        L.append(f"  assign {prefix}_mc[{4*(c+12)+3}:{4*(c+12)}] = {n0} ^ {n1} ^ {n2};")
    return L


def midori_shuffle_lines(prefix, inp):
    perm = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]
    L = [f"  // Midori ShuffleCell"]
    terms = ", ".join(f"{inp}[{4*perm[i]+3}:{4*perm[i]}]" for i in range(15, -1, -1))
    L.append(f"  wire [63:0] {prefix}_sh = {{{terms}}};")
    return L


def chi3col_lines(prefix, inp):
    """3-bit column chi on groups (i, i+21, i+42). Drives wire {prefix}_chi[63:0]."""
    L = [f"  // 3-bit column chi"]
    L.append(f"  wire [63:0] {prefix}_chi;")
    for i in range(21):
        b0, b1, b2 = f"{inp}[{i}]", f"{inp}[{i+21}]", f"{inp}[{i+42}]"
        L.append(f"  assign {prefix}_chi[{i}] = {b0} ^ (~{b1} & {b2});")
        L.append(f"  assign {prefix}_chi[{i+21}] = {b1} ^ (~{b2} & {b0});")
        L.append(f"  assign {prefix}_chi[{i+42}] = {b2} ^ (~{b0} & {b1});")
    L.append(f"  assign {prefix}_chi[63] = {inp}[63];")
    return L


def gen_theta(nrounds):
    def gen():
        L = [f"module PLACEHOLDER{PORTS};",
             f"  wire [63:0] st0 = val ^ key;"]
        cur = "st0"
        for rnd in range(nrounds):
            p = f"r{rnd}"
            L += sbox4_lines(p + "_a", cur, SBOX_RASC2_0)
            L += theta_lines(p + "_b", p + "_a_sb")
            rk = rotl(64, "key", 13 * (rnd + 1))
            L.append(f"  wire [63:0] st{rnd+1} = {p}_b_th ^ {RC_HEX[rnd]} ^ {rk};")
            cur = f"st{rnd+1}"
        L.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
        L.append("endmodule")
        return "\n".join(L)
    return gen


def gen_midori(nrounds):
    def gen():
        L = [f"module PLACEHOLDER{PORTS};",
             f"  wire [63:0] st0 = val ^ key;"]
        cur = "st0"
        for rnd in range(nrounds):
            p = f"r{rnd}"
            L += sbox4_lines(p + "_a", cur, SBOX_MIDORI0)
            L += midori_shuffle_lines(p + "_b", p + "_a_sb")
            L += midori_mc_lines(p + "_c", p + "_b_sh")
            rk = rotl(64, "key", 13 * (rnd + 1))
            L.append(f"  wire [63:0] st{rnd+1} = {p}_c_mc ^ {RC_HEX[rnd]} ^ {rk};")
            cur = f"st{rnd+1}"
        L.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
        L.append("endmodule")
        return "\n".join(L)
    return gen


def gen_chi3col(nrounds):
    def gen():
        L = [f"module PLACEHOLDER{PORTS};",
             f"  wire [63:0] st0 = val ^ key;"]
        cur = "st0"
        for rnd in range(nrounds):
            p = f"r{rnd}"
            L += chi3col_lines(p + "_a", cur)
            # rotations: s = rotl(chi,7) ^ rotl(chi,29)
            r7 = rotl(64, p + "_a_chi", 7)
            r29 = rotl(64, p + "_a_chi", 29)
            rk = rotl(64, "key", 13 * (rnd + 1))
            L.append(f"  wire [63:0] st{rnd+1} = ({r7} ^ {r29}) ^ {RC_HEX[rnd]} ^ {rk};")
            cur = f"st{rnd+1}"
        L.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
        L.append("endmodule")
        return "\n".join(L)
    return gen


GEN_B4 = {
    "t6_theta5": gen_theta(5),
    "t6_theta6": gen_theta(6),
    "t6_theta7": gen_theta(7),
    "t6_midori6": gen_midori(6),
    "t6_midori7": gen_midori(7),
    "t6_midori8": gen_midori(8),
    "t6_chi3col8": gen_chi3col(8),
    "t6_chi3col10": gen_chi3col(10),
}


def main():
    for name, gen in GEN_B4.items():
        fn, desc = CANDIDATES_B4[name]
        _nm = fn.__name__
        assert _nm.isidentifier(), (f"GEN BUG: {name} scalar fn __name__={_nm!r} not a valid identifier; "
                                            f"gen emits `return {{_nm}}(v,k)` which would be a SyntaxError (lambda?)")
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(T6, "t6_models_b4.py")) as f:
            src = f.read()
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(src + f"""
def _mix_scalar(v, k):
    return {fn.__name__}(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B4['{name}'](v, k)

def mix_np(V, K):
    return MIX_NP_B4['{name}'](V, K)
""")
        rtl = gen().replace("PLACEHOLDER", name)
        with open(os.path.join(cdir, "rtl.v"), "w") as f:
            f.write(rtl + "\n")
        with open(os.path.join(cdir, "impl.c"), "w") as f:
            f.write("/* stub */\n")
        g1 = fn(0x0, 0x123456789ABCDEF0)
        g2 = fn(0x123456789ABCDEF0, 0x0)
        meta = {"name": name, "description": desc,
                "screen_keys": ["0x123456789abcdef0", "0x0"],
                "practrand_keys": ["0x123456789abcdef0", "0x0"],
                "goldens": [
                    {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(int(g1))},
                    {"val": "0x123456789abcdef0", "key": "0x0", "out": hex(int(g2))}]}
        with open(os.path.join(cdir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print(f"created {name}: {desc}")


if __name__ == "__main__":
    main()
