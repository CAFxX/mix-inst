# Track-3 supervisor — resume note (wave-14 pivot)

Written 2026-10-11 ~01:15 CEST by the respawned track-3 supervisor.
Updated 2026-10-11 05:35 CEST by the new incarnation (VM rebooted ~02:59:50Z).
Updated 2026-10-11 05:47 CEST by the newest incarnation (predecessor AGENT
errored 03:43:16Z — runtime hiccup; the screen itself never died).
Updated 2026-10-11 ~08:55 CEST by the post-05:24Z-reboot incarnation
(screen completion + S0 + battery launch; supersedes the 05:47 state).

## CURRENT STATE (08:55 CEST, verified from raw)

- **SCREEN COMPLETE 602/602.** The original run died in the 05:24Z reboot
  at 557/602. Completed DEDUP-SAFELY by `finish_screen.py`: regenerated
  the deterministic task list, subtracted tags present in
  work/screen_wave14.jsonl (602 unique tags asserted), ran ONLY the 45
  missing (all W3) into the SEPARATE work/screen_wave14_rest.jsonl.
  Original JSONL never appended to. Totals: 133 KEEPs, 0 errors.
- **W1: 0/402 KEEPs, min z_seq = 676.6** (68× over the KEEP bar).
  ADJUDICATION: scoped empirical kill of the 402 screened W1 schedules
  ONLY (400 random + 2 hand, seeds 0x714E). NO family-level claim —
  verdict-scope rules; a co-designed (non-random) W1 schedule search
  remains a possible future re-test, not scheduled.
- **W3: 133/200 KEEPs (66.5%)** — the perfect-diffusion hypothesis is
  strongly supported at exact-DIFF triage level. Best max(z_seq,z_rnd)
  = 2.52. Hill-climb phase of the original script DELIBERATELY NOT RUN:
  with 133 KEEPs at z≈2.5 (bar <10), hill-climbing could only refine z,
  which is not the binding constraint; the escalation need is saturated.
  Recorded decision, not a silent gap.
- **Harvest → bundles (bit-exact verified)**: best-z member per
  structural class (stages, ANDs): al_w3a (3,3) z 2.52; al_w3b (2,4)
  z 2.54; al_w3c (2,4, 2nd P) z 2.63; al_w3d (2,2) z 7.00 minimal-AND
  probe. Class (3,6) not bundled: same stages as (3,3), strictly more
  ANDs, best z 2.71 > 2.52 — cost-dominated (cut reason recorded in
  gen_wave14.py). Verification: bundle model == screen w3_form
  (2000 vec × 3 keys); C == Python (200 random vectors); goldens in meta.
- **S0 (run_synth.py, XCHECK clean, ref mul64 103.5u) — ALL under the
  123.4u adder-like bar**: al_w3d 27.7u (cells 11281), al_w3c 31.9u
  (13930), al_w3b 34.6u (10717), al_w3a 41.8u (16571). All above the
  19.8u frontier (t6_b33c) — wave-14's mission is the adder-like bar,
  so all four are COST-ELIGIBLE for the staged battery.
- **Battery IN FLIGHT**: `run_battery_w3.sh` (tag track3/w14-battery,
  backoff-gated) runs run_fast_battery.sh START=1 for al_w3c → al_w3b;
  `run_battery_w3_wave2.sh` (tag track3/w14-battery2) waits for wave-1
  completion, then al_w3d → al_w3a. Logs: work/battery_w3.log,
  work/battery_w3_wave2.log; verdicts land in fast_battery/results/.
  NOTE: battery START=1 skips its internal S0 (frontier bar ≤0.9×mul is
  NOT the wave-14 gate; S0 adjudicated separately above). Q1 follows
  for any S1–S4 survivor per the b33 playbook.
