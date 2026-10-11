# Batch-44 design note — dual-nonlinear-tap cascades (track 6, 2026-10-11)

**Status: PILOT LAUNCHED** (track-6 supervisor incarnation XIV).
Trigger: batch-43 COMPLETED 2026-10-11T09:48:05Z, all three
complemented-output 5-stage arms 0/40 (axis closed, VALID scoped kill).

## Axis
AND + OR-mask cascades, NO linear mask. Two arms:
- **andorM-5**: `x ^= (ra&rb) ^ (rc|rd)` @ 5 stages  (prize arm)
- **andorM-6**: `x ^= (ra&rb) ^ (rc|rd)` @ 6 stages  (mechanism control)

Pre-whiten `x ^= k`; final `x ^= rotl(k,13)` (same as b33c/b41/b43).

## Co-design rationale
The 5-stage wall evidence now reads (b42 + b43): neither a bijective final
nor complement-inverted firing breaches it — the wall lives in the
cascade's insufficient nonlinear depth. But "depth" is ambiguous between
**sequential nonlinear depth** (stages) and **nonlinear tap count**
(nonlinear ops per stage). The two quality-proven 5-stage forms BOTH have
>1 nonlinear tap per stage:
- MUX-5st (track-5 batch-28, IS the frontier 19.3u): 2 ANDs + OR per stage.
- dual-mask-5st (fused fz15_c, S1+S2 clean): 1 AND + 2 linear taps per stage.
The single-AND 5-stage form (1 tap) is multiply dead. **Hypothesis: the
5-stage wall is a tap-count deficit, and a second nonlinear tap per stage
breaches it.**

The OR-mask is the right second tap, not a second AND: b36's dual-AND2
`x ^= (ra&rb)^(rc&rd)` died 0/200 at triage — a second AND shares the
sparse-corner pathology (AND fires ~never on sparse inputs; killkey 0x0
dominates every killed arm). OR is dense-firing: on a single-bit input
`e_p`, `(ra&rb)=0` but `(rc|rd)` fires 2 bits — EVERY sparse input gets a
nonlinear response from the OR term where the AND term vanishes.

Cost thesis (measured, not estimated): the AND2 and OR2 compute IN
PARALLEL from rotated inputs (~1.5u), then a 2-level XOR tree
(`x ^ and_out ^ or_out`, ~1.8u) — the SAME gate depth as the frontier
stage `x ^= (ra&rb) ^ rc` (~3.3u measured, 19.8u/6). The OR-mask fuses
two diffusion taps into one nonlinear tap with NO extra XOR level
(contrast fz15_c's dual linear mask: 3 XOR levels, 4.5u/stage measured,
22.6u — cost-doomed). Projected: 5st ≈ 16.5u, 6st ≈ 19.8u. Real S0 on a
STRATIFIED keep sample decides (wave-38 lesson: triage z does not rank
S0 within a form).

**Falsifier:** 0/40 on the 5st arm with mins in the hundreds (the b43
signature) → tap-count does NOT breach the wall; the wall is sequential
nonlinear depth; close scoped. If 6st keeps while 5st dies → the form
has quality but the wall holds at 5 (cost-doomed vs 19.3u — close as
challenger, mechanism recorded).

## De-dup (grep-verified 2026-10-11)
- `x ^= (ra&rb) ^ (rc|rd)` (OR-mask, NO linear mask): NEVER triaged —
  zero hits for `(rc|rd)`, `|rd)` across new_constructions/t6_*.py,
  new_constructions/gen_t6_*.py, new_constructions/batch*/t6_*.py,
  fused/gen_fused*.py, hybrid/, directed_design/, adder_lat/.
- adder-lat al_orand6/al_orand4 (`x ^= (ra&rb) ^ (rc|rd) ^ re`): DIFFERENT
  form (extra linear mask `^re` = 3rd XOR level) AND different key
  schedule (per-stage key fold, O83-proven to introduce differential
  bias). O76's S1-FLAG was marginal-only (LIN/DIFF pass) — caution, not
  a kill; verdict scoped to its construction per VERDICT_SCOPE.md.
