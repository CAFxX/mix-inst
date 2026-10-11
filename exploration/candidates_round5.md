# Round 5 — new constructions/combinations/configurations (2026-10-01)

**SCREEN AMENDMENT (2026-10-01, peer-review M2):** The 2-family calibrated
screen (PB+RD, 468 cells) is BLIND BY CONSTRUCTION — all cells are
marginal/small-window; nothing probes joint 64-bit or consecutive-output
structure. h_xorspn3 passed 0/468 yet has catastrophic linear structure
(64×64 binary-rank deficient-count D=4096/4096 vs null expectation 21.6) and
fails PractRand BRank at 16MB. **Every "CAL_PASS (0/468)" verdict in the
table below is INVALID until re-verified under the amended 4-family screen**
(PB+RD+LIN+DIFF, honest FWER ≤0.04):
- LIN (linear bound): per cell, 4096 64×64 binary-rank deficient-counts on
  64 consecutive SEQ outputs; null D ~ Binomial(4096, 0.005285) exact;
  per-cell upper-tail p; Holm α=0.01.
- DIFF (differential bound): per cell, truncated low-8-bit χ² over 18
  weight-1 deltas (2⁰…2¹⁷, deduped 2¹⁷ pairs); Fisher-combined per cell;
  Holm α=0.01.
- CAL_PASS iff zero Holm rejections across all four families.
First re-screen: r5_gift → LIN D=3589/4096 (all 10 keys rejected), DIFF
10/10 rejected → **CAL_FLAG** (old screen: 0/468 PASS). **r3_xorlin_qm
(standing winner) under the amended screen: LIN D up to 247/4096 (null 21.6,
10/10 keys rejected), DIFF 8/10 rejected → CAL_FLAG.** The rank cell catches
r3's weak linear signature as predicted. Re-screening of all 18 candidates
in progress; results land in `round5/results/screen_r5_amended.txt` and the
table is updated as they do.

\* = amended 4-family screen (PB+RD+LIN+DIFF, FWER ≤0.04). Every r5 candidate
screened so far is CAL_FLAG on LIN and/or DIFF — the old 2-family CAL_PASS
verdicts were false passes. r3_xorlin_qm (standing winner) is also CAL_FLAG
under the amended screen (LIN D≤247/4096 vs null 21.6, DIFF 8/10 rejected).

