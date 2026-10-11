#!/usr/bin/env python3
"""Batch 6: Key-schedule × linear-layer stacking.

Axis: tests whether batch-4 ks gains (-0.2u for norc/smallrc/rot1 on lin(5,13))
stack additively with batch-1 linear-layer leads (lin(5,9) @ 26.3u, lin(8,15)).

Base construction (fixed): 4r keyed SPN, rasC2_0 S-box, pba19 P-box, LPS order.

Hypothesis D3: If ks and linear layer affect different parts of the critical
path, gains stack. If they collide, no improvement.

Non-duplication vs hybrid: hybrid owns P-box × linear co-design. This is
ks × linear — a different axis.

Verdicts scoped to "<ks,lin> in the 4r rasC2_0/pba19 construction".
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOX_RASC2_0 = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]
PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]

# (ks_tag, ks_spec, lin_tag, rots)
COMBOS = [
    ("norc",    {"rot_step": 13, "rc": "zero"},      "5_9",  [5, 9]),
    ("smallrc", {"rot_step": 13, "rc": [1, 2, 3, 4]}, "5_9",  [5, 9]),
    ("rot1",    {"rot_step": 1,  "rc": "golden"},     "5_9",  [5, 9]),
    ("norc",    {"rot_step": 13, "rc": "zero"},      "8_15", [8, 15]),
    ("smallrc", {"rot_step": 13, "rc": [1, 2, 3, 4]}, "8_15", [8, 15]),
    ("rot1",    {"rot_step": 1,  "rc": "golden"},     "8_15", [8, 15]),
]

specs = []
for ks_tag, ks, lin_tag, rots in COMBOS:
    specs.append({
        "name": f"dd6_ks{ks_tag}_lin{lin_tag}_nw",
        "desc": f"Directed Design 6: ks={ks_tag} x lin({rots[0]},{rots[1]}) stacking test",
        "nrounds": 4,
        "sbox": SBOX_RASC2_0,
        "pbox": PBOX_PBA19,
        "rots": rots,
        "ks": ks,
        "order": "LPS",
    })

outp = os.path.join(OUTDIR, "batch6_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: {s['desc']}")
