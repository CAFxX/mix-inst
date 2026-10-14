# Round 23 — systematic r22c-neighborhood sweep (2026-10-04)

**Directive:** Carlo 2026-10-04 — "surprised we're not finding new candidates in the r22c neighborhood."

**Baseline (not rebuilt):** r22c_spn_mix4r_lp_nw = 4r keyed SPN
x_{i+1} = L(P(S16(x_i ^ rk_i))), P(i)=(5i+27)%64, L=lin(3,11), S1.
28.3u/4656/12949, full battery PASS, bic 0.00865.

**Method:** staged kill-chain S0 ([run_synth.py](../run_synth.py) only) → S1 → S2 (N=2^22,
115 deltas, kill repeats>10) → S3 (PractRand 16M→1G ×2 configs) → S4
(SmallCrush) → Q1 (sac_z5=0 mandatory). C↔model 10k + RTL↔model 300
before any synthesis. Polite ≤2-heavy-pipeline concurrency (binary-counted).
Generator: [`gen_r23.py`](gen_r23.py); model: [`models/r23.py`](models/r23.py); specs frozen in [`specs23.json`](specs23.json).

**Per-layer bijectivity (SPN hard gate):** every spec's S-box verified a
4-bit permutation, P-box a 64-permutation, L GF(2) rank 64 (pre-synthesis);
plus 5k×2-key empirical collision-free per spec at generation.

## Spec table

| # | Candidate | Axis | Spec |
|---|---|---|---|
| 1 | r23_spn_mix3r_lp_nw | P1: rounds | 3r, S1, P=O34, L=(3,11) |
| 2 | r23_spn_mix4r_l0307_nw | P2: linear | L=x^R3^R7 |
| 3 | r23_spn_mix4r_l0313_nw | P2: linear | L=x^R3^R13 |
| 4 | r23_spn_mix4r_l0511_nw | P2: linear | L=x^R5^R11 |
| 5 | r23_spn_mix4r_l0713_nw | P2: linear | L=x^R7^R13 |
| 6 | r23_spn_mix4r_l1117_nw | P2: linear | L=x^R11^R17 |
| 7 | r23_spn_mix4r_l0107_nw | P2: linear | L=x^R1^R7 |
| 8 | r23_spn_mix4r_l030711_nw | P2: linear | L=R3^R7^R11 (no-id 3-term) |
| 9 | r23_spn_mix4r_l031117_nw | P2: linear | L=R3^R11^R17 (no-id 3-term) |
| 10 | r23_spn_mix4r_l051123_nw | P2: linear | L=R5^R11^R23 (no-id 3-term) |
| 11 | r23_spn_mix4r_l010925_nw | P2: linear | L=R1^R9^R25 (no-id 3-term) |
| 12 | r23_spn_mix4r_pba03b03_nw | P3: P-box | (3,3), 2-cycle |
| 13 | r23_spn_mix4r_pba05b01_nw | P3: P-box | (5,1), single 64-cycle |
| 14 | r23_spn_mix4r_pba07b01_nw | P3: P-box | (7,1), 4-cycle |
| 15 | r23_spn_mix4r_pba09b01_nw | P3: P-box | (9,1), single 64-cycle |
| 16 | r23_spn_mix4r_pba11b01_nw | P3: P-box | (11,1), 2-cycle |
| 17 | r23_spn_mix4r_pba13b01_nw | P3: P-box | (13,1), single 64-cycle |
| 18 | r23_spn_mix4r_pba15b01_nw | P3: P-box | (15,1), 8-cycle |
| 19 | r23_spn_mix4r_pba17b01_nw | P3: P-box | (17,1), single 64-cycle |
| 20 | r23_spn_mix4r_pba19b01_nw | P3: P-box | (19,1), 2-cycle |
| 21 | r23_spn_mix4r_pba23b01_nw | P3: P-box | (23,1), 4-cycle |
| 22 | r23_spn_mix4r_pba25b01_nw | P3: P-box | (25,1), single 64-cycle |
| 23 | r23_spn_mix4r_pba27b01_nw | P3: P-box | (27,1), 2-cycle |
| 24 | r23_spn_mix4r_pbrnd13_nw | P3: P-box | random, 3-cycle |
| 25 | r23_spn_mix4r_pbrnd14_nw | P3: P-box | random, 5-cycle |
| 26 | r23_spn_mix4r_sb1_nw | P4: S-box | [5,6,3,1,12,2,4,7,10,11,13,9,8,0,14,15] DU6/LAT8/deg3 |
| 27 | r23_spn_mix4r_sb2_nw | P4: S-box | [12,13,15,2,7,3,1,4,6,0,14,11,5,8,10,9] DU6/LAT8/deg3 |
| 28 | r23_spn_mix4r_sb3_nw | P4: S-box | [7,9,6,3,15,10,4,0,8,12,11,13,5,1,14,2] DU6/LAT8/deg3 |
| 29 | r23_spn_mix4r_pl_nw | P5: order | P(L(S)) vs baseline L(P(S)) |
| 30 | r23_spn_mix4r_hs_alt_nw | P6a: hetero S-box | lanes alternate S1/SB1 |
| 31 | r23_spn_mix4r_hs_aff_nw | P6b: hetero S-box | per-lane affine S1 variants S1(x^n)^(7n%16) |
| 32 | r23_spn_mix4r_hs_rh_nw | P6c: hetero S-box | rounds 0-1 S1, rounds 2-3 SB1 |
| 33 | r23_spn_mix4r_mols8a_nw | P8: MOLS8 P-box | OA cols J,I base(1,2) off(0,1), 16×4-cyc |
| 34 | r23_spn_mix4r_mols8b_nw | P8: MOLS8 P-box | OA cols L1,J base(1,2) off(0,1), 16×4-cyc |
| 35 | r23_spn_mix4r_mols8c_nw | P8: MOLS8 P-box | OA cols L1,J base(1,3) off(0,2), 16×4-cyc |
| 36 | r23_spn_mix4r_ks0_nw | P9: key schedule | rk_i=rotl(key,13(i+1)), no GOLDEN (null probe) |

