# S5 GATE REPORT — r22c vs multiplier, Sky130 P&R (identical conditions)

**Date:** 2026-10-04  
**Status:** GATE PASSES — r22c delay 4.41ns ≤ mult delay 12.80ns (0.344×)

## 1. Methodology (identical conditions)

Both designs run through the SAME flow:
- **Synth:** yosys 0.69 → sky130_fd_sc_hd structural netlist (ABC mapped)
- **Equivalence:** 20k random vectors, RTL vs mapped netlist (both PASS)
- **Floorplan:** 40% utilization, 1:1 aspect, unithd site
- **Place:** RePlAce global + detailed placement
- **Route:** Global route + Steiner parasitic estimation (detailed routing infeasible on loaded VM — 35min for 10% of r22c; see §5)
- **Timing:** Virtual 20ns clock, 0.5ns in/out delays; achieved_delay = 19.0 − worst_slack
- **SDC:** `flow/constraints.sdc` (identical for both)

## 2. Delay (the hard requirement)

| Design | Worst slack | Achieved delay | Status |
|--------|-------------|----------------|--------|
| r22c_spn_mix4r_lp_nw | 14.5907 ns | **4.41 ns** | MET |
| mul64 (64×64 ref) | 6.2019 ns | **12.80 ns** | MET |

**Ratio: 4.41 / 12.80 = 0.344×**  
**Requirement: delay ≤ multiplier → PASS** (S0 unit-delay showed 0.273×; silicon shows 0.344× — same order, both well under 1.0)

Critical path r22c: key[5] → out[35] via XNOR2/NOR3/AOI chain (4.91ns arrival).  
Critical path mult: b[4] → p[63] (13.30ns arrival).

Evidence:
- r22c: `s5_r22c/r22c/reports/timing_max_global.rpt`
- mult: `s5_r22c/mult/reports/timing_max_global.rpt`

## 3. Area / Power / Utilization

| Design | Cells | Die | Power | Utilization |
|--------|-------|-----|-------|-------------|
| r22c | 1,459 | 171.1×171.1 µm (29,266 µm²) | 27.4 mW | 40% |
| mult | 9,639 | 409.5×409.5 µm (167,658 µm²) | 50.8 mW | 40% |

r22c is 6.6× smaller in cell count, 5.7× smaller in die area, 1.85× lower power.

Evidence:
- r22c: `s5_r22c/r22c/reports/power_global.rpt`, `s5_r22c/r22c/placed.def`
- mult: `s5_r22c/mult/reports/power_global.rpt`, `s5_r22c/mult/placed.def`

## 4. SVG Layout Visualizations

**r22c:** `s5_r22c/reports/r22c_layout.html` (446KB)
- 3,579 cells colored by functional block (structural attribution):
  - **SBOX** (orange, 1,223): nonlinear cells (AND/OR/NAND/NOR/AOI/OAI)
  - **LIN** (blue, 101): linear-layer XORs reaching PO/TXOR
  - **TXOR** (purple, 135): round-input XORs (x^rk, one key-only input)
  - **KEY** (green, 0): key schedule (absorbed into XNOR2s by ABC — 0 standalone cells)
  - **FILL** (grey, 2,120): filler/tap/decap
- P-box nets (123) highlightable via toggle
- val/key/out pins highlighted (toggle)
- Pan/zoom, block visibility toggles, legend

**mult:** `s5_r22c/reports/mult_layout.html` (2.9MB)
- 9,639 cells (grey, `--plain` mode — no SPN blocks for multiplier)
- Pins highlighted

**Renderer:** `s5_r22c/def2svg.py` (475 lines)
- Parses LEF (cell sizes), DEF (placement), structural Verilog (block attribution)
- Block attribution is STRUCTURAL (PI-support analysis), not name-based — internal RTL names don't survive yosys+ABC
- Methodology documented in module docstring

## 5. Wirelength: Proxy vs Routed Reality

