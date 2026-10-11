#!/usr/bin/env python3
"""Generate Verilog RTL for Track 6 batch 7 (AND-OR fused), bit-exact with t6_models_b7.py."""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t6_models_b7 import CANDIDATES_B7, ROTS_A_5, ROTS_B_5, ROTS_A_4

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
T6 = os.path.dirname(os.path.abspath(__file__))

PORTS = "(input [63:0] val, input [63:0] key, output [63:0] out)"

RC_HEX = ["64'h9e3779b97f4a7c15", "64'h3c6ef372fe94f82a",
          "64'hdaa66d2c7ddf743f", "64'h78dde6e5fd29f054",
          "64'h2545f4914f6cdd1d"]

def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return f"{{{x}[{63-r}:0], {x}[63:{64-r}]}}"

# Map candidate names to their rotation sets
ROTS_MAP = {
    "t6_aor5a": (5, ROTS_A_5),
    "t6_aor5b": (5, ROTS_B_5),
    "t6_aor4a": (4, ROTS_A_4),
}

def gen_candidate(name, desc):
    nstages, rotations = ROTS_MAP[name]
    lines = [f"module {name}{PORTS};",
             f"  wire [63:0] st0 = val ^ key;"]
    cur = "st0"
    for i in range(nstages):
        rots = rotations[i]
        ra, rb, rc, rd, re, rf, rg, rh, ri = rots
        # Rotated wires
        vra = rotl(cur, ra)
        vrb = rotl(cur, rb)
        vrc = rotl(cur, rc)
        vrd = rotl(cur, rd)
        vre = rotl(cur, re)
        vrf = rotl(cur, rf)
        vrg = rotl(cur, rg)
        vrh = rotl(cur, rh)
        vri = rotl(cur, ri)
        # AND-OR fused: x = ((x&ra)|(rb&rc)) ^ ((rd&re)|(rf&rg)) ^ (rh&ri)
        t1 = f"(({cur} & {vra}) | ({vrb} & {vrc}))"
        t2 = f"(({vrd} & {vre}) | ({vrf} & {vrg}))"
        t3 = f"({vrh} & {vri})"
        rk = f"({rotl('key', 13*(i+1))} ^ {RC_HEX[i % len(RC_HEX)]})"
        nxt = f"st{i+1}"
        lines.append(f"  wire [63:0] {nxt} = {t1} ^ {t2} ^ {t3} ^ {rk};")
        cur = nxt
    lines.append(f"  assign out = {cur} ^ {{32'h0, key[63:32]}};")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"

def main():
    from t6_models_b7 import CANDIDATES_B7 as C7
    # Import here to get the functions for golden generation
    import t6_models_b7 as m7
    import numpy as np
    
    for name, (fn, desc) in C7.items():
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        # RTL
        with open(os.path.join(cdir, "rtl.v"), "w") as f:
            f.write(gen_candidate(name, desc))
        # model.py (import from t6_models_b7)
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(f'''"""Model for {name}, delegates to t6_models_b7."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions")
from t6_models_b7 import CANDIDATES_B7
import numpy as np
_fn, _desc = CANDIDATES_B7["{name}"]
def mix_model(val, key):
    return int(_fn(np.uint64(val), np.uint64(key)))
''')
        # impl.c stub (S1 uses Python model; S2/S3 need real C - TODO)
        with open(os.path.join(cdir, "impl.c"), "w") as f:
            f.write("/* stub - S1 uses Python model */\n")
        # meta.json with goldens
        g1 = fn(np.uint64(0x0), np.uint64(0x123456789ABCDEF0))
        g2 = fn(np.uint64(0x123456789ABCDEF0), np.uint64(0x0))
        meta = {"name": name, "description": desc,
                "screen_keys": ["0x123456789abcdef0", "0x0"],
                "practrand_keys": ["0x123456789abcdef0", "0x0"],
                "rtl_top": name,
                "goldens": [
                    {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(int(g1))},
                    {"val": "0x123456789abcdef0", "key": "0x0", "out": hex(int(g2))}]}
        with open(os.path.join(cdir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print(f"{name}: RTL + model + meta written to {cdir}")

if __name__ == "__main__":
    main()