- b36 dual-AND2 `x ^= (ra&rb)^(rc&rd)`: different secondary gate
  (sparse-firing AND vs dense-firing OR); 0/200 triage kill is the
  motivation for OR, not a duplicate.
- b5 `andor` (`x ^= (ra&rb)|(rc&rd) ^ re`): OR of two ANDs + linear mask
  — different wiring and cost class (t6_andor6 29.5u dominated).
- fz15_c dual-mask `x ^= (ra&rb)^rc^rd`: linear masks, 4.5u/stage
  measured — the cost problem this form is designed to dodge.
- Sparse 2-input-gate complement space (wave-38 de-dup note): fully
  triaged — this batch does not touch it.

## Cuts recorded (defensible reason at each cut site)
1. **orandM-5 (`x ^= (ra|rb) ^ (rc&rd)`, OR-main + AND-mask): CUT from
   pilot, not killed.** Reason: gate-order sensitivity is a follow-up
   variable, not a pilot arm — the pilot answers the tap-count/wall
   question with the AND-main form (the frontier's gate order).
   Re-test trigger: if andorM-5 shows triage signal (any KEEP), orandM-5
   becomes the immediate next arm.
2. **4 stages: CUT.** Structurally dead three ways (fz16_a catastrophic
   S1 FLAG; xc4a S1-killed; dual4a S1-killed) + b34 d2a3@4st 0/200. No
   new mechanism proposed for 4st.
3. **7+ stages: CUT on measured cost.** 7 × 3.3u (frontier per-stage,
   measured) ≈ 23u > 19.3u. No quality question justifies it.
4. **Extra linear mask `^re`: CUT on measured cost.** fz15_c measured
   4.5u/stage with 3 XOR levels; the OR-mask already provides the second
   tap. The linear mask is pure cost.
5. **LIN proxy triage: N/A.** b39/b40/b41 precedent: DIFF-only triage for
   rotation cascades; the S1 LIN family gates escalation.
6. **Second AND as secondary (`(rc&rd)`): CUT on evidence.** b36
   dual-AND2 0/200 triage-killed; sparse-firing secondary shares the
   zero-corner pathology the OR secondary is designed to dodge.

## Cost bar
Strictly **<19.3u MEASURED** via run_synth.py, XCHECK clean — the live
frontier is hyb28_mu5_324 19.3u (11:05 entry), not b33c's 19.8u. (The
19.8u figure in the supervisor brief is stale; using it would admit a
dominated challenger.)

## Pipeline (b33 playbook + the two hard lessons)
1. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Positive control:
   and1/b33c → z=3.3 (fail-loud; run `calibrate` first). Keeps appended
   to JSONL per-try (b39 lesson).
2. S0: STRATIFIED sample of keeps (span the z range), bar strictly
   <19.3u MEASURED, XCHECK clean (lesson a: triage z does not rank S0).
3. S1 FAIL-FAST on the first cost-eligible keep (lesson b: exact-DIFF
   triage is blind to the marginal/inner-DIFF kills — do not batch all
   S0s first).
4. Survivors → staged battery S1→S2→S3→S4→Q1 (round13/q1_sacbic.py).

## Pre-registered kill rule
0/40 keeps on an arm with min orders of magnitude above bar → arm
closed, mechanism refuted for that form (scoped to the tested
construction). Both arms dead → the dual-nonlinear-tap hypothesis is
FALSIFIED; next axis per the widen directive (never stop silently).

## Draw constraints (fail-loud asserts)
`a == b` degenerates the AND term to `ra` (excluded); `c == d`
degenerates the OR term to `rc` (reduces to the known-dead frontier-5st
form — excluded). Duplicate stage-tuples re-drawn (b41 precedent).
Rotations drawn 1..63 (b43 convention).
