#!/usr/bin/env python3
"""Batch 4: Key schedule variants.

Axis: key schedules (rotations, constants, mixing strategies) — the one
README axis batch1-3 did not cover, and the batch-3 pivot note's choice.

Base construction (fixed): 4r keyed SPN, rasC2_0 S-box, pba19 P-box,
lin(5,13), LPS order — the current frontier lead (dd1_lin_5_13_nw).

Round-23 precedent (r22c construction): key-schedule probe ks0 hit 27.9u
(-0.4u vs r22c) but died at S1 (marginal kill) — "key schedule is a real
delay lever; follow-up = simpler nonzero round constants". These probes
re-test that lever in the (5,13) construction; verdicts are scoped to
THIS construction only (VERDICT_SCOPE.md).

Variants (rk_i forms):
  golden  : rotl(key,13*(i+1)) ^ RC_GOLDEN[i]            (control)
  norc    : rotl(key,13*(i+1))                            (no constants)
  smallrc : rotl(key,13*(i+1)) ^ (i+1)                    (simplest nonzero RC)
  rot7    : rotl(key, 7*(i+1)) ^ RC_GOLDEN[i]
  rot1    : rotl(key, 1*(i+1)) ^ RC_GOLDEN[i]
  rot32   : rotl(key,32*(i+1)) ^ RC_GOLDEN[i]             (half-swap)
  norot   : key ^ RC_GOLDEN[i]                            (no rotation)
  fold    : rotl(key,13*(i+1)) ^ rotl(key,37*(i+1)) ^ RC_GOLDEN[i]  (mixing)
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOX_RASC2_0 = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]
PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]

KS_VARIANTS = [
    ("golden",  {"rot_step": 13,      "rc": "golden"},
     "control: rotl13 ^ RC_golden"),
    ("norc",    {"rot_step": 13,      "rc": "zero"},
     "no round constants"),
    ("smallrc", {"rot_step": 13,      "rc": [1, 2, 3, 4]},
     "simplest nonzero constants RC=i+1"),
    ("rot7",    {"rot_step": 7,       "rc": "golden"},
     "rotation step 7"),
    ("rot1",    {"rot_step": 1,       "rc": "golden"},
     "rotation step 1"),
    ("rot32",   {"rot_step": 32,      "rc": "golden"},
     "rotation step 32 (half-swap)"),
    ("norot",   {"rot_step": 0,       "rc": "golden"},
     "no rotation: rk = key ^ RC"),
    ("fold",    {"rot_step": [13, 37], "rc": "golden"},
     "mixing: rotl13 ^ rotl37 ^ RC"),
]

specs = []
for tag, ks, reason in KS_VARIANTS:
    specs.append({
        "name": f"dd4_ks_{tag}_nw",
        "desc": f"Directed Design 4: key schedule {reason}",
        "nrounds": 4,
        "sbox": SBOX_RASC2_0,
        "pbox": PBOX_PBA19,
        "rots": [5, 13],
        "order": "LPS",
        "include_id": True,
        "rank": 64,
        "ks": ks,
    })

outpath = os.path.join(OUTDIR, "batch4_specs.json")
with open(outpath, "w") as f:
    json.dump(specs, f, indent=1)

print(f"Wrote {len(specs)} specs to {outpath}")
for s in specs:
    print(f"  {s['name']}: {s['desc']}")
