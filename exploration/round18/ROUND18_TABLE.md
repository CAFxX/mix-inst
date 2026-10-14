# Round 18 — parsplit offsets, truncation, palindromic key, asymmetric, chi variant

**Date:** 2026-10-03. **Frontier after round:** REPLACED — single point
{r18_feist6_alt_notr_nw: 37.9u / 4,119 / 11,621}.
It dominates ALL FOUR previous frontier points (r13 alt, r15 parsplit, r9,
r8) on delay, cells, and area.

**Multiplier reference:** 103.5u (pinned Yosys-0.69 flow; S0 bar ≤ 93.15u).
All 9 candidates pass S0.

## Families (all 6r Feistel, no whitening, affine r7/r8/r9 key schedule)

- **F1** — `ps_chioff13`: parsplit F with chi16 offsets (1,3) mod 16
  (incumbent (1,2); r17 killed (0,1) on DIFF, r16 showed (2,3) dominated).
- **F2** — `ps_chioff02`: parsplit F with chi16 offsets (0,2) mod 16.
- **F3** — `ps_s18_chi24`: parsplit with S1 on R[7:0] (2 nibbles), chi24 on
  R[31:8] with offsets (1,2) mod 24 — lighter S-box rounds.
- **F4** — `alt_notr`: **truncation probe** — r13 alt structure, but round 6
  (even/chi) F = chi32(R)^rk, no linear layer. Tests whether the final
  diffusion round's linear layer is load-bearing.
- **F5** — `alt_palk`: r13 alt with palindromic round keys
  rk_i = RK32(key,i) ^ RK32(key,7-i).
- **F6** — `alt_asym`: odd rounds full S1-F; even rounds
  F = lin(3,11)((R[31:16]<<16) | chi16(R[15:0]))^rk
  (chi on low half, passthrough high half).
- **F7** — `ps_517`: parsplit with (5,17) rotmix.
- **F8** — `s1xorchi`: F = lin(3,11)(S1(R) ^ chi32(R))^rk — XOR of nonlinear
  outputs BEFORE a single shared linear layer (r17's parmix had separate
  linears and died on DIFF).
- **F9** — `alt_chioff13`: r13 alt with even-round chi variant
  b_i = a_i ^ (~a_{i+1} & a_{i+3}).

Generator: `round18/gen_r18.py`; reference: `round18/models/r18.py`.
Structural note (premix lesson): all are plain balanced Feistel with an
arbitrary F — bijective in val for fixed key regardless of F; no novel
topology, no invertibility round-trip needed beyond the fixed-key bijection
self-test (2000 vals × 9 candidates, distinct OK).

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 for all 9 — first try on all
novel conventions (chi16(1,3)/(0,2), chi24(1,2), chi32v, palindromic key,
truncated final round). One generator bug caught by the chi self-test before
emission: `_rotrN_np` computed rotate-left instead of rotate-right
(self-test failed on chi16(1,3) as designed); fixed, all self-tests pass.
Dedupe: all 9 specs pairwise-distinct by numpy model output before
generation.

## S0 ([run_synth.py](../run_synth.py), authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r18_feist6_alt_notr_nw | 37.9u | 0.366× | 4,119 | 11,621 | **dominates all 4 frontier points** — full battery |
| r18_feist6_alt_palk_nw | 40.5u | 0.391× | 4,447 | 12,905 | not dominated (slower than r13 alt, smaller) — full battery |
| r18_feist6_alt_asym_nw | 37.8u | 0.365× | 4,167 | 11,812 | would-be dominator — S1-killed |
| r18_feist6_ps_chioff02_nw | 38.2u | 0.369× | 3,712 | 10,465 | would-be dominator — S1-killed |
| r18_feist6_alt_chioff13_nw | 40.1u | 0.387× | 4,661 | 13,273 | dominated (ties r13 alt delay, larger) |
| r18_feist6_ps_s18_chi24_nw | 40.4u | 0.390× | 4,944 | 14,052 | dominated |
| r18_feist6_ps_chioff13_nw | 41.1u | 0.397× | 4,593 | 12,912 | dominated |
| r18_feist6_ps_517_nw | 41.1u | 0.397× | 4,563 | 12,851 | dominated |
| r18_feist6_s1xorchi_nw | 50.5u | 0.488× | 5,451 | 15,264 | dominated + S1-killed |

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r18_feist6_alt_notr_nw | **CAL_PASS** | full screen clean |
| r18_feist6_alt_palk_nw | **CAL_PASS** | full screen clean |
| r18_feist6_alt_chioff13_nw | **CAL_PASS** | full screen clean (dominated — no S2 per r17 precedent) |
| r18_feist6_ps_chioff13_nw | **CAL_PASS** | full screen clean (dominated — no S2) |
| r18_feist6_ps_s18_chi24_nw | **CAL_PASS** | full screen clean (dominated — no S2) |
| r18_feist6_ps_517_nw | **CAL_PASS** | full screen clean (dominated — no S2) |
| r18_feist6_ps_chioff02_nw | **FLAG** | LIN/DIFF pass; marginal PB rej=190, RD rej=20 |
| r18_feist6_alt_asym_nw | **FLAG** | DIFF rej=10 (LIN pass) |
| r18_feist6_s1xorchi_nw | **FLAG** | DIFF rej=10 (LIN pass) |

