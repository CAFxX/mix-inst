#!/usr/bin/env python3
"""Generate fast_battery candidates for round25 specs25.json (Track A' + B)."""
import json
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
sys.path.insert(0, R25)
sys.path.insert(0, os.path.join(R25, "models"))
import gen_r25  # noqa: E402

FB = os.path.join(EXP, "fast_battery", "candidates")


def main():
    specs = json.load(open(os.path.join(R25, "specs25.json")))
    for s in specs:
        # normalize rots to tuple for the model
        s["rots"] = tuple(s["rots"])
        name = s["name"]
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "impl.c"), "w") as f:
            f.write(gen_r25.build_c(s))
        with open(os.path.join(d, "rtl.v"), "w") as f:
            f.write(gen_r25.build_verilog(s))
        with open(os.path.join(d, "model.py"), "w") as f:
            f.write(gen_r25.build_model_py(s))
        meta = {
            "name": name,
            "description": s["desc"],
            "composition": s["desc"],
            "rtl_top": name,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": [],
        }
        with open(os.path.join(d, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print(f"generated {name}")


if __name__ == "__main__":
    main()
