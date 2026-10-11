#!/usr/bin/env python3
"""Stage GHA bundles for the and6 schedule-search winners (2026-10-10).

Copies impl.c/model.py/rtl.v from fast_battery/candidates/ into the local
fanout mirror and writes the full campaign meta.json (goldens from model,
screen/practrand keys) per the wave-10 bundle format.
"""
import importlib.util
import json
import os
import shutil
import sys

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
DST = "/home/hatch/workspace/fanout/projects/mix-sbox-search/battery/candidates"

CANDS = [
    # (name, S0, proxy z)
    ("as6_200_15", 19.2, 5.1),
    ("as6_200_68", 19.2, 7.6),
    ("as6_200_38", 19.2, 7.8),
    ("as6_200_106", 19.8, 5.4),
    ("as6_200_67", 19.8, 8.1),
    ("as6_200_80", 19.8, 8.2),
    ("as6_200_118", 19.5, 7.1),
]


def main():
    staged = []
    for name, s0, z in CANDS:
        src = os.path.join(FB, name)
        dst = os.path.join(DST, name)
        os.makedirs(dst, exist_ok=True)
        for fn in ("impl.c", "model.py", "rtl.v"):
            shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn))
        modname = f"bundle_{name}"
        if modname in sys.modules:
            del sys.modules[modname]
        spec = importlib.util.spec_from_file_location(
            modname, os.path.join(dst, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        g1 = m.mix(0x0, 0x123456789ABCDEF0)
        g2 = m.mix(0x123456789ABCDEF0, 0x0)
        # bit-exactness model-vs-impl.c was already asserted inside
        # gen_waveP.build() when the bundle was generated.
        meta = {
            "name": name,
            "description": (f"6-stage AND-rotation cascade, schedule-search winner "
                            f"(seed 200): S0={s0}u, v3 proxy z={z}"),
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "rtl_top": name,
            "goldens": [
                {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(g1)},
                {"val": "0x123456789ABCDEF0", "key": "0x0", "out": hex(g2)},
            ],
        }
        with open(os.path.join(dst, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        staged.append(f"projects/mix-sbox-search/battery/candidates/{name}/impl.c")
        staged.append(f"projects/mix-sbox-search/battery/candidates/{name}/model.py")
        staged.append(f"projects/mix-sbox-search/battery/candidates/{name}/rtl.v")
        staged.append(f"projects/mix-sbox-search/battery/candidates/{name}/meta.json")
        print(f"staged {name}: S0={s0}u z={z} goldens={hex(g1)[:10]}..", flush=True)
    print(f"\n{len(staged)} files staged")
    with open("/tmp/and6sched_staged.txt", "w") as f:
        f.write("\n".join(staged))


if __name__ == "__main__":
    main()
