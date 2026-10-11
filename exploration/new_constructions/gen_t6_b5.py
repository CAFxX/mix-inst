#!/usr/bin/env python3
"""Generate Verilog RTL for Track 6 batch 5, bit-exact with t6_models_b5.py."""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t6_models_b5 import CANDIDATES_B5

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
T6 = os.path.dirname(os.path.abspath(__file__))

PORTS = "(input [63:0] val, input [63:0] key, output [63:0] out)"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d", "64'h9e3779b9a1e7c2fa",
          "64'h3c6ef372eca0ae52", "64'hdaa66d2cd6129b3e"]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"


def gen_cascade(op, sched):
    def gen():
        L = [f"module PLACEHOLDER{PORTS};",
             f"  wire [63:0] st0 = val ^ key;"]
        cur = "st0"
        for i, rots in enumerate(sched):
            r = [rotl(cur, t) for t in rots]
            if op == "maj":
                # x ^= maj(ra,rb,rc) ^ rd ; maj = (a&b)|(a&c)|(b&c)
                maj = f"(({r[0]} & {r[1]}) | ({r[0]} & {r[2]}) | ({r[1]} & {r[2]}))"
                nl = f"({maj} ^ {r[3]})"
            elif op == "andor":
                nl = f"((({r[0]} & {r[1]}) | ({r[2]} & {r[3]})) ^ {r[4]})"
            elif op == "majxor":
                maj = f"(({r[0]} & {r[1]}) | ({r[0]} & {r[2]}) | ({r[1]} & {r[2]}))"
                nl = f"({maj} ^ ({r[3]} & {r[4]}))"
            elif op == "xor3and":
                nl = f"({r[0]} ^ {r[1]} ^ {r[2]} ^ ({r[3]} & {r[4]} & {r[5]}))"
            rk = f"({rotl('key', 13*(i+1))} ^ {RC_HEX[i % 8]})"
            L.append(f"  wire [63:0] st{i+1} = {cur} ^ {nl} ^ {rk};")
            cur = f"st{i+1}"
        L.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
        L.append("endmodule")
        return "\n".join(L)
    return gen


from t6_models_b5 import SCHED6, SCHED6_5, SCHED8, SCHED8_5, SCHED6_6, SCHED8_6

GEN_B5 = {
    "t6_maj6": gen_cascade("maj", SCHED6),
    "t6_maj8": gen_cascade("maj", SCHED8),
    "t6_andor6": gen_cascade("andor", SCHED6_5),
    "t6_andor8": gen_cascade("andor", SCHED8_5),
    "t6_majxor6": gen_cascade("majxor", SCHED6_5),
    "t6_majxor8": gen_cascade("majxor", SCHED8_5),
    "t6_xor3and6": gen_cascade("xor3and", SCHED6_6),
    "t6_xor3and8": gen_cascade("xor3and", SCHED8_6),
}


def main():
    for name, gen in GEN_B5.items():
        fn, desc = CANDIDATES_B5[name]
        _nm = fn.__name__
        assert _nm.isidentifier(), (f"GEN BUG: {name} scalar fn __name__={_nm!r} not a valid identifier; "
                                            f"gen emits `return {{_nm}}(v,k)` which would be a SyntaxError (lambda?)")
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(T6, "t6_models_b5.py")) as f:
            src = f.read()
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(src + f"""
def _mix_scalar(v, k):
    return {fn.__name__}(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B5['{name}'](v, k)

def mix_np(V, K):
    return MIX_NP_B5['{name}'](V, K)
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
