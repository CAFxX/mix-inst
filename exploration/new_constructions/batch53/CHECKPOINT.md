# Batch-53 checkpoint (track-6 supervisor incarnation XXIII; pilot relaunched by the 22:01 report run)

## 2026-10-11 ~22:05 CEST — first pilot wrapper died on spurious double-gate BACKOFF-FAIL, patched + RELAUNCHED

- **The 19:34Z pilot wrapper died at 19:38:51Z without doing any science:**
  pilot.log shows "backoff clear after 2 polls" then the post-loop
  `backoff` re-check flaked -> "BACKOFF-FAIL: load never cleared in 12h"
  (the wrapper polled twice; load never held 12h). Same race class as the
  b50 pre-pilot wrapper's 17:43Z death.
- **Root-cause fix (not just relaunch):** `run_b53_pilot.sh` patched to a
  `cleared` flag — no second backoff re-check after the loop; the flag is
  the single source of truth; the 12h deadline still fails loudly via the
  cleared==0 branch; per-poll backoff output now logged to
  `backoff_poll.out` for diagnosis. Class hunt: 6 wrappers in
  `new_constructions/batch*/run_b5*.sh` carry the double-gate pattern —
  b50/b51/b52/b53-prepilot are all terminal (historical), only the b53
  pilot wrapper is live and it is now patched. Future wrappers must use
  the cleared-flag pattern (recorded in DESIGN.md "Backoff / launch log").
- **Pilot RELAUNCHED** 20:04:04Z via `setsid agentwork-launch.sh --nice 19
  --tag track6/b53-pilot` (setsid per the batch-43 precedent). Backoff
  cleared after 1 poll; CALIBRATION exit=0; hetMA5 40 draws (seed 0xB533)
  in flight -> `pilot_keeps.jsonl` -> muxS5d 40 draws (seed 0xB534) ->
  "PILOT COMPLETE". heartbeat.txt re-touched every 30 min while live.

## 2026-10-11 ~21:30 CEST — co-design complete, pre-pilot queued

- **Batch-52 adjudication VERIFIED from raw artifacts** (not trusted from
  the ledger): `batch52/prepilot.log` has 12 try-lines, CALIBRATION
  exit=0, CALIB-1 and1/b33c z=3.3 EXACT, CALIB-2 MU5-324 z=3.24 KEEP,
  muxS5nl 0/6 KEEP minz=12465.2 (seed 0xb521), muxS5d 2/6 KEEP minz=3.2
  (seed 0xb522), exactly 2 keeps in `prepilot_keeps.jsonl`, both arms
  exit=0, "PRE-PILOT COMPLETE" 2026-10-11T18:40:25Z. The pre-registered
  falsifier (nl 0/6 b47-class AND control keeping >=1) triggered cleanly:
  **KILL LOUDLY — the linear d term is load-bearing for MUX-5st cascade
  quality.** Recorded as O90 in VERDICT_SCOPE.md (scoped: the tested 5st
  no-d MUX cascade + the class claim "MUX-5st without the linear term";
  NOT a claim about MUX-5st with d — the frontier stands — or hetero
  MUX/AND mixes).
- **t6_b33b terminal verdict recorded (O91)**: S1 CAL_PASS, S2
  max_repeats=0 max|z|=21.2, S3 4-stage PASS, S4 rc=0, Q1 sac_z5=0
  bic=0.0091 — FULL BATTERY PASS at 20.1u, cost-blocked vs 19.3u. The
  AND-6st form CAN pass everything; its measured floor is 19.8–20.1u.