- **Next**: harvest battery verdicts from fast_battery/results/*/battery.log;
  S1 inner-DIFF opacity lesson (track-5, 08:04 ledger): a FLAG with empty
  cells needs a verbose inner probe before adjudication. Frontier
  unchanged: t6_b33c 19.8u.

## PRIOR STATE (05:47 CEST, verified from raw)

- **Family verdicts RE-VERIFIED** by independent recomputation from
  work/calib.json: W1 COMMIT (2st~55/3st~84 < 123.4 bar), W2 KILL
  (2st~192; ideal-CSA floor ~170 > bar), W3 COMMIT (2st~35), W4 KILL
  (mul16 51.9 = 6.5× the <8u bar). All confirmed; see HB 03:47Z.
- **Screen ALIVE, do NOT relaunch**: parent pid 3837 + workers
  3886/3887/3888 (STAT=RN, nice-19). wave14_screen.py has NO resume/dedup
  (regenerates all 602 tasks from seeds 0x714E/0x314159, appends blindly) —
  a relaunch would duplicate work and corrupt the JSONL. The run covers
  W1 AND W3 in one task list (402 W1 first, then 200 W3).
- **GATE 0 canaries re-verified from this run's log**: 71.4 KILL / 3.0 KEEP
  / 3.2 KEEP, exact.
- **Progress**: 289/602 at 03:47Z, all W1, 0 KEEPs, 0 errors,
  min z_seq = 676.6 (W1 random schedules catastrophically seq-killed;
  W3 block not yet reached). Workers CPU-starved (box load ~13.9);
  ETA ~35-40 min for the remainder. Waiter armed on pid 3837.
- **/tmp blocker RESOLVED** (1% used) — S0 path clear when KEEPs land
  (TMPDIR=work/tmp in run_calib.py remains a harmless belt-and-braces).
- **Next**: at screen completion → harvest KEEPs → S0 via authorized
  run_synth.py (cost bar < 123.4u MEASURED) → staged battery
  S1→S2→S3→S4→Q1 (b33 playbook). If W1 finishes 0/402 with min-z in the
  hundreds, adjudicate as scoped empirical kill of screened W1 schedules
  (verdict-scope rules) before any terminal family claim.

## Settled state (do NOT redo)

- **Wave-14 calibration: COMPLETE + CONSUMED** (work/calib.json, 9 primitives,
  XCHECK-clean, ref mul64 103.5u): add64=82.3u, add32x2=43.4u, add16x4=23.0u,
  add3=94.4u (+12.1u/op), add4=101.3u (+19.0u), mul16=51.9u, mul32=92.2u,
  mulc64=87.0u, gf64=15.9u. Final run: calib6.log DONE 02:41Z.
- **Family verdicts (2026-10-11 05:35 CEST, in wave14_design.md):**
  W1 COMMIT (adder-like flagship; sub-frontier math falsified),
  W2 KILL (cost-terminal), W3 COMMIT (perfect-diffusion lead),
  W4 KILL (contingency failed 6.5×). Wave-14 mission = adder-like bar
  (123.4u), NOT the 19.8u frontier (structurally out of reach on calib).
- **Wave-13 (4-bit-replacement axis): TERMINALLY CLOSED (VALID, cost).**
  Basis: sbox-cost sweep2 DONE 2026-10-10T21:13:49Z — all 7 pool S-boxes at
  pure-stage 3.5–5.0u (>3.3u bar). **Do NOT re-run the wave-13 triage.**
- **Frontier: t6_b33c 19.8u** (speed) / t6_b33b 20.1u (size). PARETO.md current.
- **Ledger**: wave-14 entry prepended 05:35 CEST (W1/W3 COMMIT, W2/W4 KILLED,
  screen launched, W3 first-blood lead opened).

## In flight (updated 05:35 CEST)

1. **Wave-14 screen RUNNING** (tag track3/w14-screen, nice-19, 3 workers):
   `wave14_screen.py` → work/screen_wave14.jsonl (JSONL checkpointing);
   log work/screen.log. 400 W1 + 200 W3 seeded schedules, exact-DIFF triage
   (triage_core, both domains, KEEP bar max|z|<10 sequential), then
   hill-climb (40 mutants/KEEP). Gate 0 exact canaries PASS (71.4/3.0/3.2);
   GF(2^64) vec==scalar self-test OK. ETA ~60–100 min. Launched 03:3xZ after
   backoff CLEAR (load 11.61 < 12).
2. **Early signal (smoke, pre-launch):** W3 first random draw KEEPs
   (seq z=2.7, rnd64 z=2.9; 2 stages, 2 ANDs/stage, P=0xBF58476D1CE4E5B9) —
   perfect-diffusion hypothesis supported on first contact. W1 hand schedule
   seq-killed z=1417 / rnd64-clean 2.5 — DIFF wall brutal for ARX lanes;
   sequential-primary rule confirmed again.
