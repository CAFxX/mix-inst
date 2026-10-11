# RV64 `mix` — Cumulative Pareto Frontier

**Updated:** 2026-10-11 (324: hyb28_mu5_324 joins as new speed point 19.3u with full battery + Q1 evidence; t6_b33c demoted to second row, survives on cells/area)
**Multiplier reference:** 103.5u (cells 12,645, area 35,323), re-measured per
round in the pinned Yosys-0.69 flow. S0 bar: ≤ 0.9 × 103.5 = 93.15u.

Two frontiers are maintained (Carlo 2026-10-03):

- **Frontier S (standard):** Pareto-eligible iff the candidate passes S0–S4
  plus the Q1 spot check (sac_z5=0). BIC is reported, not gated.
- **Frontier Q (BIC-clean):** Frontier S gates **plus** Q1
  `bic_maxcorr ≤ 0.02` (family norm is ~0.008; the 0.02 bar admits the norm
  with headroom and rejects the unmixed-final-chi blemish class at
  0.14–0.17).

Delay/area/cells from `run_synth.py` (authorized path).

**Retention:** "retired" below means off the Pareto frontier — never deleted.
Every candidate that ever passed the full battery is retained indefinitely
for future extended-PractRand breaking-point batteries; the registry is
[RETAINED.md](RETAINED.md).

## Frontier S (delay, cells, area — lower is better)

