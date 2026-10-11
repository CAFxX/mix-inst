# Batch-51 design note — "muxS4": 4-stage MUX-gate masked cascade (track 6, 2026-10-11)

**Status: CO-DESIGN COMPLETE / PRE-PILOT QUEUED.**
(track-6 supervisor incarnation XXI, 2026-10-11.)

**Trigger:** batch-50 CLOSED 2026-10-11T17:02Z — QLOW quality-confirmed
(2/40, min z=3.1) but S0 cost-closed (24.6/25.7u vs 19.3u bar;
6.2–6.4u/stage vs <4.83u/stage budget). The dense-S-box line is now
cost-closed twice (Q4 7.0u/stage, QLOW 6.2u/stage): the S-box+XOR-forest
maps ~55–75% worse than projected, and no rotation schedule rescues a
schedule-independent per-stage cost. The next axis must attack the
cost thesis directly — the cheapest gate with dense-class quality.

## Axis audit (batches 19–50, 2026-10-11)

Three candidate leads were evaluated against the <19.3u bar:

**(a) fz24_g/h nibble-chi — DEAD, not opened.** The b45/b49/b50 de-dup
notes ("NEVER SCREENED, stay OPEN") are STALE: they grepped
new_constructions/ and fused/ logs but missed the LEADS_LEDGER
candidate table, where track-8 recorded on 2026-10-10:
- fz24_g: **STRUCT-KILLED** 11:35Z — proxy max|z|=256.0 (constant-dead
  output bit). Root cause: even-length chi has a systematic dead bit —
  single-bit input diff at within-nibble position i forces nch output
  bit (i+1)%4 to 0 for ALL x (chi_n is a permutation iff n is odd).
- fz24_i/j (nch2 dead-bit rescue): **PROXY-KILLED** 11:45Z, max|z|=256.0
  — "dead-bit fix and diffusion are in direct conflict for slice-chi."
- fz24_k/l (nch2L): **PROXY-KILLED** 12:00Z — "slice-chi axis TERMINAL."
Independently re-derived by this incarnation from the chi_4 definition
(Δq_i analysis: single-bit Δ at j → Δq_j≡1, Δq_{(j+1)%4}≡0,
Δq_{(j+2)%4}=~b_{(j+3)%4}, Δq_{(j+3)%4}=b_{(j+1)%4} — the (j+1)%4 bit is
dead ∀x). Combined with b47 cut #1 (chi_4 CUT ON PROOF: 16→12
non-bijective, b42 exhaustion proof), the nibble-chi axis is closed on
**proof + two independent measurements**. No pilot. The stale "OPEN"
notes in b45/b49/b50 are superseded by this entry.

