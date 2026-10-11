#!/usr/bin/env python3
"""Wave-30 axis B5: build the top-3 v3-repair proxy hits (unbuilt at reboot).

From wave30_repair3.log (seed 0xB34, 250 tries, killed ~TRY166):
  TRY122 marg=+4.7 DIFFz=24.0  -> fz30_n
  TRY158 marg=+3.8 DIFFz=24.0  -> fz30_p
  TRY 93 marg=+3.6 DIFFz=16.8  -> fz30_q
All: [t3,t3,and,and,chi(29,17,33,51)] template. S0 target: beat fz30_m 19.8u.
"""
import json, os, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from gen_fused24 import gen_model, gen_c, gen_rtl
EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")
CHI = ("chi", (29, 17, 33, 51))
SPECS30C = [
    ("fz30_n", [("t3", (1, 7, 13, 29)), ("t3", (1, 12, 19, 39)),
                ("and", (5, 17, 19)), ("and", (10, 23, 45)), CHI],
     "v3 repair TRY122: marg+4.7 DIFFz24.0"),
    ("fz30_p", [("t3", (2, 8, 12, 30)), ("t3", (2, 13, 19, 38)),
                ("and", (7, 14, 23)), ("and", (10, 21, 41)), CHI],
     "v3 repair TRY158: marg+3.8 DIFFz24.0"),
    ("fz30_q", [("t3", (3, 9, 11, 30)), ("t3", (1, 13, 21, 38)),
                ("and", (6, 17, 20)), ("and", (8, 22, 44)), CHI],
     "v3 repair TRY93: marg+3.6 DIFFz16.8"),
]
def main():
    for name, stages, desc in SPECS30C:
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