**P7 (MOLS(4) S-boxes): CLOSED — complete negative.** All 6,912 orthogonal
pairs of the 576 Latin squares of order 4 yield affine S-boxes (DU=16,
deg=1). See F5. No candidates.

## Stage results

*(a) failing signal / (b) mechanistic hypothesis / (c) follow-up per kill*

| Candidate | xcheck | rtlcheck | S0 | S1 | S2 | S3 | S4 | Q1 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| r23_spn_mix3r_lp_nw | PASS | PASS | 21.4u/3812/10367 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_l0307_nw | PASS | PASS | 27.9u/5525/14878 | CAL_PASS | PASS r=1 z=7.3 |  |  |  |  |
| r23_spn_mix4r_l0313_nw | PASS | PASS | 28.1u/5187/14124 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_l0511_nw | PASS | PASS | 27.8u/5345/14422 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_l0713_nw | PASS | PASS | 28.5u/4800/13275 | CAL_PASS | PASS r=0 z=4.5 |  |  |  |  |
| r23_spn_mix4r_l1117_nw | PASS | PASS | 27.9u/5231/14116 | CAL_PASS | PASS r=0 z=7.5 |  |  |  |  |
| r23_spn_mix4r_l0107_nw | PASS | PASS | 27.8u/5561/15025 | CAL_PASS | **KILL** 0x0000000080000000×11 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_l030711_nw | PASS | PASS | 27.8u/5246/14113 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_l031117_nw | PASS | PASS | 28.1u/5166/14077 | CAL_PASS | PASS r=0 z=12.8 |  |  |  |  |
| r23_spn_mix4r_l051123_nw | PASS | PASS | 28.1u/5118/13912 | CAL_PASS | PASS r=0 z=4.7 |  |  |  |  |
| r23_spn_mix4r_l010925_nw | PASS | PASS | 28.2u/4782/13054 | CAL_PASS | **KILL** 0x0000000000000002×29 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_pba03b03_nw | PASS | PASS | 28.2u/5409/14654 | CAL_PASS | PASS* r=1 z=390.7 |  |  |  |  |
| r23_spn_mix4r_pba05b01_nw | PASS | PASS | 28.0u/5263/14266 | CAL_PASS | PASS r=0 z=7.0 |  |  |  |  |
| r23_spn_mix4r_pba07b01_nw | PASS | PASS | 28.0u/5312/14360 | CAL_PASS | PASS r=1 z=44.0 |  |  |  |  |
| r23_spn_mix4r_pba09b01_nw | PASS | PASS | 28.4u/4718/13080 | CAL_PASS | **KILL** 0x7000000000000000×39 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_pba11b01_nw | PASS | PASS | 28.2u/5182/13973 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_pba13b01_nw | PASS | PASS | 28.2u/5026/13765 | CAL_PASS | **KILL** 0x0000000000000004×56 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_pba15b01_nw | PASS | PASS | 28.3u/4897/13431 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_pba17b01_nw | PASS | PASS | 28.4u/4903/13465 | CAL_PASS | **KILL** 0x9000000000000000×18 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_pba19b01_nw | PASS | PASS | 27.8u/5732/15374 | CAL_PASS | PASS r=0 z=12.2 |  |  |  |  |
| r23_spn_mix4r_pba23b01_nw | PASS | PASS | 28.2u/4820/13298 | CAL_PASS | **KILL** 0x0000000080000000×34 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_pba25b01_nw | PASS | PASS | 27.8u/5276/14219 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_pba27b01_nw | PASS | PASS | 28.2u/5093/13870 | CAL_PASS | PASS r=8 z=22.0 |  |  |  |  |
| r23_spn_mix4r_pbrnd13_nw | PASS | PASS | 28.1u/5313/14330 | CAL_PASS | **KILL** 0x0000000600000000×40 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_pbrnd14_nw | PASS | PASS | 28.2u/5128/14036 | CAL_PASS | **KILL** 0x0000000008000000×586 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_sb1_nw | PASS | PASS | 29.2u/5874/15896 | CAL_PASS | PASS r=0 z=12.3 |  |  |  |  |
| r23_spn_mix4r_sb2_nw | PASS | PASS | 29.0u/6817/18438 | CAL_PASS | PASS r=0 z=3.8 |  |  |  |  |
| r23_spn_mix4r_sb3_nw | PASS | PASS | 29.4u/5861/15881 | CAL_PASS | PASS r=0 z=7.5 |  |  |  |  |
| r23_spn_mix4r_pl_nw | PASS | PASS | 27.4u/5482/14723 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_hs_alt_nw | PASS | PASS | 28.7u/5492/14881 | CAL_PASS | PASS r=1 z=16.5 |  |  |  |  |
| r23_spn_mix4r_hs_aff_nw | PASS | PASS | 28.5u/4873/13320 | CAL_PASS | PASS r=0 z=14.2 |  |  |  |  |
| r23_spn_mix4r_hs_rh_nw | PASS | PASS | 28.5u/5591/15290 | CAL_PASS | PASS r=7 z=26.5 |  |  |  |  |
| r23_spn_mix4r_mols8a_nw | PASS | PASS | 28.3u/4780/13234 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_mols8b_nw | PASS | PASS | 27.8u/5493/14752 | CAL_PASS | **KILL** 0x0000000000002000×54 | — | — | — | **S2-KILLED** |
| r23_spn_mix4r_mols8c_nw | PASS | PASS | 27.9u/5205/14020 | **FLAG** | — | — | — | — | **S1-KILLED** |
| r23_spn_mix4r_ks0_nw | PASS | PASS | 27.9u/5330/14510 | **FLAG** | — | — | — | — | **S1-KILLED** |

