# Adder-latency iteration status (worker: adder-lat design worker, 2026-10-07)
# Heartbeat: append a timestamped line at least every 30 min. No heartbeat = dead.

- 2026-10-07 20:52 CEST: worker start. al_cascad validated (S0 25.5u, S1-S4+Q1 pass).
  Box saturated (load ~12-17 on 2 CPU; round_tweak sweep has priority) -> polite mode:
  numpy triage first, S0 via run_synth.py one-at-a-time, S1/S2 after. Plan: wave-1 =
  chi-cascade axis (al_chi4/6/8, al_chi4k w/ per-stage key fold), al_orand6 (AND/OR mix),
  al_triand5 (3-input AND), al_arx2 (2-add ARX), al_feist_chi6 (Feistel chi-F),
  al_andxor10 (2u/stage). Also screen existing untested al_cascad4/al_andlin/al_arx1 models.
  Writing single-source generator (model.py + impl.c + rtl.v from one spec) now.

- 2026-10-07 21:10 CEST: KEY FINDING on the north star itself. Measured 64-bit adder via
  authorized run_synth.py: DUT adder64 cells=340 area=978 crit=83.0u (ref mul64=103.5u).
  => In the unit-delay model a plain 64-bit ADDER is 83.0u, i.e. 3.3x SLOWER than the
  already-validated al_cascad (25.5u). The literal "adder-like latency" target is already
  beaten; the meaningful goal is pushing well below 25.5u. (All numbers measured, not modeled.)
  Corollary: addition-heavy ARX is delay-expensive in this model (each add ~= 83u);
  search priority stays on shallow AND/XOR/chi cascades, Feistel, OR/AND mixes.
- 2026-10-07 21:10 CEST: wave-1 generator done (gen_wave1.py: single source -> model.py +
  impl.c + rtl.v + meta.json for 9 candidates). Triage (C-vs-Python xcheck OK on all 9;
  avalanche N=20k; mini-diff N=2^18, 12 deltas):
  * KILL al_chi4: 4-stage chi cascade fails avalanche (aval_maxdev=0.3826, meandev=0.3767,
    minidiff_zmax=385.3). Scoped: 4 chi stages insufficient in this rotation schedule.
  * KILL al_chi4k: same 4-stage chi + per-stage key fold, also fails (aval_maxdev=0.3800,
    zmax=385.6). Scoped: per-stage key injection does NOT rescue 4-stage chi.
  * PASS triage: al_chi6 (aval_maxdev=0.0158, zmax=3.6), al_chi8 (0.0126, 3.9),
    al_orand6 (0.0121, 3.8). Queued: S0 via run_synth.py next, then S1/S2.
  * Remaining triage running: al_triand5, al_arx2, al_feist_chi6, al_andxor10.

- 2026-10-07 21:25 CEST: triage kills (scoped):
  * KILL al_arx2: 2-addition ARX fails avalanche catastrophically (aval_maxdev=0.4979,
    meandev=0.448). Diagnosis: high input bits (63,62,61..) never flip low output bits --
    2 additions with XOR-only spreading give insufficient upward diffusion in this schedule
    (x+k; ^rot13^rot29; +=rot7; ^rot17^rot41^rot23; ^k). Scoped to this construction.
  * KILL al_feist_chi6: 6-round 32-bit Feistel w/ chi-F fails avalanche (maxdev=0.2558,
    meandev=0.1328, broadly under-diffused). Scoped: 6 rounds insufficient for this F.
  * Triage survivors -> S0 running: al_chi6, al_chi8, al_orand6, al_triand5, al_andxor10.

- 2026-10-07 21:45 CEST: wave-2 triage kills (scoped):
  * KILL al_dualand4 (=al_cascad4 exact construction): 4-stage dual-AND fails
    (aval_maxdev=0.1632, minidiff_zmax=162.2). 4-stage barrier holds for dual-AND too.
  * KILL al_chi5: 5-stage chi fails differential (minidiff_zmax=17.5 > 9; avalanche OK).
    => chi needs >=6 stages in these schedules.
  * KILL al_orand4: 4-stage AND/OR fails (aval_maxdev=0.1375, zmax=134.9).
  * KILL al_dense4: 4-stage dense (3 AND-pairs/stage) fails differential (zmax=26.2).
  * KILL al_nibchi3: 3-round nibble-chi SPN fails (aval_maxdev=0.3160, zmax=320.3).
  * PASS triage: al_nibchi4 (4-round nibble-chi SPN; aval_maxdev=0.0131, zmax=4.3).
  Consistent picture: cascades need ~6 nonlinear levels; nibble-SPN needs 4 rounds.
  S0 batch running for: al_chi6, al_chi8, al_orand6, al_triand5, al_andxor10 (+al_nibchi4 next).