**(b) Cost-driven cubic S-box mining (b50 cut-#4 trigger) — DEFERRED, not
batch-51.** Cost thesis evaluated and found weak: a cubic S-box needs
≥2 AND levels; QLOW (minimal quadratic: 3 ANDs, 1 level) measured
6.2–6.4u/stage, so a cubic stage projects ~7–8u → 3st ≈ 21–24u vs the
<6.43u/stage 3st budget. Viability would require the cubic S-box proper
<5.2u — *below* the measured minimal-quadratic S-box cost (~5u) while
carrying an extra AND level. Not impossible (the miner optimizes cost,
not DU), but strictly weaker than (c). The mining lead stays OPEN and
deferred; it is the fallback if (c) dies.

**(c) MUX-4st — SELECTED (strongest cost thesis).** 4-stage masked
MUX-gate cascade. Never screened (de-dup below). Cost thesis:
track-5's MU5 (identical stage form, 5 stages) measured **19.3u/5 =
3.86u/stage** → 4 stages project **≈15.4u < 19.3u (3.9u margin)** —
the strongest margin of any open axis. Quality mechanism: MUX is the
**cheapest no-zero-corner gate**. Zero-corner analysis (b37/b45):
- AND-mask `x ^= (ra&rb) ^ rc` on single-bit input: (ra&rb) fires 0
  bits (rotations separate the single bits) → stage degrades to linear
  `x ^= rc`. This is the b43/b47 5st/4st wall mechanism.
- MUX `x ^= mux(ra,rb,rc) ^ rd`, mux(s,a,b)=(s&a)|(~s&b), on single-bit
  input: s,a,b each carry 1 bit at distinct positions; mux output at
  p = (s_p&a_p)|(~s_p&b_p) fires at b's bit position (~s_p&b_p=1) → the
  mux FIRES ≥1 bit. No zero-corner degradation — the same property
  that makes chi stages quality-alive (b45), at 3.86u/stage instead of
  chi's 5.77u/stage.
The 5-stage wall was sparse-AND-specific; MUX-5st breached it (19/40
KEEP → frontier 19.3u). **Mechanism question: does MUX's no-zero-corner
+ denser gate buy enough for 4 stages, where AND-4st is dead (b43/b44)?
The triage decides.** Either outcome is informative: KEEP → a
~15.4u-class frontier challenger; 0/40 → the MUX wall sits at 5 stages,
closing the cheapest no-zero-corner gate on mechanism.

## Axis
Two arms (pre-whiten `x ^= k`; final `x ^= rotl(k,13)` — the
b33c/b45/track-5-MU5 frame; the ONLY delta from MU5-324 is the stage
count):

- **muxS4** (prize): 4 stages of
  `x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)`,
  mux(s,a,b) = (s&a)|(~s&b).
- **muxS3** (wall probe): 3 stages of the identical stage form.
  (Rationale: b47's 3st dense kills (chi3S-3 min 2163, chi5S-3 min 790,
  maj3S-3 min 21319) predict death, but a 3st MUX KEEP at ~11.6u would
  be a decisive frontier jump; the probe is cheap and pins the MUX
  wall location.)

Draw constraints (fail-loud asserts): s,a,b ∈ 0..63 pairwise distinct
(degeneracy proof: s==a → mux=s|b; s==b → mux=s&a; a==b → mux=a — all
collapse the 3-input gate); d ∈ 0..63 free (no degeneracy when d
coincides — linear term only). Duplicate (s,a,b,d) stage-tuples
re-drawn within a try (b41); draw-loop cap 10000 (b45).

## Cost thesis (measured at S0, not estimated — bar strictly <19.3u)
4st × 3.86u/stage ≈ **15.4u < 19.3u** (MU5 measured; 3.9u margin).
3st × 3.86u ≈ 11.6u (secondary bar, only if muxS4 lives). The per-stage
cost is schedule-independent (rotations are wires; the MUX gate + XOR
forest is the driver — MU5's 3.86u/stage already includes the 4-rotation
wiring). S0 measurement decides; the projection above is the
co-design bar.

## Mechanism question (crisp)
MU5 (MUX-5st) keeps 19/40 with min z=2.34 (frontier). AND-4st is dead
(b43 and5 0/10; b44 andorM5 0/40). chi-3st is dead (b47). **Does the
MUX gate's no-zero-corner firing (≥1 bit on single-bit input vs AND's
0) carry cascade quality at 4 stages, or does the wall hold for MUX
below 5?** Sub-mechanisms: (a) the zero-corner was the load-bearing
killer for AND at ≤5st, and MUX's firing repairs it → 4st keeps;
(b) 4 stages give insufficient nonlinear depth regardless of the gate's
firing (the b47 dense-wall reading) → 0/40. The triage decides; a
clean kill closes the cheapest no-zero-corner gate on mechanism, not
just cost.

**Falsifier:** 0/40 on both arms with min z in b47-class (≥1e3) or
b48-class (≥1e4) with killkey-0x0 dominance → wall holds for MUX at
4st; axis closed scoped to (4st/3st masked MUX cascade, pre-whiten,
rotl(k,13)). Any KEEP → mechanism alive → S0 spot-check → pilot.