## Critpath redirects (2026-10-04, from [exploration/critpath/CRITPATH.md](../critpath/CRITPATH.md))

Backtraced top-10 critical paths on all frontier designs (unit-delay STA).
Three findings redirect round-23 priorities:

1. **Linear-layer sweeps cannot move delay.** NONLIN (S-box/chi DNF) is
   79–90% of every frontier design's critical path; XORLIN (linear
   layers + key schedule) is 10–21%. The P2 (a,b) rotation-pair sweep
   stays valuable for mapping the S2 clean/dirty boundary and for BIC,
   but do NOT expect it to beat 28.3u on delay — delay expectations for
   P2 are hereby capped. (r22c: NONLIN 17/22.3u, XORLIN 3/6.0u.)
2. **r22c has a 10-path wall at exactly 28.3u (spread 0.0u).** No
   single-path tweak can help; only round count (3r — S1-killed, F1) or
   per-round DNF depth moves it. S-box scoring must rank by *mapped DNF
   depth per round*, not just DU/NL crypto metrics — DNF depth is the
   delay lever. (r22c: 4 rounds × 4.25u NL/round; S1's depth-minimality
   claim was about the S-box in isolation, not its ABC-mapped DNF.)
3. **Key schedule is on r22c's critical path** (starts at key[15];
   key[5] in S5 silicon STA). One round-key restructuring probe is
   warranted (P9 below). Note the wall is balanced key-side/data-side,
   so expectations are capped — this is a cost-model calibration probe.

