# Batch-62 CHECKPOINT — resume instructions

**Axis:** weakness-gated local — m~U{1,2,3} perturbation around
t6_b59_47 (18.6u frontier, the single proven-clean basin center),
triaged by the failing instruments themselves: fisher + inner
DIFF-SEQ/LIN gate (screen_lindiff, the t6_b61_56 killer) + RD-SEQ
reduction gate (the t6_b61_24 cell class) + Low1/64 PractRand
prescreen at 256MB (the t6_b61_38 killer). Strict S0 bar <18.6u.
DESIGN.md (sibling) was written BEFORE any run; it carries the
failure-signature characterization and pre-registered rules.

## Pipeline state

- [ ] Pre-pilot (12 draws, seed 0xB621): calibration (CALIB-1..4c)
      + selftest + draws. Log: `prepilot.log`, keeps: `prepilot_keeps.jsonl`.
- [ ] Pilot (80 draws, seed 0xB622): log `pilot.log`, keeps `pilot_keeps.jsonl`.
- [ ] Bundles: `gen_b62_bundle.py` (b61-adapted); bit-exact 2000/2000
      C-vs-Python + 500/500 screener-vs-bundle per keep.
- [ ] S0: `run_b62_s0.sh` (run_synth.py, strict <18.6u, ref mul64
      103.5u, XCHECK). Log `s0_all.log`.
- [ ] Battery: cost-eligible keeps in z-order, `run_b62_battery.sh`
      (start_stage=1) → S1→S2→S3→S4 → Q1 (sac_z5=0 mandatory).
- [ ] Verdicts: O127+ in VERDICT_SCOPE.md; ledger prepended;
      PARETO/RETAINED/RTL only on a full-pass (S0-S4+Q1 sac_z5=0)
      challenger, adjudicated from raw files.

## Resume

Pre-pilot and pilot are resumable via JSONL checkpoints: re-running
with the same seed reproduces the draw sequence; skip
already-recorded tries by counting lines in the keeps file (all tries
print to stdout — check the log for the last completed try number).
The PractRand prescreen compiles a per-try gen binary into
`build_prescreen/` (idempotent; safe to re-run).

## Runners

- `run_b62_prepilot.sh` / `run_b62_pilot.sh`: cleared-flag backoff
  pattern (see batch61 runners). Launch via
  `setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 --tag track6/b62-<stage> -- ...`
- Heartbeat: touch `heartbeat.txt` every ~20 min while live.
- Never two workers on one candidate: check `pgrep -f track6/b62`
  and heartbeat.txt mtime before relaunching.
