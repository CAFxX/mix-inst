#!/usr/bin/env python3
"""Wave-30 axis A: stage-order permutation of the fz24_o body (structural, not
schedule). All waves so far used [t3,t3,AND,AND,CHI] or [t3,AND,AND,AND,CHI];
stage-KIND order itself has never been varied. The chi final keeps the
fz24_o winning schedule (31,19,35,53); the body rotations are carried over.

  fz30_a: [t3#1, AND#1, t3#2, AND#2, CHI]  (interleaved)
  fz30_b: [t3#1, AND#1, AND#2, t3#2, CHI]  (t3 delayed to stage 4)

t3#1=(1,7,13,29) t3#2=(3,11,19,37) and#1=(5,15,21) and#2=(9,23,43)
"""
import json, os, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from gen_fused24 import gen_model, gen_c, gen_rtl
EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery", "candidates")
T1 = ("t3", (1, 7, 13, 29))
T2 = ("t3", (3, 11, 19, 37))
A1 = ("and", (5, 15, 21))
A2 = ("and", (9, 23, 43))
CHI = ("chi", (31, 19, 35, 53))
SPECS30 = [
    ("fz30_a", [T1, A1, T2, A2, CHI],
     "5-stage [t3,AND,t3,AND,CHI]: interleaved body, fz24_o rotations+chi"),
    ("fz30_b", [T1, A1, A2, T2, CHI],
     "5-stage [t3,AND,AND,t3,CHI]: t3 delayed to stage 4, fz24_o rotations+chi"),
]
def main():
    for name, stages, desc in SPECS30:
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