## Failure analyses

### F1 (2026-10-04): r23_spn_mix3r_lp_nw — 3-round SPN S1-killed (round-count cliff mapped)
- (a) **Failing signal:** S1 FLAG (rc=2). LIN family: D=3618–4080/4096 rejected
  on all 10 keys (logp=-inf). DIFF family: worst|z|=814–3040 on all 10 keys.
  Not marginal — catastrophic on both statistical families.
- (b) **Mechanistic hypothesis:** 3 S-P-L rounds give insufficient
  confusion/diffusion depth. Each S-box layer is only 4-bit-local; after 3
  rounds the best linear characteristic still holds with probability ~0.94
  (D~3800/4096), and differentials retain |z|>800. The 4th round is doing the
  qualitative work: 4r has 0 rejections across all families (max|z|=13.6 at
  S2). The cliff is between 3 and 4 rounds — sharp, not gradual.
- (c) **Follow-up:** none on 3r (dead). The r22c neighborhood speed floor is
  ~28u (4 rounds), not ~21u. Do not probe 2r. If a future construction wants
  <28u, it needs a fundamentally stronger round function, not fewer rounds.

### F2 (2026-10-04): 7 marginal S1 kills — weak-bias differences, not breaks
- (a) **Failing signal:** 7/28 4r candidates FLAG at S1, all marginal:
  l030711 LIN rej=1; l0313 DIFF rej=3; l0511 DIFF rej=10; pba11b01 DIFF rej=9;
  pba15b01 DIFF rej=1; pba25b01 DIFF rej=9; pl DIFF rej=5. (Compare F1's
  thousands of rejections.) 21/28 pass clean, including the (3,11) baseline
  family and all 3 S-box variants.
- (b) **Mechanistic hypothesis:** rotation amounts and P-box wirings shift the
  linear/differential branch structure slightly; some choices leave weak
  residual trails detectable at N=2^18. Notably the fastest 4r (pl order-flip,
  27.4u) is among the marginal kills — speed and statistical cleanliness
  trade off even within the neighborhood. The rej=1 cases (l030711, pba15b01)
  are plausibly S1 false positives (nominal ~4% FWER per candidate); rej=9–10
  (l0511, pba11b01, pba25b01) are less likely noise.
- (c) **Follow-up:** killed per staged protocol (no S2). If a future design
  wants the pl order's 27.4u, it must first cure the DIFF rej=5 blemish —
  candidate follow-up, not a retest of these instances.

### F3 (2026-10-04): 2 S2 differential kills — real weaknesses, not noise
- (a) **Failing signal:** l0107 (linear (1,7)): KILL delta=0x0000000080000000
  (bit 31) repeats=11 > 10. l010925 (3-term (1,9,25) no-id): KILL
  delta=0x0000000000000002 (bit 1) repeats=29 > 10. Both at N=2^22, 115 deltas.
  (Compare l0307 (3,7): PASS max_repeats=1, max|z|=7.3 — clean.)
- (b) **Mechanistic hypothesis:** the linear layer's rotation amounts control
  the differential branch number. (1,7) and (1,9,25) admit single-bit input
  differences that propagate with anomalously high probability through 4
  rounds; (3,7) and (3,11) do not. The killing deltas are single-bit (bit 31,
  bit 1) — the weakest possible differential signal, yet it exceeds the
  kill threshold. This confirms (3,11) is not arbitrary: the rotation choice
  is load-bearing for S2 cleanliness.
