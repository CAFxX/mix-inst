# Round 16 — Verdict-scope re-tests + parsplit variants

**Date:** 2026-10-03. **Frontier after round:** UNCHANGED
{r13_feist6_alt_s1chi_nw: 40.1u, r15_feist6_parsplit_nw: 40.7u,
r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u}.

**Multiplier reference:** 103.5u (re-measured fresh in the pinned Yosys-0.69
flow; S0 bar ≤ 93.15u). All 12 candidates pass S0.

## Families

- **F1** — [re-test O1, HIGH] crypto S-boxes in HETEROGENEOUS rounds:
  odd rounds XBOX-F = lin(3,11)(XBOX(R))^rk, even rounds chi-F, 6r.
  XBOX in {GIFT, PRESENT, SKINNY-4 (corrected table)}. r11 tested crypto
  S-boxes only in the homogeneous single-S-box-F slot; here only 3/6 rounds
  pay S-box cost (different economics).
- **F2** — [re-test O2, MEDIUM] 3-rotation linear in chi-F rounds:
  odd S1-F(3,11), even chi-F with lin3 = x^rotl(x,a)^rotl(x,b)^rotl(x,c),
  (3,7,11) and (7,13,19). r12 tested 3-rot lin only with S1-F.
- **F3** — parsplit variants (r15 parsplit: t[31:16]=chi16(R[31:16]),
  t[15:0]=S1(R[15:0]), F=lin(3,11)(t)^rk, 6r):
  `rev` (S1 high / chi16 low), `713` (lin(7,13)), `chioff23` (chi16 offsets
  (2,3)), `w24` (S1 on 24 bits + chi8 on high 8 bits), `giftsplit` (GIFT low /
  chi16 high).
- **F4** — (S1-F, parsplit-F) alternation: odd rounds r13 S1-F, even rounds
  r15 parsplit-F, 6r.
- **F5** — [re-test O5, LOW] mid-key on the alt structure: odd rounds
  F=lin(3,11)(S1(R)^rk), even rounds F=lin(3,11)(chi32(R)^rk). r13 tested
  mid-key only on the r9 (homogeneous) structure.

