# Peer review: `r3_xorlin_qm` synthesis / timing claims (round 3)

Reviewer: independent synthesis/timing reviewer (not the designer).
Date: 2026-10-01. Scope: timing claims only — statistical gates out of scope.
Design: [`rtl/r3/r3_xorlin_qm.v`](rtl/r3/r3_xorlin_qm.v) (4-round SPN, Quine–McCluskey-minimized PRESENT S-box).
Claims under review: **40.0 unit-delays = 0.787× the 64×64 multiplier, bar 44.3**;
**Sky130: 5.07 ns critical path, 0 violations @ 10 ns, 6883 cells, 0.410× area**.

All numbers below were independently reproduced by re-running the flow
([`exploration/run_synth.py`](run_synth.py) on [`rtl/r3/r3_xorlin_qm.v`](rtl/r3/r3_xorlin_qm.v)); the re-run netlist is
md5-identical to `results/r3/s_r3_xorlin_qm/_dut/mapped_r3_xorlin_qm.v`.

---

## 1. Unit-delay model & critical-path computation ([probe3_delay.py](probe3_delay.py) / [run_synth.py](run_synth.py))

**How it works** ([`exploration/run_synth.py`](run_synth.py), [`synth/mini.genlib`](../synth/mini.genlib), [`synth/analyze.py`](../synth/analyze.py)):

- Flow: Yosys `proc; opt; flatten; opt; techmap; opt` → `abc -fast -genlib mini.genlib`
  → `opt; clean` → mapped netlist (`[run_synth.py](run_synth.py):24-31`). Identical for DUT and reference.
- Per-gate delays come from the genlib PIN fields (max of rise/fall block delay),
  [`synth/mini.genlib`](../synth/mini.genlib):
  INV/BUF 1.0, NAND2/NOR2 1.0, NAND3/NOR3 1.2, NAND4/NOR4 1.4, AND2/OR2 1.5,
  AOI21/OAI21 1.5, AND3/OR3 1.7, AND4/OR4 1.9, XOR2/XNOR2/MUX2 2.0.
  (Note: these are the PIN delays, *not* the GATE area numbers in column 2 —
  e.g. AND2 delay is 1.5, area 3. A reader confusing the two would compute 92.0,
  not 40.0.)
- **Fanout costs zero**: every PIN line's fanout-delay fields are 0
  (`mini.genlib`, e.g. `PIN * NONINV 1 999 1.5 0 1.5 0`). There is no wire-load
  model. All top-level inputs arrive at t=0; crit = max arrival over outputs.
- Critical path is the **exact longest topological path** (memoized DFS,
  [`synth/analyze.py`](../synth/analyze.py)), cross-checked by a second independent analyzer
  ([`exploration/analyze2.py`](analyze2.py)); `[run_synth.py](run_synth.py):43-46` aborts unless both agree
  bit-exactly. It is not a heuristic — it *is* the true critical path **under
  this model**. The limitation is the model, not the path search.

**Independent re-run** (Yosys 0.69 from [`exploration/bin`](bin/)):
`REF mul64: cells=17893 area=46073 crit=50.8` /
`DUT r3_xorlin_qm: cells=6883 area=18910 crit=40.0` /
`delay_ratio=0.787 area_ratio=0.410`. Reproduces the claimed numbers exactly.
Baseline [`rtl/spn4_xorlin_1137.v`](rtl/spn4_xorlin_1137.v) re-run: 44.8 / 7360 cells / 21568 area —
the 44.8 → 40.0 (4.8u) saving is real under identical conditions.

