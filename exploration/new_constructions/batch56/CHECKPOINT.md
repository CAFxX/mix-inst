# Batch-56 checkpoint (track-6 supervisor incarnation XXX)

## 2026-10-12 ~01:40 CEST — batch-55 CLOSED (O97) + batch-56 co-designed + harness verified + pre-pilot launched

- **Leads ledger reconciled** (top entries read): active leads = 2
  (track-3 W3' harvest battery, owned by track-3 supervisor; track-6
  AND-form-variant co-design — the XXIX escalation lead, now owned by
  XXX). Added: 1 (the AND-form lead, by XXIX); resolved terminal: 1
  (batch-55 pos1+fisher → CLOSED, O97).
- **O95–O97 confirmed in VERDICT_SCOPE.md** from raw disk: O95 hetMA5
  AND3 Q1-SAC-killed (sac_z5=9); O96 hetMA5p1 5/5 S1 per-bit-DIFF-
  killed; O97 hetMA5p1f t6_b55_f0 S1 joint-DIFF-killed (rej=2,
  worst chi2|z|=3.3) — axis closed, instrument confound resolved.
- **Closed-axis audit (b19–b55) + de-dup** (grep-verified code/log
  dirs AND ledger candidate rows): batch-39 andn/andnM, batch-43
  ornM5, batch-44 andorM were all HOMOGENEOUS cascades — the hetero
  ANDN / OR-AND frame (one variant stage inside 4xMUXD) was NEVER
  run. fz24_g/h lesson applied (ledger candidate rows grepped).
- **Batch-56 axis: AND-form variants hetero** — prize arms hetMA5N
  (ANDN `x ^= (ra&~rb)` @pos1) + hetMOA5 (OAAND
  `x ^= ((ra|rb)&rc) ^ rd` @pos1) + control hetMA5p1f (AND3
  b55-verbatim, rate discriminator). Instrument FIXED verbatim
  (b55 gate-matched Holm-Bonferroni fisher triage) — any keep-rate
  or S1-fate difference isolates the FORM. 11 cuts with defensible
  reasons (DESIGN.md), incl. pos0/2/3/4 as a PRIORITY cut (pos1 is
  the only position with measured S1-clearing evidence) and NO
  in-triage joint-chi2 gate (would confound form vs instrument;
  S1 fail-fast at 41s wall IS the joint test).
- **Harness** `batch56/t6_b56_screen.py`: py_compile clean,
  `selftest` PASS (AND3 zero-corner=x^rc, ANDN zero-corner=x^ra,
  OAAND zero-corner=x^rd, all bit-exact; degeneracy asserts fire),
  1-draw smoke PASS on all 3 arms (discriminating, no GATE-FAIL),
  `calibrate` PASS both gates (CALIB-1 and1/b33c z=3.3 EXACT;
  CALIB-2 MU5-324 n_reject=0, z=3.24 — bar not miscalibrated).
- **Pre-pilot LAUNCHED** via `setsid agentwork-launch.sh --nice 19
  --tag track6/b56-prepilot` (cleared-flag backoff; backoff CLEAR
  at launch, load 5.11). Wrapper: calibration fail-loud → 12
  draws/arm (0xB561/0xB562/0xB563) → `prepilot_keeps.jsonl` →
  "PRE-PILOT COMPLETE".
- **Heartbeat**: `batch56/heartbeat.txt` touched at launch; re-touch
  every ~30 min while live.
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.
- **Next**: adjudicate on "PRE-PILOT COMPLETE" in `prepilot.log`
  (harness check only → PILOT 80+80+24 draws regardless, per the
  pre-registered rules) → launch `run_b56_pilot.sh`.

## 2026-10-12 ~01:47 CEST — Pre-pilot adjudicated from raw, pilot launched (incarnation XXX)