- 2026-10-07 21:36 CEST: CRON TIMEOUT - work paused mid-flight. S1 (official) for al_chi6 was
  running; al_nibchi4 S1/S2 queued behind it. Wave-3 generator edits partially complete
  (specs+model for ornot/nibchib/hybrid added; impl/RTL branches for nibchib+hybrid NOT yet
  added -- gen_wave1.py must be finished before generating wave-3). Resume: finish
  generator branches, generate+screen wave-3 (al_andxor6/8, al_ornot6, al_chi6k,
  al_nibchi4b, al_hybrid6), then S1/S2/S0 for survivors.
- 2026-10-07 22:04 CEST: worker start (resume of 21:36 CRON TIMEOUT session).
- 2026-10-07 22:10 CEST: s12_wave.py NOT running (pgrep clean) — wave completed 19:35-20:02 UTC
  before the timeout; all 6 verdicts in s12_results.txt. Final: al_chi8 S1-PASS+S2-PASS
  (max|z|=4.3, repeats=0; S0 26.1u) = lead. al_chi6 S1-FLAG (marginal RD rej=1; S0 20.4u).
  al_orand6/al_andxor10 S1-FLAG (marginal PB rej=1 each). al_triand5 S1-FLAG DIFF rej=7
  (worst|z|=10.2). al_nibchi4 S1-KILL LIN/DIFF rej=10/10 worst|z|=64.3 (triage-passed on
  single key -> key-dependent weakness; O73 HIGH).
- 2026-10-07 22:14 CEST: wave-3 generator FINISHED (nibchib + hybrid branches added to
  gen_model/gen_impl/gen_rtl; also fixed unreachable ornot RTL/impl cascade tuples).
  6 candidates generated (al_andxor6/8, al_ornot6, al_chi6k, al_nibchi4b, al_hybrid6).
  Triage running (nice -19). Verdicts O64-O77 recorded in VERDICT_SCOPE.md (scoped).
- 2026-10-07 22:20 CEST: wave-3 triage verdicts (xcheck OK all 6, C-vs-Python bit-exact):
  * KILL al_andxor6 (O78): 6-stage andxor fails (aval_maxdev=0.2750, zmax=274.0).
    Scoped: 6 stages insufficient for andxor in this schedule.
  * PASS -> S0: al_andxor8 (0.0146/3.6), al_ornot6 (0.0140/3.3), al_chi6k (0.0137/3.3),
    al_nibchi4b (0.0131/5.3), al_hybrid6 (0.0122/3.4).
  * O73 follow-up: al_nibchi4b multi-key (4 keys) avalanche/diff check: aval 0.017-0.021,
    zmax 4.1-5.3 across all keys -- no key-dependent catastrophic failure (AND variant's
    pathology absent); still needs official S1.
- 2026-10-07 22:21 CEST: S0 batch launched for 5 wave-3 survivors (s0_wave1.py, nice -19,
  sequential; log s0_wave3_run.log). Next: S1/S2 wave for S0 survivors + S3/S4/Q1 for lead al_chi8.
- 2026-10-07 22:16 CEST: S0 wave-3 done (all pass S0 bar):
  al_andxor8 25.3u/8343 | al_ornot6 **20.1u**/6209 | al_chi6k 26.0u/5894 (key fold cost
  +5.6u vs al_chi6, contradicts "no extra depth" comment) | al_nibchi4b 24.5u/4432 |
  al_hybrid6 **20.1u**/6165. New fastest: al_ornot6 & al_hybrid6 (20.1u < al_cascad 25.5u).
- 2026-10-07 22:20 CEST: s12 wave-3 verdicts so far: al_andxor8 S1-FLAG (marginal PB rej=1;
  LIN/DIFF pass; S0 25.3u) | **al_ornot6 S1 CAL_PASS** (LIN/DIFF pass, marginal 0/0; S0
  20.1u) -- fastest S1-clean candidate ever on this track; S2 running. Remaining: al_chi6k,
  al_nibchi4b, al_hybrid6.