All: 32-bit halves, {R,L} output, NO whitening, affine r7/r8/r9 key schedule.
Generator: `round16/gen_r16.py`; reference: `round16/models/r16.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 for all 12 — first try on all
novel conventions (crypto-S-box DNF layers, chi16/chi8 offsets, 3-term
linear, mid-key alt, parsplit variants, S1/parsplit alternation).
DNF self-test: 4 tables x 4 bits x 16 inputs; chi16/chi8 spot-check vs
independent bit loops (3 offset-pairs x 200 vectors); lin3 spot-check vs
independent shift-or (2 triples x 200 vectors). Dedupe: all 12 specs
pairwise-distinct by numpy model output before generation.

## S0 (run_synth.py, authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r16_feist6_parsplit_chioff23_nw | 40.7u | 0.393× | 4,479 | 12,591 | ties r15 parsplit delay, larger — dominated |
| r16_feist6_parsplit_rev_nw | 40.9u | 0.395× | 4,639 | 13,096 | dominated by r13 alt |
| r16_feist6_parsplit_w24_nw | 41.0u | 0.396× | 4,813 | 13,351 | ties r9 delay, larger — dominated |
| r16_feist6_alt_s1ps_nw | 41.0u | 0.396× | 4,438 | 12,532 | ties r9 delay, larger — dominated |
| r16_feist6_gift_het_nw | 41.8u | 0.404× | 5,265 | 15,123 | dominated |
| r16_feist6_parsplit_713_nw | 42.4u | 0.410× | 4,619 | 13,018 | dominated |
| r16_feist6_alt_lin71319_nw | 42.5u | 0.411× | 5,123 | 14,535 | dominated |
| r16_feist6_sk4_het_nw | 42.6u | 0.412× | 4,739 | 13,379 | dominated |
| r16_feist6_giftsplit_nw | 43.0u | 0.415× | 5,103 | 14,582 | dominated |
| r16_feist6_alt_lin3711_nw | 43.4u | 0.419× | 5,102 | 14,428 | dominated |
| r16_feist6_present_het_nw | 44.7u | 0.432× | 5,160 | 14,535 | dominated |
| r16_feist6_alt_midk_nw | 45.1u | 0.436× | 5,753 | 16,088 | dominated |

No candidate is Pareto-eligible on (delay, cells, area): every point is
dominated by at least one frontier point. Per the round-11/round-14
precedent, S2/S3/S4/Q1 are not run (no frontier claim exists to gate);
S1 is run to completion because the verdict-scope re-tests need the
statistical answer, not just the delay answer.

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r16_feist6_gift_het_nw | **CAL_PASS** | full screen clean |
| r16_feist6_present_het_nw | **CAL_PASS** | full screen clean |
| r16_feist6_sk4_het_nw | **CAL_PASS** | full screen clean |
| r16_feist6_alt_lin3711_nw | **CAL_PASS** | full screen clean |
| r16_feist6_alt_lin71319_nw | **CAL_PASS** | full screen clean |
| r16_feist6_parsplit_rev_nw | **CAL_PASS** | full screen clean |
| r16_feist6_parsplit_713_nw | **CAL_PASS** | full screen clean |
| r16_feist6_parsplit_chioff23_nw | **CAL_PASS** | full screen clean |
| r16_feist6_parsplit_w24_nw | **CAL_PASS** | full screen clean |
| r16_feist6_giftsplit_nw | **FLAG** | LIN rej=1, DIFF PASS (marginals skipped on LIN/DIFF kill) |
| r16_feist6_alt_s1ps_nw | **CAL_PASS** | full screen clean |
| r16_feist6_alt_midk_nw | **CAL_PASS** | full screen clean |

11/12 pass S1. S2/S3/S4/Q1 not run: no candidate is Pareto-eligible on S0,
so no frontier claim exists to gate (round-11/round-14 precedent). S1 was
run to completion because the verdict-scope re-tests need the statistical
answer, not just the delay answer.

## Findings (2026-10-03)

**FRONTIER UNCHANGED.** 12 candidates, 11 S1 passes, 0 Pareto-eligible on S0.
The round's value is entirely in the verdict-scope re-tests:

1. **[O1 re-test, HIGH] Crypto S-boxes in heterogeneous rounds are
   statistically clean but still delay-dominated.** GIFT-het (41.8u),
   PRESENT-het (44.7u), SKINNY-4-het (42.6u) all CAL_PASS — the r11
   statistical story is not the problem; the delay cost is. The
   heterogeneous-economics argument was directionally right (SKINNY-4 het
   is 2.9u faster than SKINNY-4 homogeneous at 45.5u) but insufficient:
   deeper S-boxes cost 1.7–4.6u even when only 3/6 rounds pay. Refined
   ledger claim: "crypto 4-bit S-boxes cost 1.7–4.6u in heterogeneous
   rounds (vs 3–8u homogeneous); statistical quality holds."
2. **[O2 re-test, MEDIUM] 3-rotation linear is statistically fine with chi-F.**
   Both (3,7,11) and (7,13,19) pass S1 CAL_PASS — the r12 LIN kill does NOT
   reproduce with chi-F. The remaining objection is pure delay
   (43.4u/42.5u vs 40.1u). Refined: "3-rot lin fails LIN with S1-F;
   statistically clean but delay-dominated with chi-F."
3. **[O5 re-test, LOW] Mid-key on the alt structure is statistically clean
   but worse on delay.** 45.1u CAL_PASS (vs 50.3u on r9). Closed: mid-key
   is dominated on both structures.
4. **Parsplit variants all dominated.** Reversed split 40.9u, (7,13) 42.4u,
   w24 41.0u — none beats r15 parsplit (40.7u/4,318/12,356). chi16 offsets
   (2,3) tie r15's delay at 40.7u but cost cells (4,479 vs 4,318): the
   (1,2) chi16 remains the right one.
5. **giftsplit fails LIN (rej=1): GIFT on only 16 bits of a parsplit F is
   statistically weak**, while full-width GIFT-het passes. Partial-width
   crypto layers leave weak spots — consistent with r12's partial-S-box
   lesson (S2-killed on un-S-boxed bits), now reproduced at the S1 LIN
   level with a different primitive.
6. **(S1-F, parsplit-F) alternation: 41.0u, dominated** — mixing two good
   Fs across rounds does not beat either alone (same lesson as r14's
   stacking result, at the round level).

## Evidence locations

- Candidates: `exploration/fast_battery/candidates/r16_*/`
- S0: `round16/s0/*.log` (RESULT lines; ref mul 103.5u); S1: `round16/s1/*.log`
- xcheck: `round16/xcheck/` (12/12 PASS 10k/10k); rtlcheck: `round16/rtlcheck/`
  (12/12 PASS 300/300)
- Generator: `round16/gen_r16.py`; reference: `round16/models/r16.py`
- Generator: `round16/gen_r16.py`; reference: `round16/models/r16.py`

## Process notes

1. run_s1.sh's progress-line grep (`CAL_PASS|CAL_FLAG|KILL`) does not match a
   bare `verdict: FLAG` line — giftsplit's FLAG was recorded correctly in
   its log but the progress line showed an empty verdict. Future round
   scripts should grep `CAL_PASS|FLAG|KILL` (bare FLAG included). The logs,
   not the progress lines, are the record — no verdict was missed.
2. The (i+2) round-key derivation discipline held for all novel conventions
   (crypto-S-box DNF, chi16/chi8 offsets, lin3, mid-key alt): check_rtl
   300/300 first try on all 12.
3. Dedupe: all 12 specs pairwise-distinct by numpy model output before
   generation (assert capable of failing; passed).
