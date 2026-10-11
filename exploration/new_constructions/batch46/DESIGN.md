# Batch-46 design note — hetero chi+AND interleave (track 6, 2026-10-11)

**Status: PILOT LAUNCHED** (track-6 supervisor incarnation XV).
Trigger: batch-45 CLOSED 2026-10-11T10:56:51Z — pure-chi cascade
QUALITY-CONFIRMED (chiS5 40/40 KEEP, median z=2.8; chiS4 10/40, two
sub-b33c keeps; the 5-stage wall was specific to sparse-gate cascades)
but COST-CLOSED (S0 22.9–23.2u vs <19.3u bar; cost thesis falsified:
5.77u/stage measured, not ~4.5u). This is the pre-registered
cost-engineering follow-up.

## Axis
4-stage HETERO cascade interleaving dense chi-S-box stages with cheap
sparse AND-mask stages — buy quality from chi, buy cheap depth from AND:

- **hetCA4a** (chi-led): chi, AND, chi, AND
- **hetCA4b** (AND-led): AND, chi, AND, chi

Stage definitions verbatim from their proven forms:
- chi stage: `y = chi3(x); x = y ^ rotl(y,a) ^ rotl(y,b)` (b45; 2 rotations)
- AND stage: `x ^= (ra&rb) ^ rc` (b33c; 3 rotations)

chi3 = chi_3 on 21 contiguous 3-bit lanes (bits 0..62), bit 63 identity
(b42 geometry). Pre-whiten `x ^= k`; final `x ^= rotl(k,13)` (same frame).

## Co-design rationale
Batch-45 proved dense chi stages carry the quality (5-stage wall
breached) but cost 5.8u/stage — 75% worse than the sparse AND stage's
3.3u/stage. The AND stage is quality-dead at 4st alone (structurally
dead three ways) but it is CHEAP depth: in a hetero cascade the chi
stages supply the nonlinear quality while the AND stages supply cheap
sequential depth. Cost thesis (measured components, S0 decides):
2×5.77 + 2×3.3 ≈ 18.1u < 19.3u — LIVE but tight (1.2u margin; the
b41 spread-settlement window is ~1.1u, so a clean S0 under bar with
margin is required — a borderline 19.0u would need a second schedule).

**Falsifier:** 0/40 on both arms with mins in the hundreds → the AND
stages reintroduce the sparse-corner weakness faster than the chi
stages repair it; hetero does not preserve chi quality; close scoped.
If one interleave keeps and the other dies → order matters (follow-up:
C-C-A-A block order). If both keep → S0 the best keep per pre-registered
plan.

## De-dup (grep-verified 2026-10-11)
- b8 t6_het5a: hetero with DIFFERENT ops (maj/andor/sparse-chi/
  majxor/xor3and, fused x-enters-nonlinearly + per-stage rk); S0 25.2u
  dominated. Different stage functions AND key schedule.
- b45: pure-chi cascade (this batch's parent) — hetero interleave is
  the explicitly pre-registered follow-up, not a duplicate.
- No batch (19–46) interleaved true-chi-S-box stages with AND-mask
  stages in a masked cascade (pre-whiten + final whiten, no per-stage rk).

## Cuts recorded (defensible reason at each cut site)
1. **5-stage hetero (3 chi + 2 AND): CUT on measured cost.**
   3×5.77 + 2×3.3 = 23.9u > 19.3u. No quality question justifies it.
2. **3-chi + 1-AND 4-stage: CUT on measured cost.**
   3×5.77 + 3.3 = 20.6u > 19.3u.
3. **Block order (C-C-A-A): CUT from pilot, not killed.** Reason: order
   is a follow-up variable — the pilot answers whether ANY 2+2
   interleave preserves chi quality. Re-test trigger: any hetCA KEEP
   → C-C-A-A arm next.
4. **chi_5 lanes: CUT from pilot.** Lane-width follow-up (b45
   precedent); re-test trigger = any hetCA KEEP.
5. **Per-stage round key: CUT.** b45 frame (pre-whiten + final whiten
   only); b8's rk-bearing hetero measured 5.0u/stage (cost-dominated).
6. **Fused stage forms: CUT on evidence.** b8's fused chi S1-killed;
   masked-cascade wiring is the quality-proven one.
7. **LIN proxy triage: N/A.** b39/b40/b41/b44/b45 precedent.

## Cost bar
Strictly **<19.3u MEASURED** via run_synth.py, XCHECK clean — the live
frontier is hyb28_mu5_324 19.3u.

## Pipeline (b33 playbook + the two hard lessons)
1. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Positive control:
   and1/b33c → z=3.3 (fail-loud; run `calibrate` first). Keeps appended
   to JSONL per-try (b39 lesson). Fail-loud draw-loop cap (b45 lesson).
2. S0: STRATIFIED sample of keeps (span the z range), bar strictly
   <19.3u MEASURED, XCHECK clean (lesson a: triage z does not rank S0).
   NOTE the tight margin: projection 18.1u leaves 1.2u — demand a clean
   sub-bar S0 with margin, else run a second schedule before any
   form-level claim (b41 spread-settlement precedent).
3. S1 FAIL-FAST on the first cost-eligible keep (lesson b: exact-DIFF
   triage is blind to the marginal/inner-DIFF kills).
4. Survivors → staged battery S1→S2→S3→S4→Q1 (round13/q1_sacbic.py).

## Pre-registered kill rule
0/40 keeps on an arm with min orders of magnitude above bar → arm
closed, hetero-does-not-preserve-quality for that order (scoped to the
tested construction). Both arms dead → the hetero cost-engineering
hypothesis is FALSIFIED; next axis per the widen directive.

## Draw constraints (fail-loud asserts)
Chi stage: rotations (a,b) drawn 1..63, a!=b (else linear layer =
identity). AND stage: (a,b,c) drawn 1..63, a!=b (else AND degenerates
to `ra`, linear). Duplicate (type, rotations) stage-tuples re-drawn
(b41 precedent).