## S2 (N=2^22, 115 deltas, kill threshold 10 — verified at call site)

| Candidate | S2 verdict | Detail |
|---|---|---|
| r18_feist6_alt_notr_nw | **PASS** | 0 repeats, max\|z\|=10.7 (all 115 deltas) |
| r18_feist6_alt_palk_nw | **PASS** | 0 repeats, max\|z\|=12.4 (all 115 deltas) |

## Q1 (SAC/BIC, N=2^18, mandatory sac_z5=0 for frontier claims)

| Candidate | sac_z5 | bic_maxcorr | avalanche_mean |
|---|---|---:|---:|
| r18_feist6_alt_notr_nw | 0 ✓ | **0.17247** (blemish — see finding 1) | 32.0004 |
| r18_feist6_alt_palk_nw | 0 ✓ | 0.00890 (clean, matches r13/r15 family) | 32.0009 |

Reference: r13 alt bic_maxcorr=0.00800, r15 parsplit bic_maxcorr=0.00842.

## S3 / S4

| Candidate | S3 PractRand | S4 SmallCrush |
|---|---|---|
| r18_feist6_alt_notr_nw | 1GB clean, both configs (sequential + golden-stride) | all passed |
| r18_feist6_alt_palk_nw | 1GB clean, both configs | all passed |

## Frontier decision

**r18_feist6_alt_notr_nw ENTERS and collapses the frontier to a single
point.** 37.9u / 4,119 cells / 11,621 area vs:
- r13 alt (40.1 / 4,563 / 13,041): −2.2u, −444 cells, −1,420 area
- r15 parsplit (40.7 / 4,318 / 12,356): −2.8u, −199 cells, −735 area
- r9 (41.0 / 4,265 / 11,996): −3.1u, −146 cells, −375 area
- r8 (42.9 / 4,133 / 11,670): −5.0u, −14 cells, −49 area

Full evidence: S0 (authorized path), S1 CAL_PASS, S2 0 repeats
max\|z\|=10.7, Q1 sac_z5=0, PractRand 1GB clean both configs, SmallCrush all
passed. **Caveat:** Q1 bic_maxcorr=0.172 (20× the r13/r15 family norm of
~0.008) — documented blemish, below every gate's threshold, flagged for a
possible future BIC gate.

**r18_feist6_alt_palk_nw** passes the full battery (S1 CAL_PASS, S2 0
repeats |z|=12.4, Q1 sac_z5=0 bic=0.0089, PractRand 1GB clean, SmallCrush
passed) but is dominated by the new speed point on all three axes
(40.5 > 37.9, 4,447 > 4,119, 12,905 > 11,621) — does NOT enter.

## Findings (scoped per [VERDICT_SCOPE.md](../VERDICT_SCOPE.md))

1. **The final round's linear layer is not load-bearing — for delay OR the
   gates.** Dropping it (alt_notr) saves 2.2u/444 cells AND passes S1–S4 +
   Q1 sac_z5=0. But it leaves a Q1 BIC blemish (bic_maxcorr=0.172 vs 0.008
   family norm): the last round's unmixed chi output leaves output-bit flip
   indicators correlated under single-bit input changes. Real effect (85×
   the N=2^18 noise floor), below every gate's detection threshold. Recorded
   as a caveat on the new frontier point; a BIC gate is a possible future
   addition, not a unilateral change.
2. **chi16 offsets are knife-edge in parsplit-F:** (0,2) gives the tempting
   38.2u/3,712-cell would-be dominator but dies hard at S1 marginals
   (PB rej=190, RD rej=20); (1,3) is CAL_PASS but dominated at 41.1u.
   (1,2) remains the only viable offset.
3. **Asymmetric even rounds are differentially unsound:** chi16 on the low
   half + passthrough high half (alt_asym) dies on DIFF rej=10 despite the
   tempting 37.8u. The passthrough half is the weak spot — consistent with
   r12's partial-S-box lesson (un-nonlinearized bits don't survive).
4. **Sharing one linear layer doesn't save the S1+chi XOR:** s1xorchi
   (F=lin(S1(R)^chi32(R))^rk) dies on DIFF rej=10 at 50.5u — worse than
   r17's separate-linear parmix on both axes. XORing the nonlinear outputs
   before mixing is unsound in both tested wirings.
5. **Palindromic keys are statistically clean but pointless:** alt_palk
   passes the full battery (Q1 clean) at 40.5u — the key schedule is off the
   critical path AND off the statistical path. Dominated by notr.
6. **chi variant (1,3) is clean but dominated:** alt_chioff13 CAL_PASS at
   40.1u (ties r13 alt delay exactly) but 98 more cells / 232 more area —
   the variant buys nothing.
7. **Lighter S-box rounds don't pay:** ps_s18_chi24 (S1 on 8 bits) is
   CAL_PASS but dominated at 40.4u/4,944 — the chi24 logic costs more than
   the S-box bits save.
8. **(5,17) rotmix in parsplit:** CAL_PASS, dominated at 41.1u — no reason
   to leave (3,11).
