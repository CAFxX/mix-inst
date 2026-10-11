#!/usr/bin/env python3
"""Batch 8: Hypothesis D5 — 3r hetero was structurally too shallow (D4 falsified).

Two axes:
  (a) 4-round hetero SPN (dd8_r4_*): does the extra round fix the S1 weakness
      that killed all six dd7 3r candidates? Expected ~27u (depth test, scoped).
  (b) 3-round hetero with PER-ROUND LIN variation (dd8_r3_*_vlin*): the dd7 kill
      was 10 LIN + 10 DIFF rejections on identical keys — the rotation set's
      generated group has a small-order invariant subspace. Varying (a,b) per
      round changes the group each round, which may break the trails while
      keeping ~21u latency (rotations are wiring, not gates).

Base for all: pba19 P-box, LPS order, golden key schedule.
S-boxes: R=rasC2_0, M=midori_sb0, U=user_sbox1 (same as batch-7).
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
KS_GOLDEN = {"rot_step": 13, "rc": "golden"}

specs = []

def add(name, desc, nrounds, pattern, rots, order="LPS"):
    sbox_rounds = [SBOXES[c] for c in pattern]
    specs.append({
        "name": name,
        "desc": desc,
        "nrounds": nrounds,
        "sbox_rounds": sbox_rounds,
        "sbox_pattern": pattern,
        "pbox": PBOX_PBA19,
        "rots": rots,
        "ks": KS_GOLDEN,
        "order": order,
        "sbox": SBOXES["R"],  # fallback; sbox_rounds takes precedence
    })

# (a) 4-round hetero — depth test
add("dd8_r4_RMRM_513_nw",
    "Directed Design 8 (D5a): 4r hetero R/M/R/M - does depth fix S1?",
    4, "RMRM", [5, 13])
add("dd8_r4_MRMR_513_nw",
    "Directed Design 8 (D5a): 4r hetero M/R/M/R - does depth fix S1?",
    4, "MRMR", [5, 13])

# (b) 3-round hetero with per-round LIN — mixing test
VLIN1 = [[5, 13], [8, 15], [3, 11]]
VLIN2 = [[5, 13], [11, 19], [7, 23]]
add("dd8_r3_RMR_vlin1_nw",
    "Directed Design 8 (D5b): 3r hetero R/M/R, per-round LIN (5,13)/(8,15)/(3,11)",
    3, "RMR", VLIN1)
add("dd8_r3_MRM_vlin1_nw",
    "Directed Design 8 (D5b): 3r hetero M/R/M, per-round LIN (5,13)/(8,15)/(3,11)",
    3, "MRM", VLIN1)
add("dd8_r3_RMR_vlin2_nw",
    "Directed Design 8 (D5b): 3r hetero R/M/R, per-round LIN (5,13)/(11,19)/(7,23)",
    3, "RMR", VLIN2)
add("dd8_r3_RUM_vlin1_nw",
    "Directed Design 8 (D5b): 3r hetero R/U/M, per-round LIN (5,13)/(8,15)/(3,11)",
    3, "RUM", VLIN1)

outp = os.path.join(OUTDIR, "batch8_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: {s['desc']}")
