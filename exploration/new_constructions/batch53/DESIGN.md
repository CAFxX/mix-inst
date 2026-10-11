# Batch-53 design note — "hetMA5": 5-stage hetero MUX/AND cascade (track 6, 2026-10-11)

**Status: PRE-PILOT ADJUDICATED -> PILOT LIVE (incarnation XXIV, 2026-10-11 ~21:34 CEST).**
Pre-pilot verified from raw artifacts: calibration PASS both gates,
hetMA5 0/6 KEEP min z=14.5 (seed 0xb531), muxS5d 2/6 KEEP min z=3.4
(seed 0xb532), 2 keeps in `prepilot_keeps.jsonl`, both arms exit=0,
"PRE-PILOT COMPLETE" 2026-10-11T19:19:21Z. Fired rule: 0 keeps with
min z < 100 (near-miss) -> NOT catastrophe -> PILOT (2x40 draws:
hetMA5 seed 0xB533, muxS5d seed 0xB534). Pilot live; adjudicate when
"PILOT COMPLETE" lands in `batch53/pilot.log`.

**Trigger:** batch-52 CLOSED 2026-10-11T18:40:25Z — KILL LOUDLY,
raw-verified by XXIII from `batch52/prepilot.log` (not trusted from the
ledger): calibration PASS both gates (CALIB-1 and1/b33c z=3.3 exact;
CALIB-2 MU5-324 z=3.24 KEEP), 12 try-lines, muxS5nl 0/6 KEEP
min z=12465.2 (seed 0xb521), muxS5d control 2/6 KEEP min z=3.2
(seed 0xb522), exactly 2 keeps in `prepilot_keeps.jsonl`, both arms
exit=0, "PRE-PILOT COMPLETE" 18:40:25Z. The pre-registered falsifier
(nl 0/6 b47-class AND control keeping >=1) triggered cleanly:
**the linear d term is load-bearing for MUX-5st cascade quality**.
The no-zero-corner firing (b51) is insufficient without the linear
mixing term. The frontier's own stage cannot be cheapened by ablation.
The next axis must change the stage MIX, not subtract from the stage.

## Axis audit (batches 19–52, 2026-10-11, incarnation XXIII)

The b52 wall map stands, plus the b52 verdict:

- <=4st: every sparse mechanism dead (b43 zero-corner, b44 tap-count,
  b46 hetero, b51 firing-geometry); dense-4st quality-alive (b45 chiS4
  10/40, b49 Q4 4/6, b50 QLOW 2/40) but cost-doomed 22.9–28u.
- 5st: sparse-AND homogeneous dead (b43); MUX-5st homogeneous IS the
  19.3u frontier (MU5 19/40 keeps, full battery PASS on 324);
  **MUX-5st-no-d dead on mechanism (b52: d load-bearing)**.
- 3st: dead on 4 distinct mechanisms.
- Cubic mining CUT on structural cost (b52 cut #1, unchanged — no new
  evidence; re-test trigger stands).
- AND-6st (b33 form): t6_b33b now FULL BATTERY PASS (S1 CAL_PASS, S2
  max_repeats=0 max|z|=21.2, S3 4-stage PASS, S4 rc=0, Q1 sac_z5=0
  bic=0.0091) at **20.1u** — terminal evidence the form CAN pass
  everything, but cost-blocked vs 19.3u (floor ~19.8–20.1u measured).
- adder_lat: all candidates >=19.8u S0 (al_chi8 26.1u) or S2-killed.
- Track-8 fz13_het5a/b (18.8/19.0u): S1 DIFF-killed 10/10 — but those
  are wave-13 WORD-LEVEL FUSED 5-stage hetero, a different frame from
  the per-stage MU5 cascade (see de-dup).