Extracted true critical path (my own trace of the mapped netlist, consistent
with [analyze.py](../synth/analyze.py)'s 40.0): **30 gates**, mix
XNOR2×1, XOR2×1, NOR4×6, NAND3×3, NOR2×8, OAI21×4, AOI21×4, NAND4×2, NOR3×1 —
i.e. ABC mapped the QM SOP into inverting CMOS-style gates, not a literal
AND-OR plane. No deep XOR tree on the path (only 2 XOR-class gates, at the
path start).

## 2. The 50.8 reference and the 44.3 bar

- The reference is [`synth/mul64.v`](../synth/mul64.v): behavioral `assign p = a * b` (64×64
  variable multiplier), mapped by **ABC's own internal multiplier**
  implementation. `[run_synth.py](run_synth.py):32` re-measures it fresh inside every
  invocation, so DUT and reference always share tool version and flow —
  apples-to-apples *within* a run.
- [`exploration/gen_wallace.py`](gen_wallace.py) is a **constant**-multiplier (CSD/Wallace)
  generator used in a separate experiment; it is **not** the 50.8 reference
  and should never be cited as its source.
- 49.2 → 50.8 drift is the Yosys 0.33 → 0.69 (ABC version) change in how `*`
  is mapped (`[candidates.md](candidates.md):103`, 3.3% drift). The bar 44.3 = 0.9 × 49.2 is
  kept as an absolute bar, which is *stricter* than 0.9 × 50.8 = 45.72 —
  conservative, consistently applied (`[candidates.md](candidates.md):139-141`: "Absolute bar
  kept at 44.3 (conservative)"). Usage is consistent: verdicts vs absolute
  44.3, ratios vs 50.8. 40.0 clears the bar by 4.3u (9.7% margin).
- Caveat (their own, `[candidates.md](candidates.md):103`): ABC `-fast` does no Booth/CSD
  recoding and maps multiplier adder structure naively, so the reference is
  slower (and bigger) than a production Booth–Wallace multiplier. The 0.787
  ratio is therefore a **flow-relative screening number, not a silicon
  prediction** — it flatters the DUT against what a real multiplier achieves.

## 3. Glitch / hazard / structural optimism

- **Glitch power**: the QM-minimized SOP is mapped by ABC into multi-level
  NAND/NOR/AOI logic (histogram: NAND2 999, NOR2 1238, NAND3 1220, NOR3 1092,
  AOI21 532, OAI21 539, …). Multi-level logic glitches more than a literal
  2-level AND-OR plane, so dynamic power will be higher than the gate count
  alone suggests. This does **not** lengthen the worst-case path — STA covers
  all arcs regardless of hazards — so it is a power note, not a timing
  refutation. No functional hazard concern in a synchronous (registered
  pipeline) context.
- **Structural optimism — confirmed, one-directional**: the model charges 0
  for fanout, and the DUT's critical path is the one that leans on it.
  Measured on the mapped netlists:
  - `r3_xorlin_qm`: max fanout overall 14; **on the critical path** nets with
    fanout 11, 12, 13, 14 (4 nets ≥ 8 on-path); 629 nets ≥ 8 overall.
  - `mul64` reference: max fanout overall 76, but **max fanout on its
    38-gate critical path is only 4** (11 NOR2, 7 AOI21, 7 OAI21, 4 XOR2…).
  - In any slew/load-dependent model the DUT's path degrades
    disproportionately: the 40.0 number is optimistic *relative to the
    reference*. This is the strongest structural reason the 0.787 ratio
    overstates the silicon advantage.
- **No deep-XOR-tree concern**: only 2 XOR-class gates on the crit path; the
  2.0u XOR cost is not a driver of optimism here.

## 4. Sky130 placement + STA ([`pnr_sky130.sh`](pnr_sky130.sh), `results/r3/pnr_qm/`)

- Synthesis leg is proper: Yosys `abc -liberty` against the real
  `sky130_fd_sc_hd__tt_100C_1v80.lib` ([`pnr_sky130.sh`](pnr_sky130.sh)).
- **No routing was performed.** The script runs global + detailed placement,
  then `write_def`; global/detailed routing are skipped (tech-LEF TRACKS gap,
  [`pnr_sky130.sh`](pnr_sky130.sh) comments). `timing.rpt` therefore has pin-cap loads but
  **no wire parasitics**, ideal (0) input slews, and 0 input/output delays.
  5.07 ns (key[8] → out[39]) is a **lower bound** for routed silicon —
  expect roughly +10–25% with real wires at this size, plus IO/clock reality.
- **"0 violations at 10 ns virtual clock" is vacuous as a closure claim.**
  Constraints: `create_clock -period 10000`, `set_input_delay 0`,
  `set_output_delay 0`. Slack is 9994.93 ps simply because 10 ns ≫ 5.07 ns
  (`timing.rpt`: arrival 5.0703, required 10000.0, tns/wns 0.00). This proves
  the design meets 100 MHz — unsurprising — not that it is timing-closed
  anywhere near its fmax. The informative datum is the 5.07 ns placed arrival
  itself.
- `results/r3/pnr_mul64/` is **empty** — the multiplier P&R was never completed
  (ABC blowup on the 64×64). There is no silicon-side counterpart to the
  0.787 ratio; the ratio exists only inside the unit-delay model.

## 5. Area

- 6883 cells / area 18910 vs reference 17893 / 46073 → area ratio
  18910/46073 = 0.410 ✓, computed in identical flow and library
  (`mini.genlib` area column) — apples-to-apples within the flow, same
  production-flow caveat as delay. (0.410 is the *area* ratio; the cell-count
  ratio is 0.385. The claim states "0.410x multiplier area" — correct as
  worded.)
- Predecessor `spn4_xorlin_1137`: my re-run gives 7360 cells (memory notes said
  7450 — trivial discrepancy, immaterial).

---

## Findings by severity

- **Major — fanout-blind model flatters the DUT asymmetrically.** The DUT's
  30-gate critical path drives fanout-11/12/13/14 nets; the multiplier
  reference's 38-gate critical path never exceeds fanout 4. The unit-delay
  model charges 0 for fanout ([`synth/mini.genlib`](../synth/mini.genlib) PIN fanout-delay fields all
  0), so 40.0 is optimistic relative to the 50.8 it is divided by. True
  silicon ratio is worse than 0.787 by an unquantified amount.
- **Major — the reference is an ABC-naive multiplier, not a production one.**
  ABC `-fast` does no Booth/CSD recoding (`[candidates.md](candidates.md):103` acknowledges
  this class of overpricing); a real 64×64 multiplier would be faster and
  smaller than 50.8u / 46073, pushing the true ratio further above 0.787.
  Both biases point the same way.
- **Major — Sky130 "0 violations at 10 ns" misframes the result.** The design
  was constrained at 10 ns with ideal IO; 5.07 ns placed arrival trivially
  passes. No routing was done (unrouted → no wire RC, optimistic), and
  `results/r3/pnr_mul64/` is empty, so no placed multiplier exists for
  comparison. The honest statement: "placed, unrouted STA gives 5.07 ns
  (TT/100C/1.8V), a lower bound; physical feasibility demonstrated, not
  timing closure."
- **Minor — [`gen_wallace.py`](gen_wallace.py) is not the reference.** It generates
  constant-multiplier RTL for a separate experiment; the 50.8 number comes
  from behavioral [`synth/mul64.v`](../synth/mul64.v) via ABC. Keep the provenance straight in
  write-ups.
- **Minor — predecessor cell count.** `spn4_xorlin_1137` measures 7360 cells
  in the current flow, not 7450. Immaterial to the verdict.
- **Info — glitch power, not delay.** QM SOP → multi-level NAND/NOR/AOI
  glitches more than 2-level AND-OR; expect higher dynamic power. No
  worst-case-delay or functional impact under STA / registered use.
- **Info — bar conservatism.** Keeping the absolute 44.3 bar (0.9 × old 49.2)
  instead of 0.9 × 50.8 = 45.72 is stricter; the 4.3u margin is genuine
  within the model.

## Verdict

**The "40.0 unit-delays, 0.787× the multiplier, comfortably under the 44.3
bar" claim is SOLID as a flow-relative screening result**: independently
reproduced bit-exactly (md5-identical netlist), exact (non-heuristic)
critical-path computation cross-checked by two analyzers, reference
re-measured fresh in the same run, conservative absolute bar, 9.7% margin,
and the 44.8 → 40.0 improvement over the baseline verified under identical
conditions.

**It is NOT solid as a silicon prediction**, and the headline ratio should
not be quoted as one: (1) the fanout-free delay model favors the DUT's
critical path over the reference's by construction; (2) the reference
multiplier is ABC-naive, slower/larger than a production Booth–Wallace
implementation; (3) the Sky130 corroboration is placed-only, unrouted
(optimistic lower bound), unconstrained near fmax, and has no multiplier
counterpart. None of this invalidates the bar pass — the bar is itself a
flow-relative construct and the margin is comfortable — but the *true*
silicon delay ratio is strictly worse than 0.787 by an amount that cannot be
determined without a routed P&R of both designs (or at least a
fanout/wire-aware model applied to both).

Recommended follow-ups (for the parent, not this review): complete the
`pnr_mul64` P&R for a silicon-side ratio; re-run both through the unit-delay
flow with a fanout-penalty variant of `mini.genlib` as a sensitivity check;
when quoting, say "0.787× under the ABC/mini.genlib screening model" rather
than "0.787× the multiplier".