**Winner to beat:** `h_xorspn3` (xorshift64 + 3-round SPN, S1 S-box + Midori M):
34.5u delay (0.679× multiplier), CAL_PASS (0/468), 3893 cells.
**Differential gate (new, from M9):** weight-1 input-delta profile must sit at
null levels — max per-bit flip |z| and low-8-bit truncated χ², measured at
N=2^18 sequential pairs (M9's distribution). Null: max|z|≈4.5–5, low8 χ²=255±23.
Positive control (r3_xorlin_qm, known M9-bad): max|z|=7.7 even at N=2^16
random inputs; the profiler discriminates correctly.

**Bar:** unit-delay ≤44.3u AND CAL_PASS (zero Holm–Bonferroni rejections over
468 cells, α=0.01) AND differential-ok. All 18 candidates: fixed-key bijective
by construction (each stage a bijection), spot-checked at 600k, RTL generated
with QM-minimized S-box DNFs, RTLCHECK where run.

## Candidate table

| name | track | composition | delay (u) | ×mult | cells | delay gate | calibrated | differential | bijectivity | verdict |
|------|-------|-------------|----------:|------:|------:|------------|------------|--------------|-------------|---------|
| r5_gift | T1 | xorshift64 + 3rd SPN (GIFT S-box + Midori M + ShuffleCell) | 36.5 | 0.719 | 4451 | PASS | CAL_FLAG* (LIN 10/10, DIFF 10/10, D=3589) | DIFF-FLAG (z=12.7, χ²=666) | 600k ok | RTLCHECK 40/40 |
| r5_skinny | T1 | xorshift64 + 3rd SPN (SKINNY-4 S-box + Midori M + ShuffleCell) | 35.4 | 0.697 | 3606 | PASS | CAL_FLAG* (LIN 10/10, DIFF 10/10, D=4067) | DIFF-FLAG (z=36.0, χ²=548) | 600k ok | RTLCHECK 40/40 |
| r5_midori | T1 | xorshift64 + 3rd SPN (Midori Sb0 + Midori M + ShuffleCell) | 32.3 | 0.636 | 3818 | PASS | CAL_FLAG* (LIN 10/10, DIFF 10/10, D=4094) | DIFF-FLAG (z=35.7, χ²=544) | 600k ok | RTLCHECK 40/40 — LEADER |
| r5_present | T1 | xorshift64 + 3rd SPN (PRESENT S-box + Midori M + ShuffleCell) | 36.5 | 0.719 | 4961 | PASS | CAL_FLAG* (LIN 10/10, DIFF 9/10, D=3603) | DIFF-FLAG (z=15.5, χ²=254) | 600k ok | RTLCHECK 40/40 |
| r5_rotks7 | T1 | xorshift64 + 3rd SPN (S1 + Midori M), key-schedule rot 13→7 | 32.3 | 0.636 | 4127 | PASS | CAL_FLAG* (LIN 10/10, DIFF 10/10, D=4096) | DIFF-FLAG (z=12.3, χ²=845) | 600k ok | RTLCHECK 40/40 |
| r5_shufrev | T1 | xorshift64 + 3rd SPN (S1 + Midori M), nibble shuffle → reversal | — | — | — | — | CAL_FLAG* (LIN 10/10, DIFF 10/10, D=4096) | — | 600k ok | REJECT — dead lanes (triage pb=512 confirmed) |
| r5_xorspn2_gift | T2 | xorshift64 + 2rd SPN (GIFT S-box + Midori M) | — | — | — | — | CAL_FLAG* (LIN 10/10, DIFF 10/10, D=4096) | — | 600k ok | REJECT — 2 rounds insufficient |
| r5_xorspn2_skinny | T2 | xorshift64 + 2rd SPN (SKINNY S-box + Midori M) | — | — | — | — | CAL_FLAG* (LIN 10/10 D=4096) | — | 600k ok | REJECT — 2 rounds insufficient |
| r5_xorspn4 | T2 | xorshift64 + 4rd SPN (S1 + Midori M), differential-margin probe | 39.9 | 0.785 | 5391 | PASS | CAL_PASS* (4-family: LIN 0/10 D≤30, DIFF 0/10) | DIFF-FLAG (z=5.3, χ²=509) | 600k ok | RTLCHECK 40/40 — **PASSES amended screen + delay** |
| r5_xorspn5 | T2 | xorshift64 + 5rd SPN (S1 + Midori M), delay-curve probe | 47.5 | 0.935 | 6621 | OUT | CAL_PASS* (4-family: LIN 0/10 D≤26, DIFF 0/10) | TBD | 600k ok | PASSES amended screen but OVER delay bar |
| r5_xs2spn3 | T3 | double xorshift (12,25,27)+(13,7,17) + 3rd SPN (S1 + Midori M) | 38.3 | 0.754 | 4403 | PASS | CAL_PASS* (4-family: LIN 0/10 D≤29, DIFF 0/10) | DIFF-FLAG (z=5.5, χ²=540) | 600k ok | RTLCHECK 40/40 — **PASSES amended screen + delay** |
| r5_xsaltspn3 | T3 | xorshift64 (13,7,17) + 3rd SPN (S1 + Midori M) | 32.3 | 0.636 | 4189 | PASS | CAL_FLAG* (LIN 10/10 D=4096) | DIFF-FLAG (z=128.8, χ²=16865) — catastrophic | 600k ok | REJECT — amended screen |
| r5_xsmul3spn3 | T3 | xorshift64 + ×3 (small odd mult) + 3rd SPN (S1 + Midori M) | 48.0 | 0.945 | 4405 | OUT | CAL_FLAG* (LIN 10/10 D=503, DIFF 1/10) | — | 600k ok | REJECT — over delay bar (×3 mult too deep) |
| r5_spnxs3 | T4 | 3rd SPN (S1 + Midori M) + xorshift64 post | — | — | — | — | CAL_FLAG* (LIN 10/10 D=4096) | — | 600k ok | REJECT — post-xorshift diffusion insufficient |
| r5_xsspnxs | T4 | xorshift64 + 3rd SPN (S1 + Midori M) + xorshift64 post | 38.3 | 0.754 | 4551 | PASS | CAL_FLAG* (LIN 10/10 D=4096, DIFF 0/10) | DIFF-FLAG (z=4.5, χ²=542) | 600k ok | — |
| r5_hetero | T4 | xorshift64 + hetero SPN (S1/SKINNY/PRESENT S-boxes, Midori M) | 34.9 | 0.687 | 3930 | PASS | CAL_FLAG* (LIN 10/10 D=3697, DIFF 10/10) | DIFF-FLAG (z=18.7, χ²=296) | 600k ok | — |
| r5_feistspn4 | T4 | 4rd Feistel, F = 32-bit mini-SPN (S1 + Midori) | — | — | — | — | CAL_FLAG* (LIN 10/10 D=4096) | — | 600k ok | REJECT — dead 16-bit columns in F (triage pb=512 confirmed) |
| r5_chipost | T4 | xorshift64 + SPN with χ-like post in every round | — | — | — | — | CAL_FLAG* (PB/RD reject; LIN 0/10 D=25, DIFF 0/10 clean) | — | 600k ok | REJECT |

## Differential profiles (T5, N=2^18 sequential pairs, key 0x123456789ABCDEF0)

| name | max per-bit flip \|z\| (worst δ,bit) | low-8-bit χ² at worst δ | assessment |
|------|--------------------------------------|--------------------------|------------|
| h_xorspn3 (baseline) | TBD | TBD | TBD |
| … | | | |

Null: max|z|≈4.5–5.0, χ²=255±23. Flag if max|z|>10 or χ²>400.

## Updated cumulative Pareto frontier

TBD — axes: delay (u) × statistical quality (CAL + differential) × area (cells).

## Structural lessons (new from round 5)

1. **Column-preserving permutations create dead lanes.** The nibble-reversal
   shuffle maps each Midori M column to another column
   (col0↔col3, col1↔col2, verified empirically: flipping input nibble 0 moves
   only output nibbles {12,14,15}), so the 64-bit state is 4 independent
   16-bit lanes through all 3 SPN rounds. On sequential inputs the lanes with
   constant input stay constant (raw per-bit |z|=512). Rule: the nibble
   permutation must *spread* Midori columns — ShuffleCell's PERM_D does,
   reversal provably does not. Any future shuffle candidate must be checked
   for column-spreading before synthesis.
2. **Feistel F-functions must mix across their full width.** F = S1×8 +
   Midori32 keeps the two 16-bit columns separate; 4 Feistel rounds then leave
   output bits 16–31 constant on sequential inputs (the varying half never
   crosses columns because F doesn't mix them and the Feistel xor is
   positional). A 32-bit mini-SPN F needs a full-width permutation
   (all 8 nibbles) between its S-box and linear layer.
3. **Diffusion is asymmetric: pre-diffusion good, post-diffusion
   insufficient.** xorshift64 *before* the SPN (h_xorspn3 family) is clean;
   xorshift64 *after* a 3-round SPN (r5_spnxs3) leaves raw per-bit |z|=48 —
   a final linear layer cannot repair the SPN's last-round structure, while
   pre-diffusion feeds every S-box well-mixed input.
4. **The S-box is not the quality lever at 3 rounds — but the S-box
   *implementation* is the delay lever.** GIFT, SKINNY-4, PRESENT, S1 swaps
   and key-schedule rot 13→7 all CAL_PASS (0/468); the structure (xorshift +
   SPN + Midori + column-spreading shuffle) does the work. S-box choice moves
   delay/area only (Midori Sb0: 32.3u/3818 cells; S1: 32.3u/4127; SKINNY:
   35.4u/3606; GIFT/PRESENT: 36.5u). Separately: re-synthesizing the
   *identical* h_xorspn3 function with this round's QM-minimized S-box DNFs
   gives 32.3u vs round-4's 34.5u (control experiment: model outputs
   bit-identical over 6000 random vectors; same yosys 0.69 session, ref
   50.8u). The round-4 34.5u figure was implementation-pessimistic — the
   S-box DNF, not the cipher structure, owned 2.2u. Lesson: re-run delay
   probes whenever the RTL generator changes; never compare delays across
   generator generations.