| Candidate | Delay | Ratio | Cells | Area | Round claimed | Quality notes |
|---|---|---:|---:|---:|---|---|
| **hyb28_mu5_324** | **19.3u** | **0.186×** | 6,146 | 20,001 | batch-28 | **New speed point — 0.5u faster than t6_b33c (19.8u); NOT dominating (cells/area slightly above b33c).** 5-stage MUX-rotation cascade (hyb batch-28 schedule, MU5 keep z=3.24, pre-whiten, final x^=rotl(k,13)). S0 19.3u via run_synth.py (XCHECK analyze.py == analyze2.py, ref mul64 103.5u); S1 CAL_PASS (all rejection lists empty); S2 PASS (max|z|=76.9, all 115 deltas); S3 PractRand 1GB clean + S3b strided clean; S4 SmallCrush all passed; Q1 sac_z5=0, bic_maxcorr=0.0087 (**BIC-clean — qualifies on Frontier Q**). Battery chain 2026-10-11 (results/hyb28_mu5_324/battery.log); Q1 from raw q1_hyb28_mu5_324.json. |
| **t6_b33c** | **19.8u** | **0.191×** | 6,133 | 19,817 | batch-33 | Former speed point (2026-10-10 → 2026-10-11); survives on cells/area vs 324. 6-stage AND-rotation cascade (exact-DIFF-proxy-guided schedule selection), same stage form as as6_200 (pre-whiten; 6x x^=(ra&rb)^rc; final x^=rotl(k,13)). S0 19.8u via run_synth.py (XCHECK analyze.py == analyze2.py, ref mul64 103.5u, equiv 1000/1000); S1 CAL_PASS (all rejection lists empty, marginal 187s); S2 PASS; S3 PractRand 1GB clean (0 anomalies in 227); S4 SmallCrush all passed; Q1 sac_z5=0, bic_maxcorr=0.01002 (**BIC-clean — qualifies on Frontier Q**). Battery chain 2026-10-10 (results/t6_b33c/battery.log); Q1 verified by status report 2026-10-10 23:01 CEST from raw q1_t6_b33c.json. |
| **t6_b33b** | **20.1u** | **0.194×** | 5,992 | 19,280 | batch-33 | **New size point — ties al_and6a on delay (20.1u) and dominates it on cells (5,992<6,116) and area (19,280<19,541).** 6-stage AND-rotation cascade (exact-DIFF-proxy-guided schedule selection), same stage form as b33c. S0 20.1u via run_synth.py (XCHECK analyze.py == analyze2.py, ref mul64 103.5u, equiv 1000/1000); S1 CAL_PASS; S2 PASS; S3 PractRand 1GB clean (16MB→1GB + strided, 0 FAIL, fail-LOUD guard passed — first S3b attempt voided by a mid-edit broken s3_practrand.sh, re-run on the fixed script); S4 SmallCrush all passed; Q1 sac_z5=0, bic_maxcorr=0.00913 (**BIC-clean — qualifies on Frontier Q**). Re-run 2026-10-10 (results/t6_b33b/battery_resubmit.log); Q1 by status report from raw q1_t6_b33b.json. |
| **r25_spn_pba19_sb_rasC2_0_513_nw** | **26.4u** | **0.255×** | 5,385 | 14,415 | 25 | **New speed point — joins (does not replace) rasC2_0 (3,11): 0.1u faster, 260 cells / 396 area larger; genuine tradeoff, neither dominates.** 4r keyed SPN (pba19 construction, P(i)=(19i+1)%64, lin(5,13)) with the rasC2_0 S-box. S1 CAL_PASS; S2 PASS (max_repeats=1, max\|z\|=25.1, all 115 deltas); S3 PractRand 1GB clean (standard + strided) + deep 2GB→8GB PASS (GHA, 0 FAIL); S4 SmallCrush all passed; Q1 sac_z5=0, bic_maxcorr=0.00907 (**BIC-clean — qualifies on Frontier Q**). Parent-verified from raw logs 2026-10-07 (deep PractRand + local S4/Q1). |
| **r25_spn_pba19_sb_rasC2_0_nw** | **26.5u** | **0.256×** | 5,125 | 14,019 | 25 | 4r keyed SPN (pba19 construction, P(i)=(19i+1)%64, lin(3,11)) with the rasC2_0 S-box from the Rasoolzadeh depth-3 pool. S1 CAL_PASS; S2 PASS (max_repeats=1, max\|z\|=11.3, all 115 deltas); S3 PractRand 1GB clean (standard + strided) + deep 2GB→8GB PASS (GHA, 0 FAIL); S4 SmallCrush all passed; Q1 sac_z5=0, bic_maxcorr=0.01012 (**BIC-clean — qualifies on Frontier Q**). Parent-verified from raw logs 2026-10-05 (full fast-battery re-run). |
| **r22c_spn_mix4r_lp_nw** | **28.3u** | **0.273×** | 4,656 | 12,949 | O44 | Size point — beats rasC2_0 on cells (−9%) and area (−8%); strictly nondominated. 4-round keyed SPN x_{i+1}=L(P(S16(x_i^rk_i))), P(i)=(5i+27)%64, L=lin(3,11). S1 CAL_PASS; S2 0 kills max|z|=13.6; PractRand 1GB ×2 clean; SmallCrush all passed; Q1 sac_z5=0, bic_maxcorr=0.00865; 2M×2-key bijectivity. Parent-verified 2026-10-03. |
| **r21_feist6_alt_notr_chioff31final_nw** | **36.7u** | **0.355×** | 4,198 | 12,005 | 21 | New speed point — **strictly dominates r20 chioff13all on all three axes** (36.7<37.0, 4,198<4,357, 12,005<12,511). 6r Feistel notr: chi(1,3) on rounds 2,4, (3,1) chi on the truncated round 6. S1 CAL_PASS; S2: 0 repeats, max\|z\|=11.2; Q1 sac_z5=0, bic_maxcorr=0.14029 (blemish class); S3 PractRand 1GB clean (both configs); S4 SmallCrush all passed. |
| **r21_feist6_alt_notr_3rot_ns_nw** | **37.4u** | **0.361×** | **3,667** | **10,742** | 21 | New size point — **strictly dominates r20 chioff31 (37.5/3,863/11,199) and r19 chioff13 (37.4/4,149/11,820) on all three axes**. 6r Feistel notr with the NONSINGULAR 3-rotation layer lin3ns = R³x^R⁷x^R¹¹x (identity term dropped) on all five linear rounds, truncated chi final. Born as the FA1 diagnosis probe for the 3rot S1-LIN kill (even-term singularity); the fix also removed one XOR level per bit per round (−3.8u vs the singular 3rot). S1 CAL_PASS; S2: 0 repeats, max\|z\|=4.7 (round's best); Q1 sac_z5=0, bic_maxcorr=0.25384 (strongest blemish in the family — Frontier-S only); S3 PractRand 1GB clean (both configs); S4 SmallCrush all passed. |

The 28-MUX 324 now anchors the frontier: hyb28_mu5_324 is the speed point (19.3u),
t6_b33c (19.8u) survives on cells/area, and b33b is the size play at 20.1u
(141 fewer cells than b33c).
The r25 SPN pair survives on the size axis (5,125–5,385 cells vs
5,992–6,133 for the batch-33 pair — genuine tradeoff, neither dominates):
(5,13) is 0.1u faster than (3,11) but 260 cells / 396 area larger;
(3,11) is 6.4u slower than b33b but 867 cells / 5,261 area smaller.
r22c beats chioff31final on delay by 8.4u; chioff31final is 0.7u faster
than 3rot_ns and 458 cells smaller than r22c; 3rot_ns is 531 cells /
1,263 area smaller than chioff31final. No point dominates another. The notr
family's BIC blemish class (0.14–0.25) does not touch the SPN/batch-33 points
(0.00865–0.01012). Retired 2026-10-10: al_and6a (20.1/6,116/19,541) —
dominated by t6_b33b (delay tie, fewer cells, less area); al_cascad
(25.5/7,891/26,566) — dominated by t6_b33c on all three axes. Retired
2026-10-05: r23 pba19b01 (27.8/5,732/15,374) and
wf2d aff_a17_b17 (27.9/5,299/14,223) — both strictly dominated by rasC2_0 (3,11) on
all three axes; retained in RETAINED.md. Full evidence in
`round21/ROUND21_TABLE.md`, `round22/ROUND22_TABLE.md` (O44 section),
`round23/ROUND23_TABLE.md` (pba19b01), and `round25/ROUND25_TABLE.md`
(rasC2_0). RTL
for the Frontier-S points plus the Frontier-Q fm points in
`~/workspace/your_files/mix_rtl_pareto/` (package tracks both frontiers per
Carlo 2026-10-03; the r15/r9/r8 Frontier-Q points keep their existing RTL
under `fast_battery/candidates/` and round dirs).

Excluded (verified but effectively dominated): r21 keyin31 (36.9u / 4,191 /
11,986) is a near-duplicate of chioff31final with the round key mixed
inside the (3,1) final chi instead of XORed after — fully verified (S1–S4 +
Q1 clean, bic 0.14092) but +0.2u for a 7-cell / 19-area edge that sits
below the flow's meaningful-tradeoff threshold (standing rule); r20 keyin
was excluded on the same grounds in round 20.

## Frontier Q (BIC-clean; adds bic_maxcorr ≤ 0.02)

| Candidate | Delay | Ratio | Cells | Area | Round claimed | Quality notes |
|---|---|---:|---:|---:|---|---|
| **t6_b33c** | **19.8u** | **0.191×** | 6,133 | 19,817 | batch-33 | **New speed point — dominates al_cascad on delay and cells.** BIC-clean (0.01002 ≤ 0.02), sac_z5=0. Full battery per Frontier-S entry. |
| **t6_b33b** | **20.1u** | **0.194×** | 5,992 | 19,280 | batch-33 | **New size point at 20.1u — dominates al_and6a on cells and area at equal delay.** BIC-clean (0.00913 ≤ 0.02), sac_z5=0. Full battery per Frontier-S entry. |
| **r25_spn_pba19_sb_rasC2_0_513_nw** | **26.4u** | **0.255×** | 5,385 | 14,415 | 25 | **New speed point — joins (does not replace) rasC2_0 (3,11): 0.1u faster, 260 cells larger; genuine tradeoff. BIC-clean (0.00907 ≤ 0.02), sac_z5=0. Full battery per Frontier-S entry.** |
| **r25_spn_pba19_sb_rasC2_0_nw** | **26.5u** | **0.256×** | 5,125 | 14,019 | 25 | BIC-clean (0.01012 ≤ 0.02), sac_z5=0; full battery per Frontier-S entry. |
| **r22c_spn_mix4r_lp_nw** | **28.3u** | **0.273×** | 4,656 | 12,949 | O44 | Size point on Frontier Q: beats rasC2_0 on cells (−9%) and area (−8%); BIC-clean (0.00865); see Frontier-S entry for full evidence. |
| **r21b_3rot_ns_fm311_nw** | **38.3u** | **0.370×** | 4,299 | 12,356 | r21b | **New mid-frontier point — strictly dominates r21 chioff13all_fm311 (39.1/4,485/12,763) and r19 fm311 (39.5/4,467/12,769) on all three axes.** 3rot_ns base + fm311 cure inside F_6 (32-bit, Feistel-bijective). Cure cost +0.9u/+632 cells (cheaper than the (1,3)-base fm311's +1.7u — fm cost scales with chi cone). S1 CAL_PASS; S2: 0 repeats, max|z|=4.7; Q1 sac_z5=0, bic_maxcorr=0.00883 (cured from 0.25384); S3 PractRand 1GB clean (both configs); S4 SmallCrush all passed — **BATTERY-PASS**. Parent-verified from raw logs 2026-10-03. |
| r9_feist6_rot311_nw | 41.0u | 0.396× | 4,265 | 11,996 | 9 | S1–S4 + Q1 clean, bic_maxcorr=0.0085. |
| r8_feist6_s1_1sbox_nw | 42.9u | 0.414× | 4,133 | 11,670 | 8 | S1–S4 + Q1 clean, bic_maxcorr=0.008037. Size/quality point. |

Retired in round 21: r19 fm11 (39.3u/4,877/13,748) — strictly dominated by
r21 chioff31_fm07 (39.2/4,661/13,159) on all three axes; r21 chioff31_fm07
itself dominated by r21 chioff13all_fm311 (39.1/4,485/12,763); r21
chioff13all_fm07 (39.4/4,870/13,729) dominated by chioff31_fm07. Retired in
O44: r19 fm07 (38.8u/5,053/14,320) — strictly dominated by r22c
(28.3/4,656/12,949) on all three axes. Retired in r21b: r21
chioff13all_fm311 (39.1u/4,485/12,763) and r19 fm311 (39.5u/4,467/12,769) —
both strictly dominated by r21b (38.3/4,299/12,356) on all three axes;
r15 parsplit (40.7u/4,318/12,356) — dominated by r21b (≤ on all axes,
< on delay and cells, exact area tie). Retired in batch-33 (2026-10-10): al_cascad (25.5u/7,891/26,566, bic 0.00891) —
strictly dominated by t6_b33c (19.8/6,133/19,817) on delay, cells, and area;
al_and6a was never on Frontier Q as a separate point (dominated by b33b on
Frontier S). All retired points remain in
RETAINED.md for the future breaking-point batteries. No point dominates
another among the four survivors. r13 alt (40.1u, bic 0.008) is dominated by
fm311 and sits out; fm03 and chioff13_fm03 are dominated by fm311.

## History

| Round | Frontier after round | Change |
|---|---|---|
| 6 | { r6_feist8_spn: 86.5u } | First S0–S4 survivor |
| 7 | { r7_feist8_s1_1sbox: 56.5u } | Dominated r6 on all axes |
| 8 | { r8_feist6_s1_1sbox_nw: 42.9u } | Dominated r7 on all axes |
| 9 | { r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | Frontier extended (speed/quality tradeoff, not domination) |
| 10 | { r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Unchanged.** 13 candidates; no (delay,area) domination. Quality finds: (3,13) @41.4u with S2 |z|=4.1 (target hit); alternating (3,11)/(7,13) @41.9u with |z|=3.6 (cleanest 6r); 5r phase transition holds (3/3 fail). |
| 11 | { r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Unchanged.** S-box sweep (PRESENT/GIFT/SKINNY-4/Piccolo × {(3,11),(7,13)}, 4×SKINNY-8 probe, S1/PRESENT hetero): 10/10 pass S0 bar and S1, but ALL dominated — best delay 43.8u (GIFT), best cells 4,737 (SKINNY-4). S1's minimal boolean depth is load-bearing for the delay frontier; 8-bit S-boxes not competitive (67.2u). |
| 12 | { r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Unchanged.** Linear/diffusion-structure attack (10 candidates): 5r+3-rotation linear all fail LIN (rej=9) — the 5r phase transition is robust to stronger per-round diffusion; partial-S-box F needs 8r to pass S1 and then dies at S2 (70 repeats on a delta avoiding the S-box) — cheaper-F/more-rounds does not beat the optimum; 3-rotation linear at 6r is slower (46.7u) AND fails LIN — 2-rotation (3,11) remains optimal; 16-bit-half rotation mixing fails LIN+DIFF (rej=10/10) despite a tempting 41.6u/4,041-cell S0. |
| 13 | { r13_feist6_alt_s1chi_nw: 40.1u, r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Extended — new speed point.** 13 candidates, new F topologies: heterogeneous (S1,chi) alternating rounds take the speed point (40.1u, S1–S4 + Q1 clean, S2 |z|=10.7). Pure chi at 6r passes S1's marginal screen but fails avalanche (Q1 sac_z5=57, S2 |z|=86.5) — S1's PB family is blind to single-bit-flip avalanche, so Q1 is now mandatory for ALL frontier claims, not just 4r/5r. 4r double-strength-F crosses the round barrier statistically (full S1 + clean S2 at |z|~3.7) but is dominated (56–59u). Fixed Lai-Massey (D-invariance bug caught by S0) still dominated; key-schedule variants and sandwich diffusion all dominated. |
| 14 | { r13_feist6_alt_s1chi_nw: 40.1u, r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Unchanged.** 13 candidates exploiting the heterogeneity breakthrough: 10 S1 passes, 6 clean S2s, 0 Pareto improvements. The 31.9u/3,282-cell alt_chinolin (chi without rotmix) dies at S1 DIFF (rej=10) — chi needs its rotmix. Reversed alt is 1.3u slower AND worse differentially (order matters: S1 leads). alt713 is the cleanest 6r ever measured (S2 |z|=3.6) but dominated at 40.6u. Rotating key-half on chi rounds is exactly neutral (bit-identical S0/S2 to r13 alt). 4r lighter-strong-F probes both die at S1 — the 4r barrier needs the full double-S1 F. 5r double-F passes S1 (round-strength question closed) but is dominated at 70.6u. r9 + invertible 64-bit final diffusion is pure cost (+2.1u). |
| 15 | { r15_feist6_parsplit_nw: 40.7u, r13_feist6_alt_s1chi_nw: 40.1u, r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Extended — new Pareto point.** 12 candidates: mixed single/double-F rounds, alt rotation-heterogeneity, key diffusion, parallel-split F. parsplit (S1 on R[15:0] \|\| chi16 on R[31:16] in parallel, 40.7u/4,318/12,356) enters the frontier — S1–S4 + Q1 clean, not dominated (faster than r9, smaller than r13 alt). Heterogeneous LAYERS in parallel beat serial stacking (r14's 57u). Rotation heterogeneity inside alt is neutral-to-negative; whitening on alt is +2.1u AND an S1 FLAG (PB rej=1) — closed; key diffusion neutral; mixed double-F rounds statistically fine but delay-doomed (48.6–55.3u). |
| 16 | { r13_feist6_alt_s1chi_nw: 40.1u, r15_feist6_parsplit_nw: 40.7u, r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Unchanged.** 12 candidates: verdict-scope re-tests + parsplit variants. 11/12 S1 passes, 0 Pareto-eligible on S0. O1 (HIGH): crypto S-boxes in heterogeneous rounds all CAL_PASS statistically but still delay-dominated (GIFT 41.8u, PRESENT 44.7u, SKINNY-4 42.6u) — the het-economics argument was directionally right (SKINNY-4 het 2.9u faster than homogeneous) but insufficient; refined claim "1.7–4.6u cost in het rounds (vs 3–8u homogeneous)". O2 (MEDIUM): 3-rot lin is statistically clean with chi-F (both triples CAL_PASS) — the r12 LIN kill does not reproduce; remaining objection is pure delay. O5 (LOW): mid-key on alt CAL_PASS at 45.1u, dominated on both structures — closed. Parshift variants all dominated; chi16 (2,3) ties r15 delay but costs cells; giftsplit (GIFT on 16 bits) fails LIN rej=1 — partial-width crypto layers leave weak spots. |
| 17 | { r13_feist6_alt_s1chi_nw: 40.1u, r15_feist6_parsplit_nw: 40.7u, r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u } | **Unchanged.** 10 candidates: 5r probes (parsplit-F, alt S1-first/chi-first), O3/O4 re-tests, parsplit variants. The 5r phase transition does NOT reproduce at S1 for stronger Fs — 5r parsplit-F and 5r alt (S1-first) both CAL_PASS at ~34-35u — but BOTH die at S2 on the same single-bit delta (input bit 32, 33/45 repeats, |z| 217/1216): the transition is F-strength-dependent at S1 but round-count-absolute at S2. S1-first order matters at 5r (chi-first: PB rej=7). O4 closed: parallel S1+chi fails DIFF at 6r too (rej=7). O3 closed: half-S1 in alt fails DIFF rej=1. chi16(0,1) kills the tempting 39.1u would-be dominator (DIFF rej=3). premix is structurally degenerate (x^rotl32(x,16) is 2^16-to-1; S0's 21.0u was true for the broken design). 4r parsplit-F dies at S1 (rej=10/10). dbs1split CAL_PASS but dominated by r9. |
| 18 | { r18_feist6_alt_notr_nw: 37.9u } | **Frontier REPLACED — single point.** 9 candidates: parsplit chi16 offsets (1,3)/(0,2), S1-8/chi-24 split, truncation probe (round 6 drops the linear layer), palindromic key, asymmetric rounds, parsplit (5,17), S1^chi-XOR shared-linear F, chi variant (1,3) in alt. The truncation probe (alt_notr, 37.9u/4,119/11,621) passes the FULL battery (S1 CAL_PASS, S2 0 repeats |z|=10.7, Q1 sac_z5=0, PractRand 1GB clean both configs, SmallCrush all passed) and dominates ALL FOUR round-17 frontier points on delay, cells, AND area. The final round's linear layer is not load-bearing for delay or any gate — but its absence leaves a Q1 BIC blemish (bic_maxcorr=0.172 vs 0.008 family norm), documented as a caveat. Palindromic key (40.5u) passes the full battery but is dominated by notr. Three tempting would-be dominators die at S1: ps_chioff02 (38.2u, marginal PB rej=190/RD rej=20 — chi16 offsets are knife-edge), alt_asym (37.8u, DIFF rej=10), s1xorchi (50.5u, DIFF rej=10 — shared-linear XOR of nonlinear outputs is unsound). |
| 19 | { r19_feist6_alt_notr_chioff13_nw: 37.4u, r18_feist6_alt_notr_nw: 37.9u } | **Extended to two points.** 10 candidates: BIC-fix probes (notr + y^rotl(y,m) final mixing), truncation axis (round-5 linear drop, parsplit/r9 round-6 drops, chi(1,3) on notr rounds 2,4, (5,17) on notr). **Objective A achieved scientifically:** the extra XOR+rotation cures the BIC blemish on all five tested structures (bic 0.172 → 0.008–0.0098) but costs 0.9–1.9u — none reaches the ≤38.5u bar, all dominated. notr5 (34.9u) passes S1 and formally passes S2 yet has |z|=477 single-bit differential spikes — dropping the round-5 S1 linear is differentially fatal; truncation is safe only on the final chi round. chioff13 (37.4u/4,149/11,820) passes the FULL battery and enters as the new speed point (0.5u faster than notr, 30 cells larger; same blemish class bic=0.142, documented). |
| 20 | { r20_feist6_alt_notr_chioff13all_nw: 37.0u, r19_feist6_alt_notr_chioff13_nw: 37.4u, r20_feist6_alt_notr_chioff31_nw: 37.5u } | **Extended to three points; r18 notr retired.** 9 candidates: S1-final, chi(1,3) on round 6, chioff13+(5,17), key-inside-chi, drop-round-4 probe, notr(7,13), fm16, chi(1,3)-on-round-6-only variant, r13-full-alt+chi(1,3). chioff13all (37.0u/4,357/12,511) passes the FULL battery — new speed point (chi(1,3) on the truncated round 6 is pure speed, −0.4u vs chioff13). chioff31 (37.5u/3,863/11,199) passes the FULL battery and **dominates r18 notr on all three axes** — the (3,1) chi variant is the size play. keyin (37.2u) passes the FULL battery but is a near-duplicate of chioff13all (effectively dominated: +0.2u/+25 cells for a 0.1% area edge) — excluded from the frontier. drop4 (34.3u) is the notr5 class again: formal S2 PASS but 46/115 deltas with |z|=100–743 — truncation safe only on the final chi round, confirmed a second time. Frontier Q backfill complete: fm07/fm11/fm311 all confirmed (S3 PractRand 1GB ×2 PASS, SmallCrush passed) — no provisional markers remain. |
| 21 | { r21_feist6_alt_notr_chioff31final_nw: 36.7u, r21_feist6_alt_notr_3rot_ns_nw: 37.4u } | **Frontier S REPLACED (two points); Frontier Q: fm11 retired, one entrant.** 11 candidates (10 designed + 1 diagnosis probe). chioff31final (36.7u/4,198/12,005) passes the FULL battery — new speed point, **strictly dominates r20 chioff13all** on all axes ((3,1) chi on the truncated final is speed AND size). 3rot_ns (37.4u/3,667/10,742) passes the FULL battery — new size point, **strictly dominates r20 chioff31 and r19 chioff13**; born as the FA1 diagnosis probe (see below). keyin31 (36.9u) passes the FULL battery but is a near-duplicate of chioff31final — threshold-excluded (standing rule). 3rot/3rot_chioff13 KILLED at S1 (LIN rej=9): the x^R³x^R⁷x^R¹¹x layer is GF(2)-singular (rank 31) — parity(out_lo) input-independent, LIN rows confined to a 63-dim affine subspace (verified: constant equals predicted parity(rk32_1⊕rk32_3⊕rk32_5)); refines O2 — the killer is singularity (even XOR-term count), not rotation count. Diagnosis probe 3rot_ns (R³x^R⁷x^R¹¹x, rank 32) is S1 CAL_PASS, confirming the mechanism — and dominates on size. Frontier Q: chioff13all_fm311 (39.1u, bic 0.00860) enters (tradeoff vs fm311); fm11 retired (dominated by chioff31_fm07, itself dominated by chioff13all_fm311); chioff13all_fm07 dominated. |
| r21b | Q: { r22c_spn_mix4r_lp_nw: 28.3u, r21b_3rot_ns_fm311_nw: 38.3u, r9: 41.0u, r8: 42.9u } | **Frontier Q consolidated 6→4.** r21b (3rot_ns + fm311 inside F_6, 38.3u/4,299/12,356, bic 0.00883, full battery PASS) strictly dominates chioff13all_fm311 and fm311 on all axes, and dominates r15 parsplit (≤ all, < delay+cells, area tie) — all three retired (retained in RETAINED.md). r21b becomes the mid-frontier point: +10u slower than r22c but −357 cells/−593 area (genuine tradeoff); −2.7u faster than r9 but +34 cells/+360 area (genuine tradeoff). Cure cost +0.9u vs base (fm scales with chi cone). Parent-verified from raw logs. |
| wf2d | { wf2d_aff_a17_b17: 27.9u, r23_spn_mix4r_pba19b01_nw: 27.8u, r22c_spn_mix4r_lp_nw: 28.3u, r21_feist6_alt_notr_chioff31final_nw: 36.7u, r21_feist6_alt_notr_3rot_ns_nw: 37.4u } / Q: same S set minus the notr pair | **Wire-friendly 2D track's first S2 survivor becomes a frontier point.** The corrected 2D objective (P&R happens in 2D; the 1D sum|P(i)-i| conflated index-locality with physical locality) inverted the pipeline: S2-screen first, optimize W2d among survivors. Of the three affine finalists, aff_a49_b49 (delta 0x0000000700000000, 14 reps) and aff_a09_b25 (single-bit 0x8000000000000000, 18 reps) S2-killed; aff_a17_b17 (P(i)=(17i+17)%64) S2-PASS (6 reps, |z|=57.7). W2d verified 384 vs baseline 424 on 5/5 SA seeds (-9.4%, seed-stable). Full battery PASS (S0 27.9u/5,299/14,223, S1 CAL_PASS, PractRand 1GB x2, SmallCrush, Q1 sac_z5=0 bic 0.00901, 2M×2-key bijectivity) — new mid-SPN point on both frontiers: 0.4u faster than r22c at +14% cells, 0.1u slower than pba19b01 at -8% cells. Parent-verified from raw logs 2026-10-04. |
| 23 | { r23_spn_mix4r_pba19b01_nw: 27.8u, r22c_spn_mix4r_lp_nw: 28.3u, r21_feist6_alt_notr_chioff31final_nw: 36.7u, r21_feist6_alt_notr_3rot_ns_nw: 37.4u } / Q: { r23_spn_mix4r_pba19b01_nw: 27.8u, r22c_spn_mix4r_lp_nw: 28.3u, r21b_3rot_ns_fm311_nw: 38.3u, r9: 41.0u, r8: 42.9u } | **New speed point on both frontiers.** Round 23 = systematic r22c-neighborhood sweep (affine/random P-boxes, hetero S-boxes, S-box variants, MOLS(8), key-schedule probes, 3r probe). 3r probe S1-killed (|z|=3040 — the 4th round is load-bearing). Affine P-boxes a=19/b=01 (27.8u) and a=27/b=01 (28.2u) both S1+S2 clean; hetero S-boxes (hs_alt/aff/rh) and sb1/sb2/sb3 all S2-clean but slower than 28.3u; mols8b 27.8u S2-KILLED (repeats=54); pbrnd13/pbrnd14/pba23b01 S2-killed. pba19b01 (27.8u/5,732/15,374) passes the FULL battery (PractRand 1GB ×2, SmallCrush, Q1 sac_z5=0 bic 0.01092, 2M×2-key bijectivity) — new speed point, strictly nondominated vs r22c (beats on delay, loses on cells/area). pba27b01 (28.2u/5,093/13,870, full battery PASS, bic 0.008529) threshold-excluded: 0.1u/0.35% delay edge at +9% cells is a near-duplicate of r22c (standing rule; precedent: r21 keyin31). Key-schedule probe ks0: 27.9u (−0.4u vs r22c!) but S1-marginal kill — key schedule is a real delay lever; follow-up = simpler nonzero round constants. Parent-verified from raw logs 2026-10-04. |
| O44 | { r22c_spn_mix4r_lp_nw: 28.3u, r21_feist6_alt_notr_chioff31final_nw: 36.7u, r21_feist6_alt_notr_3rot_ns_nw: 37.4u } / Q: { r22c_spn_mix4r_lp_nw: 28.3u, r21 chioff13all_fm311: 39.1u, r19 fm311: 39.5u, r15: 40.7u, r9: 41.0u, r8: 42.9u } | **BREAKTHROUGH — first non-Feistel frontier point, both frontiers.** O44 (O37 differential-freezing fix): 4r keyed SPN x_{i+1}=L(P(S(x_i^rk_i))) with validated P-box + lin(3,11). **28.3u/4,656/12,949** — 8.4u faster than the old speed point; full battery PASS (S1 CAL_PASS, S2 0 kills |z|=13.6, PractRand 1GB ×2, SmallCrush, Q1 sac_z5=0 bic 0.00865 — no BIC blemish). Strictly dominates r19 fm07 on all axes (fm07 retired from Frontier Q). Analytical kills along the way: x^rotl(x,R) as MIX is GF(2)-singular (rank 63, killed pre-synthesis, bijectivity gate); triangular shift-XOR at 5r S2-killed (systematic under-diffusion). Positive mechanism: the P-box is load-bearing at 4r — candidate A (identical minus P-box) died with a deterministic differential; L∘P ≠ L as a linear layer. Parent-verified from raw logs + 2M×2-key empirical bijectivity. |
| 25 | { r25_spn_pba19_sb_rasC2_0_nw: 26.5u, r22c_spn_mix4r_lp_nw: 28.3u, r21_feist6_alt_notr_chioff31final_nw: 36.7u, r21_feist6_alt_notr_3rot_ns_nw: 37.4u } / Q: { r25_spn_pba19_sb_rasC2_0_nw: 26.5u, r22c_spn_mix4r_lp_nw: 28.3u, r21b_3rot_ns_fm311_nw: 38.3u, r9: 41.0u, r8: 42.9u } | **New speed point on both frontiers — S-box swap in the pba19 SPN.** Round 25 = Rasoolzadeh depth-3 S-box pool in the pba19b01 construction (top-4 in-context S0/S1/S2). rasC2_0 (26.5u/5,125/14,019) passes the FULL battery (S1 CAL_PASS, S2 max|z|=11.3, PractRand 1GB ×2, SmallCrush, Q1 sac_z5=0 bic 0.01012) and **strictly dominates r23 pba19b01 (27.8/5,732/15,374) and wf2d aff_a17_b17 (27.9/5,299/14,223) on all three axes** — both retired (retained). rasC2_5 (28.1u, full battery PASS, bic 0.01009) threshold-excluded as a pba19b01 near-duplicate; rasC1_2 (28.5u, S0–S2+Q1 clean, bic 0.00847) in S3/S4. FA4 mechanism closed: MIDORI Sb0's S1 kill is a low-weight weak-key phenomenon (reproduces at key Hamming weight 0–4, clean ≥5), not key=0-specific; Sb1 is S1-clean in the identical construction. Parent-verified from raw logs 2026-10-05. |
| batch-33 | { t6_b33c: 19.8u, t6_b33b: 20.1u, r25_spn_pba19_sb_rasC2_0_513_nw: 26.4u, r25_spn_pba19_sb_rasC2_0_nw: 26.5u, r22c_spn_mix4r_lp_nw: 28.3u, r21_feist6_alt_notr_chioff31final_nw: 36.7u, r21_feist6_alt_notr_3rot_ns_nw: 37.4u } / Q: { t6_b33c: 19.8u, t6_b33b: 20.1u, r25_spn_pba19_sb_rasC2_0_513_nw: 26.4u, r25_spn_pba19_sb_rasC2_0_nw: 26.5u, r22c_spn_mix4r_lp_nw: 28.3u, r21b_3rot_ns_fm311_nw: 38.3u, r9: 41.0u, r8: 42.9u } | **BREAKTHROUGH — exact-DIFF-proxy-guided rotation search finds S1-clean 6-stage AND schedules in the same stage form the O86 generalization had declared dead.** Track-6's t6_b33_screen.py (exact S1 DIFF computation, all 10 keys, ~40s/candidate — reproduces S1 DIFF bit-for-bit) screened 20 random 6-stage schedules: 7/20 KEEP (z 2.6–8.3). t6_b33c (19.8u/6,133/19,817) passes the FULL battery (S1 CAL_PASS, S2, S3 1GB clean, S4, Q1 sac_z5=0 bic 0.01002) — **new speed point**, strictly dominates al_cascad (25.5/7,891/26,566) on all axes (retired). t6_b33b (20.1u/5,992/19,280) passes the FULL battery (S1 CAL_PASS, S2, S3+strided clean on a fixed-script re-run after the first S3b was voided by a mid-edit broken s3_practrand.sh, S4, Q1 sac_z5=0 bic 0.00913) — **new size point at 20.1u**, dominates al_and6a (20.1/6,116/19,541) on cells and area at equal delay (retired). b33a died at S1 marginal (PB rej=2 — triage is DIFF-only; marginal is a separate gate). The 6-stage AND DIFF wall is schedule-variant and common, not universal: the selection method was the differentiator (v3 proxy → 7/7 kills; exact-DIFF proxy → 2 survivors so far). |
| 25b | { r25_spn_pba19_sb_rasC2_0_513_nw: 26.4u, r25_spn_pba19_sb_rasC2_0_nw: 26.5u, r22c_spn_mix4r_lp_nw: 28.3u, r21_feist6_alt_notr_chioff31final_nw: 36.7u, r21_feist6_alt_notr_3rot_ns_nw: 37.4u } / Q: { r25_spn_pba19_sb_rasC2_0_513_nw: 26.4u, r25_spn_pba19_sb_rasC2_0_nw: 26.5u, r22c_spn_mix4r_lp_nw: 28.3u, r21b_3rot_ns_fm311_nw: 38.3u, r9: 41.0u, r8: 42.9u } | **(5,13) linear variant JOINS both frontiers (Carlo 2026-10-07).** The lin(5,13) swap in the rasC2_0 pba19 construction: 26.4u/5,385/14,415 — 0.1u faster than (3,11) but 260 cells / 396 area larger; genuine tradeoff, neither dominates. Full battery PASS: S1 CAL_PASS, S2 (max|z|=25.1), S3 PractRand 1GB ×2 + deep 2GB→8GB PASS (GHA, 0 FAIL, positive evidence), S4 SmallCrush all passed, Q1 sac_z5=0 bic 0.00907. Parent-verified from raw logs 2026-10-07. |

## Qualified but dominated (selected)

| Candidate | Delay | Cells | Area | Notes |
|---|---|---:|---:|---|
| al_and6a | 20.1u | 6,116 | 19,541 | Former speed point (2026-10-09); dominated by t6_b33b (delay tie, fewer cells, less area). Full battery PASS (S1 CAL_PASS, S2 0 repeats, S3 1GB clean, S4 all passed, Q1 sac_z5=0 bic=0.00868). |
| al_cascad | 25.5u | 7,891 | 26,566 | Former frontier point; dominated by t6_b33c on all three axes. Full battery PASS (Q1 sac_z5=0 bic=0.00891). |
| r20_feist6_alt_notr_keyin_nw | 37.2u | 4,382 | 12,497 | Full battery PASS (S1 CAL_PASS, S2 0 repeats |z|=10.7, Q1 sac_z5=0 bic=0.17232, PractRand 1GB clean, SmallCrush passed); near-duplicate of chioff13all, effectively dominated (+0.2u/+25 cells for a 0.1% area edge). |
| r18_feist6_alt_notr_nw | 37.9u | 4,119 | 11,621 | Former frontier point (round 18–19); dominated on all axes by r20 chioff31. Full battery evidence in round18. |
| r13_feist6_alt_s1chi_nw | 40.1u | 4,563 | 13,041 | Former speed point (round 13–17 frontier); dominated on all axes by r18 alt_notr. Full battery evidence in round13. |
| r18_feist6_alt_palk_nw | 40.5u | 4,447 | 12,905 | Full battery PASS (S1 CAL_PASS, S2 0 repeats |z|=12.4, Q1 sac_z5=0 bic=0.0089, PractRand 1GB clean, SmallCrush passed); dominated by r18 alt_notr on all axes. |
| r15_feist6_parsplit_nw | 40.7u | 4,318 | 12,356 | Former frontier point (round 15–17); dominated on all axes by r18 alt_notr. Full battery evidence in round15. |
| r9_feist6_rot311_nw | 41.0u | 4,265 | 11,996 | Former frontier point (round 9–17); dominated on all axes by r18 alt_notr. |
| r8_feist6_s1_1sbox_nw | 42.9u | 4,133 | 11,670 | Former frontier point (round 8–17, max-quality); dominated on all axes by r18 alt_notr. |
| r10_feist6_rot0313_nw | 41.4u | 4,645 | 12,855 | S4 PASS, S2 |z|=4.1, Q1 clean — quality-preferred, dominated on (delay,area) |
| r9_feist6_rot0719_nw | 41.8u | 4,602 | 12,963 | Dominated by rot311 |
| r9_feist6_ksalt_nw | 41.8u | 4,628 | 12,946 | Dominated by rot311; clean S2 |
| r10_feist6_altrot311_713_nw | 41.9u | 4,480 | 12,598 | S4 PASS, S2 |z|=3.6 (cleanest 6r), Q1 clean, heterogeneous — dominated |
| r9_feist6_ksrot_nw | 42.5u | 4,777 | 13,351 | Dominated by rot311 |
| r10_feist6_rot0411_nw | 42.8u | 4,150 | 11,847 | S4 PASS, S2 |z|=4.1, Q1 clean; 0.1u faster than r8 but larger — below P&R noise floor |
| r9_feist6_altrot_nw | 43.2u | 4,338 | 12,239 | Heterogeneous, fully clean, dominated |
| r9_feist6_rot517_nw | 43.2u | 6,444 | 17,638 | Clean, dominated |
| r8_feist6_pbox | 43.5u | 4,544 | 12,929 | Dominated by r8 leader |
| r8_feist6_s1_1sbox | 43.7u | 4,744 | 13,387 | Dominated by r8 leader |
| r9_feist7_rot517_nw | 49.3u | 5,454 | 15,308 | 7r-nw repair, dominated |
| r8_feist7_s1_1sbox | 50.2u | 5,452 | 15,421 | Dominated |
| r8_feist6_s1_alt | 55.0u | 5,436 | 15,095 | Dominated |
| r7_feist8_s1_1sbox | 56.5u | 6,063 | 17,098 | Dominated |
| r9_feist7_s1_lin2_nw | 66.6u | 7,532 | 20,968 | Dominated |

## Fast but not qualified

| Candidate | Delay | Reason |
|---|---|---|
| r9_feist5_s1_1sbox_nw | 35.1u | S0–S4 pass, but Q1 spot check fails (sac_z5=61; S2: 34/115 deltas with repeats, max\|z\|=35.1). 5-round differential phase transition. |
| r9_feist5_s1_1sbox | 36.6u | Same 5-round caveat (sac_z5=55). |
| r10_feist5_rot311 | 35.7u | S1 marginal FLAG (PB rej=2) — fastest S0 of round 10, cannot cross the 5r phase transition. |
| r10_feist5_s1_2sbox_nw | 52.9u | S0–S4 pass formally, but Q1 fails (sac_z5=118, bic_max=0.087; S2 max|z|=170.3). 5-round phase transition holds. |
| r12_feist6_s1half311_nw | 37.3u | S1 kill (LIN rej=10, DIFF rej=10). Tempting S0 (faster+smaller than r9) but 6r partial-S-box has gross structural weakness. |
| r12_feist5_lin31125_nw | 38.9u | S1 kill (LIN rej=9). 5r phase transition robust to 3-rotation linear. |
| r12_feist5_lin31119_nw | 39.3u | S1 kill (LIN rej=9). |
| r12_feist5_lin3711_nw | 39.5u | S1 kill (LIN rej=9). |
| r12_feist5_lin71319_nw | 39.9u | S1 kill (LIN rej=9). |
| r12_feist6_s1_16rot_nw | 41.6u | S1 kill (LIN rej=10, DIFF rej=10). Heterogeneous 16-bit-half rotation mixing structurally unsound. |
| r12_feist7_s1half311_nw | 42.5u | S1 kill (marginal PB rej=4). |
| r12_feist6_lin3711_nw | 46.7u | S1 kill (LIN rej=9). 3-rotation linear worse on delay AND linear profile than 2-rotation. |
| r12_feist6_lin71319_nw | 46.8u | S1 kill (LIN rej=9). |
| r12_feist8_s1half311_nw | 47.0u | S1 CAL_PASS but S2 kill (70 repeats on delta 0x0000000000080000 avoiding the S-box; max|z|=20.1 on 0x4_0000). |
| r13_lm4_s1_311_nw | 31.0u | S1 kill (LIN rej=10). Fixed Lai-Massey (orthomorphism) still leaks through the linear half at 4r. |
| r13_feist5_chi311_nw | 34.0u | S1 kill (DIFF rej=10). Pure chi needs the 6th round, like S1-F. |
| r13_feist6_chi311_nw | 40.9u | S1–S2 pass formally (0 repeats) but Q1 avalanche fails (sac_z5=57, sac_maxdev=0.0214; S2 max|z|=86.5 on single-bit deltas). First sub-41u design, rejected on quality. |
| r17_feist5_parsplit_nw | 35.0u | S1 CAL_PASS, but S2 kill (33 repeats on input-bit-32 delta, max\|z\|=217.2). 5r phase transition holds at S2 for parsplit-F. |
| r17_feist5_alt_s1chi_nw | 34.3u | S1 CAL_PASS, but S2 kill (45 repeats on input-bit-32 delta, max\|z\|=1215.8). 5r phase transition holds at S2 for alt S1/chi. |
| r17_feist6_parsplit_chioff01_nw | 39.1u | S1 kill (DIFF rej=3, worst\|z\|=246.5). Would have dominated r13 alt and r15 parsplit on (delay,cells,area) — chi16(0,1) breaks it. |

## Killed in Round 9 (S1)

r9_feist6_rot0824_nw (LIN+DIFF FLAG), r9_feist6_rot1119_nw (marginal FLAG),
r9_feist6_rot0925_nw (DIFF FLAG), r9_feist6_nork (marginal FLAG).

## Killed in Round 10 (S1)

r10_feist6_rot0511_nw (marginal FLAG, RD rej=1), r10_feist5_s1_lin2_nw (marginal FLAG, RD rej=1), r10_feist5_rot311 (marginal FLAG, PB rej=2).

## Killed in Round 13 (S1)

r13_feist5_chi311_nw (DIFF rej=10), r13_lm4_s1_311_nw (LIN rej=10). Both sub-35u S0; both fail the round-count phase transition for their F.

## Killed in Round 15 (S1)

r15_feist6_alt_wh_nw (LIN/DIFF pass, marginal PB rej=1 — whitening on the heterogeneous structure adds a statistical blemish on top of +2.1u cost), r15_feist5_db3_nw (LIN/DIFF pass, marginal RD rej=1 — 5r with one double round; dominated at 41.4u). Both FLAGged; no S2.

## Killed in Round 14 (S1)

r14_feist6_alt_chinolin_nw (DIFF rej=10, worst|z|~29.8 — chi without rotmix has weak diffusion), r14_feist4_chis1l_nw (DIFF rej=1, marginal), r14_feist4_pars1chi_nw (LIN rej=9 + DIFF rej=10 — parallel S1+chi mix is weak). The tempting 31.9u/3,282-cell chinolin dies here; both 4r lighter-strong-F probes die here.

## Killed in Round 16 (S1)

r16_feist6_giftsplit_nw (LIN rej=1, DIFF pass — GIFT on only 16 bits of a parsplit F is statistically weak; full-width GIFT-het passes). All other 11 pass S1; the round's kills are on S0 domination, not statistics.

## Killed in Round 17 (S1)

r17_feist6_premix_nw (LIN rej=10 + DIFF rej=10, worst|z|=272775.1 — x^rotl32(x,16) is 2^16-to-1, F sees 16 effective bits; S0's 21.0u was true for the degenerate design), r17_feist4_parsplit_nw (LIN rej=10 + DIFF rej=10 — 4r barrier holds for parsplit-F; S1-gated probe, stop), r17_feist6_parmix_nw (DIFF rej=7, worst|z|=857.6 — [O4 re-test] parallel S1+chi fails at 6r as well as 4r), r17_feist6_parsplit_chioff01_nw (DIFF rej=3, worst|z|=246.5 — chi16 offsets (0,1) break parsplit-F diffusion; the tempting 39.1u would-be dominator dies here), r17_feist5_alt_chifirst_nw (LIN/DIFF pass, PB rej=7 — S1-first order matters at 5r), r17_feist5_parsplit_713_nw (DIFF rej=5 — rotation pair controls the 5r boundary: (3,11) passes S1, (7,13) fails), r17_feist6_alt_pshalf_nw (DIFF rej=1 marginal — [O3 re-test] half-S1 in alt context).

## Killed in Round 17 (S2)

r17_feist5_parsplit_nw (delta 0x0000000100000000: 33 repeats > 10, max|z|=217.2 — S1 CAL_PASS at 35.0u, killed at S2), r17_feist5_alt_s1chi_nw (same delta: 45 repeats, max|z|=1215.8 — S1 CAL_PASS at 34.3u, killed at S2). The 5r phase transition is F-strength-dependent at S1 but round-count-absolute at S2.

## Killed in Round 18 (S1)

r18_feist6_ps_chioff02_nw (LIN/DIFF pass, marginal PB rej=190, RD rej=20 — chi16 offsets (0,2) in parsplit-F are statistically broken; the 38.2u/3,712-cell would-be dominator dies here), r18_feist6_alt_asym_nw (DIFF rej=10 — asymmetric even rounds (chi16 low half + passthrough high half) are differentially unsound in alt at 6r; the 37.8u would-be dominator dies here), r18_feist6_s1xorchi_nw (DIFF rej=10 — F=lin(S1(R)^chi32(R))^rk: XORing nonlinear outputs before a shared linear layer is unsound).

## Killed in Round 19 (S2 structural — formal PASS, frontier-dead)

r19_feist6_alt_notr5_nw (34.9u): S1 CAL_PASS and formal S2 PASS (repeats=1 < 10), but systematic single-bit differential spikes |z|=165–477 (e.g. 0x0000001000000000: 477.2) — dropping the round-5 S1 linear destroys diffusion. The tempting 34.9u/4,028-cell would-be dominator is a "fast number, broken design" (r17 premix class). Truncation is safe only on the final chi round in alt at 6r.

## Killed in Round 20 (S2 structural — formal PASS, frontier-dead)

r20_feist6_alt_notr_drop4_nw (34.3u): S1 CAL_PASS and formal S2 PASS (repeats=2 < 10), but 46/115 deltas show systematic single-bit differential spikes |z|=114–743 (e.g. 0x0000000800000000: 712.1, 0x0000001000000000: 676.0) — dropping round 4's chi linear destroys diffusion into F_5's input. The tempting 34.3u/4,198-cell would-be dominator is a "fast number, broken design" (r17 premix / r19 notr5 class). Truncation is safe only on the final chi round in alt at 6r — confirmed a second time (ledger O15 closed).