- 2026-10-07 22:45 CEST: wave-3 S12 complete (5 candidates):
  * al_andxor8 S1-FLAG marginal (O81); al_nibchi4b S1-KILL LIN/DIFF 10/10 worst|z|=69.4 (O80);
    al_hybrid6 S1-FLAG marginal (O82); al_chi6k S1-PASS + S2 tool-PASS w/ |z|=103.0 @ bit52
    (2nd-key check running); al_ornot6 S1-CAL_PASS + S2 tool-PASS w/ systematic high-bit
    differential bias (O79 KILL: |z|=156.7 @ bit42 key1; 33/115 deltas |z|>9 @ key0).
  * Lesson: S2's repeats-only gate is blind to strong |z| biases -- raw-log verification
    caught two tool-PASS verdicts with real differential anomalies. Recorded in ledger.
  * Only genuinely clean candidate on the track remains al_chi8 (26.1u, S2 max|z|=4.3).
    Next: S3/S4/Q1 for al_chi8.
- 2026-10-07 23:01 CEST: CRON TIMEOUT (2nd) - work paused. al_chi6k 2nd-key diffprof DONE:
  KILL (O83): 49/115 deltas |z|>9 @ key0, peak 95.2 @ bit34 (key1: 103.0 @ bit52) --
  per-stage key fold introduces systematic differential bias. Wave-3 final: 6 candidates,
  1 triage kill (andxor6), 1 S1 kill (nibchi4b), 2 S1 marginal FLAGs (andxor8, hybrid6),
  2 differential-profile kills on tool-PASS verdicts (ornot6 O79, chi6k O83).
  ONLY clean candidate on track: al_chi8 (26.1u; S1 CAL_PASS; S2 max|z|=4.3, repeats=0).
  NEXT (not started): S3/S4/Q1 for al_chi8 -- binaries built (build/gen_al_chi8,
  build/sc_al_chi8); commands: s3_practrand.sh al_chi8 <gen> <outdir> <key> 1 (+strided
  2nd key), sc_al_chi8 <key>, round13/q1_sacbic.py al_chi8 <outdir>.
- 2026-10-08 00:08 CEST: resume worker start (3rd session; replaces 23:01 timeout).
  State found: build/gen_al_chi8 + build/sc_al_chi8 paths STALE -- actual binaries live in
  fast_battery/build/ (gen_al_chi8, sc_al_chi8 both present). Load 7.2 (sweep prio) ->
  holding S3/S4 heavy stages until load < 4; doing Q1 + wave-4 design (light) meanwhile.
