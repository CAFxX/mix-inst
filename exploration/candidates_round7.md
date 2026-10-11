# Round 7 Candidates — Feistel Family Expansion (2026-10-01)

## Strategic context
- **Delay bar**: relative, ≤0.9× the 64×64 multiplier re-measured in the current
  flow via `exploration/run_synth.py` (ONLY authorized delay path).
  Multiplier ref: 103.5u → **bar ≈ 93.2u**.
- **Round-6 finding**: Feistel with SPN F-functions is the ONLY structure to
  pass LIN/DIFF. Winner r6_feist8_spn (86.5u, 0.836×) cleared S0–S4.
- **Round-7 mission**: expand the Feistel family (round counts, F variants,
  key schedules, unbalanced/Misty) + justified outsiders. The search continues
  regardless of r6_feist8_spn — no ISA freeze.
- **Infra fix (round 7)**: `fast_battery/src/s0_delay.py` was missing
  `memory_map` before `techmap` (same bug class as round 6); hardened analyzers
  made it fail loudly instead of silently. Fixed 2026-10-01.

## Results

| candidate | composition | S0 delay | S1 | S2 | S3 | S4 | verdict |
|-----------|-------------|----------|----|----|----|----|---------|
| r7_ufeist48_16 (D) | 8r unbalanced Feistel 48/16, F:16→48 | — | FLAG (LIN 10/10 D=4096; DIFF 10/10) | — | — | — | **KILL S1** |
| r7_ufeist16_48 (D) | 8r unbalanced Feistel 16/48, F: S1×12→xor-fold→rotl-xor→^rk16 | **73.8u / 0.713×** / 5186 cells / 14606 area — PASS | **CAL_PASS** (0/10, 0/10, PB 0, RD 0) | PASS (0 repeats, max\|z\|=3.6) | PASS (1GB, no FAIL) | **FLAG** Collision p=1.6e-4 (repro p=1.1e-6 key0) | **KILL S4** |
| r7_feist4_spn (A) | 4r Feistel, val^key whitening | 44.1u / 0.426× / 4297 cells — PASS | FLAG (LIN 0, DIFF 0, **PB 24**, RD 0) | — | — | — | **KILL S1** |
| r7_feist6_spn (A) | 6r Feistel, val^key whitening | 66.1u / 0.639× / 6314 cells — PASS | FLAG (LIN 0, DIFF 0, PB 0, **RD 3**) | — | — | — | **KILL S1** (borderline) |
| r7_feist8_spn_nw (A) | **8r Feistel, NO whitening** (L=val>>32, R=val) | **84.7u / 0.818×** / 8489 cells / 22942 area — PASS | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=3.6) | PASS (1GB, no FAIL) | **PASS (15/15)** | **SURVIVES S0–S4** |
| r7_feist10_spn (A) | 10r Feistel, val^key whitening | 107.5u / 1.039× / 10798 cells — **FAIL** | CAL_PASS (0/0/0/0) | — | — | — | **KILL S0** |
| r7_feist8_gift (B) | 8r Feistel, GIFT S-box 2-layer F | **92.5u / 0.894×** / 10568 cells / 30300 area — PASS (0.7u margin) | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=3.8) | PASS (1GB, 227 clean, re-run confirmed) | **PASS** (s4b: all passed) | **SURVIVES S0–S4** (dominated by nw on delay/area) |
| r7_feist8_s1_1sbox (B) | 8r Feistel, S1 **1-S-box-layer** F | **56.5u / 0.546×** / 6063 cells / 17098 area — PASS | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=3.8) | PASS (1GB, 227 clean) | **PASS** (all 15) | **SURVIVES S0–S4 — NEW LEADER** |
| r7_feist8_s1_3sbox (B) | 8r Feistel, S1 3-S-box-layer F | — | FLAG (LIN 0, **DIFF 1**, marg skipped) | — | — | — | **KILL S1** |
| r7_feist8_msb0 (B) | 8r Feistel, Midori-Sb0 2-layer F | **85.7u / 0.828×** / 7869 cells / 22048 area — PASS | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=3.4) | PASS* (1GB; 16MB: 1 mild suspicious [Low1/64]Gap-16:B R=+7.0 p=1.5e-5, reproduced ×2) | **SUSPECT** (HammingIndep p=0.9991) | **KILL S4** |
| r7_feist8_r311 (C) | 8r Feistel, F linear `x^rotl32(x,3)^rotl32(x,11)` | **84.3u / 0.814×** / 8218 cells — PASS | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=3.7) | PASS (1GB, no FAIL) | **PASS** (15/15) | **SURVIVES S0–S4** |
| r7_feist8_r517 (C) | 8r Feistel, F linear `x^rotl32(x,5)^rotl32(x,17)` | **86.3u / 0.834×** / 8652 cells — PASS | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=3.5) | PASS (1GB, no FAIL) | **PASS** (15/15) | **SURVIVES S0–S4** |
| r7_feist8_rksimple (C) | 8r Feistel, rk=`rotl64(k,13(i+1))` (no const) | **87.4u / 0.844×** / 8510 cells — PASS | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=4.1) | PASS (1GB, no FAIL) | **PASS** (15/15) | **SURVIVES S0–S4** ⚠ weak-key caveat (k=0 → zero round keys) |
| r7_feist8_rkcheap (C) | 8r Feistel, rk=`k^(i+1)·G` (no rotation) | **87.4u / 0.844×** / 8552 cells — PASS | **CAL_PASS** (0/0/0/0) | PASS (0 repeats, max\|z\|=4.0) | PASS (1GB, no FAIL) | **PASS** (15/15) | **SURVIVES S0–S4** ⚠ related-key caveat |
| r7_feist8_mid32 (C) | 8r Feistel, 32-bit Midori linear in F | — | **KILLED** LIN 10/10, DIFF 10/10 | — | — | — | **KILL S1** (genuine flaw: column-local Midori splits F into two independent 16-bit lanes) |
| r7_misty (D) | 8r Feistel, recursive 3r-Feistel F | — | FLAG (LIN 10/10 D=4096; DIFF 10/10) | — | — | — | **KILL S1** |
| r7_spn_s1rotl (D) | 4r 64b SPN, S1 + rotl-xor linear | — | FLAG (LIN 10/10 D=4096; DIFF 10/10) | — | — | — | **KILL S1** |

