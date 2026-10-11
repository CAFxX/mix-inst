# Batch-52 design note — "muxS5nl": 5-stage 3-rotation MUX cascade, linear-term ablation (track 6, 2026-10-11)

**Status: CO-DESIGN COMPLETE / PRE-PILOT QUEUED.**
(track-6 supervisor incarnation XXII, 2026-10-11.)

**Trigger:** batch-51 CLOSED 2026-10-11T17:40:48Z — MUX-4st/MUX-3st both
0/6 with min z in b47-class (3823.6 / 54054.4); mechanism (b) CONFIRMED:
4 stages give insufficient nonlinear depth regardless of the gate's
firing. The cheapest no-zero-corner gate is closed ON MECHANISM at <=4st.
The frontier is still MU5 (MUX-5st, 19.3u). The next axis must attack
the frontier's own cost — not a new gate, but a cheaper stage for the
proven-quality gate.

## Axis audit (batches 37–51, 2026-10-11, incarnation XXII)

| Batch | Axis | Verdict | Scope |
|---|---|---|---|
| b37 | no-mask shift family | STRUCTURALLY DEAD, both arms 0/40 | mechanism confirmed+falsified |
| b38 | nested shift-AND | dead all 3 arms | boundary test |
| b40 | ormM6 / andnM6a | TERMINALLY CLOSED on 3-schedule S0 evidence (20.8/21.3/21.9u); andnM6a 21.8u closed as challenger; andnM5 killed | cost |
| b41 | complemented-output masked cascades | nandM6 29/40 keep (6st); 5st arms 0/40 | b43 closed 5st |
| b42 | odd-width (bijective) chi | both arms 0/40 | VALID scoped kill |
| b43 | violent-avalanche 5-stage | complemented-output 5st arms 0/40 | VALID scoped kill |
| b44 | dual-nonlinear-tap | andorM5 0/40 (5st wall holds for dual-tap) | VALID scoped kill |
| b45 | true chi S-box repeated stage | chiS5 40/40 KEEP (5st wall breached for dense degree-2); chiS4 10/40 KEEP; BOTH S0 cost-closed (22.9–23.2u) | quality-confirmed, COST-CLOSED |
| b46 | hetero 2xchi+2xAND interleave | hetCA4a/b 0/40 + 0/40 | VALID scoped kill |
| b47 | 3-stage dense-quadratic | chi3S-3/chi5S-3/maj3S-3 all 0/40 (min 2163/790/21319) | VALID kill |
| b48 | cheap-chi-stage (1-XOR linear) | CLOSED pre-pilot | proof (singular layer) + loud kills |
| b49 | bijective quadratic Q4 repeated stage | q4bS4 4/6 KEEP (quality-alive) but S0 28.0u COST-DOOMED | VALID scoped kill |
| b50 | minimal-AND quadratic QLOW repeated stage | qlowS4 2/40 KEEP (quality-confirmed) but S0 24.6/25.7u COST-CLOSED; QLOW = AND-minimal floor (exhaustive probe) | VALID scoped kill |
| b51 | MUX-4st/MUX-3st masked cascade | 0/6 + 0/6, min z 3823.6/54054.4 (b47-class) | mechanism (b) CONFIRMED, VALID kill |

**The wall map after b51:**
- <=4 stages: every sparse mechanism dead (b43 zero-corner firing, b44
  tap-count, b46 hetero, b51 firing-geometry for MUX); dense-4st is
  quality-alive (b45 chiS4 10/40, b49 Q4 4/6, b50 QLOW 2/40) but
  cost-doomed at 22.9–28u (the synthesis mapping taxes dense XOR
  forests ~55–75%; no synthesis-path fix in scope).
- 5 stages: sparse AND dead (b43/b44); MUX-5st (MU5) keeps 19/40 and IS
  the 19.3u frontier.
- 3 stages: dead for 4 distinct mechanisms (b47 x3, b49, b50, b51).

