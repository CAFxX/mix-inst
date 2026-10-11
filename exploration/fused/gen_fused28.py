#!/usr/bin/env python3
"""Wave-28: new chi-final schedule hits from the REAL 24c re-run (seeds C41/BEEF, 60 tries, logN=16 proxy, z<12 bar).
Prefix [t3(1,7,13,29), t3(3,11,19,37), and(5,15,21), and(9,23,43)] (same as fz24_o).
"""
import json, os, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from gen_fused24 import gen_model, gen_c, gen_rtl
EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")
PREFIX = [("t3", (1, 7, 13, 29)), ("t3", (3, 11, 19, 37)),
          ("and", (5, 15, 21)), ("and", (9, 23, 43))]
SPECS28 = [
    ("fz28_a", PREFIX + [("chi", (52, 6, 59, 13))],
     "5-stage [t3,t3,AND,AND,CHI(52,6,59,13)]: 24c re-run hit z=8.7@16 (seed BEEF, try 24)"),
    ("fz28_b", PREFIX + [("chi", (6, 11, 19, 42))],
     "5-stage [t3,t3,AND,AND,CHI(6,11,19,42)]: 24c re-run hit z=10.9@16 (seed C41, try 6)"),
    ("fz28_c", PREFIX + [("chi", (48, 8, 24, 52))],
     "5-stage [t3,t3,AND,AND,CHI(48,8,24,52)]: 24c re-run BEST z=6.3@16 (seed C41, try 36)"),
    ("fz28_d", PREFIX + [("chi", (44, 5, 26, 58))],
     "5-stage [t3,t3,AND,AND,CHI(44,5,26,58)]: 24c re-run hit z=9.2@16 (seed C41, try 60)"),
]
def main():
    for name, stages, desc in SPECS28:
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(gen_model(name, stages, desc))
        open(os.path.join(d, "impl.c"), "w").write(gen_c(name, stages))
        open(os.path.join(d, "rtl.v"), "w").write(gen_rtl(name, stages))
        open(os.path.join(d, "meta.json"), "w").write(
            json.dumps({"name": name, "description": desc, "rtl_top": name,
                        "screen_keys": ["0x123456789abcdef0", "0x0"],
                        "practrand_keys": ["0x123456789abcdef0", "0x0"]}, indent=2))
        print(f"generated {name}", flush=True)
if __name__ == "__main__":
    main()

# fz28_c appended: real 24c re-run (seed C41, 60 tries) best hit z=6.3@16
