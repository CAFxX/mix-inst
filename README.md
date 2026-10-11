# mix — RV64 `mix` instruction design

Design of a custom RISC-V instruction `mix rd, rs1, rs2` (custom-0 encoding):
a deterministic 64-bit hash-map finalizer, searched against a staged
validation battery with adder-like latency as the goal.

## Layout

- `isa_spec.md` — instruction specification.
- `mix64.py`, `spn.py` — reference models.
- `rtl/` — RTL for frontier designs.
- `synth/` — synthesis flow (pinned Yosys 0.69; `run_synth.py` is the only
  authorized path to delay/area numbers).
- `exploration/` — the open-ended design search: `PARETO.md` is the live
  frontier record, `LEADS_LEDGER.md` the leads ledger, `VERDICT_SCOPE.md`
  the verdict-scoping rules, `RETAINED.md` the registry of every design
  that ever passed the full battery.
- `exploration/fast_battery/candidates/` — candidate bundles (RTL, model,
  metadata) for the designs under test.
- `tests_*.py` — test suites.

## Validation method

Staged kill-chain, cheapest first: (S0) unit-delay synthesis probe →
(S1) fast statistical screen → (S2) differential early-kill → (S3)
PractRand incremental → (S4) TestU01 SmallCrush → Q1 spot check
(sac_z5 = 0 mandatory for frontier claims). The current frontier and its
evidence are in `exploration/PARETO.md`.

## Sync note

This repository is a mirror of the local working tree, pushed via the
Git Data API (`push_mix.py`) and kept up to date by a recurring sync.
Excluded from the mirror, by the same rationale as `.gitignore`: bulk
battery outputs under any `results/` directory and compiled simulation
binaries — both are regenerable from the checked-in generators and
candidate bundles.