**Selected axis: (e) 5-stage hetero MUX/AND cascade (hetMA5).** The only
open frontier attack with a MEASURED cost thesis: keep 4 of MU5's proven
MUX stages, replace 1 stage with the cheaper b33 AND stage. Never
screened (de-dup below). The b52 cut #2 killed hetero MUX+chi at 4st
only — different stage count, different second gate, and b51's
mechanism (b) is <=4st-scoped.

## Axis

Two arms (pre-whiten `x ^= k`; final `x ^= rotl(k,13)` — the
b33c/b45/track-5-MU5 frame; the ONLY delta from MU5-324 is one stage's
gate swap):

- **hetMA5** (prize): 5 stages — 4x full MUX
  `x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)` + 1x AND
  `x ^= (rotl(x,p)&rotl(x,q)) ^ rotl(x,r)` (the b33 stage form verbatim).
  The AND stage's position is drawn Uniform{0..4} per try (fail-loud;
  recorded per try) — position-quality interaction is unknown, and
  fixing it risks a position-specific foregone conclusion.
- **muxS5d** (control): 5 stages of the FULL MU5 form with fresh random
  draws (the b52 control arm verbatim). Separates "hetero mixing is
  bad" (prize dies, control keeps) from "the draw distribution is bad"
  (both die) from "mechanism alive" (prize keeps).

Draw constraints (fail-loud asserts): MUX stages s,a,b pairwise
distinct (b51 cut #10 degeneracy proof); AND stage p,q,r pairwise
distinct (p==q -> `x ^= ra ^ rc`, a 2-XOR layer — strictly weaker,
proven by substitution); d free. Duplicate stage-tuples re-drawn
within a try (b41); draw-loop cap 10000 (b45).

## Cost thesis (measured at S0, not estimated — bar strictly <19.3u)

MU5 measured 19.3u = 5 x 3.86u/stage. The b33 AND stage measured
19.8u/6 = 3.3u/stage (t6_b33c S0). Replacing one MUX stage with one AND
stage projects **4x3.86 + 3.3 = 18.74u < 19.3u**. The projection is
directional only (synthesis need not compose additively); S0
measurement decides. If quality survives, this is a direct frontier
challenger assembled from two proven stage forms.

## Mechanism question (crisp)

**Does one AND stage poison the proven 5-stage MUX cascade, or does the
cascade absorb its single-bit linearity?**

First-principles (verified bit-exact in the harness unit check):
- AND stage on single-bit input: (ra&rb) fires 0 bits (rotations
  separate the single bits — the b43/b47 zero-corner) -> the stage
  degrades to LINEAR `x ^= rc` for that differential.
- MUX stage on single-bit input (s,a,b distinct): fires exactly 1 bit
  (b52 unit-verified) — stays nonlinear.
- The b33 AND-6st cascade keeps at S1 (t6_b33b full battery pass), so
  AND stages contribute quality at sufficient depth; the b43 wall says
  homogeneous sparse-AND dies at <=4st from exactly this degradation.

Sub-mechanisms: (a) the 4 MUX stages' diffusion absorbs the AND stage's
single-bit linearity -> hetMA5 keeps at a MU5-comparable rate -> S0
decides the frontier; (b) the AND stage poisons the cascade -> hetMA5
dies at triage (0/6, b47-class) while the MUX control keeps -> axis
closed WITH a mechanism finding (the zero-corner linearity is not
absorbable even inside a proven 5st MUX cascade); (c) both die ->
draw-distribution or 5st-form issue, not a hetero-verdict (the MU5-324
calibration guards the harness).

**Falsifier:** 0/6 on hetMA5 with min z >= 1e3 (b47-class) AND the
muxS5d control keeping >=1 -> the AND stage poisons the MUX-5st cascade
-> axis closed scoped to (5st 4xMUX+1xAND cascade, pre-whiten,
rotl(k,13)). Any KEEP on hetMA5 -> mechanism alive -> S0 spot-check ->
pilot. 0/6 on BOTH arms -> no hetero-verdict (falsifier's control
condition unmet); diagnose draws before any re-run.

**The two hard lessons (applied):**
(a) Triage z doesn't rank S0 within a form -> S0 on a STRATIFIED keep
    sample spanning the z range (min/median/max-z), never best-z-only.
(b) Exact-DIFF triage is blind to the S1 marginal/inner-DIFF kill -> S1
    FAIL-FAST on the FIRST cost-eligible keep.

## De-dup (grep-verified 2026-10-11, incarnation XXIII)

- 5-stage MUX/AND hetero cascade in the MU5 per-stage frame (`x ^=`
  wiring, pre-whiten, rotl(k,13)): NEVER screened. `grep -rn "mux"`
  over new_constructions hits only: b8 fused forms (F=MUX(x,ra,rb), x
  enters nonlinearly — different construction), b51 (4st/3st
  homogeneous WITH d), track-5 MU5 (5st homogeneous WITH d, the
  frontier), b52 (5st homogeneous no-d). No hetero MUX/AND cascade at
  any stage count.
- batch46: 4st 2xchi+2xAND interleave — different stage count AND
  different second gate (chi, not MUX).
- Ledger candidate rows grepped (the b51 fz24_g/h stale-note lesson —
  always grep the ledger, not just code dirs): hetero rows are
  fz13_het5a/b (track-8 wave-13 WORD-LEVEL FUSED 5-stage hetero,
  S1-killed 2026-10-09 — different frame: fused, not per-stage cascade;
  its "5-stage word-level fused dies at S1" verdict is scoped to the
  fused construction and does not transfer), dd3_hetero_* (4-round SPN
  round-heterogeneity — different family), fz_xor_trail (a finding, not
  a construction), fz_majx_4/5 (maj3 fused — different gate and frame).
  None is a 5st MUX/AND per-stage cascade.
- directed_design: no MUX-gate cascade (batch-9 keccak is the sparse
  `(ra&~rb)` term — different function).
- adder_lat: "4-stage non-AND nonlinearities (maj/mux/ternary)" listed
  as an axis to open (supervisor.log:16) — never executed for mux at
  ANY stage count in a cascade; no conflict.

## Cuts recorded (defensible reason at each cut site)

1. **Cost-driven cubic S-box mining (the pre-registered fallback): stays
   CUT.** b52 cut #1's structural argument is unchanged (QLOW =
   AND-minimal floor by exhaustive probe; cubic => >=2 AND levels
   definitional; 3st budget needs proper <~5.1u < QLOW's ~5u; every
   structural delta points cost UP). No new evidence since b52. The
   re-test trigger stands (a MEASURED sub-5.1u-proper cubic S-box).
