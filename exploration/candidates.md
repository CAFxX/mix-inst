# Design-Space Exploration — Candidate Consolidation (screening stage)

**Date:** 2026-10-01. **Stage: SCREENING ONLY.** No winner declared; no candidate meets all requirements.
**Round 1:** 0 / 19 pass both gates. **Round 2:** 0 / 28 pass both gates (3 CAL_PASS, all 0.5u over on delay).
**Reference:** 64×64-bit variable multiplier, D_mult = **49.2 unit-delays** (Yosys/ABC `-fast`, mini.genlib; measured twice, stable), area 44548.
**Hard bars:** combinational crit ≤ **44.3** (0.90×); screen PASS = no per-bit |z|>4.0 AND no reduction |z|>4.5.
**Pipeline rule (brief AND-condition):** partitions built ONLY if delay ≤ 0.90 AND screen PASS. T_clk = max_stage × 1.10 (10% reg-overhead ASSUMPTION).

## Headline result: 0 / 19 candidates pass both gates

| Gate | Pass | Fail |
|------|------|------|
| Delay ≤ 44.3 | 5 (A2, A4, B2, B3, D3) | 14 |
| Screen PASS | 0 | 19 (all FLAG; mildest: A8, REF) |
| **Both** | **0** | **19** |

No pipeline partitions were built (none qualify). The three nearest misses are analyzed below without partitions.

## Full candidate table