- (c) **Follow-up:** killed. Do not use (1,7) or (1,9,25) linears in this SPN.
  The S2-clean set so far: (3,7), (3,11), (7,13), (11,17), (3,11,17),
  (5,11,23). [2026-10-04 update: all 7 S1-passing linears now have S2
  results — 5 PASS, 2 KILL. The remaining S2 queue (7 runs: pba19b01
  re-run, pba27b01, pbrnd13, pbrnd14, sb1–3) covers P-boxes and S-boxes,
  not linears.]

### F4 (2026-10-04): 3 affine P-box S2 kills — P-box wiring is load-bearing for S2
- (a) **Failing signal:** pba09b01: KILL delta=0x0000000070000000 (bits
  32–34) repeats=39. pba13b01: KILL delta=0x0000000000000004 (bit 2)
  repeats=56. pba17b01: KILL delta=0x9000000000000000 (bits 60,63)
  repeats=18. pba23b01: KILL delta=0x0000000080000000 (bit 31)
  repeats=34. All at N=2^22, 115 deltas, kill threshold 10. (Compare
  pba05b01: PASS r=0 z=7.0 — clean; baseline (5,27) P-box: max|z|=13.6.)
- (b) **Mechanistic hypothesis:** the affine P-box (a,b) controls which
  S-box lanes feed which in the next round. (9,1), (13,1), (17,1) admit
  2–3-bit input differences that stay confined to weak lane groupings
  across 4 rounds; (5,1), (3,3), (7,1) do not. Cycle structure does NOT
  determine cleanliness: killed (9,1)/(13,1)/(17,1) are all single
  64-cycles, but so is clean (5,1). The killing deltas are 1–3 adjacent
  bits — same confined-trail class as F3's linear kills. The (5,27)
  baseline P-box is not arbitrary: P-box choice is load-bearing for S2
  cleanliness, at least as much as the linear layer.
- (c) **Follow-up:** killed. Do not use (9,1), (13,1), (17,1), (23,1) affine
  P-boxes in this SPN. S2-clean P-box set so far: (5,27) baseline,
  (5,1), (3,3), (7,1). Remaining S2 runs (pba19b01 re-run, pba27b01,
  pbrnd13, pbrnd14, sb1–3) will complete the map. Note bit 31 kills
  both l0107 (linear) and pba23b01 (P-box) — a recurring weak spot.

**Note (2026-10-04):** pba03b03 is S2-PASS by the repeat gate (r=1) but
carries a |z| blemish: delta 0x0000000700000000 max|z|=390.7 (baseline
13.6), plus 0x9000000000000000 at 268.1 and 0x0000000070000000 at 133.5
— all with full_repeats=0. The distribution is highly non-uniform even
though no single output repeats. Flagged for S3 arbitration: if
PractRand kills it, the |z| gate needs a threshold; if it passes, the
repeat gate stands as the S2 arbiter.

**Note (2026-10-04):** pbrnd13 (random 3-cycle P-box): S2 KILL
delta=0x0000000600000000 (bits 33–34) repeats=40. pbrnd14 (random
5-cycle P-box): S2 KILL delta=0x0000000008000000 (bit 27) repeats=586
— an order of magnitude worse. Same confined-trail class as the affine
kills, but in *random* P-boxes — the weakness is not specific to affine
structure, and random P-boxes are not automatically safe. Both random
P-boxes dead: 0/2 viable. The S2-clean P-box set remains: (5,27)
baseline, (5,1), (3,3), (7,1), (19,1), (27,1).

**Note (2026-10-04):** heterogeneous S-boxes are S2-clean. hs_alt
(lanes alternate S1/SB1): S2 PASS r=1 z=16.5. hs_aff (per-lane affine
S1 variants): S2 PASS r=0 z=14.2. Both are dominated on delay
(28.7u/28.5u > 28.3u baseline) so no Pareto value, but the
construction is validated: lane-heterogeneous S-boxes don't break
differential cleanliness in this SPN. hs_rh (round-split S1/SB1) in
S2 queue.