2. **maj-5st: DEPRIORITIZED, not killed.** No measured cost thesis: the
   maj gate ((s&a)|(s&b)|(a&b), 3 product terms) is strictly richer than
   MUX (2 product terms) by verified ANF, and MU5's 3.86u/stage is
   measured with the cheaper gate — maj-5st would need <3.86u/stage with
   a costlier gate, and there is no evidence path to that. Priority
   goes to the axis with a measured per-stage delta (this batch). This
   is a priority call, not a verdict — maj-5st is NOT closed.
3. **d -> constant XOR on MUX-5st: CUT on the b52 mechanism finding.**
   Premises (verified): b52 showed the no-d form 0/6 b47-class while the
   full-form control kept 2/6 — the kill is attributed to lost
   diffusion/mixing, not to the XOR's presence. Inference: a constant
   XOR provides zero mixing (differential propagation is invariant under
   constant XOR — first-principles), so it cannot supply what the kill
   removed; it is the no-d kill with extra steps. No re-test trigger
   (mechanism-covered).
4. **MUX-6st full form: CUT on measured per-stage cost.** Premise:
   MU5 measured 3.86u/stage. Inference: 6 x 3.86 = 23.2u > 19.3u by
   arithmetic; adding stages only raises cost (schedule-independent per
   b52 cut #5). Scope: the homogeneous full-form MUX cascade.
5. **3+2 MUX/AND (two AND stages): CUT as pre-pilot scope, reserved as
   escalation.** The 4+1 is the minimal single-variable delta from the
   frontier; 3+2 doubles the poisoning risk. If 4+1 keeps strongly, 3+2
   is the natural follow-up (recorded in the escalation path).
6. **AND stage without its linear term (`x ^= (ra&rb)`): CUT on
   first-principles.** On single-bit input this is the IDENTITY (b52
   DESIGN.md: catastrophic — worse than linear). The b33 form's rc is
   load-bearing; the AND stage keeps it.
7. **Fixed AND position (e.g., always stage 2): CUT.** The
   position-quality interaction is unknown; fixing it risks a
   position-specific foregone conclusion. Varied position with per-try
   recording is strictly more informative at identical cost.
8. **Schedule search for COST within hetMA5: CUT (rotations are wires).**
   b52 cut #5 precedent: schedule selection changes quality (b33
   precedent), not synthesis cost — the cost thesis here is structural
   (one cheaper stage), not schedule-dependent.