3. **Next:** harvest KEEPs from JSONL → S0 via authorized run_synth.py
   (cost-eligibility bar < 123.4u; TMPDIR=work/tmp workaround still set in
   run_calib.py — verify /tmp state before S0; global yosys flock inside
   run_synth.py, never parallel yosys outside it) → staged battery
   S1→S2→S3→S4→Q1 per the b33 playbook for survivors.

## Settled state (do NOT redo)

- **Wave-13 (4-bit-replacement axis): TERMINALLY CLOSED (VALID, cost).**
  Basis: sbox-cost sweep2 DONE 2026-10-10T21:13:49Z — all 7 pool S-boxes at
  pure-stage 3.5–5.0u (>3.3u bar). The dead triage (pid 34633, log mtime
  2026-10-10 22:04:52Z, last line `[dead] ORTHROS_S0 5st z=449.9`) was
  auxiliary differential evidence only — its death loses nothing
  verdict-relevant. **Do NOT re-run the wave-13 triage.**
- **Frontier: t6_b33c 19.8u** (speed) / t6_b33b 20.1u (size). PARETO.md current.
- **Ledger**: closure confirmed + wave-14 pivot opened in the 01:05 CEST entry
  (prepend-at-top convention). Heartbeat: new incarnation HB 23:05Z appended.

## In flight (updated 01:25 CEST)

1. **Calibration worker RUNNING** (pid 34969, tag track3/w14-calib, nice-19):
   `run_calib.py` → work/calib.json (9 word-level primitives via authorized
   run_synth.py); log work/calib.log (empty until first synth completes);
   ETA ~30 min. TMPDIR=work/tmp workaround active (yosys-abc-* temp dirs
   confirmed in use).
2. **Canary gate DONE — PASS** (01:18 CEST): as6_200_106 seq z=71.4 KILL
   (exact reproduction); t6_b33b seq z=3.0 KEEP (exact); al_and6a seq z=3.2
   KEEP. Harness (triage_core.py) trusted. Bonus finding: as6_200_106 is
   rnd64-clean (z=2.5) — the DIFF wall is invisible on random-64, confirming
   the wave-34 sequential-primary rule (recorded in wave14_design.md).

## BLOCKER (infrastructure, affects ALL tracks' S0)

`/tmp` (512M tmpfs) is **100% full** — filled in the last hour by sibling
graalgo scratch (exitrewrite-testcache*, gofrontend-*, elliptic_export.json).
Yosys ABC temp dirs die there → run_synth.py (the authorized S0 path) fails
for every track right now ("ERROR: ABC script did not complete successfully").

- Root cause identified, NOT yet fixed box-wide. Did NOT delete siblings'
  files (all created <63 min ago = live work; /tmp is tmpfs, cleared hourly
  by reboots).
- **Workaround applied for track-3**: run_calib.py sets
  `TMPDIR=<wave14>/work/tmp` (created). A Yosys ABC smoke test with that
  TMPDIR is running (session proc_5b8bf06d015f) to prove the workaround
  before re-launching the calibration worker.
- **Next**: if smoke passes → re-launch calibration worker (command above).
  Escalate the /tmp-full condition to the parent: needs a box-wide policy
  (sibling tmp hygiene or larger tmpfs), not a track-3 unilateral delete.

## Next steps (in order)

1. Confirm TMPDIR smoke test passes → re-launch calibration worker.
2. Collect canary results → harness trusted (or fix).
3. When work/calib.json lands: pick cost-viable families (W1 flagship;
   W2/W3/W4 contingent), write wave14_screen.py (W1 schedule screen, both
   domains, bar max|z|<10), launch via agentwork-launch nice-19.
4. S0 for cost-eligible KEEPs → staged battery for survivors.
5. Heartbeat every ~15 min to adder_lat/supervisor_heartbeat.txt.

## Key paths

- Design doc: ~/workspace/mix/exploration/adder_lat/wave14/wave14_design.md
- Calib RTL:   .../wave14/calib.v · driver .../wave14/run_calib.py
- Triage core: .../wave14/triage_core.py (canaries embedded)
- Triage method reference: ~/workspace/mix/exploration/new_constructions/t6_b33_screen.py
- lin_diff: ~/workspace/mix/exploration/fast_battery/src/lin_diff.py
- Ledger: ~/workspace/mix/exploration/LEADS_LEDGER.md
