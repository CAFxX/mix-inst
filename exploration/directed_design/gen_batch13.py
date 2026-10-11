#!/usr/bin/env python3
"""Batch 13: Hypothesis D10 — two genuinely untested axes for the directed SPN.

D10 screen (d10_screen.py, results/d10_screen.txt; control DIAG reproduced
D9's D0=20 exactly) established:

Axis 1 — rot+shift 2-term LIN (x ^ rotl(x,a) ^ (x<<b)/(x>>b)) on the
  SCSC-Midori-CHI_A vehicle, full LIN all rounds:
  35/98 combos bijective (GF(2) rank 64); 63 dead at rank 61-63), and ALL 35
  bijective combos are screen-clean (D 11-33, multi-key <50, DIFF probes
  13-20 in-band with the dd12 control). The invariant defect is broken by
  the rot+shift class just as by rotation pairs.
  Promoting 4 spanning the D range and both shift directions (D9 showed S0
  cost is structurally insensitive to the exact rotation choice, so 4
  representatives bound the cost question; all 35 stay in d10_screen.txt).

Axis 2 — all-S-box SSSS Midori template, full 2-XOR LIN all rounds:
  (5,13) D=22 CLEAN, (13,27) D=23 CLEAN, (7,19) D=34 borderline
  (multi 34/42/25 — deferred lead), (1,2) D=430 DEAD. rasC2_0 (5,13) D=23
  clean (S-box choice secondary). 3r SSS: all D=4096 DEAD (long shot fails).
  New finding vs D8: on the pure-S-box template the LIN pair choice matters
  ((1,2) dies here but lived on the mixed template) — chi's cross-nibble
  AND terms were load-bearing for narrow pairs.
  Promoting the 2 clean Midori SSSS configs (no chi AND gates — the cost
  question: is pure-S-box cheaper than the 27.1u mixed floor?).

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
    """Axis-1: mixed SCSC template, LIN via lin_terms [[kind,n],...]."""
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
        "lin": "all", "ks": KS_GOLDEN, "batch": "batch13",
    })


def add_ssss(name, desc, rots):
    """Axis-2: 4 rounds of pure Midori-Sb0 S-box layers, rotation-pair LIN."""
    layers = [{"type": "sbox", "sbox": SBOX_M} for _ in range(4)]
    specs.append({
        "name": name, "desc": desc, "nrounds": 4, "layers": layers,
        "pattern": "SSSS", "pbox": PBOX_PBA19,
        "rots": list(rots), "lin": "all", "ks": KS_GOLDEN, "batch": "batch13",
    })


# Axis 1: top-D rot+shift combos (screen: D, multi-key, dprobe0/dprobe1)
add_mixed("dd13_ax1_r5_shl6",
          "D10 axis-1: 4r SCSC Midori/CHI_A, LIN=x^rotl(x,5)^(x<<6) all rounds (screen D=11, multi 11/22/24, probe 14.6/13.5)",
          [("rotl", 5), ("shl", 6)])
add_mixed("dd13_ax1_r13_shr6",
          "D10 axis-1: 4r SCSC Midori/CHI_A, LIN=x^rotl(x,13)^(x>>6) all rounds (screen D=12, multi 12/20/14, probe 15.4/14.7)",
          [("rotl", 13), ("shr", 6)])
add_mixed("dd13_ax1_r5_shl3",
          "D10 axis-1: 4r SCSC Midori/CHI_A, LIN=x^rotl(x,5)^(x<<3) all rounds (screen D=15, multi 15/26/20, probe 14.4/15.3)",
          [("rotl", 5), ("shl", 3)])
add_mixed("dd13_ax1_r7_shr5",
          "D10 axis-1: 4r SCSC Midori/CHI_A, LIN=x^rotl(x,7)^(x>>5) all rounds (screen D=17, multi 17/33/16, probe 13.2/14.2)",
          [("rotl", 7), ("shr", 5)])

# Axis 2: pure-S-box SSSS
add_ssss("dd13_ax2_ssss_midori_513",
         "D10 axis-2: 4r SSSS Midori Sb0, LIN(5,13) all rounds (screen D=22, multi 22/28/20, probe 13.6/16.3)",
         [5, 13])
add_ssss("dd13_ax2_ssss_midori_1327",
         "D10 axis-2: 4r SSSS Midori Sb0, LIN(13,27) all rounds (screen D=23, multi 23/19/21, probe 16.3/14.4)",
         [13, 27])

outp = os.path.join(OUTDIR, "batch13_specs.json")
json.dump(specs, open(outp, "w"), indent=1)
print(f"Wrote {len(specs)} specs to {outp}")
for s in specs:
    lin = s.get("lin_terms", s.get("rots"))
    print(f"  {s['name']}: pattern={s['pattern']} lin={lin}")