9. **Per-stage round key: CUT on measured cost** (b8 5.0u/stage
   precedent; MU5's no-rk frame is the comparability basis; b45–b52
   precedent).
10. **Non-distinct rotation draws: CUT on degeneracy proofs** (MUX
    s,a,b distinct — b51 cut #10; AND p==q -> 2-XOR layer, proven by
    substitution).
11. **Track-1 next-tweak-batch as batch-53: CUT for this batch.**
    Premises (measured): the sweep is terminal COMPLETE (1220 probed);
    its winners sit at 36.7–38.6u, ~2x the 19.3u frontier. Inference:
    the frontier moved from the tweak family to the cascade family by
    construction change, not by tweaking — no tweak neighborhood
    bridges a 17u gap. The deferred lead stays deferred for a
    coordinator design call, but it is not a frontier-challenger axis.

## Pipeline (b33 playbook + lessons)

1. Calibration: TWO gates, both fail-loud (`t6_b53_screen.py
   calibrate`): (i) and1/b33c must reproduce z=3.3 (harness sanity);
   (ii) MU5-324 schedule through the FULL MUX stage (with d) must KEEP
   (z<10; b51/b52 harnesses measured 3.24).
2. Unit check (harness self-test, bit-exact): the AND stage on
   single-bit input degrades to `x ^= rc` (the mechanism's premise —
   verified, not assumed).
3. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Pre-pilot: 6 draws/arm
   (seeds 0xB531 hetMA5, 0xB532 muxS5d). Keeps -> JSONL per-try
   appended immediately (b39). Fail-loud draw-loop cap 10000 (b45).
   Duplicate stage-tuples re-drawn (b41). AND position recorded per try.
4. Pre-registered pre-pilot verdict rules (see next section).
5. Escalation on any hetMA5 KEEP: bundle gen bit-exact 2000/2000 ->
   `gen_b53_bundle.py` (4xMUXD + 1xAND3 stage; new) -> S0 via
   `run_synth.py` (bar strictly <19.3u MEASURED, XCHECK clean — ref
   mul64 103.5u) on a STRATIFIED keep sample (lesson a) -> S1 FAIL-FAST
   on the FIRST cost-eligible keep (lesson b) -> survivors staged
   battery S1->S2->S3->S4->Q1 (round13/q1_sacbic.py; sac_z5=0 mandatory
   for any Frontier-S claim). Position study on keeps (does the AND
   position matter?) -> 3+2 follow-up if 4+1 keeps strongly.

## Pre-registered pre-pilot verdict rules

- Calibration FAIL on either gate -> no verdict; fix the harness.
- >=1 KEEP on hetMA5 -> **mechanism alive -> S0 spot-check on a
  stratified keep sample** (cost thesis: ~18.7u projected; if S0 lands
  >19.3u, cost-doomed -> retained as evidence, closed) -> PILOT.