**Proxy (pre-layout, parent-measured):** Σ|P(i)−i| = 1450 bit-pitches (avg 22.66, max 57)

**Routed (HPWL from placement, measured):**
| Metric | All nets (1,587) | P-box nets (123) | Ratio |
|--------|------------------|------------------|-------|
| Total HPWL | 44,514.6 µm | 7,325.8 µm | — |
| Avg HPWL | 28.05 µm | **59.56 µm** | **2.12×** |
| Max HPWL | 226.67 µm | 123.30 µm | — |

**Finding:** P-box nets (structurally identified as S-box outputs leaving the S-box cone) average **2.12× the HPWL of typical nets**, confirming the proxy's prediction that P-box wires are the long global routes. The 123 P-nets carry 16.5% of total wirelength (7,326 / 44,515 µm) despite being only 7.7% of nets.

**Caveat:** HPWL from placement, not detailed-routed wirelength (detailed routing infeasible — see below). HPWL is a standard pre-route estimator, typically within 10-20% of routed length.

**Detailed routing status:** Attempted but infeasible on the loaded VM (load avg 9.29). TritonRoute detailed routing: 35min for 10% of r22c at 55% utilization (stuck at 60% with 4,147 violations after 77min); restarted at 40% utilization, still 25min for 10%. Killed. **DRC-clean status: NOT VERIFIED** (requires detailed routing). The delay/power numbers above use global-route + Steiner estimation, which is the standard fast path for pre-DRC timing closure.

## 6. Equivalence Gates (both PASS)

- r22c: `s5_r22c/r22c/equiv_result.txt` — EQUIV-PASS 20000/20000
- mult: `s5_r22c/mult/equiv_result.txt` — EQUIV-PASS 20000/20000

## 7. Files & Evidence

```
s5_r22c/
├── def2svg.py              # DEF→SVG renderer (475 lines)
├── wirelength.py           # HPWL analysis script
├── flow/                   # OpenROAD flow scripts
│   ├── run_s5.sh           # Driver (checkpoint-based, fails hard)
│   ├── s0_ysynth.ys.tmpl   # Yosys synth template
│   ├── s1_link.tcl         # Link
│   ├── s2_floorplan.tcl    # Floorplan (40% util)
│   ├── s3_place.tcl        # Placement
│   ├── s4b_global.tcl      # Global route + estimation (fast path)
│   ├── s5_reports.tcl      # Final reports
│   ├── constraints.sdc     # Identical SDC for both
│   ├── equiv_r22c.sh       # r22c equivalence
│   └── equiv_mult.sh       # mult equivalence
├── r22c/                   # r22c design checkpoints
│   ├── ysynth.v            # Mapped netlist (1,459 cells)
│   ├── placed.def          # Placed (40% util)
│   ├── global_routed.def   # Global routed
│   ├── reports/            # Timing/power reports
│   └── equiv_result.txt    # EQUIV-PASS
├── mult/                   # Multiplier checkpoints (same structure)
└── reports/
    ├── r22c_layout.html    # SVG visualization (446KB)
    └── mult_layout.html    # SVG visualization (2.9MB)
```

## 8. Limitations & Follow-ups

1. **DRC not verified:** Detailed routing infeasible on current VM load. If DRC-clean status is required, re-run `s4_route.tcl` on an unloaded machine.
2. **Wirelength is HPWL, not routed:** Standard pre-route estimator; detailed routes would refine by ~10-20%.
3. **Utilization changed 55%→40%:** Initial 55% caused routing congestion (4,147 violations). Both designs at 40% for identical conditions.
4. **Mult block attribution:** Multiplier has no SPN structure; SVG uses `--plain` mode.

## Verdict

**S5 GATE: PASS.** r22c achieves 4.41ns vs multiplier 12.80ns (0.344×) under identical Sky130 P&R conditions. The ≤multiplier hard requirement is met with 2.9× margin. No frontier reopening.
