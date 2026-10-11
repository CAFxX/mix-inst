#!/usr/bin/env python3
"""Batch 5: Round-count variants (3r/5r/6r SPN).

Axis: round-count vs security tradeoff — the one README axis batch1-4 did not
cover. Tests whether fewer rounds (lower latency) can maintain S2 security,
or whether more rounds buy meaningful margin.

Base construction (fixed): keyed SPN, rasC2_0 S-box, pba19 P-box, lin(5,13),
LPS order, golden key schedule — the dd1_lin_5_13_nw baseline (26.5u @ 4r).

Hypothesis D1: Per-round cost ~6.6u. 3r → ~19.8u (matches al_chi6b S0!);
the question is whether 3r with lin(5,13) still passes S2, or if differential
trails become too strong. 5r/6r test the other direction: does extra depth
buy security margin worth the delay cost?

Verdicts scoped to "Xr in the 4r rasC2_0/pba19/lin(5,13) construction"
per VERDICT_SCOPE.md.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOX_RASC2_0 = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]
PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]

ROUND_VARIANTS = [
    (3, "3-round: ~19.8u target, tests if lin(5,13) diffuses enough in 3r"),
    (5, "5-round: ~33u, tests if extra round buys S2 margin"),
    (6, "6-round: ~40u, tests the cost/benefit curve endpoint"),
]

specs = []
for nrounds, reason in ROUND_VARIANTS:
    specs.append({
        "name": f"dd5_r{nrounds}_513_nw",
        "desc": f"Directed Design 5: {reason}",
        "nrounds": nrounds,
        "sbox": SBOX_RASC2_0,
        "pbox": PBOX_PBA19,
        "rots": [5, 13],
        "ks": {"rot_step": 13, "rc": "golden"},
        "order": "LPS",
    })

outp = os.path.join(OUTDIR, "batch5_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: {s['desc']}")
