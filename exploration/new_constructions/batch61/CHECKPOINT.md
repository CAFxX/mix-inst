# Batch-61 CHECKPOINT — resume instructions

**Axis:** muxD5f-local2 — m~U{1,2,3} perturbation around t6_b59_47
(18.6u frontier) + t6_b60_27 (18.7u best b60 keep). Fisher-matched
triage. Strict S0 bar <18.6u.

## Pipeline state

- [x] Pre-pilot (12 draws, seed 0xB611): COMPLETE 04:01:52Z — 6/12 KEEP minz=2.2
- [x] Pilot (80 draws, seed 0xB612): COMPLETE 04:08:41Z — **57/80 KEEP minz=2.2** (`pilot_keeps.jsonl` = 57 lines)
- [x] Bundles: `gen_b61_bundle.py` (b57-adapted, b61 screener cross-check); all 57 ranks bit-exact (2000/2000 C-vs-Python + 500/500 screener-vs-bundle)
- [x] S0: `run_b61_s0.sh` ranks 0..56 COMPLETE 04:46:51Z (`s0_all.log`;
  ref mul64 103.5u stable, XCHECK clean). 3 cost-eligible (strict <18.6u):
  t6_b61_56 18.3u/5262/17260 (z=2.499), t6_b61_24 18.5u/6948/22904 (z=2.794),
  t6_b61_38 18.5u/6344/20544 (z=3.090). 54/57 S0-doomed (18.6u t6_b61_32
  to 20.1u t6_b61_23).
- [x] Battery (z-order, `run_b61_battery.sh`, setsid nice-19): t6_b61_56
  **S1-KILLED** (inner calibrated DIFF-SEQ gate CAL_FLAG, rej
  0xffffffffffffffff + 0xaaaaaaaaaaaaaaaa, worst|z|=4.92); t6_b61_24
  **S1-KILLED** (RD rej=1, SEQ all-ones key); t6_b61_38 S1 CAL_PASS,
  S2 PASS (max|z|=415.3), **S3-KILLED** @1GB [Low1/64]Gap-16:A p=1.0e-17.
- [x] Verdicts: **O126 batch-61 COST-TERMINAL** (VERDICT_SCOPE.md);
  ledger prepended 07:35 CEST. No PARETO/RETAINED/RTL change (no
  challenger). Frontier unchanged: t6_b59_47 18.6u speed; t6_b59_41
  19.0u delay; t6_b59_0 19.1u cells/area; t6_b57_8 area; hyb28_mu5_324
  cells/area.

## Resume

Pre-pilot and pilot are resumable via JSONL checkpoints: re-running
with the same seed reproduces the draw sequence; skip already-recorded
tries by counting lines in the keeps file (all tries print to stdout —
check the log for the last completed try number).

## Runners

- `run_b61_prepilot.sh` / `run_b61_pilot.sh`: cleared-flag backoff
  pattern (see batch59 runners). Launch via
  `setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 --tag track6/b61-<stage> -- ...`
- Heartbeat: touch `heartbeat.txt` every ~20 min while live.
