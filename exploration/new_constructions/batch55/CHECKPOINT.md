# Batch-55 checkpoint (track-6 supervisor incarnation XXIX)

## 2026-10-12 ~01:10 CEST — batch-54 CLOSED (O96) + batch-55 co-designed + pre-pilot launched

- **Batch-54 terminal adjudication VERIFIED FROM RAW ARTIFACTS (not
  trusted from the brief):** `fast_battery/results/t6_b54_{h1,h2,h3,h4,h6}/
  battery.log` + `s1_result.json` + `new_constructions/batch54/
  run_b54_battery.log` (battery COMPLETE 2026-10-11T22:56:36Z): all five
  **S1-DIFF-KILLED (rc=2)** — LIN PASS (rej=0 all), DIFF FLAG
  rej=1/1/2/4/5 (worst|z|=4.3/4.6/5.5/7.3/9.4, fisher_logp=-8.00/-7.38/
  -15.45/-11.76/-70.37); killkeys mixed across the 10-key set —
  key-independent. Full-S1 worst|z| reproduces triage z bit-for-bit.
- **Mechanism finding (O96):** the triage's worst-z KEEP bar (z<10)
  does NOT predict the S1 DIFF gate — all five keeps died on the
  Holm-Bonferroni fisher aggregation. The AND@pos1 "tolerance" was
  h0-schedule-specific, not position-specific. hetMA5 QUALITY-CLOSED
  in this construction (S1 0/5 + Q1 0/1), but the S1 gate never saw a
  fisher-clean schedule — instrument confound isolated, not resolved.
- **O96 recorded** in VERDICT_SCOPE.md (scope: the five tested
  schedules + hardened O95 class claim; NOT other AND forms, NOT MU5,
  NOT a fisher-matched triage).
- **Batch-55 axis: hetMA5p1f** — bit-identical form to b54, KEEP bar
  replaced with the S1 gate's own rule (Holm-Bonferroni at ALPHA=0.01
  on per-key fisher_logp, 0 rejections via `lin_diff.holm_reject`
  verbatim). De-dup grep-verified (never run). 11 cuts, each with its
  defensible reason (DESIGN.md). Pre-registered: pre-pilot 12 draws
  (0xB551) = harness check → PILOT 80 draws (0xB552) regardless;
  >=1 fisher-KEEP → bundle → S0 (<19.3u strict) → S1 → battery → Q1;
  0/80 → close pos1+fisher, escalate to ANDN/OR-AND forms.
- **Harness** `batch55/t6_b55_screen.py`: py_compile clean,
  `selftest` PASS, 1-draw smoke PASS, `calibrate` PASS both gates
  (CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2 MU5-324 n_reject=0 —
  the bar is not miscalibrated against a known-good schedule).
- **Pre-pilot LAUNCHED**: `run_b55_prepilot.sh` via `setsid
  agentwork-launch.sh --nice 19 --tag track6/b55-prepilot`
  (cleared-flag backoff pattern).
- **Heartbeat**: `batch55/heartbeat.txt` touched at launch; re-touch
  every ~20 min while live (next due ~01:30 CEST).
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.
- **Next**: launch the 80-draw pilot after the pre-pilot harness
  check; adjudicate per DESIGN.md's pre-registered rules when
  "PILOT COMPLETE" lands in `batch55/pilot.log`.

## 2026-10-12 ~01:18 CEST — Pre-pilot adjudicated, pilot launched (incarnation XXIX, continued)