### Team D detail
- **r7_ufeist16_48** is the **second structure in the entire search to clear the
  amended S1** (after r6_feist8_spn) and the first to beat the winner on delay
  (73.8u = 0.713× vs 86.5u = 0.836×; 5186 cells vs 8660). Composition:
  `val^key` whitening → 8× unbalanced-Feistel
  (`newL=(R>>32)&0xFFFF`, `newR=(((R&0xFFFFFFFF)<<16)|((L^F(R))&0xFFFF))&0xFFF…`);
  F = S1 on 12 nibbles → xor-fold 48→16 → `x^rotl16(x,3)^rotl16(x,7)` → ^rk16;
  out `(L<<48)|R`. Killed at S4: SmallCrush Collision excess
  (obs 3106 vs exp 2909.25±53.9, p=1.6e-4; key0 repro 3169, p=1.1e-6) —
  real joint-distribution anomaly, not fluke. Equivalence: model≡C 10k/10k,
  RTL≡model 200/200 iverilog; bijectivity 1500/1500 inverse round-trips.
  Reference: `mix(0,0x123456789ABCDEF0)=0x2a49589392def95d`.
- **r7_ufeist48_16**: F's 48→16 truncation discards nibbles; dead nibbles,
  avalanche bits 31/63 → 1.0 output-bit change. Killed S1.
- **r7_misty**: G(b)=sbox16(b)^rk16 has no diffusion (4 parallel S-boxes);
  end-to-end avalanche 8.01 bits. Killed S1.
- **r7_spn_s1rotl**: rotl-xor linear at 64b does not rescue deep-SPN linearity
  (same failure as round-6 Midori-M SPNs). Killed S1. Note: proposed
  `x^rotl64(x,7)^rotl64(x,13)^rotl64(x,29)` is provably singular
  (even-term rotation-XOR divisible by x+1 over GF(2), rank 63) — used
  2-term version instead.
- Infra: `/tmp` was wiped mid-run; binaries rebuilt into
  `round7/results/r7_ufeist16_48/_bin/`. Teams should build into results dir.

## Key findings
- Unbalanced Feistel 16/48 is viable: passes amended S1, S2, S3, and is
  FASTER than the balanced winner (0.713× vs 0.836×). The S4 Collision excess
  (~+7% pair collisions) is small but real and reproducible across keys —
  suggests a mild structural weakness in the 16-bit R path's joint
  distribution, possibly fixable (more rounds? different F?).
- Unbalanced 48/16 fails: expanding F then truncating loses nibbles.
- Misty-like recursive F fails: inner G needs its own diffusion.
- SPN with rotl-xor linear fails exactly like Midori-M SPNs: the linear
  layer choice is not what breaks deep-SPN linearity.
