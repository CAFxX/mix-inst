#!/usr/bin/env python3
"""Batch 3: Heterogeneous S-box rounds.

Idea: Use different S-boxes in different rounds. If a shallower S-box
(depth 2 vs 3) is used in some rounds, the overall delay might drop,
while the stronger S-box in other rounds maintains quality.

Candidates:
- rasC2_0 (depth 3, DU=4) in rounds 0,2; Midori Sb0 (depth 2?) in rounds 1,3
- Alternating patterns
- Different S-boxes per round

S-boxes to try:
- rasC2_0: [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14] (current)
- Midori Sb0: need to look up
- USER_SBOX1: [8,4,3,14,9,13,6,12,2,7,0,15,5,1,10,11] (from summary)

For now, focus on the concept: generate specs with per-round S-boxes.
The Verilog generator needs to support this.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

# S-box definitions
SBOXES = {
    "rasC2_0": [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14],
    "midori_sb0": [12,10,13,3,14,11,15,7,8,9,1,5,0,2,4,6],  # From literature
    "user_sbox1": [8,4,3,14,9,13,6,12,2,7,0,15,5,1,10,11],
}

BASE = {
    "nrounds": 4,
    "pbox": [(19*i+1) % 64 for i in range(64)],
    "rots": [5, 9],  # Use the (5,9) lead from Batch 1
    "order": "LPS",
    "include_id": True,
    "rank": 64,
    "ks": "golden",
}

# Heterogeneous patterns: list of S-box names per round
PATTERNS = [
    (["rasC2_0", "midori_sb0", "rasC2_0", "midori_sb0"], "alternating rasc2/midori"),
    (["midori_sb0", "rasC2_0", "midori_sb0", "rasC2_0"], "alternating midori/rasc2"),
    (["rasC2_0", "rasC2_0", "midori_sb0", "midori_sb0"], "rasc2x2 then midorix2"),
    (["user_sbox1", "rasC2_0", "user_sbox1", "rasC2_0"], "alternating user/rasc2"),
]

specs = []
for pattern, reason in PATTERNS:
    spec = dict(BASE)
    # Create a name from the pattern
    abbrev = "".join("R" if s == "rasC2_0" else "M" if s == "midori_sb0" else "U" for s in pattern)
    spec["name"] = f"dd3_hetero_{abbrev}_nw"
    spec["desc"] = f"Directed Design 3: heterogeneous S-box {reason}"
    spec["sbox_rounds"] = [SBOXES[s] for s in pattern]
    spec["sbox_pattern"] = pattern
    specs.append(spec)

outpath = os.path.join(OUTDIR, "batch3_specs.json")
with open(outpath, "w") as f:
    json.dump(specs, f, indent=1)

print(f"Wrote {len(specs)} specs to {outpath}")
for s in specs:
    print(f"  {s['name']}: {s['desc']}")
