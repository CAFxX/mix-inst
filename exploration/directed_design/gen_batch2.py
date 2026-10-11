#!/usr/bin/env python3
"""Batch 2: P-box variants for the rasC2_0 SPN.

The P-box P(i) = (a*i+b) % 64 must be a permutation (a odd, gcd(a,64)=1).
Current: (19,1). Try other affine parameters with good diffusion.

Design: Keep the best linear layers from Batch 1 ((5,9), (8,15), (5,13))
and vary the P-box.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

BASE = {
    "nrounds": 4,
    "sbox": [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14],  # rasC2_0
    "order": "LPS",
    "include_id": True,
    "rank": 64,
    "ks": "golden",
}

# Affine P-box parameters (a must be odd for permutation)
# (a, b, reason)
PBOX_PARAMS = [
    (19, 1, "baseline pba19"),
    (17, 17, "wf2d aff_a17_b17 - S2 survivor"),
    (27, 1, "pba27 - S1+S2 clean in r23"),
    (23, 1, "pba23 - tested in r23"),
    (21, 7, "variant"),
    (25, 3, "variant"),
    (29, 5, "variant"),
    (31, 11, "variant"),
]

# Best linear layers from Batch 1
LIN_LAYERS = [
    ((5, 9), "26.3u S0 leader"),
    ((8, 15), "26.4u, fewer cells"),
    ((5, 13), "26.4u frontier"),
]

specs = []
for (a, b), (la, lb), lin_reason in [
    ((pa, pb), (la, lb), f"{reason}; lin{la,lb} {lin_reason}")
    for (pa, pb, reason) in PBOX_PARAMS
    for ((la, lb), lin_reason) in LIN_LAYERS
]:
    # Skip the baseline combination (already tested)
    if (a, b) == (19, 1) and (la, lb) == (5, 13):
        continue
    # Limit to reasonable count: test all P-boxes with (5,9), and (19,1) with all lin
    if not ((a, b) != (19, 1) and (la, lb) == (5, 9)) and not ((a, b) == (19, 1)):
        continue
    
    spec = dict(BASE)
    spec["name"] = f"dd2_pb{a}_{b}_lin{la}_{lb}_nw"
    spec["desc"] = f"Directed Design 2: P({a},{b}) + lin({la},{lb})"
    spec["pbox"] = [(a*i+b) % 64 for i in range(64)]
    spec["rots"] = [la, lb]
    specs.append(spec)

outpath = os.path.join(OUTDIR, "batch2_specs.json")
with open(outpath, "w") as f:
    json.dump(specs, f, indent=1)

print(f"Wrote {len(specs)} specs to {outpath}")
for s in specs:
    print(f"  {s['name']}")
