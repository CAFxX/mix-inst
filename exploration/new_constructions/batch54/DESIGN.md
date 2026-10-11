# Batch-54 design note — "hetMA5p1": AND@pos1-fixed hetero cascade + exact-DIFF-proxy schedule search (track 6, 2026-10-12)

**Status: PRE-PILOT ADJUDICATED -> PILOT LIVE (incarnation XXVI, 2026-10-12 ~00:14 CEST).**
Pre-pilot verified from raw artifacts: calibration PASS both gates,
hetMA5p1 1/12 KEEP min z=2.6 (seed 0xB541), `prepilot_keeps.jsonl`
verified (form=hetMA5p1, z=2.64, and_pos=1, AND3@stage1), "PRE-PILOT
COMPLETE" 2026-10-11T22:13:39Z. Fired rule: >=1 KEEP -> PILOT (80
draws, seed 0xB542). Pilot live; adjudicate when "PILOT COMPLETE"
lands in `batch54/pilot.log`.

**Trigger:** batch-53 CLOSED 2026-10-11T21:34:42Z — Q1 adjudication
RE-VERIFIED FROM RAW ARTIFACTS by XXVI (not trusted from the brief):
`batch53/q1_t6_b53_h0/q1_t6_b53_h0.json` sac_z5=9 (N=262144,
key 0x123456789abcdef0, all 64 bits in the log, wall 589.5s);
`run_b53_battery.log` staged verdicts match the brief exactly
(h1/h3/h4 S1-screen rc=2 DIFF-kills; h0 S1 CAL_PASS, S3 PASS all 4
stages, S4 survivor; h2 excluded at S0 19.7u cost-doom per O92).
The hetMA5 axis is QUALITY-KILLED at the LAST gate — no frontier
challenger. Recorded as O95 in VERDICT_SCOPE.md.

## Axis audit (batches 19–53, 2026-10-12, incarnation XXVI)

The b52/b53 wall map stands, plus the b53 verdicts:

- <=4st: every sparse mechanism dead (b43 zero-corner, b44 tap-count,
  b46 hetero, b51 firing-geometry); dense-4st quality-alive but
  cost-doomed (22.9–28u).
- 5st: sparse-AND homogeneous dead (b43); MUX-5st homogeneous IS the
  19.3u frontier (hyb28_mu5_324); MUX-5st-no-d dead on mechanism (b52:
  d load-bearing); **hetMA5 (4xMUX+1xb33-AND) dead at Q1 (b53, O95)**.
- 3st: dead x4 distinct mechanisms.
- Cubic mining CUT on structural cost (b52 cut #1, unchanged — re-test
  trigger unmet).
- maj-5st DEPRIORITIZED (no measured cost thesis, unchanged).
- 3+2 MUX/AND: reserved escalation at b53 — its pre-registered
  condition ("4+1 keeps strongly") FAILED; see cut #3.

**The b53 position sub-read (raw-verified `pilot_keeps.jsonl`):** 5
hetMA5 keeps, and_pos 0/1/2/3/4 exactly one each, z=2.95/3.01/6.45/
9.18/9.89. AND@pos1 (h0, z=2.95) is the ONLY position to clear S1
(->S2->S3->S4, Q1 sac_z5=9); AND@pos2/3/4 (h4/h1/h3) S1-DIFF-killed
even though h1's triage z=3.01 < h0's 2.95; AND@pos0 (h2) cost-doomed
19.7u, quality untested. **The poisoning is schedule-PARTIAL, not
binary, and triage z does not rank it.**

## Selected axis: hetMA5p1 — AND@pos1-fixed + exact-DIFF-proxy schedule search

**The honest gap it fills:** b53 drew BLIND schedules with position as
a recorded variable and got exactly ONE S4-surviving schedule out of 40
draws. O86's corrected claim says the SELECTION method is the
differentiator: exact-DIFF-proxy-guided schedule search found t6_b33b
in a form where 7/7 wall-blind selections died, and t6_b33b then
passed the FULL battery including Q1 sac_z5=0. batch-54 applies the
proven selection method to the b53-measured quality-tolerant position.