- **Whitening is statistically irrelevant and costs delay** (Team A):
  `r7_feist8_spn_nw` CAL_PASSes identically to the whitened winner
  (0 rejections all families) while 1.8u faster and smaller.
- **Minimum viable rounds = 8** under the amended screen: 4r dies hard
  (24 PB rejections), 6r borderline (3 RD rejections), 8r clean, 10r buys
  zero additional margin but misses the delay bar (1.039×).
- **Delay is ~linear in rounds** in this regime: 4r=44.1 (0.426×),
  6r=66.1 (0.639×), 8r-nw=84.7 (0.818×), 8r-whit=86.5 (0.836×),
  10r=107.5 (1.039×) — ~22–24u per 2 rounds.
- **Single-S-box F is dramatically cheaper and still CAL_PASS** (Team B):
  `r7_feist8_s1_1sbox` = 56.5u (0.546×), 6063 cells — 35% faster and 30%
  smaller than the winner, **S0–S4 clear**.
- **3 S-box layers in F is WORSE than 2**: `r7_feist8_s1_3sbox` flags DIFF
  (1 rejection) where the 2-layer winner is clean — more S-boxes ≠ better.
- **GIFT S-box passes everything but barely passes S0** (92.5u = 0.894×,
  0.7u margin) — GIFT's S-box is slower in this library than S1.
- **Midori Sb0 is SUSPECT at S4** (HammingIndep p=0.9991) with a reproduced
  mild PractRand anomaly — not a winner.
- **Rotation pair barely matters** (Team C): r311 (3,11) = 84.3u, r517
  (5,17) = 86.3u, winner's (7,13) = 86.5u — all CAL_PASS, S2/S3/S4 clean,
  no statistical daylight at this battery depth. r311 marginally fastest.
- **Key schedule is nearly free** (Team C): dropping the round-constant
  multiply (rksimple) or the rotation (rkcheap) both survive S0–S4 at
  87.4u — but carry structural caveats OUTSIDE the fixed-key battery:
  rksimple has k=0 → all-zero round keys (weak key); rkcheap's round keys
  differ only by known constants (related-key structure). Flag for M9.
- **Column-local linear layers are fatal** (Team C): 32-bit Midori splits F
  into two independent 16-bit lanes — the "64-bit" Feistel is really two
  concatenated 32-bit ciphers. Genuine design flaw, not a bug (RTL 24/24
  vs model). Follow-up lead: 8-nibble single-column Midori adaptation.

## Pareto frontier (cumulative, amended screen + delay)

### Round 8 update (2026-10-02) — THE PARETO POINT MOVED
- **r8_feist6_s1_1sbox_nw** (round 8): 6r Feistel, F = S1 S-box layer →
  x^rotl32(x,7)^rotl32(x,13) → ^rk32, NO input whitening. **42.9u, 0.414×,
  4133 cells, area 11,670** — S0–S4 CLEAR + Q1 (SAC/BIC, N=2^18) at noise
  floor (sac_z5=0, maxdev 0.0038, bic 0.0080, mean 31.999). **NEW STANDING
  LEADER** — dominates r7_feist8_s1_1sbox on all three axes (24% faster,
  32% fewer cells, 32% less area). Full evidence in
  `round8/ROUND8_TABLE.md`. Lesson: 6 rounds of this F suffice; the 8-round
  leader was over-engineered, and whitening is pure cost at 6 rounds (nw is
  0.8u faster than the whitened twin).
- **r8_feist6_pbox** (round 8): same 6r F + P32 bit-perm on new R each round,
  whitened. **43.5u, 0.420×, 4544 cells** — S0–S4 CLEAR + Q1 noise floor.
  Second-fastest; the permutation costs ~0.6u of nothing (free in unit
  delay) but buys no statistics — strictly dominated by the nw twin.
  (RTL generator bug — module-level assign read of an always-block reg →
  Yosys combinational loop — fixed and re-verified; see AGENTS.md.)
- **r8_feist6_s1_1sbox** (round 8): 6r, whitened. **43.7u, 0.422×, 4744
  cells** — S0–S4 CLEAR + Q1 noise floor. The 6-round SPN-F kill from
  round 7 does NOT generalize: this F is stronger per round.
- **r8_feist7_s1_1sbox** (round 8): 7r, whitened. **50.2u, 0.485×, 5452
  cells** — S0–S4 CLEAR + Q1 noise floor.
- **r8_feist6_s1_alt** (round 8): 6r, alternating 1-S-box/2-S-box F,
  whitened. **55.0u, 0.531×, 5436 cells** — S0–S4 CLEAR + Q1 noise floor.