**The two hard lessons (applied):**
(a) Triage z doesn't rank S0 within a form → S0 on a STRATIFIED keep
    sample spanning the z range (min/median/max-z), never best-z-only.
(b) Exact-DIFF triage is blind to the S1 marginal/inner-DIFF kill → S1
    FAIL-FAST on the FIRST cost-eligible keep.

## De-dup (grep-verified 2026-10-11, incarnation XXI)
- 4-stage masked MUX cascade (`x ^=` wiring, x NOT entering the gate):
  NEVER screened. Track-5 batch-28: MU5 (5st, 19/40 → frontier) and
  MU6 (6st, pilot died mid-run) only; no MU4 in hybrid/batch21 or
  anywhere else. Track-6 b8's fmux6a/b are FUSED forms
  (`F=MUX(x,ra,rb)`, x enters nonlinearly) — different construction,
  killed (b50 cut #7).
- adder_lat: "4-stage non-AND nonlinearities (maj/mux/ternary)" listed
  as an axis to open (supervisor.log:16) — never executed for mux (no
  *mux* candidates on disk). No conflict; track-6 runs it.
- directed_design: no MUX-gate cascade (batch-9 keccak is the sparse
  `(ra&~rb)` term — different function).
- All "mux" hits in new_constructions/ batches 19–50: b8 fused only.
- fz24_g/h/i/j/k/l: see axis audit (a) — closed, not duplicated.

## Cuts recorded (defensible reason at each cut site)
1. **fz24_g/h nibble-chi as batch-51: CUT ON PROOF + MEASUREMENT.**
   b47 cut #1 (chi_4 non-bijective 16→12, b42 proof) + track-8
   STRUCT-KILLED (proxy max|z|=256.0, 2026-10-10) + independent
   dead-bit re-derivation. Re-test trigger: none (proof, not samples).
2. **nch2/nch2L rescue forms (fz24_i/j/k/l): CUT ON MEASUREMENT.**
   Track-8 PROXY-KILLED max|z|=256.0: "dead-bit fix and diffusion are
   irreconcilable within budget." Re-test trigger: none within
   slice-chi.
3. **Cubic S-box mining as batch-51: CUT ON COST-THESIS (deferred, not
   killed).** 2 AND levels project ~7–8u/stage → 3st ~21–24u vs
   <6.43u/stage budget; needs cubic S-box proper <5.2u, below the
   measured minimal-quadratic cost with an extra AND level. The mining
   lead stays OPEN/deferred — fallback if muxS4 dies.
4. **chi_5-lane stage: CUT (b45 trigger answered).** b45 cut #1's
   re-test trigger (any chiS KEEP) was met, but b47 then measured
   chi5S-3 0/40 (min z=790, dead) and 4st projects ~23u > 19.3u.
   Re-test trigger: none.
5. **MUX-5st re-pilot: CUT.** It IS the frontier (track-5's axis);
   re-triaging it is theater.
6. **MUX-6st: CUT on measured cost.** 6 × 3.86u = 23.2u > 19.3u
   (track-5 MU6 in flight regardless).
7. **MUX-3st as prize arm: NOT cut — wall probe.** b47's 3st dense
   kills predict death, but the probe is cheap and a KEEP would be a
   decisive ~11.6u frontier jump; it pins the MUX wall location.
8. **Fused MUX (x entering the gate): CUT on evidence** (b8 fmux6a/b
   killed; b50 cut #7).
9. **Per-stage round key: CUT on measured cost** (b8 5.0u/stage
   precedent; MU5's no-rk frame is the comparability basis).
10. **Non-distinct (s,a,b) draws: CUT on degeneracy proof** (s==a →
    s|b; s==b → s&a; a==b → a). d left free (no degeneracy — linear
    term only; restricting it would be narrowing without reason).
11. **3-rotation MUX (dropping the linear d): CUT on comparability.**
    MU5's quality was proven WITH d; the ONLY delta from MU5 is the
    stage count (b45/b49/b50 discipline).

## Pipeline (b33 playbook + lessons)
1. Calibration: TWO gates, both fail-loud (`t6_b51_screen.py
   calibrate`): (i) and1/b33c must reproduce z=3.3 (harness sanity —
   proves the exact-DIFF code path is intact); (ii) MU5-324 schedule
   `[(62,50,55,2),(48,58,23,30),(44,45,7,40),(49,26,32,35),
   (46,51,43,44)]` through the MUX stage must KEEP (z<10; track-5
   measured 2.34 — proves the MUX stage is wired right).
2. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Pre-pilot: ~6
   draws/arm (seeds 0xB511 muxS4, 0xB512 muxS3). Keeps → JSONL
   per-try appended immediately (b39). Fail-loud draw-loop cap 10000
   (b45). Duplicate stage-tuples re-drawn (b41). s,a,b distinct
   asserted at draw.
3. Pre-registered pre-pilot verdict rules (see next section).
4. Escalation on any KEEP: bundle gen bit-exact 2000/2000 →
   `gen_b51_bundle.py` (MUX stage; new) → S0 via `run_synth.py` (bar
   strictly <19.3u MEASURED, XCHECK clean — ref mul64 103.5u) on a
   STRATIFIED keep sample (lesson a) → S1 FAIL-FAST on the FIRST
   cost-eligible keep (lesson b) → survivors staged battery
   S1→S2→S3→S4→Q1 (round13/q1_sacbic.py; sac_z5=0 mandatory for any
   Frontier-S claim).

## Pre-registered pre-pilot verdict rules
- Calibration FAIL on either gate → no verdict; fix the harness.
- 0 keeps both arms with min z ≥1e3 (b47-class) or ≥1e4 (b48-class)
  with killkey-0x0 dominance → **KILL LOUDLY**: the wall holds for MUX
  at 4st (mechanism (b) confirmed); axis closed scoped to the tested
  construction; no pilot; no S0. Next lead per the widen directive
  (cubic mining is the queued fallback).
- 0 keeps with min z < 100 (near-misses) → NOT catastrophe →
  **PILOT** (2×40 draws): the mechanism is alive enough to deserve the
  full pre-registered pilot.
- ≥1 KEEP on either arm → **mechanism alive → S0 spot-check on one
  schedule** (cost thesis: ~3.86u/stage at 4st; if S0 lands >19.3u,
  cost-doomed → retained as evidence, closed) → PILOT.
- Pre-pilot 0 kills at all (all keeps — GATE-FAIL) → harness vacuous
  (script exits 2) → fix the harness, no verdict.

## Pilot wiring (pre-registered, launched after pre-pilot adjudication)
- Scripts: `batch51/t6_b51_screen.py`, runner pattern
  `batch50/run_b50_prepilot.sh` (backoff-poll ≤12h, setsid launch,
  tag track6/b51-prepilot).
- 2×40 draws: muxS4 seed 0xB513, muxS3 seed 0xB514.
- Escalation: any pilot KEEP → bundle gen bit-exact 2000/2000 → S0
  stratified (bar <19.3u) → S1 fail-fast → staged battery.
- All arms dead → axis closed (VALID scoped kill); cubic mining
  promoted from deferred to active.

## Backoff / launch log
- 2026-10-11 ~19:05–19:35 CEST: axis audit + co-design under
  backoff-ENGAGED (2 frozen, shedder active at 19:05). fz24_g/h
  investigated first (brief's lead a): found DEAD via the ledger
  candidate table (track-8 2026-10-10 kills) + independent dead-bit
  re-derivation — the b45/b49/b50 "OPEN" notes are stale (de-dup
  missed the ledger table; process gap noted for future de-dups:
  always grep LEADS_LEDGER.md candidate rows, not just code dirs).
  Cubic thesis evaluated weak → deferred. MUX-4st selected: strongest
  cost thesis (15.4u projected, 3.9u margin), genuine mechanism
  question, never screened.
- Pre-pilot launch: queued below (wrapper backoff-polls ≤12h).