- **Form:** 5 stages — 4x full MUX
  `x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)` + 1x b33 AND
  `x ^= (rotl(x,p)&rotl(x,q)) ^ rotl(x,r)` at stage index 1, FIXED
  (fail-loud assert). Pre-whiten `x ^= k`; final `x ^= rotl(k,13)`.
  Bit-identical frame to batch-53; the ONLY deltas are (a) the AND
  position prior, (b) a real schedule SEARCH (80 pilot draws) under the
  exact-DIFF proxy instead of blind draws.
- **Measured cost thesis:** hetMA5 S0 18.7–19.2u on 4/5 keeps
  (raw-verified `run_s0_b53.log`: h0=19.1, h1=19.2, h3=18.9, h4=18.7;
  XCHECK clean, ref mul64 103.5u) vs the STRICT <19.3u bar. The
  frontier attack stays cost-eligible by measurement, not projection.
- **Mechanism question (crisp):** is h0's Q1 SAC failure
  schedule-specific (a better AND@pos1 schedule clears it — the b33
  precedent says proxy-selected schedules pass full batteries) or
  form-fatal (the AND stage's single-bit linearity leaks into SAC at
  every schedule)?
- **Falsifier:** pre-pilot 12 draws (seed 0xB541): 0/12 with min z in
  b47-class (>=1e3) -> KILL LOUDLY (the pos1 variant dies at triage;
  hetMA5 form closed, O95's class claim covers it). 0/12 near-miss
  (min z < 100) -> PILOT (b53 precedent: 0/6 pre-pilot min z=14.5 ->
  5/40 pilot). >=1 KEEP -> PILOT (80 draws, seed 0xB542).
- **Pilot -> escalation:** >=1 KEEP -> bundle the min-z keep
  (`gen_b54_bundle.py`, bit-exact C-vs-Python 2000/2000 +
  screener-vs-bundle 500/500, the b53 pipeline verbatim) -> S0
  (stratified min/med/max-z if multiple keeps; bar STRICTLY <19.3u,
  XCHECK clean) -> S1 fail-fast on first cost-eligible -> staged
  battery S1->S2->S3->S4 -> Q1 (sac_z5=0 mandatory). 0/80 keeps ->
  KILL: form closed at triage, scoped.
- **Terminal condition:** if the best pos1 schedule fails Q1 SAC again
  (or 0 keeps at pilot), record hetMA5 QUALITY-CLOSED at Q1 — scope:
  the tested construction (5st 4xMUX+1xb33-AND cascade, pre-whiten,
  rotl(k,13)) AND the class claim "one AND stage inside a 5-stage MUX
  cascade" (O95's scope). If a keep clears Q1 at <19.3u -> FRONTIER
  CHALLENGER, escalate per the b33 precedent.

## De-dup (grep-verified 2026-10-12, incarnation XXVI)

- hetMA5 with AND position CONDITIONED (fixed) + exact-DIFF-proxy-guided
  schedule search: NEVER run. b53 varied position uniformly and drew
  blind schedules (position was a recorded variable, not a prior);
  `grep -rn "hetMA5p1\|and_pos.*fixed"` over new_constructions/,
  hybrid/, adder_lat/ returns nothing.
- Ledger candidate rows: hetero rows are fz13_het5a/b (track-8 word-
  level FUSED 5st hetero, S1-killed 2026-10-09 — different frame;
  CLOSED), dd3_hetero_* (4r SPN round-heterogeneity — different family),
  fz24_g/h (nibble-chi — CLOSED by track-8 struct-kill + XXI's 19:23
  entry; the b45/b49/b50 stale "OPEN" notes are superseded).
- directed_design: no MUX-gate cascade (batch-9 keccak is the sparse
  `(ra&~rb)` term — different function).
- adder_lat: mux-cascade axis planned-never-executed — no conflict.

## Cuts recorded (defensible reason at each cut site)

1. **Cost-driven cubic S-box mining: stays CUT.** b52 cut #1's
   structural argument is unchanged (QLOW = AND-minimal floor by
   exhaustive probe; cubic => >=2 AND levels definitional; 3st budget
   needs proper <~5.1u < QLOW's ~5u; every structural delta points
   cost UP). No new evidence since b53. The re-test trigger stands
   (a MEASURED sub-5.1u-proper cubic S-box).
2. **maj-5st: stays DEPRIORITIZED, not killed.** No measured cost
   thesis (the maj gate is strictly richer than MUX by verified ANF;
   MU5's 3.86u/stage is measured with the cheaper gate). Unchanged
   since b53 — an honest priority call, not a verdict.
3. **3+2 MUX/AND hetero: CUT as escalation.** Premise (measured): its
   pre-registered condition was "4+1 keeps strongly"; b53 measured
   the opposite — 4+1 did NOT keep strongly (3/4 S1-DIFF-killed,
   the survivor Q1-SAC-killed). Inference: doubling the poisoning
   variable after a mechanism finding against the single-AND form is
   not escalation, it is anti-escalation. The condition's failure is
   recorded, not the axis's death — if hetMA5p1's mechanism finding
   ever reverses, the condition re-opens.
4. **AND@pos0/2/3/4 in the search: CUT on the b53 position sub-read.**
   Premises (measured, raw-verified): pos2/3/4 S1-DIFF-killed;
   pos0 cost-doomed 19.7u; only pos1 cleared S1-S4. Inference:
   conditioning the search on the single quality-tolerant position
   is strictly more informative per draw than re-probing killed
   positions. Scope: this batch's search prior, not a class claim
   about positions (pos0's quality is untested — single cost sample).
5. **MUX-6st full form: CUT on measured per-stage cost** (b53 cut #4
   unchanged: 6x3.86=23.2u > 19.3u by arithmetic).
6. **d -> constant XOR on MUX stages: CUT on the b52 mechanism
   finding** (b53 cut #3 unchanged: a constant XOR provides zero
   mixing and cannot supply what the no-d kill removed).
7. **Control arm (muxS5d): CUT for this batch.** Premise: the harness
   is already validated — the b52/b53 calibration pair (and1/b33c
   z=3.3 exact + MU5-324 z<10) is the falsifier's health gate, and
   the b53 baseline (blind draws: 5/40 keeps, best outcome Q1-kill
   at sac_z5=9) is the historical comparator. Inference: re-running
   40 control draws buys zero new information; the comparison this
   batch needs is proxy-guided-pos1 vs blind-uniform, and the blind
   side is already measured.
8. **Different AND forms (ANDN / OR-AND) in the hetero: CUT for this
   batch.** No mechanism evidence they avoid the SAC poisoning that
   killed h0 at Q1; the pos1+proxy axis is the measured-evidence
   direction. Not killed — a possible follow-up if hetMA5p1 produces
   a new mechanism finding.
9. **Track-1 next-tweak-batch as batch-54: CUT for this batch.**
   Unchanged from b53 cut #11: the sweep is terminal COMPLETE (1220
   probed); winners sit at 36.7–38.6u, ~2x the 19.3u frontier; stays
   deferred for a coordinator design call. (Audit note: the deferred
   lead is unowned; this supervisor does not pick it up — out of
   lane.)

## Harness

- `batch54/t6_b54_screen.py` — adapted from b53's verbatim
  (calibration + selftest + draw constraints + exact-DIFF triage
  unchanged; only the form changed: `hetMA5p1` with AND@pos1 fixed,
  fail-loud asserts). py_compile clean; `selftest` PASS (AND3
  zero-corner = x^rc bit-exact; MUX gate popcount=1; degeneracy
  asserts fire); 1-draw smoke PASS (try-line + andpos=1, assert path
  exercised).
- Fail-loud calibration: CALIB-1 and1/b33c z=3.3 EXACT;
  CALIB-2 MU5-324 z<10 (the b52/b53 pair). Seeds 0xB541/0xB542.

## Backoff / launch log

- Pre-pilot `run_b54_prepilot.sh`: cleared-flag backoff pattern (the
  fixed b53-pilot template; the double-gate is never re-added —
  AGENTS.md lesson); calibration fail-loud -> hetMA5p1 12 draws
  0xB541 -> `prepilot_keeps.jsonl` -> "PRE-PILOT COMPLETE".
- Launch: `setsid agentwork-launch.sh --nice 19 --tag
  track6/b54-prepilot` (setsid per the batch-43 precedent).
- Heartbeat: `batch54/heartbeat.txt` touched at launch; re-touch
  every 30 min while live.
- **Frontier unchanged**: hyb28_mu5_324 at 19.3u.
- **Next**: adjudicate pre-pilot per the pre-registered rules above
  when "PRE-PILOT COMPLETE" lands in `batch54/prepilot.log`.