- 2026-10-08 00:16 CEST: wave-4 designed+generated (8 candidates, 2 NEW ops:
  ornotand [x^=((~ra)|rb)^(rc&rd)^re, ~2u/stage] and chiconst [chi + free
  per-stage constant fold, avoids O83 key-fold pathology]; chi8b/chi6b/ornot6b
  schedule widenings; feist_chi8; hybrid8 chi/and/ornot). Triage (nice -19) so
  far: al_chi8b PASS (0.0127/3.6), al_chi6b PASS (0.0150/5.9), al_ornot6b PASS
  (0.0131/3.0 -- ornot6's O79 bias looks schedule-dependent), al_ornotand5 PASS
  (0.0126/2.8), al_ornotand6 PASS (0.0114/3.6). Remaining: chiconst8, feist_chi8,
  hybrid8. Next: S0 wave for survivors, then S1/S2.
- 2026-10-08 00:16 CEST: Q1 for al_chi8 running (bit 16/64, slow under load).
  Accidental S4 launch (no-key probe) killed -- S3/S4 for al_chi8 still staged;
  load ~10, waiting for load < 4 per polite rule. sc_al_chi8 needs
  LD_LIBRARY_PATH=/home/hatch/tools/testu01/install/lib.
- 2026-10-08 00:24 CEST: wave-4 triage FINAL: 8/8 TRIAGE-PASS (xcheck OK all).
  al_chi8b (0.0127/3.6), al_chi6b (0.0150/5.9), al_ornot6b (0.0131/3.0),
  al_ornotand5 (0.0126/2.8), al_ornotand6 (0.0114/3.6), al_chiconst8 (0.0125/3.5),
  al_feist_chi8 (0.0130/3.3), al_hybrid8 (0.0119/3.6). Generator bug caught by
  xcheck: ornot subop missing in gen_model hybrid branch (fell through to and);
  fixed, regenerated, re-triaged OK. -> S0 batch next for all 8.
- 2026-10-08 00:29 CEST: **Q1 al_chi8 = PASS**: sac_z5=0 (mandatory gate),
  sac_maxdev=0.00430, bic_maxcorr=0.00907 (Q bar 0.02), avalanche_mean=32.001
  (N=2^18, measured). al_chi8 gating so far: S0 26.1u, S1 CAL_PASS, S2 clean
  (max|z|=4.3), Q1 PASS. Remaining: S3 (PractRand 16MB->1GB, 2 key configs),
  S4 (SmallCrush) -- staged, waiting load < 4.
- 2026-10-08 00:34 CEST: S0 wave-4 results (measured, run_synth.py):
  al_chi8b 25.3u | **al_chi6b 19.8u** (new track fastest, 22% below al_cascad
  25.5u) | al_ornot6b 21.0u | al_ornotand5 24.8u | al_ornotand6 28.6u |
  al_chiconst8 25.9u | al_hybrid8 25.9u | al_feist_chi8 SYNTH-FAIL (Verilog-2005
  part-select-on-concat in rk wire -- generator bug, fixed via kk{i} intermediate
  wire, rtl regenerated, S0 re-run queued). All 8 beat the 83.0u adder; 6 of 8
  beat al_cascad 25.5u. -> S1/S2 wave for the 7 S0 survivors next.
- 2026-10-08 00:38 CEST: al_feist_chi8 S0 re-run after RTL fix: 36.1u/5659 cells
  (measured). Slower than the 25.5u bar but keeps the Feistel axis alive for
  S1/S2; a 6-round Feistel was already killed at triage (al_feist_chi6), so the
  axis needs >=8 rounds in this F. S0 wave-4 fully complete: 8/8 synthesized.
  Next: S1/S2 wave for survivors (load 8.9 -- holding for load < 4 per polite
  rule), then S3/S4 for al_chi8.
- 2026-10-08 02:44 CEST: resume supervisor start (replaces session dead since 00:38). Track nominal, nothing to restart: no drivers were running (all staged work complete: al_chi8 Q1 PASS 00:29, 8/8 wave-4 S0 done, al_feist_chi8 36.1u re-run). Inputs for staged next steps verified: build/gen_al_chi8 + sc_al_chi8 present; 7 wave-4 S0 survivors installed (al_chi8b, al_chi6b, al_ornot6b, al_ornotand5, al_ornotand6, al_chiconst8, al_hybrid8). HELD: S1/S2 wave for 7 survivors + S3/S4 for al_chi8 -- 1-min load ~13 > 4 polite gate, sweep.py priority. Load falling (17.9->15.7 15-min); will launch S1/S2 wave when gate clears.

- 2026-10-08 07:15 CEST: supervisor (Track 3) start. Wave-5 designed+generated (6 candidates: chi6c/d schedule widening, mix5a/b 5-stage mixed, ornot6c/d schedule widening). Triage: 4/6 PASS (chi6c, chi6d, ornot6c, ornot6d); 2 KILL (mix5a/b -- 5-stage barrier holds even for mixed ops, aval 0.058/0.097, zmax 49/94).
- 2026-10-08 07:30 CEST: wave-5 S0 COMPLETE: al_chi6c 19.8u/6093 (ties record), al_chi6d 20.1u/6031, al_ornot6c 19.8u/6164 (ties record), al_ornot6d 20.1u/6099.
- 2026-10-08 07:45 CEST: wave-6 designed+generated (2 candidates: al_and6a/b, 6-stage AND-rotation). Rationale: al_cascad (8-stage and) was 25.5u = 3.2u/stage; 6 stages could hit ~19.2u. Triage: 2/2 PASS. S0: al_and6a 20.1u/6116, al_and6b 19.8u/6039 (ties record).
- 2026-10-08 07:50 CEST: **KEY FINDING: 19.8u is the 6-stage floor.** Four candidates tied at 19.8u across 3 different ops (chi6b, chi6c, ornot6c, and6b) with different schedules. 5-stage barrier holds (mix5a/b killed). Breaking 19.8u requires <6 stages (proven insufficient) or sub-3.3u/stage op (none found in and/chi/ornot/ornotand family).
