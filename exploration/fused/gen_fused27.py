#!/usr/bin/env python3
"""Wave-27: S0 cost-shave variants of fz24_o (5-stage [t3,t3,AND,AND,CHI]).

Target: -0.2u vs fz24_o's 20.3u (frontier al_and6a 20.1u).
Levers: global rotate offsets, per-stage schedule nudges (+/-2, keeping
pairwise separation), chi schedule alternatives from the 24c search.
Every variant must re-pass S0 (run_synth) AND S2 diffprof before being
called a lead; an S2-breaking shave is a kill, not a lead.
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

def sh(x, d):
    return tuple((v + d) % 64 for v in x)

def repl(stages, idx, new_rots):
    out = []
    for i, (k, r) in enumerate(stages):
        out.append((k, new_rots) if i == idx else (k, r))
    return out

SPECS27 = [
    ("fz27_a",
     [(k, sh(r, 1)) for k, r in O],
     "fz24_o global rotate +1"),
    ("fz27_b",
     [(k, sh(r, -1)) for k, r in O],
     "fz24_o global rotate -1"),
    ("fz27_c",
     repl(O, 0, (2, 8, 14, 30)),
     "fz24_o t3#1 +1"),
    ("fz27_d",
     repl(O, 1, (5, 13, 21, 39)),
     "fz24_o t3#2 +2"),
    ("fz27_e",
     repl(O, 2, (7, 17, 23)),
     "fz24_o and#1 +2"),
    ("fz27_f",
     repl(O, 3, (11, 25, 45)),
     "fz24_o and#2 +2"),
    ("fz27_g",
     repl(O, 4, (33, 21, 37, 55)),
     "fz24_o chi +2"),
    ("fz27_h",
     repl(O, 4, (29, 17, 33, 51)),
     "fz24_o chi -2"),
    ("fz27_i",
     repl(O, 4, (27, 35, 7, 44)),
     "fz24_o chi <- fz24_p schedule (24c hit z=9.7@16)"),
    ("fz27_j",
     repl(O, 4, (53, 31, 19, 35)),
     "fz24_o chi params permuted (53,31,19,35)"),
]

def main():
    for name, stages, desc in SPECS27:
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
