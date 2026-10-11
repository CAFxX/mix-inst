#!/usr/bin/env python3
"""Batch 12: Hypothesis D9 — cost-optimize the 4-round S1-clean mixed SPN.

D8 established: the mixed S-box/chi SPN cannot beat al_and6a 20.1u on speed
(3r DIFF-dead at ~20.4-21u; 4r S1-clean costs 27.2u via dd9_scsc_linall_k).
BUT the 4r construction with full 2-XOR LIN on every round IS S1+S2 clean —
dd9_scsc_linall_a (27.6u, AND chi, max|z|=3.7) and dd9_scsc_linall_k
(27.2u, Keccak chi, max|z|=8.4) are the cheapest known S1-clean directed
designs.

D9 pulls four cost levers against the 27.2u floor:
  (1) Depth-2 S-box: rasC2_0 -> Midori Sb0 in the S-box rounds (track-6 data:
      4-bit S-box layers cost ~4-5u; a depth-2 box should save ~1u/round).
  (2) Cheaper rotation pairs: D8 proved [5,13],[13,27],[1,2],[7,19] all
      break the invariant (D~16-20). S0 will show which synthesizes cheapest.
  (3) Chi-layer tuning: D8's triple co-design found wideA [(1,2,37),(7,19,43)]
      the marginally-best probe — test it in the full 4r context.
  (4) Round-pattern variant: CSCS (chi-first) with the cheaper components —
      D8's 3r work showed chi-first helps diffusion; screen-only probes test
      whether chi-first 4r allows any LIN relaxation.

All candidates keep: golden KS (rot_step 13), pba19, full LIN on ALL rounds
(D7/D8 proved partial placement is S1-dead), AND-flavor chi.
"""
import json
import os

OUTDIR = "/home/hatch/workspace/mix/exploration/directed_design/specs"
os.makedirs(OUTDIR, exist_ok=True)

SBOXES = {
    "R": [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14],  # rasC2_0
    "M": [12, 10, 13, 3, 14, 11, 15, 7, 8, 9, 1, 5, 0, 2, 4, 6],  # midori_sb0 (depth-2)
}

PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]
KS_GOLDEN = {"rot_step": 13, "rc": "golden"}

CHI_A = [(1, 2, 13), (7, 19, 5)]          # al_and6a-validated, D8-confirmed
CHI_WA = [(1, 2, 37), (7, 19, 43)]        # wideA: best D8 DIFF probe

PAIR_513 = [5, 13]
PAIR_12 = [1, 2]
PAIR_719 = [7, 19]
PAIR_1327 = [13, 27]

specs = []


def add(name, desc, pattern, chi_triples, flavor, lin, rots, sbox_seq):
    """pattern: e.g. "SCSC" — S = S-box round, C = chi round.
    sbox_seq: list of sbox keys cycled over the S rounds.
    rots: [a,b] bijective rotation pair (D8: all four pairs S1-viable).
    """
    layers = []
    ci = si = 0
    for ch in pattern:
        if ch == "S":
            key = sbox_seq[si % len(sbox_seq)]
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
        "batch": "batch12",
        "sbox": SBOXES[sbox_seq[0]],  # fallback for legacy paths
    })


MM = ["M", "M"]  # Midori Sb0 on both S-box rounds

add("dd12_scsc_midori_513_a",
    "Directed Design 12 (D9): 4r SCSC, Midori Sb0 S-box, AND-chi CHI_A, LIN(5,13) all rounds — lever 1 (depth-2 S-box swap)",
    "SCSC", CHI_A, "and", "all", PAIR_513, MM)
add("dd12_scsc_midori_12_a",
    "Directed Design 12 (D9): 4r SCSC, Midori Sb0 S-box, AND-chi CHI_A, LIN(1,2) all rounds — lever 2 (rotation pair)",
    "SCSC", CHI_A, "and", "all", PAIR_12, MM)
add("dd12_scsc_midori_719_a",
    "Directed Design 12 (D9): 4r SCSC, Midori Sb0 S-box, AND-chi CHI_A, LIN(7,19) all rounds — lever 2 (rotation pair)",
    "SCSC", CHI_A, "and", "all", PAIR_719, MM)
add("dd12_scsc_midori_1327_a",
    "Directed Design 12 (D9): 4r SCSC, Midori Sb0 S-box, AND-chi CHI_A, LIN(13,27) all rounds — lever 2 (rotation pair)",
    "SCSC", CHI_A, "and", "all", PAIR_1327, MM)
add("dd12_scsc_midori_513_wa",
    "Directed Design 12 (D9): 4r SCSC, Midori Sb0 S-box, AND-chi wideA triples, LIN(5,13) all rounds — lever 3 (chi tuning)",
    "SCSC", CHI_WA, "and", "all", PAIR_513, MM)
add("dd12_cscs_midori_513_a",
    "Directed Design 12 (D9): 4r CSCS (chi-first), Midori Sb0 S-box, AND-chi CHI_A, LIN(5,13) all rounds — lever 4 (pattern)",
    "CSCS", CHI_A, "and", "all", PAIR_513, MM)

outp = os.path.join(OUTDIR, "batch12_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    print(f"  {s['name']}: pattern={s['pattern']} rots={s['rots']} lin={s['lin']}")