- **Pre-pilot VERIFIED FROM RAW ARTIFACTS** (`prepilot.log`, "PRE-PILOT
  COMPLETE" 2026-10-11T23:11:26Z): calibration PASS both gates
  (CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2 MU5-324 n_reject=0, z=3.24);
  hetMA5p1f **0/12 KEEP, min z=21.8** (seed 0xB551, exit=0); 12/12 kills
  n_reject=5-10, min_fisher=-inf to -679.2; killkeys mixed across the
  10-key set (0x0/0xffff/deadbeef/f0b52a9e) — key-independent.
- Harness check PASSED: fail-loud gates passed, 12 draws completed,
  harness discriminating (12 kills; GATE-FAIL vacuity guard did NOT
  fire). Per DESIGN.md's pre-registered rule the 12-draw pre-pilot is a
  harness check only (P(0/12)~0.89 at a 1% true keep rate — cannot
  falsify) → PILOT runs regardless. The kills' harshness (minz=21.8 vs
  b54's 2.96) is expected: b54's keeps were selected on the wrong
  statistic and would all fail the fisher bar too.
- **PILOT LAUNCHED**: `run_b55_pilot.sh` (80 draws, seed 0xB552) via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b55-pilot`
  (cleared-flag backoff; backoff CLEAR at launch, load 4.47).
  Calibration PASS both gates in the pilot wrapper; screening live
  (early read 23/80, all kills n_reject 8-10, min_fisher=-inf).
- **Heartbeat**: `batch55/heartbeat.txt` re-touched at pilot launch
  (23:15:25Z); re-touch every ~20-30 min while live.
- **Next**: adjudicate on "PILOT COMPLETE" in `pilot.log` per the
  pre-registered rules (>=1 fisher-KEEP -> bundle -> S0 (<19.3u
  strict) -> S1 fail-fast -> staged battery -> Q1 (sac_z5=0); 0/80 ->
  CLOSE the pos1+fisher axis, escalate to ANDN/OR-AND hetero forms).
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.

## 2026-10-12 ~01:22 CEST — PILOT ADJUDICATED: 1/80 FISHER-KEEP -> ESCALATION (incarnation XXIX)

- **Pilot VERIFIED FROM RAW ARTIFACTS** (`pilot.log`, "PILOT COMPLETE"
  2026-10-11T23:16:20Z): calibration PASS both gates; hetMA5p1f
  **1/80 KEEP** (seed 0xB552, exit=0): try 67, n_reject=0,
  maxworst|z|=2.9, min_fisher=-5.9, andpos=1 (AND3(49,47,40)@pos1).
  79/79 kills n_reject=5-10, min_fisher=-inf -- killkeys mixed
  (0x0/0xffff/deadbeef/f0b52a9e/123456789abcdef) -- key-independent.
- **Mechanism question ANSWERED: YES** -- fisher-clean AND@pos1
  schedules DO exist in the hetMA5p1 draw space (~1% rate, n=80). The
  O96 instrument confound is RESOLVED (not just isolated): the S1 gate
  was never the blocker for a gate-matched-selected schedule.
- **Bundle** `gen_b55_bundle.py` (b53/b54 pipeline verbatim +
  AND@pos1 fail-loud assert; keep sorted by (n_reject, z)):
  `fast_battery/candidates/t6_b55_f0/` -- bit-exact C-vs-Python
  2000/2000 OK + screener-vs-bundle (t6_b55_screen) 500/500 OK.
- **S0**: t6_b55_f0 crit=**18.8u** (5,767 cells, area 18,784),
  STRICTLY <19.3u bar, XCHECK clean (analyze.py == analyze2.py,
  ref mul64 103.5u). **COST-ELIGIBLE** -- the first hetMA5 schedule
  that is BOTH fisher-clean AND under the frontier bar.
- Per the pre-registered >=1-KEEP rule: **staged battery LAUNCHED**
  `run_b55_battery.sh` via `setsid agentwork-launch.sh --nice 19
  --tag track6/b55-battery` (cleared-flag backoff; backoff CLEAR at
  launch, load 7.07): S1->S4 on t6_b55_f0, then Q1 sac_z5=0 on any S4
  survivor.
- **Heartbeat**: re-touched at battery launch; re-touch every
  ~20-30 min while live.
- **Next**: adjudicate on "batch-55 staged battery COMPLETE;
  survivors:<...>" in `run_b55_battery.log`. A keep clearing Q1 at
  <19.3u = FRONTIER CHALLENGER (new O-entry + notify). A Q1 SAC kill
  = form-fatal CONFIRMED at the avalanche tail (O95's mechanism
  question resolved, O-entry).
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u (t6_b55_f0 is a
  challenger CANDIDATE, not a claim -- needs S0->S4 + Q1).

## 2026-10-12 ~01:30 CEST — TERMINAL: t6_b55_f0 S1-KILLED, batch-55 CLOSED (O97) (incarnation XXIX)

- **Staged battery VERIFIED FROM RAW ARTIFACTS**
  (`run_b55_battery.log`, "batch-55 staged battery COMPLETE;
  survivors:" EMPTY, 2026-10-11T23:22:39Z;
  `fast_battery/results/t6_b55_f0/s1_result.json` + `battery.log`):
  **t6_b55_f0 S1-KILLED (rc=2, wall 41s)** --
  - S1 SEQ LIN: PASS (rej=0); SEQ DIFF per-bit: PASS (rej=0) --
    the triage's n_reject=0 KEEP prediction REPRODUCED at the gate.
  - The marginal screen's inner low-8-bit chi2 DIFF gate
    (`screen_lindiff.screen_lindiff`, MAJOR-3 2026-10-02) CAL_FLAG:
    rej=2 (keys 0x0, 0x1234); PB/RD lists empty (early-kill path).
  - PB/RD marginal: not run (skipped on the inner-gate kill).
- **Kill independently reproduced** by XXIX (`screen_lindiff` on the
  bundle model, 10 keys x N=2^18 SEQ): LIN max D=31/4096 rej=0;
  DIFF **rej=2** (keys 0x0, 0x1234), worst chi2|z|=**3.3** @ delta=16,
  broad elevation (deltas 6/11/16 across keys 0x0/0x1234/0x9e37.../
  0xf0b52a9e/0x9298...) -- systematic low-byte joint-distribution
  deviation, same "many small deviations" signature as O96 but in the
  joint statistic the per-bit triage cannot see.
- **Terminal verdict (O97 recorded in VERDICT_SCOPE.md): the
  pos1+fisher axis is CLOSED.** O96's instrument confound is RESOLVED
  for the per-bit gate (fisher-clean schedules exist at ~1%, and the
  triage validated at S1), but the AND@pos1 form cannot clear S1's
  low-8-bit joint-distribution DIFF gate. Combined with O96, no
  AND@pos1 schedule clears S1 under either differential statistic.
  Scope: the tested schedule + the axis; NOT other AND forms
  (ANDN/OR-AND untested), NOT a both-statistics triage (re-test
  trigger recorded; expected yield ~0).
- **Escalation lead (pre-registered): AND-form variants (ANDN /
  OR-AND hetero)** -- the next batch's co-design, not launched here.
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.
- Heartbeat re-touched at terminal adjudication. No live track-6
  processes remain (battery wrapper exited; nothing to kill).