**The cubic-mining fallback — AUDITED, CUT (see cuts #1).** The
pre-registered fallback (b50 cut #4 trigger: "QLOW axis dies AND a
cost-viable cubic S-box is mined") does NOT survive the mechanism audit.
Its first condition is met (QLOW cost-doomed); its second condition
(a cost-viable cubic S-box) is empty by structure — see cut #1 for the
full argument. Running the miner would be theater: the target set
(cubic S-box proper <5.2u) contains no elements.

**Selected axis: (d) MUX-5st linear-term ablation.** The ONLY open
frontier attack with a measured cost thesis: cheapen MU5's own stage
by dropping the linear `d` term. Never screened (de-dup below). The
b51 cut #11 cut it only for 4st comparability — explicitly not as an
axis kill.

## Axis

Two arms (pre-whiten `x ^= k`; final `x ^= rotl(k,13)` — the
b33c/b45/track-5-MU5 frame; the ONLY delta from MU5-324 is the dropped
linear term):

- **muxS5nl** (prize): 5 stages of
  `x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b))`,
  mux(s,a,b) = (s&a)|(~s&b). No linear `d` term.
- **muxS5d** (control): 5 stages of the FULL MU5 form
  `x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)` with fresh random
  draws. Rationale: separates "d is load-bearing" (nl dies, d keeps)
  from "the draw distribution is bad" (both die) from "mechanism alive"
  (nl keeps). The MU5-324 calibration proves the full form CAN keep;
  the control measures its keep rate under random draws.

Draw constraints (fail-loud asserts): s,a,b in 0..63 pairwise distinct
(degeneracy proof: s==a -> mux=s|b; s==b -> mux=s&a; a==b -> mux=a —
b51 cut #10, unchanged); d in 0..63 free for the control arm.
Duplicate (s,a,b[,d]) stage-tuples re-drawn within a try (b41);
draw-loop cap 10000 (b45).

## Cost thesis (measured at S0, not estimated — bar strictly <19.3u)

MU5 measured 19.3u = 5 x 3.86u/stage. The per-stage critical path is
MUX (AND-OR, 2 levels) + XOR(mux_out, rd) + XOR(x) — dropping `d`
removes one full 64-bit XOR level from every stage's critical path
(~0.5–0.8u/stage by the QLOW-vs-Q4 per-AND delta class), projecting
**~16–17u < 19.3u** for 5 stages. The projection is directional only;
S0 measurement decides. If quality survives, this is a direct frontier
challenger built from the frontier's own proven gate.

## Mechanism question (crisp)

**Is the linear `d` term load-bearing for MUX-5st cascade quality?**

First-principles asymmetry (why this axis, not a blind ablation):
- AND form `x ^= (ra&rb) ^ rc` on single-bit input: (ra&rb) fires 0 bits
  (rotations separate the single bits — the b43/b47 zero-corner) -> the
  stage degrades to linear `x ^= rc`. Drop `rc` -> `x ^= (ra&rb)` is the
  IDENTITY on single-bit inputs: catastrophic. **For AND, the linear
  term is load-bearing.**
- MUX form `x ^= mux(ra,rb,rc)` on single-bit input with s,a,b distinct:
  mux output at position p = (s_p&a_p)|(~s_p&b_p); at p=b: (0&0)|(~0&1)
  = 1; at p=s: 0; at p=a: 0 -> mux fires EXACTLY 1 bit (b's position).
  The stage stays nonlinear (1 bit in -> 1 bit out through the gate)
  with NO linear term. **For MUX, the linear term is plausibly NOT
  load-bearing** — the no-zero-corner firing that b51 proved insufficient
  at 4st may suffice at 5st without the linear crutch.

Sub-mechanisms: (a) d is redundant for MUX-5st -> nl keeps at a
MU5-comparable rate -> S0 decides the frontier; (b) d carries
irreplaceable diffusion/mixing -> nl dies at triage (0/6, b47-class)
while the d-control keeps -> axis closed WITH a mechanism finding (the
linear term is load-bearing for MUX-5st, unlike the zero-corner
analysis alone); (c) both die -> draw-distribution or 5st-form issue,
not a d-verdict (the MU5-324 calibration guards the harness).

**Falsifier:** 0/6 on muxS5nl with min z >= 1e3 (b47-class) AND the
muxS5d control keeping >=1 -> d is load-bearing -> axis closed scoped
to (5st 3-rotation MUX cascade, pre-whiten, rotl(k,13)). Any KEEP on
muxS5nl -> mechanism alive -> S0 spot-check -> pilot. 0/6 on BOTH arms
-> no d-verdict (mechanism question unanswered); diagnose draws before
any re-run.

**The two hard lessons (applied):**
(a) Triage z doesn't rank S0 within a form -> S0 on a STRATIFIED keep
    sample spanning the z range (min/median/max-z), never best-z-only.
(b) Exact-DIFF triage is blind to the S1 marginal/inner-DIFF kill -> S1
    FAIL-FAST on the FIRST cost-eligible keep.

## De-dup (grep-verified 2026-10-11, incarnation XXII)

- 5-stage 3-rotation MUX cascade (`x ^=` wiring, x NOT entering the gate,
  no linear term): NEVER screened. `grep -rn "mux" new_constructions/`
  hits only: b8 fused forms (F=MUX(x,ra,rb), x enters nonlinearly —
  different construction, killed b50 cut #7), b51 (4st/3st WITH d),
  track-5 MU5 (5st WITH d, the frontier). No 3-rot MUX screen anywhere.
- b51 cut #11 ("3-rotation MUX (dropping the linear d): CUT on
  comparability") cut it only to keep the 4st test's single variable
  (stage count); the cut text does not kill it as an axis.
- directed_design: no MUX-gate cascade (batch-9 keccak is the sparse
  `(ra&~rb)` term — different function).
- adder_lat: "4-stage non-AND nonlinearities (maj/mux/ternary)" listed
  as an axis to open (supervisor.log:16) — never executed for mux at
  ANY stage count (no *mux* candidates on disk). No conflict; track-6
  runs the 5st ablation.

## Cuts recorded (defensible reason at each cut site)

1. **Cost-driven cubic S-box mining (the pre-registered fallback): CUT
   ON STRUCTURAL COST ARGUMENT — the target set is empty.**
   Premises (all verified): (i) QLOW is the AND-minimal bijective
   quadratic 4-bit S-box (3 ANDs, 1 AND level) by b50's exhaustive
   pattern-fixed hard probe (20+15 patterns) — no cheaper quadratic
   repeated stage exists. (ii) QLOW S0 = 24.6/25.7u measured (XCHECK
   clean) = 6.2–6.4u/stage; S-box proper ~5u (b51 DESIGN.md). (iii) Any
   bijective CUBIC 4-bit S-box has >=2 AND levels — definitional (a
   degree-3 term needs 2 cascaded ANDs). (iv) The 3-stage budget is
   <6.43u/stage (<19.3u/3); with ~1.2–1.4u/stage of XOR-forest+wiring
   (from QLOW's measured split), a cubic stage needs S-box proper
   <~5.1u.
   Inference: the S-box proper's critical path traverses all AND levels
   (the cubic output bit depends on the cubic term); delay is monotone
   in AND-level count; a cubic ANF is strictly richer than QLOW's (more
   terms), so its XOR tree cannot be shallower enough to compensate a
   full AND level. Every structural delta (more ANDs, more levels,
   richer ANF) points cost UP from QLOW's ~5u proper. Therefore no cubic
   S-box satisfies proper <~5.1u — the miner's target set is empty, and
   running it would be theater (his 2026-10-11 order: never fabricate a
   queue to look busy).
   Re-test trigger: a MEASURED (not projected) sub-5.1u-proper cubic
   S-box, or a construction where the S-box proper leaves the per-stage
   critical path. (A cubic hetero micro-axis — 1–2 cubic stages among
   sparse — is not batch-worthy: b46's hetero-4st 0/80 and the cost
   argument above.)
2. **Hetero MUX+chi 4-stage: CUT (b46 + b51 mechanism (b)).** b46's
   2xchi+2xAND interleave went 0/80 at 4st, and b51's mechanism (b)
   (CONFIRMED: 4 stages give insufficient nonlinear depth regardless of
   the gate's firing) covers gate-mixing: hetero doesn't add stages.
   Re-test trigger: a 4st keep in ANY hetero form (none exists).
3. **MUX-4st-3rot (no-d wall probe): CUT as foregone.** b51's MUX-4st
   WITH the linear term died 0/6 at min z=3823.6; removing diffusion
   cannot revive a b47-class kill. Burning 6 draws to confirm is
   theater (b48 precedent).
4. **MUX-6st-3rot: CUT on measured-cost projection.** 6 x ~3.3u = ~20u
   > 19.3u even under the optimistic per-stage projection.
5. **MUX-5st schedule search for COST: CUT (rotations are wires).**
   Schedule selection changes quality (b33 precedent), not synthesis
   cost — the cost thesis here is structural (one fewer XOR level), not
   schedule-dependent.
6. **Fused MUX (x entering the gate): CUT on evidence** (b8 fmux6a/b
   killed; b50 cut #7; b51 cut #8).
7. **Per-stage round key: CUT on measured cost** (b8 5.0u/stage
   precedent; MU5's no-rk frame is the comparability basis; b45–b51
   precedent).
8. **Non-distinct (s,a,b) draws: CUT on degeneracy proof** (b51 cut #10:
   s==a -> s|b; s==b -> s&a; a==b -> a).

## Pipeline (b33 playbook + lessons)

1. Calibration: TWO gates, both fail-loud (`t6_b52_screen.py
   calibrate`): (i) and1/b33c must reproduce z=3.3 (harness sanity —
   proves the exact-DIFF code path is intact); (ii) MU5-324 schedule
   `[(62,50,55,2),(48,58,23,30),(44,45,7,40),(49,26,32,35),
   (46,51,43,44)]` through the FULL MUX stage (with d) must KEEP (z<10;
   b51 harness measured 3.24 — proves the MUX stage is wired right).
2. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Pre-pilot: 6 draws/arm
   (seeds 0xB521 muxS5nl, 0xB522 muxS5d). Keeps -> JSONL per-try
   appended immediately (b39). Fail-loud draw-loop cap 10000 (b45).
   Duplicate stage-tuples re-drawn (b41). s,a,b distinct asserted at
   draw.
3. Pre-registered pre-pilot verdict rules (see next section).
4. Escalation on any muxS5nl KEEP: bundle gen bit-exact 2000/2000 ->
   `gen_b52_bundle.py` (3-rot MUX stage; new) -> S0 via `run_synth.py`
   (bar strictly <19.3u MEASURED, XCHECK clean — ref mul64 103.5u) on a
   STRATIFIED keep sample (lesson a) -> S1 FAIL-FAST on the FIRST
   cost-eligible keep (lesson b) -> survivors staged battery
   S1->S2->S3->S4->Q1 (round13/q1_sacbic.py; sac_z5=0 mandatory for any
   Frontier-S claim).

## Pre-registered pre-pilot verdict rules

- Calibration FAIL on either gate -> no verdict; fix the harness.
- >=1 KEEP on muxS5nl -> **mechanism alive -> S0 spot-check on one
  schedule** (cost thesis: ~3.1–3.4u/stage at 5st; if S0 lands >19.3u,
  cost-doomed -> retained as evidence, closed) -> PILOT.
- 0 keeps on muxS5nl with min z >= 1e3 (b47-class) AND muxS5d keeping
  >=1 -> **KILL LOUDLY**: the linear d term is load-bearing for MUX-5st
  (mechanism (b) of this batch); axis closed scoped to the tested
  construction; no pilot; no S0. Recorded as a mechanism finding, not
  just a kill.
- 0 keeps on muxS5nl with min z < 100 (near-misses) -> NOT catastrophe
  -> **PILOT** (2x40 draws): the mechanism is alive enough to deserve
  the full pre-registered pilot.
- 0 keeps on BOTH arms -> no d-verdict (falsifier's control condition
  unmet); diagnose the draw distribution / harness before any re-run —
  do NOT close the axis on this outcome.
- Pre-pilot 0 kills at all (all keeps — GATE-FAIL) -> harness vacuous
  (script exits 2) -> fix the harness, no verdict.

## Pilot wiring (pre-registered, launched after pre-pilot adjudication)

- Scripts: `batch52/t6_b52_screen.py`, runner pattern
  `batch51/run_b51_prepilot.sh` (backoff-poll <=12h, setsid launch,
  tag track6/b52-prepilot).
- 2x40 draws: muxS5nl seed 0xB523, muxS5d seed 0xB524.
- Escalation: any muxS5nl pilot KEEP -> bundle gen bit-exact 2000/2000
  -> S0 stratified (bar <19.3u) -> S1 fail-fast -> staged battery.
- muxS5nl dead + muxS5d alive -> axis closed (VALID scoped kill with
  the load-bearing-d mechanism finding); cubic mining stays CUT per
  cut #1 (no fallback queue fabrication — the honest next step is a
  new co-design round).

## Backoff / launch log

- 2026-10-11 ~19:45–20:05 CEST: axis audit + co-design under incarnation
  XXII (this file). Pre-pilot queued backoff-gated on launch.
