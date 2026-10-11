# Batch-43 design note — violent-avalanche 5-stage cascades (track 6, queued 2026-10-11)

**QUEUED, NOT RUNNING.** Track-6 supervisor incarnation XII is alive and its
batch-42 pilot (odd-width bijective chi final on 5-stage AND cascade) launched
2026-10-11 09:44 CEST and is in flight. Per the no-duplicate-supervisor rule,
this axis is QUEUED as batch-43: it runs when batch-42 concludes (either arm
dies → this becomes the next axis; batch-42 succeeds → re-evaluate). Do NOT
launch until batch-42's pilot completes. (Deconfliction record: subagent
007b254c, 2026-10-11 ~09:50 CEST.)

## Axis
Complemented-gate 5-stage rotation cascades. Three arms:
- **nandM-5**: `x ^= ~(ra & rb) ^ rc` @ 5 stages
- **norM-5**:  `x ^= ~(ra | rb) ^ rc` @ 5 stages
- **ornM-5**:  `x ^= (ra | ~rb) ^ rc` @ 5 stages  (input-complemented OR — never triaged)

Pre-whiten `x ^= k`; final `x ^= rotl(k,13)` (same as b33c/b41).

## Co-design rationale
The 5-stage wall is about **per-stage avalanche strength on the sparse corner**, not
stage count alone. Rank gates by single-bit-input flip count (sparse corner `e_p`,
`a != b`):
`AND 0 < ANDN 1 < OR 2 << NOR ~62 < NAND ~63, ORN ~63`.
Evidence: andnM-5 died 0/40 (batch-39) with the 1-flip gate; track-3's 5-stage
DIFF-wall theorem (0/500 hetero AND-masking pass); the only 5-stage single-mask
family to pass S1+S2 is fz15_c's DUAL-mask (22.6u, cost-doomed). Batch-41 proved
complemented-output gates have the best triage keep rates of any sparse form
(nandM 29/40, norM 22/40, best z 2.15/2.76) via the 0→ALLONES→0 2-cycle
(endogenous fixed-point breaking), but +0.3u/stage output-complement cost
killed them at 6 stages (21.5/21.9u). **This batch keeps the violent-avalanche
quality mechanism and fixes cost by stage count**: 5 stages × ~3.4-3.6u.
ornM is the untested violent gate that may dodge the output-complement cost
(complement on the input, like ANDN).

## De-dup (grep-verified 2026-10-11)
- nandM/norM @ 6st: batch-41 (cost-closed 21.5/21.9u). @ 5st: NEVER triaged
  (b41 logs show 6st pilots only).
- ornM (any stage count): NEVER triaged — zero hits for `ornM`, `(ra | ~rb)`,
  `(ra|~rb)` across new_constructions/batch*/t6_*.py, fused/gen_fused*.py,
  hybrid/, directed_design/, adder_lat/.
- Dual-mask 5st: fused fz15_c (22.6u S1+S2 PASS, cost-doomed); fz18 balanced-tree
  hypothesis FALSIFIED (synthesizer already optimal, 22.5u).
- andnM-5: batch-39 pilot 0/40 (dead). 4st: structurally dead three ways
  (fz16_a catastrophic S1 FLAG; xc4a S1-killed; dual4a S1-killed).

## Cost thesis (measured, not estimated)
- nandM-6 21.5u → ~3.42u/stage → 5st ≈ 18.1u. norM-6 21.9u → 5st ≈ 18.4u.
- ornM-5: input-complement gate, ANDN-class est ~3.6u/stage → ~19u.
- All under the 19.8u bar IF triage keeps exist. Real S0 on a STRATIFIED
  sample decides (wave-40 lesson: triage z does not rank S0 within a form).

## Cuts recorded (defensible reasons at the cut site)
1. **and1-5 / ormM-5: DEPRIORITIZED, not killed.** Reason: andnM-5 (sparse-corner
   gate strictly stronger than both — ANDN's 1-flip endogenous breaking beats
   AND's 0-flip fixed point and OR's 2-flip spread on the key-0 corner, per
   b39's mechanism analysis) died 0/40 with z in the hundreds–thousands.
   Prediction: both die. Re-test trigger: if nandM-5/norM-5/ornM-5 clear
   triage, the violent-avalanche hypothesis is confirmed and ormM-5 stays
   deprioritized; if they die too, the 5-stage single-mask wall is confirmed
   and this cut is revisited only with a new diffusion mechanism.
2. **Dual-mask 5st variants: CUT (covered).** fz15_c measured 22.6u; fz18
   falsified the tree-balancing fix. No headroom.
3. **Keyed AND inputs** (`x ^= ((ra^k1)&rb) ^ rc`): CUT on cost estimate — the
   key XOR adds a 4th logic level to the AND-input path (~+1.1u/stage,
   6st ≈ 26u). Re-test trigger: a keying that merges into existing levels.
4. **Complement-inside-mask** (`x ^= (ra&rb) ^ ~rc`): CUT as vacuous —
   `~rc = rc ^ ALLONES`, constant, synthesis-absorbed, DIFF-invariant.

## Pipeline (b33 playbook + the two hard lessons)
1. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys, sequential
   inputs, KEEP bar max|z|<10. Positive control: and1 + b33c schedule → z=3.3
   (fail-loud; run `calibrate` first). Keeps appended to JSONL per-try.
2. S0: STRATIFIED sample of keeps (4–6 spanning the z range), bar strictly
   <19.8u MEASURED via run_synth.py, XCHECK clean (lesson a).
3. S1 FAIL-FAST on the first cost-eligible keep (lesson b: exact-DIFF triage
   is blind to the marginal/inner-DIFF kills — do not batch all S0s first).
4. Survivors → staged battery S1→S2→S3→S4 → Q1 (round13/q1_sacbic.py).

## Pre-registered kill rule
0/40 keeps on an arm with margins orders of magnitude above bar → arm closed,
mechanism refuted for that gate (scoped). All three arms dead → the
violent-avalanche-5st hypothesis is FALSIFIED; next axis per the widen
directive (do not stop silently).

## Draw constraints (fail-loud asserts)
`a == b` collapses all three arms (nandM/norM → affine `x ^ ~ra ^ rc`;
ornM → `ra|~ra = ALLONES` → linear+const). Excluded from draws.