| # | Candidate | Construction | Bijectivity | Crit (ratio) | Area (ratio) | Worst per-bit \|z\| @ scenario | Worst red. \|z\| @ scenario | Verdict |
|---|-----------|--------------|-------------|--------------|--------------|-------------------------------|---------------------------|---------|
| A1 | spn7_present | 7-rd SPN: 16×PRESENT S-box + pLayer, KS rk[i]=ROTL(k,13(i+1))^RC[i] | S-box+pLayer+xor | 50.9 (1.035) | 26832 (0.602) | 62.8 @ DESC-jF…F/b53 | 453.7 @ PTR-j8/lemire-10 | OUT+FLAG |
| A2 | spn6_present | 6-rd SPN, PRESENT S-box + pLayer | same | 44.2 (0.898) | 22992 (0.516) | 147.3 @ DESC-jF…F/b61 | 1575.1 @ SEQ/mask32-coll | FLAG (delay PASS) |
| A3 | spn7_gift | 7-rd SPN, GIFT S-box (verified) + pLayer | same | 50.9 (1.035) | 27247 (0.612) | 100.5 @ SEQ/b63 | 2535.6 @ SEQ/lemire-10 | OUT+FLAG |
| A4 | spn6_gift | 6-rd SPN, GIFT S-box + pLayer | same | 44.2 (0.898) | 23412 (0.526) | 352.3 @ STRIDE-3/b63 | 22588.4 @ SEQ/lemire-10 | FLAG (delay PASS) |
| A5 | spn7_skinny | 7-rd SPN, SKINNY S-box (published table; brief's was wrong) + pLayer | same | 50.9 (1.035) | 27107 (0.608) | 444.5 @ POW2-2^2/b37 | 9015.3 @ SEQ/mask-m=8 | OUT+FLAG |
| A6 | spn7_present_ks2 | 7-rd SPN, PRESENT, 2-rotation key schedule | same (KS need not be bij) | 59.9 (1.217) | 30963 (0.695) | 52.3 @ SEQ/b21 | 467.3 @ SEQ/lemire-10 | OUT+FLAG |
| A7 | spn2_aes8 | 2-rd: 8×AES S-box (verified) + xor-linear L(x)=x^ROTL(x,13)^ROTL(x,41) | S-box + proven 3-term L | 66.4 (1.350) | 51189 (1.149) | 160.0 @ POW2-2^16/b55 | 22.3 @ SEQ/lemire-10 | OUT+FLAG |
| A8 | spn4_xorlin | 4-rd: 16×PRESENT S-box + xor-linear L (as A7) | same as A7 | 44.8 (0.911) | 21568 (0.484) | 5.7 @ DESC-j…f8/b14 | 3.6 @ PTR-j8/mod-7 | OUT (0.5u over) + FLAG |
| B1 | add2r_a | 2-rd ARX: x+=rk[i]; x^=ROTL(x,13)^ROTL(x,41) | add + proven 3-term L | 44.7 (0.909) | 5204 (0.117) | 502.0 @ POW2-2^5/b55 | 168232 @ SEQ/lemire-10 | OUT+FLAG |
| B2 | add2r_b | 2-rd ARX, rotations (29,53) | same | 43.9 (0.892) | 5523 (0.124) | 512.0 @ SEQ/b19 | 180063 @ SEQ/mask32-hi16 | FLAG (delay PASS) |
| B3 | m32_1stage_a | a*=0x9E3779B1; b^=a; a^=ROTL(b,11); b^=ROTL(a,17)^k_lo | odd-mult + Feistel half-steps | 43.2 (0.878) | 8022 (0.180) | 512.0 @ HIGH-ONLY/b50 | 66.4 @ PTR-j8/mask32-lo16 | FLAG (delay PASS) |
| B4 | m32_1stage_b | as B3, C=0x85EBCA77, rots (7,19) | same | 45.7 (0.929) | 8675 (0.195) | 512.0 @ HIGH-ONLY/b50 | 116.6 @ PTR-j8/mask32-lo16 | OUT+FLAG |
| C1 | feistel6_sbox | 6-rd Feistel, F=P32(8×PRESENT S-box) | Feistel (any F) | 52.0 (1.024*) | 10879 (0.236*) | 320.0 @ DESC-jF…F/b27 | 902.5 @ SEQ/lemire-10 | OUT+FLAG |
| C2 | feistel7_sbox | 7-rd Feistel, same F | same | 60.0 (1.181*) | 12550 (0.272*) | 87.7 @ DESC-jF…F/b14 | 187.8 @ SEQ/lemire-10 | OUT+FLAG |
| C3 | feistel8_xor | 8-rd Feistel, F=(x^rk)^ROTL(x,7)^ROTL(x,19) (near-affine; weak by construction) | same | 56.0 (1.102*) | 14752 (0.320*) | 2.74 @ STRIDE-FIB/b60 | 1991.2 @ SEQ/mask32-lo16 | OUT+FLAG |
| C4 | feistel6_giftsbox | 6-rd Feistel, F=P32(8×GIFT S-box, verified) | same | 50.5 (0.994*) | 11208 (0.243*) | 168.0 @ SEQ/b27 | 426.1 @ SEQ/mask32-hi16 | OUT+FLAG |
| D1 | lane2_s2_const | 2 stages: 32-bit const mults + Feistel cross (11,17) + RC | odd-mult + Feistel | 80.9 (1.644) | 28863 (0.648) | 256.0 @ POW2-2^16/b11 | 19.7 @ PTR-j8/mask32-lo16 | OUT+FLAG |
| D2 | lane2_s1_const | 1 stage: 32-bit const mults + 2 Feistel crosses (11,17),(7,19) | same | 45.7 (0.929) | 13978 (0.314) | 512.0 @ POW2-2^16/b2 | 2241 @ SEQ/mask32-coll | OUT+FLAG |
| D3 | lane4_s1_const | 1 stage: four 16-bit odd-const mults + pair Feistel (5,9) + rotate | odd-mult + Feistel + perm | 32.2 (0.654) | 6886 (0.155) | 512.0 @ SEQ/b16 | 47452590 @ SEQ/mask32-hi16 | FLAG (delay PASS) |
| REF | spn12_present | 12-round PRESENT SPN (statistical reference only; rejected on delay) | SPN | 73.6 (1.510) | — | 4.36 @ STRIDE-3/b3 | 2.87 @ SEQ/mask32-hi16 | OUT + FLAG (mild) |

\* C-batch ratios use post-restart reference 50.8 (3.3% ABC-version drift; see Methodology). Verdicts use the absolute bar 44.3 — all C crits ≫ 44.3, unaffected.

## Pareto analysis (delay vs quality)

Quality score = max(worst per-bit |z|, worst reduction |z|) (lower = better). Delay = absolute crit (lower = better).

Pareto-optimal (non-dominated) set: **D3 → B3 → A8 → REF**

| Candidate | Delay | Quality | Dominates / note |
|-----------|-------|---------|------------------|
| D3 lane4_s1_const | 32.2 | 47,452,590 | Delay-optimal; quality catastrophic (dead-lane collapse) |
| B3 m32_1stage_a | 43.2 | 512 | Best delay among non-catastrophic; stuck-bit defect |
| A8 spn4_xorlin | 44.8 | 5.7 | Best quality among delay-competitive; misses bar by 0.5u, still FLAGs |
| REF spn12_present | 73.6 | 4.36 | Quality-optimal; 1.51× — rejected as design, kept as reference |

All other 15 candidates are dominated (worse on both axes than some Pareto member). The frontier has a sharp knee: no candidate combines delay ≤ 44.3 with quality anywhere near the reference.

## Nearest misses (top-3 by Pareto rank, with blockers — NOT finalists)

**No candidate qualifies for pipeline partitioning** (brief AND-condition: delay ≤ 0.90 AND screen PASS). The three closest, in Pareto order:

### 1. A8 `spn4_xorlin` — closest overall
- Delay 44.8 (0.911×) — misses the bar by **0.5 unit-delays**. Screen: mildest of all candidates (per-bit ≤ 5.7 across 14 scenarios, zero reduction flags) but still FLAG.
- Blocker: needs −0.5u delay AND elimination of 14 marginal per-bit flags (4.0–5.7).
- Pipeline headroom (hypothetical, NOT a qualification): single combinational stage of 44.8; a 2-stage partition (≈22.4+22.4) gives T_clk ≈ 24.6, latency ≈ 49.3 — just over 49.2. Does not close even hypothetically without the delay reduction.

### 2. B3 `m32_1stage_a` — best delay among serious candidates
- Delay 43.2 (0.878×) — PASSES delay. Screen: FLAG with structural defect (output bit 50 constant under HIGH-ONLY; verified mechanism: single 32-bit mult + linear cross-mix cannot diffuse high-half-only variation).
- Blocker: structural statistical failure, not tunable (needs a second nonlinear element or a global pre-mix — both cost delay).

### 3. D3 `lane4_s1_const` — delay-optimal
- Delay 32.2 (0.654×) — PASSES delay with large margin. Screen: FLAG catastrophic (dead-lane collapse on small inputs; proven mechanism).
- Blocker: structural — single-stage sliced lanes need a global pre-mix or bit-interleaved lanes (unexplored; see below).

## Unexplored families

1. **64-bit multiply + SPN hybrids** (in the original search plan; not reached): e.g. x*=odd64; 2–3 SPN rounds; x*=odd64. The 64-bit const-mult alone is 46.2 (0.939×) in this flow — over bar before any rounds, but the production-flow caveat (Booth/CSD ≈ 0.6–0.7×) makes this the highest-leverage P&R-stage family.
2. **Bit-interleaved multi-lane designs**: D3's dead-lane collapse is an artifact of contiguous 16-bit slices; interleaved lanes (bit i → lane i mod 4) keep all lanes active on small inputs. Untested.
3. **Wallace/CSA-tree 64-bit constant multiply**: hand-built CSD+ripple tree measured 67.1 (worse than behavioral 46.2 — ABC maps each tree adder as a full CPA, no Booth/CSD). A proper compressor tree was beyond screening scope; relevant only for P&R-stage costing.
4. **Deeper ARX (3–4 rounds)**: B1/B2 show 2 rounds have no diffusion; 3+ rounds were not screened (delay risk).
5. **SPN with cheaper linear layer**: A8's xor-linear costs ~11/round vs pLayer's ~7.3; a 5-round pLayer SPN (≈36.5+whitening) was not in the grid.
6. **Feistel with fixed-point-free permutation**: C1/C2/C4's P32(31)=31 bottleneck is fixable; combined with a cheaper round function this family could re-enter.
7. **Keyed S-box / S-box-free nonlinear**: beyond the grid.

## Transferable lessons

1. **D2 rotation-sum rule**: chained Feistel crosses with (b-update rotation + next t-update rotation) ≡ 0 mod 8 annihilate byte-repeated differences in the lane projection. Check on any sequential-cross design.
2. **D1 upward-mix**: constant multipliers diffuse bits upward-only; constant low lane bits re-concentrate into bias through Feistel crosses (3/4-bias mechanism documented).
3. **D3 dead lanes**: single-stage contiguous-slice lane designs collapse when input lanes are zero (small inputs — the hash-map's common case). Needs global pre-mix or interleaved lanes.
4. **B3/B4 single-nonlinearity ceiling**: one 32-bit multiply + linear cross-mix cannot diffuse high-half-only variation (stuck bit 50, proven).
5. **B1/B2**: 2-round ARX has effectively zero diffusion (|z| saturated at 502–512 across 32/33 scenarios).
6. **A: delay is S-box-agnostic** at fixed round count (PRESENT/GIFT/SKINNY all 50.9 at 7 rounds, 44.2 at 6); S-box choice moves statistics, not delay.
7. **C: P32's fixed point** (P32(31)=31) is a diffusion bottleneck — bit 31 exactly constant through round 3 on low-entropy inputs; the permutation, not the S-box, is the weak link (PRESENT 320 vs GIFT 168 worst-z).
8. **C: per-bit tests are blind to affine structure** — feistel8_xor passes all per-bit (2.74) yet has rank-14/16 low projection (mask32-lo16 |z|=1991). Joint-distribution reductions are essential.
9. **C: Feistel round ≈ 7–8.7u** in this flow (not ~5); 6 rounds ≈ 50+ > 44.3 regardless of statistics.
10. **A6**: two-rotation key schedule costs +9.0 delay for no statistical benefit.

## Methodology notes & caveats

- **Reference drift**: a mid-day service restart replaced Yosys 0.33 (REF=49.2) with 0.69; batch C ran under a verified `-fast`-equivalent shim with REF=50.8 (3.3% ABC-version drift). Batch A rebuilt Yosys 0.33 from source (commit 2584903) and re-ran under the original version (REF=49.2). All verdicts use the absolute bar 44.3 and are unaffected.
- **Flow caveat (all ratios)**: ABC `-fast` does no Booth/CSD recoding and maps adder-tree nodes as full CPAs; constant multipliers are systematically overpriced vs a production flow (≈0.6–0.7×). Ratios are flow-relative screening numbers, not P&R predictions.
- **Tool bugs fixed centrally**: analyze2.py LHS-concat assigns; screen_lib verbose-print crash. Open limitations: analyze2.py cannot parse yosys `$func$`/`$memrd`/hierarchical-dotted net names (agents worked around with inline-SOP RTL).
- **Spec corrections during screening**: D3's `0x7F4A` → `0x7F4B` (even→odd, was a spec bug); SKINNY S-box table in the brief was wrong, published table used (C 6 9 0 1 A 2 B 3 8 5 D 4 E 7 F); A7/A8's `x^=L(x)` notation collapses to non-bijective 2-term — implemented as the proven-bijective 3-term `x:=x^ROTL(x,13)^ROTL(x,41)`.
- **Statistics**: extended scenario catalog (PTR j=8/16, STRIDE-MPOW2, HIGH-ONLY, DESC, SINGLE-BIT, key-sweep) + Lemire/mask/mod reductions; bar per-bit 4.0 / reduction 4.5. Even the 12-round reference FLAGs mildly (4.36) under the new catalog — candidates were judged against the absolute bar, with the reference as context.
- All models: scalar==vectorized checked; bijectivity spot-checks 3×200k collision-free; all RTL 64/64 vs model.

---

# Round 2 (2026-10-01): calibrated screen, 28 new candidates — 0 / 28 pass both gates

**Headline:** three `spn4_xorlin` rotation variants are the first candidates in either
round to **CAL_PASS** the statistical gate with zero rejections — but all sit at
**44.8**, exactly 0.5u over the 44.3 delay bar, and the delay is rotation-invariant
(structural, not winnable by constant choice). No winner declared.

| Gate | Pass | Fail |
|------|------|------|
| Delay ≤ 44.3 | 17 | 11 |
| Calibrated screen CAL_PASS | 3 | 25 |
| **Both** | **0** | **28** |

## Methodology changes (round 2)

- **Calibrated flagging** (`screen_cal.py`, new; `screen_lib.py` untouched): per
  (scenario, key) cell, Fisher-combine the 64 two-sided per-bit p-values (df=128);
  per (SEQ|PTR-j8, key) cell, Fisher-combine the 9 reduction p-values (df=18);
  Holm-Bonferroni across all cells (448 per-bit + 20 reduction), alpha=0.01.
  Verdict CAL_PASS iff zero rejections. Old absolute bars (|z| 4.0/4.5) reported
  for continuity but do not gate. Caveat: per-bit tests within a cell share the
  same N outputs (not independent); Fisher is used as the prescribed screening
  heuristic, with a scenario-level Bonferroni check reported alongside.
- **Validation of the calibration**: keyed splitmix64 → raw FLAG (4.36, same as
  the 12-round reference's false positive) but **CAL_PASS (0/0)**; round-1 D3
  (known catastrophic) → **CAL_FLAG (311/20)**. The calibration fixes the raw
  bar's false positive while still catching real defects hard.
- **Fresh reference**: 64×64 variable multiplier remeasured at **50.8**
  (yosys-shim flow; was 49.2 under 0.33). Absolute bar kept at **44.3**
  (conservative). Ratios reported vs both 50.8 and the new CSD reference.
- **CSD reference** (`gen_wallace.py`, new): hand-built Wallace carry-save CSD
  tree for 64-bit constant multiply. Dense splitmix const (23 CSD terms):
  **41.9** (vs 47.3 behavioral, vs 67.1 CPA-tree). Sparse 4-term consts:
  24.8–27.7; 6-term: 28.5–30.9. The 41.9 Wallace-dense is the
  production-representative const-mult reference; candidate ratios reported
  against BOTH 50.8 (naive) and 41.9 (CSD).
- All 28 round-2 candidates: vectorized Python model + combinational Verilog +
  64/64 (or 200/200) RTL-vs-model check + 3×200k bijectivity spot-check.
  No round-1 files modified.

## Full round-2 candidate table

Delay = absolute crit (bar ≤ 44.3). Ratios vs 50.8 / vs 41.9. Screen = raw
worst per-bit |z| / worst reduction |z| → raw verdict; cal = CAL_PASS/FLAG
(rej_pb/rej_red).

| # | Candidate | Construction | Crit (r50.8/r41.9) | Raw pb/red → raw | Calibrated | Verdict |
|---|-----------|--------------|---------------------|------------------|------------|---------|
| H1 | hyb_sp4b_121 | SPN1 → *=0xffffe0002001 (Wallace 4t) → SPN1 → whiten | 41.0 (0.807/0.979) | 512 @ SEQ / 229436 @ SEQ-lem10 → FLAG | CAL_FLAG (311/20) | OUT-screen |
| H2 | hyb_sp4b_12 | *=C → SPN2 → whiten | 40.5 (0.797/0.967) | 512 @ HIGH-ONLY / 811 @ SEQ-lem10 → FLAG | CAL_FLAG (180/20) | OUT-screen |
| H3 | hyb_sp4b_21 | SPN2 → *=C → whiten | 41.5 (0.817/0.990) | 512 @ SEQ / 11816962 @ SEQ-m32c → FLAG | CAL_FLAG (319/20) | OUT-screen |
| H4 | hyb_sp6a_121 | SPN1 → *=0x8001fff8001fe1 (6t) → SPN1 → whiten | 47.4 (0.933/1.131) | 512 @ HIGH-ONLY / 10735 @ SEQ-mask8 → FLAG | CAL_FLAG (310/20) | OUT-both |
| H5 | hyb_sp4b_121_gift | H1 with GIFT S-box | 40.5 (0.797/0.967) | 512 @ SEQ / 353846 @ SEQ-lem2^32 → FLAG | CAL_FLAG (310/20) | OUT-screen |
| H6 | hyb_dense_mult | (val^key)*0xBF58476D1CE4E5B9 (Wallace 23t) → whiten, no S-box (probe) | 45.1 (0.888/1.076) | 512 @ PTR-j8 / 81244 @ PTR-j8-mask8 → FLAG | CAL_FLAG (271/20) | OUT-both |
| L1 | lane4_il_a | interleave → 4×16b odd mult → downmix → 1 Feistel cross → deinterleave | 35.4 (0.697/0.845) | 448 @ POW2-2^2 / 24339 @ PTR-j8 → FLAG | CAL_FLAG (300/20) | OUT-screen |
| L2 | lane4_il_b | L1 + 2nd cross round (1,2),(3,0) | 38.4 (0.756/0.916) | 42 @ POW2-2^8 / 236 @ SEQ → FLAG | CAL_FLAG (66/20) | OUT-screen |
| L3 | lane4_il_c | L2, consts (8517,CC6D,4E35,B729), rots (5,13)/(9,21) | 36.9 (0.726/0.881) | 14 @ DESC / 22.3 @ PTR-j8 → FLAG | CAL_FLAG (3/20) | OUT-screen |
| L4 | lane4_il_d | L3 with ADDITION cross (nonlinear) | 56.1 (1.104/1.339) | 16 @ POW2-2^48 / 11.9 @ SEQ → FLAG | CAL_FLAG (5/5) | OUT-both |
| L5 | lane2_il_e | 2×32b interleaved, 2 rounds, dense consts | 50.6 (0.996/1.208) | targeted only | not fully screened | OUT-delay |
| L6 | lane2_il_f | 2×32b, 1 round, dense consts | 47.6 (0.937/1.136) | targeted ≤6.4 | not fully screened | OUT-delay |
| L7 | lane2_il_g | 2×32b, sparse consts | 32.7 (0.644/0.780) | catastrophic | CAL_FLAG (300/–) | OUT-screen |
| L8 | lane2_il_h | 2×32b, moderate consts | 46.4 (0.913/1.107) | HIGH-ONLY m32-lo16 z=303 | not fully screened | OUT-delay |
| L9 | lane2_il_i | 2×32b, sparser consts | 34.4 (0.677/0.821) | — | CAL_FLAG (279/–) | OUT-screen |
| R1 | arx2_xs_a | 2 adds + 3 xorshifts (29,17,43) + whiten | 40.7 (0.801/0.971) | 512 @ SEQ / 5928722 @ SEQ-lem10 → FLAG | CAL_FLAG (310/20) | OUT-screen |
| R2 | arx2_xs_b | 2 adds, murmur-ish shifts (33,…) | 40.0 (0.787/0.955) | 512 @ SEQ / 5928722 → FLAG | CAL_FLAG (290/20) | OUT-screen |
| R3 | arx2_xor | xor-key form, 2 adds | 39.0 (0.768/0.931) | 512 @ SEQ / 5928722 → FLAG | CAL_FLAG (310/20) | OUT-screen |
| R4 | arx3_full_probe | 3-round (add+3 xorshift) STATISTICAL PROBE, no RTL (~76.5 est) | — (>44.3) | 115.6 @ POW2-2^48 / 22.6 → FLAG | CAL_FLAG (68/20) | OUT-both |
| S1 | spn5_present | 5-round PRESENT + pLayer | 37.5 (0.738/0.895) | 448 @ HIGH-ONLY / 26521 @ SEQ-lem10 → FLAG | CAL_FLAG (308/20) | OUT-screen |
| S2 | spn5_gift | 5-round GIFT + pLayer | 37.5 (0.738/0.895) | 512 @ DESC / 22374 @ SEQ-lem10 → FLAG | CAL_FLAG (308/20) | OUT-screen |
| S3 | spn5_present_rot | S1 + free ROTL(7) S-box→pLayer | 37.5 (0.738/0.895) | 336 @ POW2-2^32 / 1824 @ PTR-j8-mask8 → FLAG | CAL_FLAG (308/20) | OUT-screen |
| S4 | spn5_present_rot11 | S1 + free ROTL(11) | 37.5 (0.738/0.895) | 478 @ PTR-j16 / 1240 @ PTR-j8-mask8 → FLAG | CAL_FLAG (308/20) | OUT-screen |
| S5 | spn5_present_ks2 | S1 + 2-rotation KS | 46.5 (0.915/1.110) | not screened (delay gate) | — | OUT-delay |
| X1 | spn4_xorlin_719 | 4-rd PRESENT + L=x^R7^R19 | 44.8 (0.882/1.069) | 4.59 @ POW2-2^48 / 2.85 @ SEQ-mask8 → FLAG | **CAL_PASS (0/0)** | OUT-delay (0.5u) |
| X2 | spn4_xorlin_1753 | 4-rd PRESENT + L=x^R17^R53 | 44.8 (0.882/1.069) | 4.26 @ DESC / 3.98 @ SEQ-mod7 → FLAG | **CAL_PASS (0/0)** | OUT-delay (0.5u) |
| X3 | spn4_xorlin_1137 | 4-rd PRESENT + L=x^R11^R37 | 44.8 (0.882/1.069) | 4.05 @ DESC / 2.70 @ PTR-j8-mod1000 → FLAG | **CAL_PASS (0/0)** | OUT-delay (0.5u) |
| X4 | spn4_xorlin_gift | 4-rd GIFT + L=x^R13^R41 | 44.8 (0.882/1.069) | 6.34 @ POW2-2^2 / 2.64 @ PTR-j8 → FLAG | CAL_FLAG (4/0) | OUT-both |

Bijectivity: H: xor-key + SPN rounds (S-box+pLayer) + odd-C mult + whitening;
L: interleave/deinterleave perms + per-lane odd mults + triangular downmix
(w^=w>>8, w^=w>>4: upper-triangular, 1s on diagonal) + Feistel crosses
(L4: addition cross, still bijective half-steps) + whitening;
R: adds + xorshifts + whitening; S/X: SPN (S-box + pLayer or 3-term L).
All spot-checks 3×200k collision-free; all RTL 64/64 (L1–L4: 200/200) vs model.

## Pareto update (delay vs quality; quality = raw worst |z|)

Round-2 non-dominated set: **D3 (r1) → lane4_il_c → spn4_xorlin_1137**.
(D3: 32.2, catastrophic — delay-optimal anchor. lane4_il_c: 36.9, 22.3 —
best quality among delay-passing non-xorlin. xorlin_1137: 44.8, 4.05/CAL_PASS
— quality-optimal, dominates round-1 A8 (44.8, 5.7) and REF (73.6, 4.36).)
All other 25 round-2 candidates are dominated. The knee moved: the quality
frontier at ≤44.8 is now CAL_PASS (was: mild FLAG).

## Nearest misses (NOT finalists — no pipeline partitions built)

### 1. spn4_xorlin_1137 / _719 / _1753 — the only CAL_PASS candidates
- Delay 44.8 — misses by **0.5u**. Screen: zero calibrated rejections across
  448+20 cells (raw worst 4.05–4.59 per-bit, 2.70–3.98 reduction).
- Blocker is delay-only, and it is structural: all four rotation pairs map to
  IDENTICAL 44.8 / 7360 cells / 21568 area — the 3-term xor tree dominates and
  ABC maps it identically. Rotation lottery cannot win; a different lever is
  needed (see round-3 directions).
- Hypothetical pipeline (NOT built, gate failed): 2 stages (2+2 rounds),
  stage ≈22.4, T_clk ≈24.6, latency ≈49.3 ≤ 50.8 — closes on latency IF the
  0.5u delay overhang is removed.

### 2. lane4_il_c — best delay-passing non-xorlin
- Delay 36.9 (0.726×) — PASSES with margin. Screen CAL_FLAG (3/20): per-bit
  nearly clean (3 cells) but all 20 reduction cells reject — systematic
  joint-distribution under-dispersion (mask8 z=+22.3 on PTR-j8).
- Blocker: structural uniformity deficit of the one-nonlinear-layer design.

### 3. hyb_sp4b_12 — best hybrid delay
- Delay 40.5 — PASSES. Screen CAL_FLAG (180/20), structural (see lesson 1).

## Family verdicts

- **Hybrids (H1–H6): DEAD at 2 SPN rounds.** Sparse-C Wallace mults are
  structurally broken (lesson 1). Dense-C mult alone (H6, 45.1) fails on the
  p[0]=x[0] law with no S-box. 3 SPN rounds (≈45–47) won't fit the bar.
- **Interleaved lanes (L1–L9): DEAD under joint constraints.** Interleaving
  fixes D3's dead lanes, and the bijective downmix (lesson 2) fixes
  triangularity, but the family is effectively a one-round SPN: one nonlinear
  layer wrapped in linear maps. Avalanche: input bit 60 flips only 20/64
  outputs. 32-bit lanes: dense too slow (47.6–50.6), sparse too weak.
- **Deeper ARX (R1–R4): DEAD.** 2-round: zero diffusion (saturated 512) at
  39–40.7 delay. 3-round statistical probe: still CAL_FLAG (115.6, 68/20) AND
  delay-excluded (~76.5). Multiply-free ARX cannot buy diffusion per unit-delay.
- **5-round pLayer SPN (S1–S5): DEAD as a structure.** All catastrophic
  (308/20); free rotations only reshuffle failure modes (reduction z down
  10–20×, per-bit unchanged); 2-rot KS costs +9.0u for nothing.
- **A8/xorlin variants (X1–X4): CLOSEST — 3 CAL_PASS, all 0.5u over delay.**
  The PRESENT S-box + 4-round 3-term-xorlin structure is the only one in 47
  screened candidates (both rounds) that is statistically clean. GIFT S-box
  strictly worse (4 rejections).

## Transferable lessons (round 2)

1. **Odd-constant multiply bit laws** (verified numerically): for ANY odd C,
   `(x*C)[0] = x[0]` exactly — a multiply must never be the last nonlinear op
   (bit 0 leaks; PTR-j8 → z=512). SPARSE C additionally copies
   `p[0..k] = x[0..k]` for k below its lowest nonzero CSD shift (e.g.
   0xffffe0002001 copies bits 0..12). Surrounding single SPN rounds neither
   whiten the mult's input structure (pLayer routes SEQ-constant S-box bits
   into the identity region: 19 constant output bits traced to nibbles 2,6,10,14)
   nor repair its output. Structural, not tunable.
2. **16-bit lane mults are lower-triangular** (out bit j ← in bits ≤j);
   interleave fixes dead lanes but constant low input bits still pin outputs.
   Fix: bijective downmix `w^=w>>8; w^=w>>4` (upper-triangular, 1s on diagonal,
   ~+2u) — required, not optional, for any lane-mult design.
3. **Wallace carry-save CSD trees beat behavioral const-mult in this flow**
   (dense 41.9 vs 47.3; the CPA-tree 67.1 was ABC mapping each node as a full
   CPA). Use `gen_wallace.py` for any future const-mult; the 41.9 number is the
   honest production-representative const-mult reference.
4. **5-round pLayer SPN is below the statistical threshold** for this use;
   free linear-layer tweaks (whole-state rotates) move failure modes, not mass.
5. **xorlin delay is rotation-invariant** (4 pairs → identical 44.8/7360/21568):
   the 3-term xor tree dominates; shaving 0.5u needs S-box/SOP or structural
   changes, not constant choice.
6. **PRESENT > GIFT for the xorlin structure** (0 vs 4 rejections); S-box choice
   is statistical, not delay (round-1 lesson 6 reconfirmed).
7. **ARX without multiplies**: 25.5u/round (add + 3 xorshifts); 3 rounds neither
   fit (76.5) nor mix (115.6). Dead end.
8. **Calibration works**: splitmix64 raw-FLAG→CAL_PASS; D3 raw-FLAG→CAL_FLAG
   (311/20). The round-1 "everything flags" problem was the uncalibrated bar.

## Round-3 directions (in priority order; not attempted)

1. **Shave 0.5u off spn4_xorlin_1137** (the winner-adjacent candidate): levers —
   (a) Espresso/QM-minimize the PRESENT S-box SOP before ABC (inline minterms
   are unoptimized); (b) absorb the final whitening xor into the last L stage;
   (c) a 4-bit S-box with cheaper SOP at equal statistical quality; (d) merge
   the initial `val^key` with rk[0]. Any success → immediate pipeline partition
   (2 stages, latency ≈49.3 ≤ 50.8) and promotion to finalist battery.
2. **Lane worker's flagged re-attempt**: 16-bit mult → PRESENT S-box → linear
   cross (≈38u est.) — one clean attempt (their S-box-after-cross test had an
   implementation bug: unmasked high nibbles).
3. **Multiply flanked by cheap 3-term xor-linear** (not full SPN rounds):
   sparse-C mult + L pre/post (≈2–3u each) might break the identity-region
   constancy within budget — one probe.
4. If (1) fails: accept that 44.3 forces a weaker statistical bar, or revisit
   whether the bar should be re-derived from post-P&R (not unit-delay) data
   once the Sky130 flow lands.

## Round-3 results (2026-10-01) — BREAKTHROUGH

**Objective**: Shave 0.5u off spn4_xorlin_1137 (44.8 → ≤44.3) via levers (a)/(b)/(c).

### Delay decomposition (probes)
- S-box layer alone: 6.2u (the hog — unoptimized 8-minterm SOP)
- L (3-term xor-linear): 4.0u
- Key XOR: 2.0u
- One full round: 12.7u

### QM minimization (lever a) — SUCCESS
Wrote exact Quine-McCluskey minimizer for PRESENT S-box. Found & fixed critical
bug: `combine()` didn't require equal don't-care masks → invalid primes
(5/64 bit-nibble mismatches). After fix: 0/64 mismatches. True minimal cubes:
bit0:6, bit1:5, bit2:5, bit3:5.

**V_a = `r3_xorlin_qm`**: QM-minimal SOP S-box, function-identical to baseline.
- EQUIV: 200/200 OK vs numpy model.
- Synth: **40.0** (0.787× multiplier; 6883 cells; area 18910, 0.410×).
- **44.8 → 40.0: saves 4.8u (needed 0.5u).** CAL_PASS inherited (bit-identical).

### Whitening absorption (lever b) — REJECTED
**V_b**: Absorb final whitening xor into L⁻¹ of last round. EQUIV-OK but
synth crit = **57.0** (dense L⁻¹ matrix → 12440 cells; the k4p network itself
is slow). Lever (b) is dead.

**V_c**: Merged initial `val^key` with rk[0]. EQUIV-OK but crit = **57.0**.
Same root cause. REJECTED.

### 2-stage pipeline — VERIFIED
`mix_pipe2_base`: rounds 0–1 | 64b state + 64b key + valid regs | rounds 2–3
+ whitening. **PIPE-OK**: 64 back-to-back inputs at 1/cycle, all outputs match
numpy model, valid tracking correct, 1-cycle latency. Throughput 1/cycle ✓.

### Sky130 P&R (V_a) — peer-reviewed 2026-10-01, numbers corrected
- Yosys synth → OpenROAD: **1700 sky130 instances, 25.5% utilization**
  (300µm die; the "6883 cells / ~9%" figure was the unit-delay screening count,
  wrongly carried over).
- STA: critical path **5.07 ns** (key[8] → out[39]) on the PLACED, UNROUTED
  netlist (wireload model, ideal IO) — a delay measurement, i.e. a lower bound,
  not a closure claim. (The "0 violations @ 10ns" framing was vacuous: the
  virtual clock is 10µs with zero IO delays.)
- Routing: was blocked by GRT-0701, root-caused to a missing `li1`
  `make_tracks` line in the script (not a tool/PDK version issue).
  `pnr_sky130.sh` fixed (li1 tracks + place_pins + full route + DRC +
  post-route STA); full detailed-route A/B did not survive the loaded machine
  (killed mid-route) — rerun `pnr/flow_full.tcl` on a quieter box.
- **Routed A/B (Sky130 TT/100C/1.8V, identical flow, 2026-10-01)** — global
  route + `estimate_parasitics -global_routing` STA (Steiner-tree wire
  estimates, strict improvement over the 5.07ns wireload number):
  mixer **5.91ns** (key[7]→out[26], 300µm, 25.50% util) vs 64×64→64
  multiplier **12.56ns** (b[23]→y[63], 545µm, 25.08% util) = **0.47×**.
  Better than the 0.787 screening ratio: the multiplier's high-fanout nets
  (max FO 76) cost real silicon delay but 0 in the unit-delay model. Caveat:
  the multiplier is ABC-mapped without Booth/CSD (M5) — a production
  multiplier would be faster than 12.56ns.

### Statistical batteries (V_a, via bit-identical models)
- **PractRand** (256MB, sequential inputs): **BRank FAIL** (R=+622 to +754,
  systematic across keys). 12-round SPN passes BRank → confirms rounds issue.
- **TestU01 SmallCrush**: 14/15 PASS; **SimpPoker FAIL** (p < 1e-300).
- **Differential profile** (peer-review remediation 2026-10-01,
  `peer_review_r3.md` §3.1): strong key-independent joint structure the screen
  never probed — per-output-bit flip biases up to ~0.05 for single-bit input
  deltas (z>200 at N=2²² pairs, sequential inputs; confirmed in C and numpy),
  low-8-bit truncated differentials χ² up to ~29000 (255 dof), full-64-bit
  output differences repeating up to 12× in 2²² pairs (~0 expected).
  Sequential inputs amplify biases ~7× vs random (δ=2¹⁸→bit20: −0.065 vs
  −0.009). Pairwise low-8-bit collision-forcing advantage ≤1.25× over brute
  force (δ=0x9); multi-way chaining unanalyzed. Does NOT break single-output
  uniformity — same class as the battery failures.
- **Interpretation**: 4 rounds sufficient for hash-map uniformity (CAL_PASS)
  but not PRNG-quality randomness. Fundamental latency-vs-randomness tradeoff:
  12 rounds passes PRNG tests but fails latency (1.51×). V_a is Pareto-optimal
  for the stated hash-map requirements.

### Round-3 candidate summary
| Candidate | Delay (u) | vs 44.3 | CAL | Verdict |
|-----------|-----------|---------|-----|---------|
| spn4_xorlin_1137 (baseline) | 44.8 | +0.5 OVER | PASS | Superseded |
| **r3_xorlin_qm (V_a)** | **40.0** | **-4.3 UNDER** | **PASS** | **WINNER** |
| r3_xorlin_qm_b (V_b) | 57.0 | +12.7 OVER | — | REJECTED |
| r3_xorlin_qm_bd (V_c) | 57.0 | +12.7 OVER | — | REJECTED |

### Updated Pareto frontier
Non-dominated set: **D3 (32.2, FLAG-catastrophic) → lane4_il_c (36.9, CAL_FLAG)
→ r3_xorlin_qm (40.0, CAL_PASS)**.
- V_a strictly dominates spn4_xorlin_1137 (40.0 < 44.8, same CAL_PASS).
- V_a is the first design to pass BOTH the delay bar (≤44.3) AND CAL_PASS.
