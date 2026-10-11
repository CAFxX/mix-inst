# Round 11 — S-box sweep (2026-10-02)

Target: beat/extend the frontier { `r9_feist6_rot311_nw`: 41.0u / 4,265 cells / 11,996,
`r8_feist6_s1_1sbox_nw`: 42.9u / 4,133 cells / 11,670 }.
Multiplier reference re-measured fresh in this round's pinned flow: **103.5u**
(cells 12,645, area 35,323). S0 bar: ≤ 0.9 × 103.5 = 93.15u.

Template (fixed for all 10): 6r Feistel, F = S-box layer → x^rotl32(x,a)^rotl32(x,b)
→ ^rk32, NO whitening, affine key schedule. Only the S-box varies — the one
primitive not yet attacked in rounds 7–10.

S-box tables verified against primary sources (cipher spec papers) before
generation; see `sboxes.json`. Notably the SKINNY-4 table was CORRECTED during
verification: three independent sources agree on
`[12,6,9,0,1,10,2,11,3,8,5,13,4,14,7,15]`, not the commonly misremembered
`[12,6,9,0,1,10,7,11,3,14,15,8,13,4,5,2]` (differs at positions 6,9,10,14).
SKINNY-8 (256 entries) from the NIST SKINNY spec, verified as a permutation;
an MDPI reproduction's typo at index 0xAA (0x80 vs 0x08) was resolved in
favor of the spec (permutation check).

RTL policy: S-box as Quine-McCluskey-minimized DNF direct boolean assigns,
all inside one `always @(*)` block, no Verilog functions. The 8-bit S-box
uses a case statement (DNF infeasible at 8 bits).

## S0 pre-screen (all 10 pass the 0.9× bar; none beats the frontier)

| Candidate | S-box | (a,b) | S0 delay | Ratio | Cells | Area |
|---|---|---|---|---:|---:|---:|---:|
| r11_feist6_gift311_nw | GIFT | (3,11) | 43.8u | 0.423× | 5,772 | 16,505 |
| r11_feist6_piccolo311_nw | Piccolo | (3,11) | 44.8u | 0.433× | 4,924 | 13,819 |
| r11_feist6_gift713_nw | GIFT | (7,13) | 44.9u | 0.434× | 5,783 | 16,404 |
| r11_feist6_sk4311_nw | SKINNY-4 | (3,11) | 45.5u | 0.440× | 4,737 | 13,397 |
| r11_feist6_sk4713_nw | SKINNY-4 | (7,13) | 45.5u | 0.440× | 5,190 | 14,308 |
| r11_feist6_piccolo713_nw | Piccolo | (7,13) | 45.7u | 0.442× | 5,024 | 14,001 |
| r11_feist6_s1mix311_nw | S1/PRESENT alt. | (3,11) | 46.3u | 0.447× | 4,814 | 13,457 |
| r11_feist6_present713_nw | PRESENT | (7,13) | 48.2u | 0.466× | 5,864 | 16,391 |
| r11_feist6_present311_nw | PRESENT | (3,11) | 49.1u | 0.474× | 5,700 | 15,726 |
| r11_feist6_sk8311_nw | 4×SKINNY-8 | (3,11) | 67.2u | 0.649× | 5,392 | 15,470 |

S0 numbers from `run_synth.py` (authorized path, Yosys 0.69 pinned,
dual-analyzer agreement).

Key finding: **every crypto S-box is slower *and* larger than the incumbent
S1.** The fastest (GIFT, 43.8u) is 6.8% slower than `r9_feist6_rot311_nw`
(41.0u); the smallest (SKINNY-4, 4,737 cells) is 14.6% larger than
`r8_feist6_s1_1sbox_nw` (4,133 cells). The 8-bit probe (67.2u) confirms
8-bit S-boxes are not delay-competitive in this template. **The S1 S-box's
minimal boolean depth is load-bearing for the delay frontier.**

Bit-exactness: C↔Python 10,000/10,000 PASS (10/10); RTL↔Python 300/300 PASS
(10/10). Pairwise model-output dedupe: all 10 distinct and distinct from the
frontier points.

Escape protocol (1 bug): the first RTL generation inlined the 1-based round-key
computation into the 0-based Verilog `for` loop keeping `(i+1)` — an off-by-one
shifting every round key by one round. C↔model passed (both 1-based); only
RTL↔model check_rtl caught it (10/10 failed pre-fix, 10/10 pass post-fix).
Fixed in `gen_r11.py`, all candidates regenerated, lesson added to
`~/AGENTS.md`.

## S1 screen (10/10 CAL_PASS)

| Candidate | S1 verdict | Notes |
|---|---|---|
| r11_feist6_present311_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_present713_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_gift311_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_gift713_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_sk4311_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_sk4713_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_piccolo311_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_piccolo713_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_sk8311_nw | CAL_PASS | 0 rejections, all 4 families |
| r11_feist6_s1mix311_nw | CAL_PASS | 0 rejections, all 4 families |

All 10 are statistically clean through S1. S2–S4 were not run: every
candidate is Pareto-dominated on S0 delay/cells/area (see below), so no
Pareto claim is possible and further stages cannot change the round's
conclusion.

## Pareto frontier

**UNCHANGED.** No round-11 candidate is non-dominated: the best delay
(43.8u) loses to 41.0u, the best cells (4,737) lose to 4,133, the best area
(13,397) loses to 11,670. The S-box axis is exhausted — S1 remains the
delay-optimal S-box for this template.

Round-11 findings:
1. Crypto S-boxes (PRESENT/GIFT/SKINNY-4/Piccolo) cost 3–8u of delay vs S1
   at 6r-nw: their stronger cryptographic properties come with deeper
   boolean circuits, and the F-function's critical path is S-box-dominated.
2. The 8-bit S-box probe (67.2u) settles it: 8-bit S-boxes are not
   delay-competitive here (4×256-entry mux trees dominate the path).
3. The heterogeneous alternating-S1/PRESENT idea (46.3u) lands between its
   parents, as expected — no synergy.
4. (3,11) vs (7,13) shows no consistent winner across S-boxes (GIFT and
   Piccolo prefer (3,11); PRESENT and SKINNY-4 are split), confirming the
   rotation-pair optimum is S-box-dependent but the differences are small
   (±1u).
