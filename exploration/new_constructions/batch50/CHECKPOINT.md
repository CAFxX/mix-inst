# Batch-50 checkpoint (track-6 supervisor incarnation XX, 2026-10-11)

## Co-design (done)
- Soft probe (`probe_lowand.py`, K=2/3/4 penalty anneal): rugged landscape,
  (bijective,DU=8) only by blowing the AND cap -> methodology cut, replaced
  by the hard probe.
- Hard probe (`probe_lowand_hard.py`): pattern-fixed exhaustive search.
  k=3: 20 patterns x 8000 steps. Pattern 0 (x0-star [x0x1+x0x2+x0x3]):
  E=9.0, coll=0, DU=8, LATbias=8, S(0)=10 -> VIABLE.
  LUT=[10,13,6,15,8,11,4,9,0,1,12,3,2,7,14,5].
  (k=3 tail + k=2 15 patterns still running at checkpoint time; only
  pattern 0 viable so far.)
- Calibration pre-verified: and1/b33c z=3.3 exact PASS.

## Pre-pilot (launched 17:43:45Z, backoff-gated)
- Wrapper `run_b50_prepilot.sh` via setsid agentwork-launch --nice 19,
  tag track6/b50-prepilot. At launch load=14.57 -> waiting on backoff.
- qlowS4 6 draws (0xB501) + qlowS3 6 draws (0xB502), keeps ->
  prepilot_keeps.jsonl.

## Adjudication (2026-10-11 ~18:05 CEST, cron timeout)
- k=2 hard probe COMPLETE: 15/15 patterns, 0 viable (best DU=16) ->
  VIABILITY: NOT VIABLE. The k=2 cut on measurement is now
  exhaustive-pattern confirmed.
- k=3 hard probe COMPLETE: 20/20 patterns; only the x0-star viable
  (QLOW). The "19/19 non-star stall at DU=16" cut is confirmed.
- PRE-PILOT COMPLETE (in-wrapper calibration z=3.3 PASS):
  qlowS4 0/6 KEEP (z: 725.9/1290.6/3432.1/31.2/2909.3/9319.5; min 31.2,
  near-miss on try 3); qlowS3 0/6 KEEP (min 8416.9, b47-class, killkey
  0x0 on try 3 -- wall probe dead as predicted).
- VERDICT per pre-registered rule: qlowS4's min z=31.2 < 100 is a
  near-miss -> **PILOT TRIGGERED** (2x40 draws, seeds 0xB503/0xB504).
  NOT launched: cron execution timeout hit before launch. Axis OPEN,
  pilot QUEUED for the successor incarnation.
- Mechanism read (directional, not a verdict): q4bS4 (Q4, 5 ANDs) went
  4/6 with min z=2.6; qlowS4 (QLOW, 3 ANDs, IDENTICAL DU=8/LATbias=8,
  same 2-rot tree) goes 0/6 with min z=31.2. The sharp degradation at
  fixed DU supports mechanism (b) (AND-thinness is load-bearing for
  cascade quality beyond what DU captures); the single 31.2 near-miss
  keeps the pilot justified per the rule rather than foregone.
- Process note: the first pre-pilot wrapper (17:43:45Z) hit a spurious
  BACKOFF-FAIL after one 5-min poll (loop exited with load still high;
  root cause unknown -- the identical loop logic verified fine in
  isolation and the relaunched wrapper worked). Wrapper now logs
  deadline + per-poll timestamps for diagnosability.

## BATCH-50 PILOT ADJUDICATION (2026-10-11T17:02Z, by the mix-search-status-30m run)
Pilot COMPLETE 17:00:10Z (pilot.log): qlowS4 2/40 KEEP minz=3.1 (seed=0xb503),
qlowS3 0/40 KEEP minz=4896.7 (seed=0xb504). Calibration z=3.3 PASS (pilot_calibrate.log).
Escalation per DESIGN.md pre-registered plan (stratified: both keeps):
- bundles t6_qlowS4a (z=3.13, [(QLOW,46,55),(QLOW,29,43),(QLOW,12,7),(QLOW,10,26)]),
  t6_qlowS4b (z=5.57, [(QLOW,55,9),(QLOW,59,42),(QLOW,45,35),(QLOW,10,37)]),
  both bit-exact C-vs-Python 2000/2000 + screener-vs-bundle 500/500.
- S0 (run_synth.py, ref mul64 103.5u, XCHECK clean on both):
  t6_qlowS4a crit=25.7u (2712 cells, area 7748); t6_qlowS4b crit=24.6u
  (3988 cells, area 11243). Both vs strict <19.3u bar -> FAIL decisively
  (5.3-6.4u over; ~6.2-6.4u/stage vs <4.83u/stage budget).
- No cost-eligible keep -> no S1 per plan (S1 fail-fast only on cost-eligible).
VERDICT: batch-50 axis QUALITY-CONFIRMED (2/40), COST-CLOSED (VALID scoped,
same class as b45/b49). The cost thesis (3-AND QLOW -> ~4u/stage) FALSIFIED
by measurement: 6.2-6.4u/stage, the S-box's 3-AND+3-XOR per bit + 2-rot XOR
tree maps ~55% worse than projected. qlowS3 0/40 KILLED (b47-class wall,
min z=4896.7). Scope: 4st/3st repeated-QLOW replacement cascade (2-rot tree,
pre-whiten, rotl(k,13)) as frontier challenger + the class claim
"3-AND minimal bijective-quadratic 4-bit S-box repeated stage" on cost.
Mechanism: quality DOES transfer at 4st (min z=3.1 = b33c-class; AND-count
not fatal), keep rate lower (2/40 vs q4bS4's 4/6); cost is the killer.
Re-test triggers: cut #5 (5st/6st qlow) needs 4st keeps AND per-stage <3.86u
-> not met; cut #4 (cubic S-boxes) needs QLOW-axis death (MET) AND a
cost-viable cubic mined (open deferred lead).
