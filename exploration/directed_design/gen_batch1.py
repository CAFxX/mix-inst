#!/usr/bin/env python3
"""Batch 1: Linear layer variants for the rasC2_0 pba19 SPN.

Design axes:
1. Rotation pairs with branch>=4, small rotations (low delay)
2. Per-round varying rotations
3. (8,15) — ties (5,13) on branch/spread2

Base construction (from r25_spn_pba19_sb_rasC2_0_nw):
- 4-round keyed SPN
- S-box: rasC2_0 = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]
- P-box: P(i) = (19*i+1) % 64
- Key schedule: rk_i = rotl64(key, 13*(i+1)) ^ RC[i]
- RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A, 0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054]
"""
import json
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
sys.path.insert(0, os.path.join(R25, "models"))
sys.path.insert(0, R25)
import numpy as np

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

# Base spec template
BASE = {
    "nrounds": 4,
    "sbox": [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14],  # rasC2_0
    "pbox": [(19*i+1) % 64 for i in range(64)],  # pba19
    "order": "LPS",
    "include_id": True,
    "rank": 64,
    "ks": "golden",  # standard golden key schedule
}

# Batch 1a: Rotation pairs with branch>=4
# From the 2026-10-06 scan: 1,431 pairs have branch>=4
# Focus on small rotations for low delay
ROT_PAIRS = [
    # (a, b, reason)
    (5, 13, "branch4 spread6 - current frontier"),
    (8, 15, "branch4 spread6 - ties (5,13)"),
    (3, 11, "branch3 spread5 - baseline"),
    (4, 9, "small rotations, branch4?"),
    (5, 9, "branch4 spread5"),
    (6, 11, "small rotations"),
    (7, 12, "small rotations"),
    (4, 13, "mixed"),
    (6, 15, "mixed"),
    (9, 17, "medium rotations"),
]

# Batch 1b: Per-round varying rotations
# Different (a,b) per round — more design freedom
VARYING = [
    # [(a0,b0), (a1,b1), (a2,b2), (a3,b3)]
    ([(3,11), (5,13), (3,11), (5,13)], "alternating 311/513"),
    ([(5,13), (8,15), (5,13), (8,15)], "alternating 513/815"),
    ([(3,11), (3,11), (5,13), (5,13)], "311x2 then 513x2"),
]

specs = []

# 1a: Fixed rotation pairs
for a, b, reason in ROT_PAIRS:
    spec = dict(BASE)
    spec["name"] = f"dd1_lin_{a}_{b}_nw"
    spec["desc"] = f"Directed Design 1a: lin({a},{b}) - {reason}"
    spec["rots"] = [a, b]
    specs.append(spec)

# 1b: Varying rotations
for rots_list, reason in VARYING:
    spec = dict(BASE)
    # Name from first pair
    a0, b0 = rots_list[0]
    spec["name"] = f"dd1_linvar_{a0}_{b0}_x4_nw"
    spec["desc"] = f"Directed Design 1b: varying rotations - {reason}"
    spec["rots"] = rots_list  # List of pairs per round
    spec["rots_varying"] = True
    specs.append(spec)

# Write specs
outpath = os.path.join(OUTDIR, "batch1_specs.json")
with open(outpath, "w") as f:
    json.dump(specs, f, indent=1)

print(f"Wrote {len(specs)} specs to {outpath}")
for s in specs:
    print(f"  {s['name']}: {s['desc'][:60]}")
