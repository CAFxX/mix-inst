#!/usr/bin/env python3
"""Batch 7: 3-round heterogeneous SPN (Hypothesis D4).

Combines batch-5 speed (3r → 20.4u) with batch-3 security (heterogeneous
S-boxes). The 3r homogeneous (dd5_r3_513_nw) was S1-KILLED at 20.4u;
heterogeneous rounds may break the differential/linear trails that killed it.

Base: 3r keyed SPN, pba19 P-box, lin(5,13), LPS order, golden key schedule.
Varies: S-box per round (R=rasC2_0, M=midori_sb0, U=user_sbox1).

Hypothesis D4: Heterogeneous S-boxes in 3r provide enough trail disruption
to survive S1/S2 while keeping the ~20u speed advantage over 4r homogeneous.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOXES = {
    "R": [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14],  # rasC2_0
    "M": [12,10,13,3,14,11,15,7,8,9,1,5,0,2,4,6],  # midori_sb0
    "U": [8,4,3,14,9,13,6,12,2,7,0,15,5,1,10,11],  # user_sbox1
}

PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]

# 3-round heterogeneous patterns
PATTERNS = [
    ("RMR", "alternating R/M/R - bookend strong S-box"),
    ("MRM", "alternating M/R/M - bookend fast S-box"),
    ("RUM", "all-different R/U/M"),
    ("UMR", "all-different U/M/R (reverse)"),
    ("RRM", "two strong then fast - front-load security"),
    ("MRR", "fast then two strong - back-load security"),
]

specs = []
for abbrev, reason in PATTERNS:
    sbox_rounds = [SBOXES[c] for c in abbrev]
    specs.append({
        "name": f"dd7_r3_{abbrev}_513_nw",
        "desc": f"Directed Design 7 (D4): 3r hetero {reason}",
        "nrounds": 3,
        "sbox_rounds": sbox_rounds,
        "sbox_pattern": abbrev,
        "pbox": PBOX_PBA19,
        "rots": [5, 13],
        "ks": {"rot_step": 13, "rc": "golden"},
        "order": "LPS",
    })

outp = os.path.join(OUTDIR, "batch7_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: {s['desc']}")
