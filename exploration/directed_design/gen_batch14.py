#!/usr/bin/env python3
"""Batch 14: Hypothesis D11 — the two tested D11 axes, promoting the clean classes.

D11 screen (d11_screen.py, results/d11_screen.txt; control DIAG reproduced
D9's D0=20 exactly) established:

Axis 1 — shift+shift 2-term LIN on the SCSC-Midori-CHI_A vehicle, full LIN
  all rounds: 126 combos, 12 shl+shr dead at GF(2) rank 61-63, 114 screened.
  STRUCTURAL FINDING: shl+shl is DIFF-dead on this vehicle — 34/34 screened
  bad (probe0 25.7-721.4). shr+shr: 1 kill (shr2_shr7 289.8), 39/40 clean.
  shl+shr: 2 bad (shl2_shr1 69.1, shl3_shr2 83.4), 38/40 clean.
  New design rule: 2-term LIN needs a right-shift or rotation term;
  pure left-shift terms are DIFF-dead (consistent with D10: rotl+shl lived).

Axis 2 — SSSS Midori with co-designed WIDER rotation pairs (D10: (5,13)
  clean, (13,27) clean, (7,19) borderline, (1,2) dead):
  (13,37) D=20 clean, (19,43) D=17 clean, (27,37) D=19 clean,
  (7,43) D=25 clean, (13,43) D=20 clean, (5,37) D=16 borderline (25.4/27.0).
  Wider pairs are viable (narrow-wide balance matters: (5,37) regresses vs
  D10's (5,13)). Transplant test: D10's best rot+shift term r5_shl6 (D=11 on
  SCSC) DIED on SSSS (probe 34.3/69.6); r13_shr6 lived (D=20, probe
  16.9/15.0). Terms do NOT always transplant across templates.

Promoting 4 representatives (S0 cost is structurally insensitive to exact
LIN choice at fixed XOR count, so reps bound the question):
  ax1 shr+shr best-D0, ax1 shl+shr best-D0, ax2 wider-pair best-D0,
  ax2 transplanted-term survivor. Campaign tests screen-fidelity for the
  new shr-containing LIN classes + wider SSSS family at real S1/S2;
  no cost breakthrough expected (~27u floor, same XOR count).

All: golden KS (rot_step 13), pba19, full LIN on ALL rounds.
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


def add_mixed(name, desc, lin_terms, pattern="SCSC"):
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
        "lin": "all", "ks": KS_GOLDEN, "batch": "batch14",
    })


def add_ssss(name, desc, rots=None, lin_terms=None):
    layers = [{"type": "sbox", "sbox": SBOX_M} for _ in range(4)]
    spec = {"name": name, "desc": desc, "nrounds": 4, "layers": layers,
            "pattern": "SSSS", "pbox": PBOX_PBA19,
            "lin": "all", "ks": KS_GOLDEN, "batch": "batch14"}
    if lin_terms is not None:
        spec["lin_terms"] = [[k, n] for k, n in lin_terms]
        spec["rots"] = [n for _, n in lin_terms]
    else:
        spec["rots"] = list(rots)
    specs.append(spec)


# Axis 1: shift+shift class reps (shl-only structurally dead — not promoted)
add_mixed("dd14_ax1_shr2_shr5",
          "D11 axis-1: 4r SCSC Midori/CHI_A, LIN=x^(x>>2)^(x>>5) all rounds (screen D=15, multi 15/28/22, probe 12.4/14.3) — shr+shr class rep",
          [("shr", 2), ("shr", 5)])
add_mixed("dd14_ax1_shl2_shr6",
          "D11 axis-1: 4r SCSC Midori/CHI_A, LIN=x^(x<<2)^(x>>6) all rounds (screen D=13, multi 13/26/21, probe 15.2/14.8) — shl+shr class rep",
          [("shl", 2), ("shr", 6)])

# Axis 2: wider SSSS pairs + transplanted-term survivor
add_ssss("dd14_ax2_ssss_midori_1943",
         "D11 axis-2: 4r SSSS Midori Sb0, LIN(19,43) all rounds (screen D=17, multi 17/29/21, probe 15.4/17.7) — wider-pair rep",
         rots=[19, 43])
add_ssss("dd14_ax2_ssss_midori_r13_shr6",
         "D11 axis-2: 4r SSSS Midori Sb0, LIN=x^rotl(x,13)^(x>>6) all rounds (screen D=20, multi 20/32/29, probe 16.9/15.0) — D10-best-term transplant survivor (r5_shl6 died on SSSS)",
         lin_terms=[("rotl", 13), ("shr", 6)])

outp = os.path.join(OUTDIR, "batch14_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    lin = s.get("lin_terms", s.get("rots"))
    print(f"  {s['name']}: pattern={s['pattern']} lin={lin}")