- **r8_feist6_r311 / r8_feist6_r517** (round 8): 6r, F=S1+lin311+S1 /
  S1+lin517+S1. **64.1u / 65.5u** — S0–S4 clear but dominated (r311/r517
  rotation pairs cost ~50% delay vs the single-S-box F at the same round
  count).
- **r8_feist4_s1_3sbox** (round 8): 4r × 3-S-box-layer F. **68.2u** —
  S0–S4 clear; 4 rounds CAN pass with a strong enough F, but delay is
  dominated.

Round-8 kills: r8_feist8_midori + r8_feist6_midori (S1: LIN+DIFF FLAG,
rej=10/10, |z|~1.5M — the Midori MixColumn preserves linear structure;
single-column adaptation fails); r8_feist7_s1_1sbox_nw (S1 LIN FLAG —
whitening matters at 7 rounds); r8_feist8_s1_1sbox_nw (S1 marginal RD
rej=1 — whitening matters at 8 rounds); r8_ufeist16_48_f2 (S0: 101.6u,
0.982× > 0.9 bar — ufeist16/48 hopeless on delay).

### Prior standings
- **r7_feist8_s1_1sbox** (round 7, Team B): 56.5u, 0.546×, 6063 cells,
  CAL_PASS, **S0–S4 CLEAR — NEW STANDING LEADER** (35% faster, 30% smaller
  than the r6 winner; single-S-box F costs nothing statistically)
- **r7_feist8_r311** (round 7, Team C): 84.3u, 0.814×, 8218 cells, CAL_PASS,
  **S0–S4 clear** — fastest of the 2-S-box-F family
- **r7_feist8_spn_nw** (round 7, Team A): 84.7u, 0.818×, CAL_PASS, **S0–S4
  clear** — third fully-cleared design
- **r6_feist8_spn** (round 6): 86.5u, 0.836×, CAL_PASS, S0–S4 clear —
  superseded (whitening + 2nd S-box layer both pure cost)
- **r7_feist8_r517** (round 7, Team C): 86.3u, 0.834×, CAL_PASS, **S0–S4
  clear** — no daylight vs winner's rotation pair
- **r7_feist8_rksimple / r7_feist8_rkcheap** (round 7, Team C): 87.4u,
  0.844×, CAL_PASS, **S0–S4 clear** — with weak-key / related-key caveats
- **r7_feist8_gift** (round 7, Team B): 92.5u, 0.894×, CAL_PASS, **S0–S4
  clear** — passes but dominated on delay and area
- **r7_ufeist16_48** (round 7, Team D): 73.8u, 0.713×, CAL_PASS, S2+S3 clear, **KILLED S4** (Collision excess) — fastest CAL_PASS design, not a winner
- **r7_feist8_msb0** (round 7, Team B): 85.7u, 0.828×, CAL_PASS, **S4 SUSPECT**
  (HammingIndep p=0.9991) — not a winner

## Kill log
| candidate | stage | reason |
|-----------|-------|--------|
| r7_ufeist48_16 | S1 | LIN 10/10 D=4096, DIFF 10/10 \|z\|≈740k — dead nibbles in F expansion |
| r7_misty | S1 | LIN 10/10 D=4096, DIFF 10/10 — inner G lacks diffusion |
| r7_spn_s1rotl | S1 | LIN 10/10 D=4096, DIFF 10/10 \|z\|≈134–152k — deep-SPN linearity |
| r7_ufeist16_48 | S4 | SmallCrush Collision p=1.6e-4 / repro 1.1e-6 — excess consecutive-pair collisions |
| r7_feist4_spn | S1 | PB 24 rejections (POW2-2^32/POW2-2^48/HIGH-ONLY cells) — 4 rounds insufficient |
| r7_feist6_spn | S1 | RD 3 rejections (borderline; LIN/DIFF clean) — 6 rounds marginal |
| r7_feist10_spn | S0 | 107.5u = 1.039× > 0.9× bar — 10 rounds too slow |
| r7_feist8_s1_3sbox | S1 | DIFF 1 rejection (marginal skipped) — 3 S-box layers in F WORSE than 2 |
| r7_feist8_msb0 | S4 | SUSPECT: SmallCrush HammingIndep p=0.9991 (outside crush bounds); PractRand 16MB mild [Low1/64]Gap-16:B reproduced ×2 |
| r7_feist8_mid32 | S1 | LIN 10/10, DIFF 10/10 — 32-bit Midori is column-local: F splits into two independent 16-bit lanes (rank 33/64 consecutive outputs; deltas 2^16/2^17 → zero low-8-bit diffs) |