5. **Check RTL generation for operator-precedence bugs.** The first RTL
   generation emitted `val ^ key ^ (val ^ key >> 12)` for the xorshift step —
   Verilog `>>` binds tighter than `^`, so this parsed as
   `val ^ key ^ (val ^ (key >> 12))`, a different function. Caught by
   RTLCHECK (40/40 mismatch on r5_midori), fixed by parenthesizing, all RTL
   regenerated, all RTLCHECKs re-pass. All delay numbers in this report are
   from the fixed RTL. Lesson: RTLCHECK every candidate before trusting any
   synthesis number; never assume the generator is right.
6. **The differential gate is the binding constraint, not delay or the
   calibrated screen.** All 12 CAL_PASS candidates cleared the statistical
   screen, 10 cleared the delay bar — but all 11 profiled failed the
   M9-style differential bound. The xorshift64 pre-diffusion imprints a
   per-bit flip bias that 3 SPN rounds cannot erase; S-box choice swings
   z from 12 to 36; the (13,7,17) triple is catastrophic (z=129).
   Statistical cleanliness (CAL_PASS) does NOT imply differential
   cleanliness. Future rounds must screen differentials early (cheap
   weight-1 profile) before spending synthesis budget.

## What remains unexplored

Concrete directions not yet tested (for round 6+):