- 0 keeps on hetMA5 with min z >= 1e3 (b47-class) AND muxS5d keeping
  >=1 -> **KILL LOUDLY**: the AND stage poisons the MUX-5st cascade
  (mechanism (b) of this batch); axis closed scoped to the tested
  construction; no pilot; no S0. Recorded as a mechanism finding, not
  just a kill.
- 0 keeps on hetMA5 with min z < 100 (near-misses) -> NOT catastrophe
  -> **PILOT** (2x40 draws): the mechanism is alive enough to deserve
  the full pre-registered pilot.
- 0 keeps on BOTH arms -> no hetero-verdict (falsifier's control
  condition unmet); diagnose the draw distribution / harness before any
  re-run — do NOT close the axis on this outcome.
- Pre-pilot 0 kills at all (all keeps — GATE-FAIL) -> harness vacuous
  (script exits 2) -> fix the harness, no verdict.

## Pilot wiring (pre-registered, launched after pre-pilot adjudication)

- Scripts: `batch53/t6_b53_screen.py`, runner pattern
  `batch52/run_b52_prepilot.sh` (backoff-poll <=12h, setsid launch,
  tag track6/b53-prepilot).
- 2x40 draws: hetMA5 seed 0xB533, muxS5d seed 0xB534.
- Escalation: any hetMA5 pilot KEEP -> bundle gen bit-exact 2000/2000
  -> S0 stratified (bar <19.3u) -> S1 fail-fast -> staged battery.
- hetMA5 dead + muxS5d alive -> axis closed (VALID scoped kill with the
  poisoning mechanism finding); the honest next step is a new co-design
  round (no fallback queue fabricated — cubic mining stays CUT per
  cut #1).

## Backoff / launch log

- 2026-10-11 ~21:05–21:30 CEST: axis audit + co-design under incarnation
  XXIII (this file). Pre-pilot queued backoff-gated on launch.
- 2026-10-11 ~21:14 CEST: pre-pilot launched (setsid,
  tag track6/b53-prepilot). Backoff cleared after 2 polls (~19:13–19:18Z);
  calibration PASS; "PRE-PILOT COMPLETE" 19:19:21Z.
- 2026-10-11 ~21:34 CEST (incarnation XXIV): pre-pilot ADJUDICATED from
  raw artifacts (not the ledger): hetMA5 0/6 KEEP min z=14.5 < 100 =
  near-miss per the pre-registered rule -> NOT catastrophe -> PILOT.
  The stale ledger entry (~21:35, actually written ~21:14 CEST) claiming
  the pre-pilot is backoff-queued is SUPERSEDED — it was written while
  the pre-pilot was mid-flight. Pilot launched 19:34:03Z via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b53-pilot --
  bash run_b53_pilot.sh` (backoff-poll <=12h -> calibration fail-loud ->
  hetMA5 40 draws seed 0xB533 -> muxS5d 40 draws seed 0xB534 ->
  `pilot_keeps.jsonl` -> "PILOT COMPLETE").
- 2026-10-11 ~22:02 CEST (report run): FIRST PILOT WRAPPER DIED ON THE
  SPURIOUS DOUBLE-GATE BACKOFF-FAIL — pilot.log: "backoff clear after 2
  polls" 19:38:51Z, then the post-loop re-check flaked and the wrapper
  exited "BACKOFF-FAIL: load never cleared in 12h" (load never held 12h;
  the wrapper polled twice). Same race class killed the b50 pre-pilot
  wrapper 17:43Z. ROOT-CAUSE FIX: `run_b53_pilot.sh` patched to a
  `cleared` flag — no second backoff re-check after the loop; the flag
  is the single source of truth, the 12h deadline still fails loudly via
  the cleared==0 branch; per-poll backoff output now logged for
  diagnosis. All future wrappers must use this pattern. Pilot
  RELAUNCHED (setsid, tag track6/b53-pilot, nice 19).
