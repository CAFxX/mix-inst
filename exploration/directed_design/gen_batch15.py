#!/usr/bin/env python3
"""Batch 15: Hypothesis D13 — S-box/chi REBALANCE (fewer S-box rounds).

D12 killed the 3-round axis structurally (SCS: D0=4096 on all LIN classes;
CSC: D0=32-564, DIFF probes 74-344 dead; mechanism: sequential-input
GF(2) rank 41-45 — see supervisor.log 2026-10-10 ~17:40 CEST and
VERDICT_SCOPE.md O85). D13 attacks cost via round COMPOSITION instead of
count: D10 established chi rounds are shallower than S-box rounds on the
critical path, so replace an S-box round with a chi round.

D13 probe (15 combos: 5 patterns x 3 best LIN classes, 2026-10-10):
  SCCS  (2S+2C): D0 22-31, probes 13-16.5 — clean (control-like)
  SCSCS (3S+2C): D0 17-28, probes 14-16.5 — clean
  SCCC  (1S+3C, S-box first): r5_shl6 D0=66 (borderline, probes clean),
      shl2_shr6 D0=19 clean, **shr2_shr5 D0=4096 DEAD**
  CSCC  (1S+3C, chi first):  D0 18-22, probes 13-17.5 — clean ALL classes
  SCCSC (3S+2C): D0 17-30, probes 12.6-16.4 — clean
New co-design rule: S-box-FIRST + shr+shr LIN is dead (D0=4096); chi-first
  is clean for the same LIN. S-box position interacts with LIN class.

Promoting the 3 CSCC (chi-first, 1 S-box + 3 chi) probe winners — the
cheapest viable directed template to date. Question for S0: does
1S+3C actually beat the 27.0u 4r-SCSC floor, and by how much?
Screen-fidelity for the rebalanced template goes to GHA S1/S2 if S0 < 27u.

All: Midori Sb0, CHI_A AND-chi, pba19, golden KS (rot_step 13),
full LIN on ALL rounds.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOX_M = [12, 10, 13, 3, 14, 11, 15, 7, 8, 9, 1, 5, 0, 2, 4, 6]  # midori_sb0
PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]
KS_GOLDEN = {"rot_step": 13, "rc": "golden"}
CHI_A = [(1, 2, 13), (7, 19, 5)]

specs = []


def add_cscc(name, desc, lin_terms):
    pattern = "CSCC"
    layers = []
    ci = 0
    for ch in pattern:
        if ch == "S":
            layers.append({"type": "sbox", "sbox": SBOX_M})
        else:
            a, b, c = CHI_A[ci % len(CHI_A)]
            layers.append({"type": "chi", "chi": [a, b, c], "flavor": "and"})
            ci += 1
    specs.append({
        "name": name, "desc": desc, "nrounds": 4, "layers": layers,
        "pattern": pattern, "pbox": PBOX_PBA19,
        "lin_terms": [[k, n] for k, n in lin_terms],
        "lin": "all", "ks": KS_GOLDEN, "batch": "batch15",
    })


add_cscc("dd15_cscc_r5_shl6",
         "D13: 4-layer CSCC (chi,S-box,chi,chi) Midori/CHI_A, LIN=x^rotl(x,5)^(x<<6) all rounds "
         "(probe D0=18, multi 18/23/16, dprobe 16.1/17.5) — rot+shift class rep",
         [("rotl", 5), ("shl", 6)])
add_cscc("dd15_cscc_shr2_shr5",
         "D13: 4-layer CSCC (chi,S-box,chi,chi) Midori/CHI_A, LIN=x^(x>>2)^(x>>5) all rounds "
         "(probe D0=19, multi 19/23/15, dprobe 14.2/14.5) — shr+shr class rep",
         [("shr", 2), ("shr", 5)])
add_cscc("dd15_cscc_shl2_shr6",
         "D13: 4-layer CSCC (chi,S-box,chi,chi) Midori/CHI_A, LIN=x^(x<<2)^(x>>6) all rounds "
         "(probe D0=22, multi 22/17/20, dprobe 14.9/13.9) — shl+shr class rep",
         [("shl", 2), ("shr", 6)])

outp = os.path.join(OUTDIR, "batch15_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: pattern={s['pattern']} lin={s['lin_terms']}")