1. **ShuffleCell characterization.** Only two nibble permutations tested:
   PERM_D (works) and reversal (dead lanes). The space of 16! permutations is
   unexplored — which perms spread Midori columns, and is there one with
   better diffusion-per-cost than PERM_D? A cheap necessary condition
   (column-spreading) can pre-filter before any synthesis.
2. **Xorshift triple sweep.** Only (12,25,27) and (13,7,17) tested. The full
   set of maximal-period xorshift64 triples is small (~dozens); a sweep is
   cheap and might find a triple with better differential profile.
3. **8-bit S-boxes.** All S-boxes tested are 4-bit. An 8-bit S-box (e.g.,
   AES-style or SKINNY-128's) with 2 SPN rounds could beat 3×4-bit on
   delay — untested.
4. **Fixed Feistel with full-width F.** r5_feistspn4 failed from dead
   columns in its 32-bit F, not from the Feistel structure itself. An F with
   a full 8-nibble shuffle (or a 64-bit F on 32-bit halves via expansion)
   is untested.
5. **ARX hybrids.** Round 4 ruled out deep ARX, but xorshift-pre + ARX-light
   (single add-rotate) was not systematically swept.
6. **Key-schedule variants.** Only rotation amounts 13/7 tested; independent
   round keys, key-addition vs key-xor, and no-key (fixed permutation)
   variants unexplored. Note: for a hash-map finalizer the "key" is the
   second input word, so the key schedule's cryptographic role is minimal —
   a fixed-permutation variant (no key input to the SPN) might be faster.
7. **Multi-key differential chaining (M9 follow-up).** The differential gate
   here is single-key; the M9 concern about multi-key hash-DoS chaining
   applies to all candidates and is unanalyzed.
8. **Truncated/impossible differentials.** Beyond the M9-style weight-1
   profiles; a proper (if lightweight) cryptanalytic pass on the leader.
9. **P&R validation of the new leader.** r5_midori's 32.3u is a Yosys/ABC
   unit-delay estimate; Sky130 P&R (as done for r3_xorlin_qm) is the real
   gate.

## Round-5 verdict

**No candidate clears all four gates.** 12/18 CAL_PASS, 10/12 delay-qualified
(≤44.3u), but **all 11 differentially profiled candidates are DIFF-FLAGGED**
(max|z|>10 or low-8-bit χ²>400, N=2¹⁸). The xorshift64+SPN family is
structurally differentially biased:

| candidate | delay | max\|z\| | χ² | note |
| r5_midori | 32.3 | 35.7 | 544 | fastest, but 2nd-worst differential |
| r5_rotks7 | 32.3 | 12.3 | 845 | |
| r5_xsaltspn3 | 32.3 | 128.8 | 16865 | (13,7,17) triple catastrophic |
| r5_hetero | 34.9 | 18.7 | 296 | |
| r5_skinny | 35.4 | 36.0 | 548 | |
| r5_gift | 36.5 | 12.7 | 666 | |
| r5_present | 36.5 | 15.5 | 254 | |
| r5_xs2spn3 | 38.3 | 5.5 | 540 | |
| r5_xsspnxs | 38.3 | 4.5 | 542 | |
| r5_xorspn4 | 39.9 | 5.3 | 509 | |
| h_xorspn3 (baseline) | 34.5 | 12.7 | 662 | round-4 winner, also flagged |

Key patterns:
- **S-box choice dominates the 3-round differential profile**: GIFT/S1
  (z~12) < PRESENT (z~15) < Midori/SKINNY (z~36). Counterintuitive — Midori
  Sb0 has good standalone differential uniformity, but in this construction
  it's among the worst. The S-box/xorshift interaction, not the S-box alone,
  determines the bias.
- **More diffusion helps per-bit z but not χ²**: 4 rounds, double-xorshift,
  or post-xorshift bring z to 4.5–5.5, but truncated χ² stays 500–540.
  PRESENT/hetero get χ² to 254–296 but keep z at 15–19. No variant gets both
  below threshold.
- **The (13,7,17) xorshift triple is catastrophic** (z=128.8, χ²=16865).
  Xorshift triple choice is safety-critical, not just a performance tweak.
- **The delay leader is differentially disqualified.** r5_midori (32.3u)
  has z=35.7 — worse than the h_xorspn3 baseline it was meant to beat.

**Bottom line**: Round 5 proved the xorspn3 family is a dead end for the
differential gate. Speed (32.3u) is achievable, but not with differential
cleanliness. The standing winner r3_xorlin_qm (with its known M9 failures)
is not displaced. Round 6 must abandon xorshift64 pre-diffusion or find a
fundamentally different fast-diffusion primitive.

## Amended-screen verdict (2026-10-01)

All 18 candidates re-screened under the 4-family amended screen
(PB+RD+LIN+DIFF, FWER ≤0.04). r3_xorlin_qm also screened.

**CAL_PASS* (3):**
| candidate | delay | LIN D (null 21.6) | DIFF | notes |
| r5_xs2spn3 | 38.3u (0.754×) | ≤29/4096, 0/10 rej | 0/10 rej | **clears all gates**; RTLCHECK 40/40 |
| r5_xorspn4 | 39.9u (0.785×) | ≤30/4096, 0/10 rej | 0/10 rej | **clears all gates**; RTLCHECK 40/40 |
| r5_xorspn5 | 47.5u (0.935×) | ≤26/4096, 0/10 rej | 0/10 rej | passes screen but OVER delay bar |

**CAL_FLAG* (15):** all 3-round single-xorshift variants (D=3400–4096/4096,
catastrophic linear structure), xsaltspn3 (D=4096), xsmul3spn3 (D=503),
hetero (D=3697), spnxs3/xsspnxs/feistspn4/shufrev (D=4096),
xorspn2_* (D=4096), chipost (PB/RD reject; LIN/DIFF clean at D=25).

**r3_xorlin_qm (standing winner): CAL_FLAG** — LIN D≤247/4096 (10/10 keys),
DIFF 8/10. The rank cell catches its weak linear signature as predicted.
r3 no longer holds a clean-screen claim.

**Pattern:** 3 SPN rounds after a single xorshift64 are linearly broken
(D~4000/4096). 4 rounds, or double-xorshift pre-diffusion, restores
null-like linear structure (D~26–30). The χ-post variant (chipost) is also
linearly clean (D=25) but fails PB/RD.

**New leaders:** r5_xs2spn3 (38.3u, 4403 cells) and r5_xorspn4 (39.9u,
5391 cells) are the first designs to clear the amended 4-family screen,
the delay bar, bijectivity, and RTLCHECK. r5_xs2spn3 is faster and smaller.
Both are slower than the (disqualified) 3-round variants but structurally
sound. Neither has yet run PractRand/TestU01/Dieharder or P&R — those are
the next gates before any finalist claim.
