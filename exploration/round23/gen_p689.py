"""Generate fast_battery candidates for the 7 new P6/P8/P9 specs."""
import json
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R23 = os.path.join(EXP, "round23")
FB = os.path.join(EXP, "fast_battery", "candidates")
sys.path.insert(0, R23)
sys.path.insert(0, os.path.join(R23, "models"))

import numpy as np  # noqa: E402
import r23  # noqa: E402
import gen_r23  # noqa: E402

specs = json.load(open(os.path.join(R23, "specs_p689.json")))
# normalize rots to tuple for the generator
for s in specs:
    s["rots"] = tuple(s["rots"])

gen_r23._selftest_all(specs)

for s in specs:
    name = s["name"]
    d = os.path.join(FB, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "impl.c"), "w") as f:
        f.write(gen_r23.build_c(s))
    with open(os.path.join(d, "rtl.v"), "w") as f:
        f.write(gen_r23.build_verilog(s))
    with open(os.path.join(d, "model.py"), "w") as f:
        f.write(gen_r23.build_model_py(s))
    fn = getattr(r23, name)
    goldens = []
    for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
        goldens.append({"val": hex(v), "key": hex(k),
                        "out": hex(int(fn(np.uint64(v), np.uint64(k))))})
    meta = {"name": name, "description": s["desc"], "composition": s["desc"],
            "rtl_top": name,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens}
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("generated", name)
print("gen_p689 complete")
