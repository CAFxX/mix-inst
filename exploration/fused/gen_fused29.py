#!/usr/bin/env python3
"""Wave-29: finer cost-shave of fz24_o — +-1 rotation nudges on individual
stages (wave-27's +-2 nudges broke S1's marginal single-bit; try finer).
Pipeline per variant: bit-exact 200/200 -> S0 (run_synth) -> S1 (exact GHA
code) on any variant <=20.1u -> S2 diffprof on any S1-pass.
"""
import json, os, sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from gen_fused24 import gen_model, gen_c, gen_rtl

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")

O = [("t3", (1, 7, 13, 29)),
     ("t3", (3, 11, 19, 37)),
     ("and", (5, 15, 21)),
     ("and", (9, 23, 43)),
     ("chi", (31, 19, 35, 53))]

def repl(stages, idx, new_rots):
    return [(k, new_rots) if i == idx else (k, r)
            for i, (k, r) in enumerate(stages)]

SPECS29 = [
    ("fz29_a", repl(O, 0, (1, 7, 13, 28)), "fz24_o t3#1 rot4 -1"),
    ("fz29_b", repl(O, 1, (3, 11, 19, 36)), "fz24_o t3#2 rot4 -1"),
    ("fz29_c", repl(O, 2, (5, 15, 20)), "fz24_o and#1 rot3 -1"),
    ("fz29_d", repl(O, 3, (9, 23, 42)), "fz24_o and#2 rot3 -1"),
    ("fz29_e", repl(O, 4, (31, 19, 35, 52)), "fz24_o chi rot4 -1"),
    ("fz29_f", repl(O, 4, (31, 19, 34, 53)), "fz24_o chi rot3 -1"),
    ("fz29_g", repl(O, 0, (1, 7, 14, 29)), "fz24_o t3#1 rot3 +1"),
    ("fz29_h", repl(O, 2, (5, 16, 21)), "fz24_o and#1 rot2 +1"),
]

def main():
    for name, stages, desc in SPECS29:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, desc))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages))
        open(os.path.join(d, "meta.json"), "w").write(
            json.dumps({"name": name, "description": desc, "rtl_top": name,
                        "screen_keys": ["0x123456789abcdef0", "0x0"],
                        "practrand_keys": ["0x123456789abcdef0", "0x0"]}, indent=2))
        print(f"generated {name}: {desc}", flush=True)

if __name__ == "__main__":
    main()
