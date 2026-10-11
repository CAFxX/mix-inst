# fast_battery — FAST STAGED screening pipeline for the RV64 `mix` search

Motivation: h_xorspn3 burned a full finalist battery (hours of P&R + full
batteries) before PractRand killed it at 16MB. Cheap tests run first with
early termination; expensive validation (P&R, peer review) only for survivors.

## Stage order (cheap kills first)

| Stage | What | Kill rule | Cost |
|---|---|---|---|
| xcheck | C `impl.c` vs Python `model.py`, 10k random vectors | any mismatch = infra FAIL | seconds |
| S0 | Yosys/ABC unit-delay probe on `rtl.v`; mapped-netlist equivalence check (iverilog, 1000 vectors vs Python model) | delay > 0.9x multiplier, or any equiv mismatch | ~1.5 min (ref cached) |
| S1 | amended 4-family screen: marginal 468-cell (PB+RD) + LIN (binary rank) + DIFF (truncated chi2), 10 keys | any Holm-Bonferroni rejection in any family (FWER ≤0.04) | minutes |
| S2 | differential early-kill in C, N=2^22, 74 deltas | max full-64-bit output-difference repeats > 1000 | seconds–min |
| S3 | PractRand piped `RNG_test stdin64`, incremental 16MB→64MB→256MB→1GB + one strided class | first FAIL | sec–low min |
| S4 | TestU01 SmallCrush (golden-checked build) | any p outside [1e-3, 1-1e-3]-ish crush bounds | minutes |
| S5 | P&R + peer review | MANUAL GATE ONLY — not automated (see below) | hours |

## S5: Sky130 place-and-route (manual gate)

S5 runs identical-condition Sky130 P&R (A/B against the reference) for
validated leaders only, on the parent's explicit go-ahead — it is not part
of the automated battery. Procedure and sign-off criteria are defined when
the gate is armed.

**Layout visualization (Carlo 2026-10-04, requirement):** every design that
survives P&R gets a visualization of the resulting placed-and-routed layout
as **SVG (vector, not raster)**. Planned implementation: parse the OpenROAD
DEF output and render a die plot — standard-cell placements as rectangles
colored by functional block (S-box lanes, linear layer, key schedule),
with P-box nets highlightable and the **input (`val`, `key`) and output
(`out`) wires highlighted** (Carlo 2026-10-04). This is also the instrument
that makes the wire-friendly P-box track's proxy wirelength (Σ|P(i)−i|)
visually checkable against real routed wirelength. The renderer is built
when S5 is armed, not before (no P&R output exists yet to render).

Orchestrator: `./run_fast_battery.sh <candidate> [start_stage]`.
Per-stage verdict + wall-clock go to `results/<candidate>/`; stops at the first
kill. Exit 0 = all pass, 2 = killed, 1 = infra error.

## Thresholds and calibration

- **S0 bar: delay ≤ 0.9 × the 64×64 multiplier**, both synthesized through the
  identical flow (multiplier measured once, cached in `ref/mult_ref.txt`).
  The user's hard requirement is "latency no higher than a multiplier"; the old
  absolute 44.3u bar belonged to a retired flow (see below) and is not used.
- **S2 kill threshold: 1000 full-64-bit repeats** (`ref/s2_kill_repeats.txt`).
  Null expectation at N=2^22 (≈2^21 deduped pairs) is C(2^21,2)/2^64 ≈ 2^-23,
  so any repeats are real signal; r3_xorlin_qm (standing winner) measures 12,
  h_xorspn3 measured 41889. 1000 sits ~83× above the best known-good design
  and ~42× below the known-catastrophic one. S2 reports (not kills on) weak
  statistical signals — flagging is S1's DIFF family job.
- **S1**: CAL_PASS iff zero Holm-Bonferroni rejections across all four
  families (PB, RD, LIN, DIFF) at α=0.01 each.

## S0 flow notes (read this before trusting a delay number)

The installed yosys 0.69+ (conda-forge, post-reboot reinstall) **dropped the
`abc -fast` option** the historical flow used, and its **default `abc` script
contains `dretime`, which was PROVEN on 2026-10-01 to produce a functionally
WRONG mapping** for `mix_h_xorspn3` (SAT miter pre-ABC vs post-ABC: concrete
counterexample; iverilog confirmed the mapped netlist computes wrong values;
pre-ABC netlist verified correct). S0 therefore uses an explicit ABC script,
`src/abc_nodretime.script` (= the built-in default with `dretime` removed;
the no-dretime mapping was SAT-proven equivalent: "no model found: SUCCESS").
Pass it via `-script <file>` — the `-script +cmd1,cmd2,...` string form does
NOT work in this build (commands aren't separated; ABC emits unmapped `$lut`
cells).

Because the synthesis flow changed, absolute unit-delays are NOT comparable
with the historical `-fast` numbers (hx 34.5u, r3 40.0u, mult 50.8u). The
ratio bar keeps S0 honest across flows.

S0 also simulates the ABC-mapped netlist (iverilog + `src/cells_sim.v`,
behavioral models of every mini.genlib cell, themselves exhaustively tested)
on 1000 random vectors against the Python model. A synthesis miscompile can
never pass as a fast design. **Project-wide warning**: any synthesis run on
this VM using default `abc` (with `dretime`) should be considered suspect
until re-verified — this includes re-runs of historical flows.

## Measured wall-clock on this VM (2026-10-01)

h_xorspn3 (killed at S2 as expected):
- xcheck 10000/10000, S0 32.9u / 4286 cells / 0.318×mult / equiv 1000/1000 PASS (~1.5 min incl. one-time 45 s ref)
- S1: (see results/h_xorspn3/)
- S2: KILL in ~3.5 s (δ=0x400, repeats=41889 > 1000)

r3_xorlin_qm:
- xcheck 10000/10000, S0 34.3u / 6798 cells / 0.331×mult / equiv 1000/1000 PASS
...[truncated 1758 chars]