- **Closed-axis audit (b19–b52)**: wall map holds — <=4st every sparse
  mechanism dead; dense-4st quality-alive but cost-doomed (22.9–28u);
  5st sparse-AND homogeneous dead; MUX-5st homogeneous IS the 19.3u
  frontier; MUX-5st-no-d dead on mechanism (b52); 3st dead x4;
  cubic mining stays CUT (b52 cut #1 unchanged); adder_lat all >=19.8u
  or S2-killed; track-8 fz13_het5a/b are word-level FUSED hetero
  (different frame — verdict doesn't transfer to per-stage cascades).
- **Batch-53 axis: 5-stage hetero MUX/AND cascade (hetMA5)** — the ONLY
  open frontier attack with a measured cost thesis: 4x3.86u (measured
  MU5 stage) + 1x3.3u (measured b33 AND stage) = 18.74u projected <
  19.3u. Mechanism question: does one AND stage (linear on single-bit
  inputs via the zero-corner) poison the proven 5st MUX cascade, or does
  the cascade absorb it? Prize hetMA5 (AND position Uniform{0..4},
  recorded per try) + control muxS5d (b52 arm verbatim). De-dup
  grep-verified incl. the ledger candidate rows (b51 fz24_g/h lesson):
  never screened at any stage count.
- **Cuts (11, each with its defensible reason in DESIGN.md)**: cubic
  mining stays CUT; maj-5st DEPRIORITIZED (not killed — no measured
  cost thesis); d->constant CUT on the b52 mechanism finding;
  MUX-6st CUT on measured per-stage cost (6x3.86=23.2u); 3+2 reserved
  as escalation; AND-without-rc CUT (identity on single-bit input);
  fixed AND position CUT; schedule-search-for-cost CUT (rotations are
  wires); per-stage round key CUT (b8 precedent); non-distinct draws
  CUT (degeneracy proofs); track-1 tweak batch CUT for this batch
  (1220 probed, winners 36.7–38.6u — not a frontier-challenger axis;
  stays deferred for a coordinator design call).
- **Harness**: `batch53/t6_b53_screen.py` — py_compile clean,
  `selftest` PASS (AND3 zero-corner = x^rc bit-exact; MUX gate
  popcount=1; degeneracy asserts fire). Fail-loud calibration:
  and1/b33c z=3.3 exact + MU5-324 z<10. Seeds 0xB531/0xB532.
- **Pre-pilot QUEUED**: `run_b53_prepilot.sh` (backoff-poll <=12h ->
  calibration fail-loud -> hetMA5 6 draws -> muxS5d 6 draws ->
  `prepilot_keeps.jsonl`), launch via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b53-prepilot`.
- **Heartbeat**: `batch53/heartbeat.txt` touched at launch; re-touch
  every 30 min while live.
- **Next**: adjudicate pre-pilot per DESIGN.md's pre-registered rules
  when "PRE-PILOT COMPLETE" lands in `batch53/prepilot.log`.

## 2026-10-11 ~21:34 CEST — pre-pilot adjudicated from raw artifacts, PILOT LIVE (incarnation XXIV)

- **Pre-pilot VERIFIED from raw artifacts** (read `prepilot.log`,
  `prepilot_calibrate.log`, `prepilot_keeps.jsonl`; did not trust the
  ledger): calibration PASS both gates (CALIB-1 and1/b33c z=3.3 exact;
  CALIB-2 MU5-324 z=3.24 KEEP); hetMA5 0/6 KEEP min z=14.5, try z's
  194.3 / 330.0 / 108.1 / 243.7 / 8535.8 / 14.5, andpos=3 on the
  near-miss (try 5, killkey=0x9e3779b97f4a7c15), seed 0xb531; muxS5d
  2/6 KEEP min z=3.4 (tries 1 z=3.4, 3 z=7.8), seed 0xb532; exactly 2
  keeps in `prepilot_keeps.jsonl`, both MUXD form; both arms exit=0;
  "PRE-PILOT COMPLETE" 2026-10-11T19:19:21Z (21:19:21 CEST).
- **Fired rule**: 0 keeps on hetMA5 with min z < 100 (near-miss) ->
  NOT catastrophe -> **PILOT** (2x40 draws). Not the kill rule (kill
  needs min z >= 1e3 b47-class; 14.5 is far below). Not GATE-FAIL
  (harness kills fine; both calibration gates reproduce exactly).
  Mechanism is alive enough to deserve the full pre-registered pilot.
- **Pilot LIVE**: `run_b53_pilot.sh` (modeled on batch52's runner:
  backoff-poll <=12h -> calibration fail-loud -> hetMA5 40 draws seed
  0xB533 -> muxS5d 40 draws seed 0xB534 -> `pilot_keeps.jsonl` ->
  "PILOT COMPLETE"), launched 19:34:03Z via setsid + agentwork-launch
  --nice 19 --tag track6/b53-pilot (setsid per the track-6 execs
  precedent; no fallback queue fabricated — cubic mining stays CUT).
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u (this batch produces
  only a triage verdict so far; any pilot KEEP escalates to S0
  stratified spot-check against the <19.3u bar).
- **Next**: adjudicate pilot per DESIGN.md's escalation rules when
  "PILOT COMPLETE" lands in `batch53/pilot.log`; heartbeat.txt
  re-touched every 30 min while live.

## 2026-10-11 ~22:35 CEST — escalation executing (supervisor incarnation XXV)

- **Pilot adjudicated from RAW artifacts (not trusted summary):**
  `pilot.log` "PILOT COMPLETE" 2026-10-11T20:11:52Z; CALIB-1 and1/b33c
  z=3.3 EXACT PASS; CALIB-2 MU5-324 z=3.24 KEEP PASS; hetMA5 5/40 KEEP
  minz=3.0 (seed 0xb533), muxS5d 15/40 KEEP minz=2.7 (seed 0xb534); both
  arms exit=0; `pilot_keeps.jsonl` = 20 entries (5 hetMA5 + 15 muxS5d),
  min z hetMA5=2.9502, muxS5d=2.7409. All numbers match expectations —
  tally VALID, science proceeds.
- **Escalation per pre-registered plan (DESIGN.md pipeline #5):**
  `gen_b53_bundle.py` written (4xMUXD + 1xAND3; the AND3 rotl(x,r) term is
  the b33 rc term, reproduced bit-exactly in Python/C/Verilog per cut #6).
  Bundles generated for all 5 hetMA5 keeps (t6_b53_h0..h4; triage
  z=2.95/3.01/6.45/9.18/9.89; AND positions 1,3,0,4,2 — all 5 positions
  keep, no position effect); C-vs-Python 2000/2000 OK and screener
  cross-check 500/500 OK on ALL 5.
- S0 in flight: `run_b53_s0.sh` launched via `setsid agentwork-launch.sh
  --nice 19 --tag track6/b53-escal`, backoff-gated (cleared-flag pattern).
  Bar: STRICTLY <19.3u measured, XCHECK clean (ref mul64 103.5u).

## 2026-10-11 ~22:43 CEST — S0 COMPLETE on all 5 keeps; battery backoff-queued

- **S0 via `run_synth.py` (bar STRICTLY <19.3u measured, XCHECK clean,
  ref mul64 103.5u) — all 5 bundles, `run_b53_s0.sh` (setsid,
  tag track6/b53-escal, nice 19, cleared-flag backoff):**
  - t6_b53_h0 (z=2.95, andpos=1): crit=**19.1u** cells=5507 — COST-ELIGIBLE
  - t6_b53_h1 (z=3.01, andpos=3): crit=**19.2u** cells=5650 — COST-ELIGIBLE
  - t6_b53_h2 (z=6.45, andpos=0): crit=**19.7u** cells=5555 — COST-DOOMED
    (>19.3u strict; record + close per pre-registered rule; excluded from
    the battery; O92 in VERDICT_SCOPE.md, scoped to this schedule)
  - t6_b53_h3 (z=9.18, andpos=4): crit=**18.9u** cells=5695 — COST-ELIGIBLE
  - t6_b53_h4 (z=9.89, andpos=2): crit=**18.7u** cells=5870 — COST-ELIGIBLE
  - All 5: XCHECK analyze.py == analyze2.py identical; delay_ratio
    0.181–0.190.
- **The cost thesis HOLDS:** 4/5 keeps land 18.7–19.2u — strictly under
  the 19.3u frontier speed point, so the hetMA5 axis is a genuine cost
  challenger (frontier currently 19.3u hyb28_mu5_324). Projected 18.7u
  was measured 18.7–19.2u (h4 hit the projection exactly).
- **Position study data point:** keeps exist at AND positions 0–4 (all
  five), with pilot z's 2.95/3.01/6.45/9.18/9.89 — AND tolerated at every
  stage position at triage; no position effect on triage quality so far.
  andpos=0 (AND-first) is the only cost-doom — single sample, not a
  position claim.
- **Staged battery LAUNCHED** `run_b53_battery.sh` (setsid,
  tag track6/b53-escal, nice 19, cleared-flag backoff): S1 fail-fast on
  t6_b53_h0 (first cost-eligible, lesson b), then
  `run_fast_battery.sh <cand> 1` staged S1→S2→S3→S4 on h0,h1,h3,h4 in z
  order (stops at first kill), then Q1 (`../../round13/q1_sacbic.py`,
  sac_z5=0 mandatory) on any S4 survivor. Currently BACKOFF-QUEUED
  (load=14.01 >= 12 at 20:42Z — the gate working as designed, not a
  stall); the runner polls every 60s with a 12h fail-loud cap.

## 2026-10-12 ~00:15 CEST — BATCH-53 TERMINAL: Q1 adjudication raw-verified, hetMA5 axis QUALITY-KILLED at the last gate (supervisor incarnation XXVI)

- **Q1 `q1_t6_b53_h0.log` / `q1_t6_b53_h0/q1_t6_b53_h0.json` raw-verified:**
  sac_z5=**9** (key 0x123456789abcdef0, N=262144, all 64 bits in the
  log, wall 589.5s) — the MANDATORY sac_z5=0 gate is FAILED.
  bic_maxcorr=0.00906 (BIC fine, reported not gated),
  avalanche_mean=32.002.
- **Staged battery `run_b53_battery.log` raw-verified:** h1/h3/h4
  S1-screen rc=2 (DIFF-kills; h1 rej=2 worst|z|=2.4, h3 rej=2
  worst|z|=9.2, h4 rej=10 worst|z|=9.9); h0 S1 CAL_PASS, S3 PASS
  (64M/256M/1G, incl. strided), S4 survivor; h2 excluded at S0
  (19.7u cost-doom, O92). "batch-53 staged battery COMPLETE"
  2026-10-11T21:34:42Z. All numbers match the XXV CHECKPOINT entries
  and `pilot_keeps.jsonl` (5 hetMA5, and_pos 0/1/2/3/4, z=2.95/3.01/
  6.45/9.18/9.89 + 15 muxS5d).
- **Position sub-read:** AND@pos1 is the ONLY position to clear S1
  (h0 -> S4, then Q1-killed); AND@pos2/3/4 S1-DIFF-killed even with
  lower triage z than h0 (poisoning is schedule-partial, triage z
  does not rank it); AND@pos0 cost-doomed, quality untested.
- **Verdict:** hetMA5 QUALITY-KILLED at Q1 — no frontier challenger.
  Recorded as O95 in VERDICT_SCOPE.md. Batch-53 processes confirmed
  dead; nothing restarted (lead resolved terminal). Batch-54
  (hetMA5p1: AND@pos1-fixed + exact-DIFF-proxy schedule search)
  co-designed and pre-pilot-launched by XXVI.
