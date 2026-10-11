#!/usr/bin/env python3
"""Generate broad S-box screening candidate bundles.

For each S-box in sbox_screen_broad/ranked.json, generates a full
pba19 + lin(5,13) candidate bundle (impl.c, model.py, rtl.v, meta.json)
using gen_r25's build functions.

Usage: python3 gen_broad_sbox.py [--submit]
  --submit: submit the GHA campaign after generating
"""
import json
import os
import subprocess
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
sys.path.insert(0, R25)
sys.path.insert(0, os.path.join(R25, "models"))

import numpy as np  # noqa: E402
import gen_r25  # noqa: E402
import r25  # noqa: E402

RANKED = os.path.join(R25, "sbox_screen_broad", "ranked.json")
# Write to the fanout battery candidates dir directly
CAND_DIR = os.path.expanduser(
    "~/workspace/fanout/projects/mix-sbox-search/battery/candidates")

# P-box for pba19: P(i) = (19*i+1) % 64, as a list where pbox[i] = dest of bit i
PBOX_19_1 = [(19 * i + 1) % 64 for i in range(64)]


def sbox_hex_to_list(h):
    return [int(c, 16) for c in h.strip()]


def main():
    submit = "--submit" in sys.argv

    ranked = json.load(open(RANKED))
    boxes = [(b["name"], b["table"]) for b in ranked["all"] if "table" in b]
    print(f"Found {len(boxes)} S-boxes with tables", flush=True)

    specs = []
    for name, table_hex in boxes:
        sbox = sbox_hex_to_list(table_hex)
        assert sorted(sbox) == list(range(16)), f"{name}: not a permutation"
        cand_name = f"r25_spn_pba19_sb_{name}_513_nw"
        spec = {
            "name": cand_name,
            "desc": (f"Broad S-box screen: 4r SPN, {name} "
                     f"({table_hex}), pba19, L=lin(5,13), golden ks."),
            "nrounds": 4,
            "sbox": sbox,
            "pbox": PBOX_19_1,
            "rots": [5, 13],
            "include_id": True,
            "ks": "golden",
            "order": "LPS",
            "rank": 64,
        }
        specs.append(spec)

    # Install specs into r25 model for golden generation
    r25._install_specs(specs)

    generated = []
    for spec in specs:
        name = spec["name"]
        d = os.path.join(CAND_DIR, name)
        os.makedirs(d, exist_ok=True)
        print(f"Generating {name}...", flush=True)
        try:
            with open(os.path.join(d, "impl.c"), "w") as f:
                f.write(gen_r25.build_c(spec))
            with open(os.path.join(d, "rtl.v"), "w") as f:
                f.write(gen_r25.build_verilog(spec))
            with open(os.path.join(d, "model.py"), "w") as f:
                f.write(gen_r25.build_model_py(spec))
            fn = getattr(r25, name)
            goldens = []
            for v, k in [(0x0, 0x123456789ABCDEF0),
                         (0x123456789ABCDEF0, 0x0)]:
                goldens.append({
                    "val": hex(v), "key": hex(k),
                    "out": hex(int(fn(np.uint64(v), np.uint64(k))))})
            meta = {
                "name": name,
                "description": spec["desc"],
                "composition": spec["desc"],
                "rtl_top": name,
                "screen_keys": ["0x123456789abcdef0", "0x0"],
                "practrand_keys": ["0x123456789abcdef0", "0x0"],
                "goldens": goldens,
            }
            with open(os.path.join(d, "meta.json"), "w") as f:
                json.dump(meta, f, indent=1)
            generated.append(name)
            print(f"  OK", flush=True)
        except Exception as e:
            print(f"  FAIL: {e}", flush=True)
            import traceback
            traceback.print_exc()

    print(f"\nGenerated {len(generated)}/{len(specs)} bundles", flush=True)

    if submit and generated:
        print("\nSubmitting GHA campaign...", flush=True)
        result = subprocess.run(
            [sys.executable,
             os.path.expanduser(
                 "~/workspace/fanout/projects/mix-sbox-search/battery/"
                 "submit_campaign_rerun.py"),
             "--candidates", ",".join(generated),
             "--stages", "s0,s1,s2,s3,s4",
             "--priority", "new-leads"],
            capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print("SUBMIT FAILED", flush=True)
            sys.exit(1)
        print("Campaign submitted!", flush=True)


if __name__ == "__main__":
    main()
