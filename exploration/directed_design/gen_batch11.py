#!/usr/bin/env python3
"""Batch 11: Hypothesis D8 — 3-round chi-first mixed SPN.

D8 analytic findings:
- The S1 LIN/DIFF "invariant subspace" is a DIFFUSION defect, not a true
  invariant: on 64-consecutive inputs, nolin outputs have low algebraic
  degree (many constant bits, rank ~25). Single-rot[13] fails differently
  (D=1923, rank ~61): 1-XOR rotation layers are insufficient even when
  bijective (rot13p63: D=1659) — the rotation structure itself is the problem.
- CHEAPEST PROVABLY-WORKING LIN: any bijective 2-XOR rotation pair on ALL
  rounds (lin513/pair13-27/pair1-2/pair7-19 all D~20, multi-key clean).
  1-XOR layers (rot/shift/passthrough) all fail or are borderline; partial
  placement (sbox-only, chi-only, drop-any-but-last) fails. The last LIN is
  load-bearing for DIFF (low-8-bit marginal), though rank-invariant.
- BREAKTHROUGH: 3-round CHI-FIRST patterns (CCS/CSC/CSS) with full 2-XOR LIN
  are D-clean (D=20-33 multi-key). Sbox-first 3-round (SCS/SSC) is dead
  (D=4096). The chi-first round spreads the 6 varying input bits before the
  nibble-structured S-box round sees them.
- Triple co-design: close-AND-tap structure (CHI_A) is load-bearing for the
  3-round template; wide triples (CHI_B) are catastrophic (D=3720).
  wideA [(1,2,37),(7,19,43)] has the best DIFF probe (14.3).

Batch-11: 3-round chi-first, lin(5,13) all rounds, golden KS, pba19.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOXES = {
    "R": [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14],  # rasC2_0
}

PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]
KS_GOLDEN = {"rot_step": 13, "rc": "golden"}
LIN513 = [5, 13]

CHI_A = [(1, 2, 13), (7, 19, 5)]          # al_and6a-validated, D8-confirmed
CHI_WA = [(1, 2, 37), (7, 19, 43)]        # wideA: best D8 DIFF probe

specs = []


def add(name, desc, pattern, chi_triples, flavor="and"):
    layers = []
    ci = 0
    for ch in pattern:
        if ch == "S":
            layers.append({"type": "sbox", "sbox": SBOXES["R"]})
        elif ch == "C":
            a, b, c = chi_triples[ci % len(chi_triples)]
            layers.append({"type": "chi", "chi": [a, b, c], "flavor": flavor})
            ci += 1
        else:
            raise ValueError(ch)
    specs.append({
        "name": name,
        "desc": desc,
        "nrounds": len(pattern),
        "layers": layers,
        "pattern": pattern,
        "pbox": PBOX_PBA19,
        "rots": LIN513,
        "lin": "all",
        "ks": KS_GOLDEN,
        "batch": "batch11",
        "sbox": SBOXES["R"],
    })


add("dd11_ccs_a",
    "Directed Design 11 (D8): 3r CCS (chi-first), AND-chi CHI_A, LIN(5,13) all rounds — D8 flagship",
    "CCS", CHI_A)
add("dd11_css_a",
    "Directed Design 11 (D8): 3r CSS (chi-first), AND-chi CHI_A, LIN(5,13) all rounds — pattern variant",
    "CSS", CHI_A)
add("dd11_csc_a",
    "Directed Design 11 (D8): 3r CSC (chi-first), AND-chi CHI_A, LIN(5,13) all rounds — pattern variant (worse DIFF probe)",
    "CSC", CHI_A)
add("dd11_ccs_wa",
    "Directed Design 11 (D8): 3r CCS, AND-chi wideA triples, LIN(5,13) all rounds — D8 triple co-design",
    "CCS", CHI_WA)

outp = os.path.join(OUTDIR, "batch11_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: pattern={s['pattern']} rots={s['rots']} lin={s['lin']}")