- **Pre-pilot VERIFIED FROM RAW** (`prepilot.log`, "PRE-PILOT
  COMPLETE" 2026-10-11T23:36:58Z): calibration PASS both gates
  (CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2 MU5-324 n_reject=0,
  z=3.24); **hetMA5N 0/12 KEEP, min z=221.8** (seed 0xB561);
  **hetMOA5 0/12 KEEP, min z=4.5** (seed 0xB562);
  **hetMA5p1f 0/12 KEEP, min z=19.7** (seed 0xB563); all arms exit=0.
  Harness check PASSED: fail-loud gates passed, 36 draws completed,
  harness discriminating (36 kills; GATE-FAIL did not fire). Per
  DESIGN.md's pre-registered rule the 12-draw pre-pilot is a harness
  check only (P(0/12)~0.89 at a 1% true keep rate — cannot falsify)
  → **PILOT runs regardless**. Honest early reads (NOT verdicts):
  OAAND min z=4.5 is a near-miss-class draw (b33c-class worst-z),
  the AND3 control reproduces b55's 0/12 (min z=19.7 vs 21.8 —
  consistent), ANDN kills harsher (min 221.8) — pilot decides.
- **PILOT LAUNCHED** `run_b56_pilot.sh` (calibration fail-loud →
  hetMA5N 80 draws 0xB564 → hetMOA5 80 draws 0xB565 →
  hetMA5p1f 24 draws 0xB566 → `pilot_keeps.jsonl` → "PILOT
  COMPLETE") via `setsid agentwork-launch.sh --nice 19 --tag
  track6/b56-pilot` (cleared-flag backoff; backoff CLEAR at launch,
  load 4.96; in-wrapper backoff clear after 1 poll).
- Heartbeat re-touched at pilot launch.
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.

## 2026-10-12 ~02:15 CEST — Batch-56 TERMINAL adjudication (supervisor incarnation, o2 escalation brief)

- **o0/o1 re-verified from raw** (`s0_t6_b56_o{0,1}.log`): o0 crit=20.1u
  (5733 cells, 16637 area), o1 crit=19.4u (6242, 18482); XCHECK clean
  both; ref mul64 103.5u. **COST-DOOMED** (strict <19.3u). Recorded as
  **O99** in VERDICT_SCOPE.md (scoped to the two schedules, NOT the form).
- **o2 escalated per pre-registered rule**: `gen_b56_bundle.py` rank=2
  -> `fast_battery/candidates/t6_b56_o2` (OAAND(30,19,7,44)@pos1, z=3.06,
  and_pos=1) — bit-exact C-vs-Python 2000/2000 OK + screener-vs-bundle
  500/500 OK; zero-corner/degeneracy fail-loud asserts fired clean. S0
  via `run_b56_s0_o2.sh` (setsid nice-19, tag track6/b56-escal,
  cleared-flag backoff, 1 poll, load 2.93): **crit=19.5u COST-DOOMED**,
  XCHECK clean, S0 COMPLETE.
- **o3 escalated** (doomed -> next-best before form verdict): rank=3 ->
  `t6_b56_o3` (OAAND(53,61,9,28)@pos1, z=3.56, and_pos=1) — bit-exact
  2000/2000 + 500/500 OK; S0 via `run_b56_s0_o3.sh` (backoff CLEAR,
  1 poll): **crit=19.5u COST-DOOMED**, XCHECK clean, ref stable.
- **FORM VERDICT (4/4 >= 3): hetMOA5 COST-CLOSED in this construction**,
  recorded as **O100**: measured 20.1/19.4/19.5/19.5u vs DESIGN.md
  projection 19.0-19.5u (tight cluster at the high end; o0 exceeded it);
  the OR gate's extra level costs ~0.1-0.8u vs the AND3 hetero
  (b55 f0 18.8u). No staged battery was ever cost-eligible — the form
  died at S0, no quality verdict. Re-test trigger: any untested keep
  (o4 z=3.58, o5 z=3.84, o6 z=4.18, o7 z=4.54, o8 z=4.55) clearing
  <19.3u re-opens the form. NOT about ANDN hetero (0/80 triage-dead)
  or the full MU5 form (19.3u frontier stands).
- **Ledger reconciled** (top entry 02:15 CEST): active leads = 0
  (track-6 batch-56 escalation RESOLVED TERMINAL, O99/O100); added 0;
  resolved terminal 4 (o0/o1/o2/o3 cost-doomed; hetMOA5 form cost-closed).
- **Heartbeat** owned (content-written 00:15Z); wrappers completed.
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.
- **Next**: none for batch-56 (terminal). ANDN hetero remains 0/80
  triage-dead; a fresh track-6 brief would need a new axis design.
