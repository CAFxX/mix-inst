#!/usr/bin/env python3
"""Batch 10: Hypothesis D7 — which layer type needs the rotation LIN layer?

D6 result (batch 9): 4-round mixed S-box/chi SPN. nolin variants (P-box only
between nonlinear layers, 17.2-18.6u, all under al_and6a's 20.1u) vs linall
variants (full LIN(5,13) every round, 27.2/27.6u, S1 CAL_PASS + S2 PASS).
Key finding: the rotation-linear layer is load-bearing for S1 in mixed
constructions — P-box alone doesn't break the linear invariant subspace
(nolin S1: LIN 10/10 + DIFF 10/10, same keys as dd7/dd8 3r failures).

D7 isolates WHICH layer type needs LIN, and probes a cheaper LIN:
  (1) lin="sbox": LIN only on S-box rounds (chi rounds: P-box only)
  (2) lin="chi":  LIN only on chi rounds (S-box rounds: P-box only)
  (3) single-rotation LIN [13] (x ^ rotl64(x,13)) vs the (5,13) pair —
      measures the S0 saving and whether S1 survives
  (4) hetero R/M S-boxes inside the S-box rounds of the best partial-LIN
      candidate (M=midori_sb0, literature table, batch-3/7 validated)

Template unchanged from D6: SCSC (S=rasC2_0 round, C=AND-chi round),
pba19 P-box, golden KS (rot_step 13). CHI_A triples from al_and6a.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOXES = {
    "R": [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14],  # rasC2_0
    "M": [12, 10, 13, 3, 14, 11, 15, 7, 8, 9, 1, 5, 0, 2, 4, 6],  # midori_sb0
}

PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]
KS_GOLDEN = {"rot_step": 13, "rc": "golden"}
LIN513 = [5, 13]
LIN13 = [13]

# al_and6a-validated chi triples (AND-taps close, linear tap far)
CHI_A = [(1, 2, 13), (7, 19, 5)]

specs = []


def add(name, desc, pattern, chi_triples, flavor, lin, rots, sbox_seq=None):
    """pattern: e.g. "SCSC" — S = S-box round, C = chi round.
    sbox_seq: list of sbox keys cycled over the S rounds (None -> all R).
    rots: [a,b] pair or [a] single-rotation LIN.
    """
    layers = []
    ci = si = 0
    for ch in pattern:
        if ch == "S":
            key = sbox_seq[si % len(sbox_seq)] if sbox_seq else "R"
            layers.append({"type": "sbox", "sbox": SBOXES[key]})
            si += 1
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
        "rots": rots,
        "lin": lin,
        "ks": KS_GOLDEN,
        "batch": "batch10",
        "sbox": SBOXES["R"],  # fallback for legacy paths
    })


add("dd10_scsc_linsbox_a",
    "Directed Design 10 (D7): 4r SCSC, AND-chi, LIN(5,13) on S-box rounds only — does the S-box round need LIN?",
    "SCSC", CHI_A, "and", "sbox", LIN513)
add("dd10_scsc_linchi_a",
    "Directed Design 10 (D7): 4r SCSC, AND-chi, LIN(5,13) on chi rounds only — does the chi round need LIN?",
    "SCSC", CHI_A, "and", "chi", LIN513)
add("dd10_sccs_linsbox_a",
    "Directed Design 10 (D7): 4r SCCS, AND-chi, LIN(5,13) on S-box rounds only — fastest D6 pattern (17.2u) + partial LIN",
    "SCCS", CHI_A, "and", "sbox", LIN513)
add("dd10_scsc_singlerot_a",
    "Directed Design 10 (D7): 4r SCSC, AND-chi, single-rotation LIN [13] on all rounds — cheaper-LIN probe",
    "SCSC", CHI_A, "and", "all", LIN13)
add("dd10_scsc_singlerot_linsbox_a",
    "Directed Design 10 (D7): 4r SCSC, AND-chi, single-rotation LIN [13] on S-box rounds only — cheapest partial-LIN combo",
    "SCSC", CHI_A, "and", "sbox", LIN13)
add("dd10_scsc_linsbox_rm",
    "Directed Design 10 (D7): 4r SCSC, AND-chi, LIN(5,13) on S-box rounds only, hetero R/M S-boxes (R round 0, M round 2)",
    "SCSC", CHI_A, "and", "sbox", LIN513, sbox_seq=["R", "M"])

outp = os.path.join(OUTDIR, "batch10_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: lin={s['lin']} rots={s['rots']} pattern={s['pattern']}")