### F5 (2026-10-04): MOLS(4)-derived S-boxes — complete negative (all affine)
- (a) **Failing signal:** Full enumeration of all 576 Latin squares of
  order 4 → 6,912 orthogonal pairs → 6,912 distinct S-boxes via
  S[(i<<2)|j]=(L1[i][j]<<2)|L2[i][j]. **All 6,912 have DU=16, LAT=8,
  deg=1** — every single one is an affine permutation. Zero pass the
  DU≤6/LAT≤8/deg=3 filter. (The 6 GF(4)-linear pairs are a subset with
  the same properties.)
- (b) **Mechanistic hypothesis:** For order 4, orthogonal Latin-square
  pairs are isotopic to the Desarguesian affine plane; the
  (L1,L2)-pair construction always yields an affine map. The
  construction is structurally incapable of producing nonlinear
  S-boxes — not a sampling artifact but a complete-enumeration proof.
- (c) **Follow-up:** P7 closed. Do not derive 4-bit S-boxes from
  MOLS(4) orthogonal pairs. Per critpath redirect, future S-box
  searches must score by *mapped DNF depth per round* (the delay
  lever), not just DU/NL — a 3.5u/round S-box at equal S2 buys ~3u.
  (sb1/sb2/sb3 already in S2 queue will report their S0 DNF depths.)

### F6 (2026-10-04): mols8a S1-killed — transpose P-box too structured
- (a) **Failing signal:** S1 FLAG. LIN PASS (rej=0), DIFF FLAG (rej=10),
  worst|z|=7.3. The (J,I) transpose+offset P-box.
- (b) **Mechanistic hypothesis:** The (J,I) column pair is just a
  transpose (swap 3-bit halves) plus offset — too regular. It maps
  structured input differences to structured output differences,
  leaving differential trails that S1 detects. The MOLS-based (L1,J)
  pairs (mols8b/c) use the nonlinear Latin structure and may fare
  better — S1 pending.
- (c) **Follow-up:** killed. The transpose+offset P-box family is not
  viable. MOLS(8) P-boxes must use the Latin structure (L1/L2 columns),
  not just (I,J). [Update: mols8c (L1,J base(1,3)) also S1-killed
  (DIFF rej=6); only mols8b (L1,J base(1,2)) survives S1. The specific
  MOLS parameters matter, not just the column-pair type.]
  [Update 2026-10-04: mols8b S2-KILLED — delta=0x0000000000002000
  (bit 13) repeats=54 > 10, decisive. The (L1,J) Latin structure that
  fooled S1 still admits a confined single-bit differential trail
  through 4 rounds. MOLS(8)-derived P-boxes: 0/3 viable (mols8a S1,
  mols8c S1, mols8b S2). The Latin-square P-box avenue is closed for
  this SPN — P-box choice remains load-bearing (F4) but MOLS structure
  is not the answer.]

### F7 (2026-10-04): ks0 S1-marginal kill — key schedule affects both delay and S1
- (a) **Failing signal:** S1 FLAG. LIN PASS (rej=0), DIFF PASS (rej=0),
  marginal PB rej=1 (RD rej=0). S0 was 27.9u — 0.4u FASTER than the
  28.3u baseline.
- (b) **Mechanistic hypothesis:** Removing the GOLDEN round constant
  saves 0.4u (the constant was NOT fully folded by ABC, or the simpler
  key schedule optimizes better — null hypothesis disproven). But the
  round constants contribute to S1 cleanliness; without them, a
  marginal poker/birthday deviation appears (rej=1, plausibly noise but
  protocol-killed). The key schedule is a real delay lever (0.4u), not
  just a cost-model curiosity.
- (c) **Follow-up:** killed per protocol (marginal). The 0.4u delay win
  is real but the S1 blemish blocks it. Future: try alternative round
  constants (simpler than GOLDEN but nonzero) to keep the delay win
  without the S1 marginality — a targeted follow-up, not a retest.

## Winners

*(full battery + Q1 sac_z5=0 with Pareto improvement; [PARETO.md](../PARETO.md) updated by parent only)*
