#!/usr/bin/env python3
"""Batch 9: Hypothesis D6 — 4 rounds with MIXED nonlinear function types.

Track-4 history: 3-round SPN (1 S-box layer/round) is S1-dead at ~20u regardless
of S-box choice (homogeneous dd5, hetero dd7, per-round-LIN dd8 — all LIN 10/10
+ DIFF 10/10). 4-round hetero SPN survives S1+S2 but costs 27.1/27.2u (dominated).

D6: alternate S-box layers (~4u) with chi/AND-cascade layers (~3.35u/stage per
track-6's al_and6a finding). Target: 4 rounds at ~17-19u — potentially beating
al_and6a's 20.1u with S1 survival.

Co-design (not a blind swap): uniform round template
  x ^= rk_i -> NL_i -> P(pba19) -> [LIN(5,13)]
where NL_i is a 4-bit nibble S-box (rasC2_0, the batch-1 winner) or a
full-width chi layer. The P-box is the shared diffusion substrate for both
layer types; chi triples are al_and6a-validated (full S0-S4+Q1 in a 6-stage
cascade). Chi AND-taps (a,b) are close for local nonlinearity, the c tap is
farther for linear diffusion inside the layer. Key schedule kept golden
(rot_step 13) — the D6 variable is function-type mixing only.

Chi flavors:
  "and":    x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)   (al_and6a style)
  "keccak": x ^ (rotl(x,a) & ~rotl(x,b)) ^ rotl(x,c)  (Keccak-chi style)

lin modes: "all" (LIN after every round), "none" (P-box only — frontier shot).
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

# al_and6a-validated chi triples (AND-taps close, linear tap far)
CHI_A = [(1, 2, 13), (7, 19, 5)]
CHI_B = [(17, 31, 7), (11, 23, 37)]  # wider AND offsets

specs = []


def add(name, desc, pattern, chi_triples, flavor, lin):
    """pattern: e.g. "SCSC" — S = S-box round, C = chi round."""
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
        "lin": lin,
        "ks": KS_GOLDEN,
        "batch": "batch9",
        "sbox": SBOXES["R"],  # fallback for legacy paths
    })


add("dd9_scsc_linall_a",
    "Directed Design 9 (D6): 4r SCSC, AND-chi, LIN after every round — safe co-design baseline",
    "SCSC", CHI_A, "and", "all")
add("dd9_scsc_linall_k",
    "Directed Design 9 (D6): 4r SCSC, Keccak-flavor chi, LIN after every round — NOT-variant probe",
    "SCSC", CHI_A, "keccak", "all")
add("dd9_scsc_nolin_a",
    "Directed Design 9 (D6): 4r SCSC, AND-chi, no LIN anywhere — ~16u frontier-challenger shot",
    "SCSC", CHI_A, "and", "none")
add("dd9_sccs_nolin_a",
    "Directed Design 9 (D6): 4r SCCS, AND-chi, no LIN — pattern variation (chi pair adjacent)",
    "SCCS", CHI_A, "and", "none")
add("dd9_cssc_nolin_a",
    "Directed Design 9 (D6): 4r CSSC, AND-chi, no LIN — pattern variation (chi-first)",
    "CSSC", CHI_A, "and", "none")
add("dd9_scsc_nolin_b",
    "Directed Design 9 (D6): 4r SCSC, AND-chi wide triples (17,31,7)/(11,23,37), no LIN — diffusion probe",
    "SCSC", CHI_B, "and", "none")

outp = os.path.join(OUTDIR, "batch9_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: {s['desc']}")
