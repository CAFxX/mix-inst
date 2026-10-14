# Round HYB — hybridization (cross-family trait combos) + wide constructions

**Date:** 2026-10-03. **Frontier after round:** TBD.
Frontier S entering: {r20_feist6_alt_notr_chioff13all_nw: 37.0u, r19_feist6_alt_notr_chioff13_nw: 37.4u, r20_feist6_alt_notr_chioff31_nw: 37.5u}.
Frontier Q entering: {r19_fm07 38.8u, fm11 39.3u, fm311 39.5u, r15 parsplit 40.7u, r9 41.0u, r8 42.9u}.

**Multiplier reference:** 103.5u (pinned Yosys-0.69 flow; S0 bar ≤ 93.15u).

## Key schedules

- **RK32** (32-bit round keys, all Feistel hybrids incl. D3, P1/P2): affine
  1-based schedule identical to r7/r8/r9/r13/r15/r18/r19/r20
  (see `round_hyb/models/rhyb.py::_rk32_std_np`).
- **RK64** (64-bit round keys, W1/W2/D1/D2 — NEW, Carlo 2026-10-03):
  `RK64(k, i) = rotl64(k, 7*i) ^ (i * 0x9E3779B97F4A7C15)`, i 1-based.
  Implemented identically in numpy (`_rk64_new_np`), C (`RK64new`),
  Verilog (`V_RK64NEW_LOOP`, `(i+2)`→`(i+1)` convention derived in comment).

## Families

### A. Feistel hybrids (10, all 6-round balanced Feistel, no whitening, RK32)

Round-F tags: s1_311 = lin(3,11)(S1(R))^rk; chi_311 = lin(3,11)(chi32(R))^rk;
chi_notr = chi32(R)^rk; chi32v_311 = lin(3,11)(chi32v(R))^rk (offsets (1,3));
chi32w_311 = lin(3,11)(chi32w(R))^rk (offsets (3,1)); chi_fm11 =
(y^rotl32(y,11)), y = chi32(R)^rk; ps_311 = lin(3,11)((chi16(R>>16)<<16) |
S1_16(R&0xFFFF))^rk; ps_notr (no linear); ps_chi16v_311 ((1,3) chi16);
ps_chi16w_311 ((3,1) chi16); ps_keyin_311 (key XORed into chi16 half input);
ps_3rot = lin3(parsplit)^rk, lin3 = x^rotl32(x,3)^rotl32(x,7)^rotl32(x,11).

1. **rh_feist6_parsplit_notr_nw** — [ps_311, chi_311, ps_311, chi_311, ps_311, chi_notr]: parsplit-F × alt-notr alternating chassis × final truncation.
2. **rh_feist6_parsplit_notr31_nw** — [ps_311, chi32w_311 ×2 alt, chi_notr]: #1 on the (3,1) size-play chassis.
3. **rh_feist6_parsplit_chioff13_nw** — [ps_chi16v_311 ×6]: chioff13's (1,3) speed trait × parsplit chassis.
4. **rh_feist6_parsplit_chioff31_nw** — [ps_chi16w_311 ×6]: chioff31's (3,1) size trait × parsplit chassis.
5. **rh_feist6_parsplit_keyin_nw** — [ps_keyin_311 ×6]: keyin × parsplit (O25 was notr-only).
6. **rh_feist6_notr_psfinal_nw** — [s1_311, chi32v_311, s1_311, chi32v_311, s1_311, ps_notr]: notr speed chassis × parsplit truncated final as BIC cure.
7. **rh_feist6_notr_psfinal31_nw** — [s1_311, chi32w_311 ×2 alt, ps_notr]: #6 on the (3,1) chassis.
8. **rh_feist6_parsplit_3rot_nw** — [ps_3rot ×6]: 3-rotation linear (O2 was alt/chi-F-only) × parsplit.
9. **rh_feist6_chioff13_fm11_nw** — [s1_311, chi32v_311, s1_311, chi32v_311, s1_311, chi_fm11]: fm11 cure × chioff13 chassis. Frontier-Q push.
10. **rh_feist6_chioff31_fm11_nw** — [s1_311, chi32w_311 ×2 alt, chi_fm11]: fm11 × chioff31 chassis. Frontier-Q push.

### B. Wide constructions (7)

- **W1 rh_spn3_s1_nw** — full-64-bit SPN, 3 rounds: X ^= RK64(k,i); X = 16× S1
  nibbles; X = lin64(X) = X ^ rotl64(X,3) ^ rotl64(X,11); then X ^= RK64(k,4).
- **W2 rh_spn4_s1_nw** — same, 4 rounds + final key RK64(k,5).
  Bijectivity: S1 is a permutation (self-test verified); lin64 is the
  GF(2)-linear map 1+x³+x¹¹; over GF(2), x⁶⁴+1 = (x+1)⁶⁴, so
  gcd(1+x³+x¹¹, x⁶⁴+1) = 1 iff (x+1) ∤ (1+x³+x¹¹) iff p(1) = 1⊕1⊕1 = 1 ≠ 0.
  Hence lin64 is a permutation; each round is key-XOR ∘ S1_64 ∘ lin64
  (all permutations) ⇒ whole SPN is bijective. Encrypt/decrypt round-trip
  self-tested (lin64 inverse via exact GF(2) Gauss-Jordan).
- **P1 rh_lm_parsplit_nw** — PROPER Lai-Massey, 6 rounds: D = L ^ R;
  T = F_parsplit(D, rk32); (L', R') = (R ^ T, D) [σ(U,V) = (V, U^V) applied
  to (L^T, R^T)]. **Re-test of the r13 LM skeleton with a new F**
  (r13 tested S1-F: 4r FAILS S1 LIN rej=10 structural — the R'=D half leaks
  the difference linearly, F-independent; 6r passes S1 but dominated at
  45.6u; "Family closed" FOR S1-F LM only). Round-input variation proof:
  D_1 = L^R; D_2 = L ^ T_1 — F's input varies across rounds (the naive-LM
  failure mode is absent). Model decrypt + round-trip tested.
- **P2 rh_lm_chi_nw** — same LM skeleton, T = lin(3,11)(chi32(D)) ^ rk32, 6r.
  Same re-test framing as P1 (chi-F ≈ 2u/round cheaper than S1-F).
- **D1 rh_wide128_feist4_nw** — 128-bit state, 64-bit halves, 4r Feistel,
  F_64(X, rk64) = lin64(S1_64(X)) ^ rk64. Expansion (injective):
  A = v ^ RK64(k,101); B = rotl64(v,13) ^ RK64(k,102). Compression:
  out = L' ^ R'. Bijectivity NOT by construction → collision gate:
  2²⁴ random + 64 single-bit + 2016 two-bit structured inputs, fixed key —
  result: **0 collisions** (log: round_hyb/collision_gate.log).
- **D2 rh_wide128_feist5_nw** — same with 5 rounds. Collision gate: **0**.
- **D3 rh_wideF_feist5_nw** — 5r STANDARD 64-bit Feistel (bijective by
  construction) with wide-internal F: X = (R‖rk32); X = S1_64(X);
  X = lin64(X); return ((X>>32) ^ (X&0xFFFFFFFF) ^ rk32) & 0xFFFFFFFF.

Wide gating (Carlo 2026-10-03): S0 ≥ ~40u or S1 kill → construction-scoped
kill, NO battery. Batteries only for S0-competitive AND S1/S2-clean wides.

Generator: `round_hyb/gen_rhyb.py`; reference: `round_hyb/models/rhyb.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 — results in `round_hyb/xcheck/`,
`round_hyb/rtlcheck/`. Round-key indexing: (i+2) convention for RK32
(round-11 lesson); (i+1) for RK64new (derivation in comment). Two self-test
helper bugs caught and fixed before generation (decrypt-side only; model
correct): wrong-half F evaluation + output packing. See Process notes §1.

## S0 ([run_synth.py](../run_synth.py), authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| rh_spn3_s1_nw | 21.5u | 0.208× | 3,108 | 8,716 | S0-fast; 3r SPN — S1-gated (wide gate: S0-competitive, battery iff S1/S2-clean) |
| rh_spn4_s1_nw | 27.2u | 0.263× | 5,531 | 14,913 | S0-competitive; battery iff S1/S2-clean |
| rh_wide128_feist4_nw | 28.9u | 0.279× | 5,726 | 16,532 | S0-competitive; battery iff S1/S2-clean |
| rh_wide128_feist5_nw | 35.4u | 0.342× | 7,263 | 20,779 | S0-competitive; battery iff S1/S2-clean |
| rh_feist6_parsplit_notr_nw | **36.7u** | 0.355× | 4,477 | 12,774 | **faster than Frontier-S speed point (37.0u)** — full battery iff S1/S2-clean |
| rh2_parsplit_fm11_nw | **39.8u** | 0.385× | 4,894 | 13,899 | M6 follow-up: +3.1u vs base (fm costs more here than r19's +1.4u); Q1-KILLED |
| rh_feist6_parsplit_notr31_nw | 37.5u | 0.362× | 4,213 | 12,007 | ties chioff31 (37.5u) on delay, larger → size-dominated |
| rh_feist6_notr_psfinal31_nw | 38.5u | 0.372× | 3,885 | 11,120 | dominated (slower + larger than chioff31 37.5u/3,863) |
| rh_wideF_feist5_nw | 38.7u | 0.374× | 5,378 | 15,265 | S0-competitive; battery iff S1/S2-clean |
| rh_feist6_chioff13_fm11_nw | 39.7u | 0.383× | 4,566 | 12,915 | dominated on Frontier Q (fm07 38.8u faster+smaller) |
| rh_feist6_chioff31_fm11_nw | 39.7u | 0.383× | 4,646 | 13,290 | dominated on Frontier Q |
| rh_feist6_parsplit_chioff13_nw | 40.8u | 0.394× | 4,879 | 13,779 | dominated |
| rh_feist6_parsplit_chioff31_nw | 40.9u | 0.395× | 4,610 | 13,022 | dominated |
| rh_lm_chi_nw | 43.4u | 0.419× | 5,287 | 15,366 | S0-doomed (≥40u wide gate) — construction kill, no battery |
| rh_feist6_parsplit_keyin_nw | 44.9u | 0.434× | 5,304 | 15,050 | dominated |
| rh_lm_parsplit_nw | 45.5u | 0.440× | 4,957 | 13,989 | S0-doomed (≥40u wide gate) — construction kill, no battery |
| rh_feist6_parsplit_3rot_nw | 45.9u | 0.443× | 5,703 | 16,143 | dominated |
| rh_feist6_notr_psfinal_nw | 38.8u | 0.375× | 3,694 | 10,674 | dominated (slower than chioff31 37.5u) |

All pass the S0 bar (≤ 93.15u). Multiplier ref: 103.5u. Dual-analyzer agreement
(`[analyze.py](../../synth/analyze.py) == [analyze2.py](../analyze2.py)`) confirmed on all logs. Note: S0 for the LM pair
was run twice (manual fix-up run + pipeline re-run after the rtlcheck fix —
same RTL, both runs agree: 45.5u / 43.4u); the duplicate is recorded in
Process notes §4.

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| rh_feist6_parsplit_notr_nw | **CAL_PASS** | LIN rej=0, DIFF rej=0, PB rej=0, RD rej=0 |
| rh2_parsplit_fm11_nw | **CAL_PASS** | (rej=0 all families) — fm layer is S1-neutral |
| rh_feist6_parsplit_notr31_nw | **CAL_PASS** | LIN rej=0, DIFF rej=0, PB rej=0, RD rej=0 |
| rh_feist6_parsplit_chioff13_nw | **CAL_PASS** | LIN rej=0, DIFF rej=0 |
| rh_feist6_parsplit_chioff31_nw | **CAL_PASS** | LIN rej=0, DIFF rej=0 |
| rh_feist6_notr_psfinal_nw | **CAL_PASS** | (rej=0 all families) |
| rh_feist6_parsplit_keyin_nw | **CAL_PASS** | (rej=0 all families) |
| rh_feist6_notr_psfinal31_nw | **CAL_PASS** | (rej=0 all families) |
| rh_feist6_chioff13_fm11_nw | **CAL_PASS** | (rej=0 all families) |
| rh_feist6_chioff31_fm11_nw | **CAL_PASS** | (rej=0 all families) |
| rh_lm_parsplit_nw (P1) | **CAL_PASS** | LIN rej=0, DIFF rej=0, PB rej=0, RD rej=0 — no r13 4r structural LIN leak at 6r |
| rh_lm_chi_nw (P2) | **CAL_PASS** | LIN rej=0, DIFF rej=0, PB rej=0, RD rej=0 — no r13 4r structural LIN leak at 6r |
| rh_feist6_parsplit_3rot_nw | **FLAG** | S1 LIN rej=9 (D=137–174/4096, 9/10 keys) — even-term linear singularity (extends O29) |
| rh_spn3_s1_nw (W1) | **FLAG** | S1 LIN rej=10 (D=4096/4096 all keys) + DIFF rej=10 — catastrophic |
| rh_spn4_s1_nw (W2) | **FLAG** | S1 LIN rej=10 (D=4096/4096) + DIFF rej=10, worst\|z\|=739994.3 — catastrophic |
| rh_wide128_feist4_nw (D1) | **FLAG** | S1 LIN rej=10 (D≈2195–2260/4096) + DIFF rej=10 |
| rh_wide128_feist5_nw (D2) | **FLAG** | LIN rej=0; DIFF rej=1 (key 0xaaaaaaaaaaaaaaaa, worst\|z\|=4.3) — marginal |
| rh_wideF_feist5_nw (D3) | **FLAG** | LIN rej=0, DIFF rej=0; marginal PB rej=3, RD rej=0 |

11 CAL_PASS / 6 killed. Full per-candidate logs: `round_hyb/s1_<name>.log`.

## S2 (N=2^22, 115 deltas, kill threshold 10 — verified `10` at ref file)

| Candidate | Repeats | max |z| | Kill? |
|---|---|---|---|
| rh_feist6_parsplit_notr_nw | 1 (delta 0x0000040000000000) | 50.1 | No (below thresholds) but borderline — early warning for Q1 kill |
| rh2_parsplit_fm11_nw | 1 (delta 0x0000040000000000) | 50.1 | No — profile IDENTICAL to base (same delta, same max|z|): fm is differential-neutral |
| rh_feist6_parsplit_notr31_nw | 0 | 25.8 | No — clean |
| (9 remaining: S2 running in background; not decision-relevant — all S0-dominated or S1-killed) | — | — | — |

**S2 discipline:** inspect the |z| column, not just repeats (|z| > ~100 on
single-bit deltas = structural kill even at 0 repeats — notr5/drop4 lesson).

## Q1 (SAC/BIC, N=2^18, fixed key, same script/procedure as r13/r18/r19)

| Candidate | sac_z5 | bic_maxcorr | Detail |
|---|---|---|---|
| rh_feist6_parsplit_notr_nw | **7** | **0.2526** | **KILL** — mandatory sac_z5=0 gate fails; bic worse than r18 alt-notr (0.172) |
| rh2_parsplit_fm11_nw | **7** | **0.00967** | **KILL** — sac_z5=7 (mandatory gate); bic CURED 0.2526→0.0097 (≤0.02 bar) but SAC untouched |

## S3 / S4

| Candidate | PractRand 16MB→1GB ×2 | SmallCrush | Verdict |
|---|---|---|---|
| (none — no candidate qualified: parsplit_notr Q1-killed, all others S0-dominated or S1-killed) |

## Findings

1. **Frontier UNCHANGED** (both S and Q). The only S0-competitive hybrid
   (parsplit_notr, 36.7u) died at Q1 (sac_z5=7).
2. **Parsplit-F × truncation is a worse interaction than alt-F × truncation**
   (M6/O43): bic 0.2526 vs r18's 0.172, plus SAC failures.
3. **Wide SPN fails for two independent reasons** (M2): slow diffusion AND
   S-box linear bias × insufficient rounds. Fastlin fixed diffusion but not LIN.
4. **Wide-128 compression hypothesis disproved** (M3): nocomp also S1-killed.
5. **LM has no viable round count** (M5): 4r S1-LIN kill (r13), 5r S1-DIFF kill
   (rh2), 6r S0-doomed (P1/P2).
6. **Even-term 3-rot linear singularity extends to parsplit-F** (M1/O38).
7. **(3,1) chi trait gives cleaner S2** (notr31: 25.8/0 vs notr: 50.1/1) but
   remains S0-dominated.

## rh2 follow-ups (failure-analysis driven)

| Candidate | S0 | S1 | Follows up | Outcome |
|---|---:|---|------------||
| rh2_parsplit_3rot_odd_nw | 41.6u | — | M1 (odd-term 3-rot) | S0-doomed (dominated); odd-term fix doesn't recover delay |
| rh2_spn4_s1_fastlin_nw | 28.9u | **FLAG** (LIN rej=10 D≈4050/4096, DIFF rej=10) | M2 (fast diffusion) | Diffusion fixed (64/64 bits) but LIN persists — S-box bias × rounds |
| rh2_wide128_feist5_nocomp_nw | 28.7u | **FLAG** (LIN rej=10, DIFF rej=10) | M3 (no compression) | Compression hypothesis DISPROVED |
| rh2_lm5_chi_nw | 37.0u | **FLAG** (DIFF rej=10) | M5 (5r LM) | 5r gap closed; LM has no viable round count |
| rh2_parsplit_fm11_nw | 39.8u | CAL_PASS | M6 (fm11 BIC cure) | Q1 KILL (sac_z5=7); bic 0.2526→0.0097 CURED; SAC pairs IDENTICAL to base — fm is SAC-neutral |

All rh2: xcheck 10k/10k, rtlcheck 300/300. Bit-exact.

## Failure analyses

(Per Carlo 2026-10-03 methodology upgrade: (a) precise failing signal with
numbers from the logs, (b) mechanistic hypothesis traced to the parent trait,
(c) one follow-up rh2_* hybrid per distinct kill mechanism, cap ~6.
The [VERDICT_SCOPE.md](../VERDICT_SCOPE.md) ledger entries stay terse and construction-scoped;
this section carries the mechanism + follow-up.)

### M1. Even-term linear singularity — rh_feist6_parsplit_3rot_nw (S1 kill)

(a) **Signal:** S1 LIN FLAG, rej=9/10 keys, D=137–174/4096 per key
(log: `round_hyb/s1_rh_feist6_parsplit_3rot_nw.log`). DIFF clean (rej=0).
(b) **Mechanism:** ps_3rot's linear lin3(x) = x^rotl32(x,3)^rotl32(x,7)^rotl32(x,11)
has FOUR XOR terms (even). p(t) = 1+t³+t⁷+t¹¹, p(1) = 1⊕1⊕1⊕1 = 0, so (t+1) | p(t);
over GF(2), x³²+1 = (x+1)³², hence lin3 is GF(2)-SINGULAR (rank 31). The singular
layer confines linear approximations to a 31-dim subspace — the same signature
as O29's r21 notr kill (rej=9, D=132–160/4096). The killer is the even-term
linear trait, not the parsplit-F: this EXTENDS O29 from notr to parsplit-F.
(c) **Follow-up:** `rh2_parsplit_3rot_odd` — parsplit-F × 3-rotation linear with
an ODD term count (e.g. x^rotl32(x,3)^rotl32(x,7): p(1)=1⊕1⊕1=1≠0, nonsingular),
keeping the parsplit chassis that earned 36.7u on the sibling.

### M2. SPN slow diffusion — rh_spn3_s1_nw, rh_spn4_s1_nw (S1 kill, grouped)

(a) **Signal:** S1 LIN FLAG rej=10/10, D=4096/4096 on ALL keys (logp=-inf);
DIFF FLAG rej=10/10, worst|z|=739994.3 (W2). Total break at S1 — stronger than
r22 O31's 4r-SPN S2 kill.
(b) **Mechanism (proven by instrumentation):** lin64(x) = x^rotl64(x,3)^rotl64(x,11)
spreads a point difference by at most 11 bit-positions per round; the S-box layer
is nibble-confined and does not help span the gap. Measured: for input bit 0,
the 4-round SPN's output difference touches only 51 of 64 bits — the HIGH 13 BITS
ARE ALWAYS ZERO (probability-1 truncated differential); 3-round touches only 39.
The lin(3,11) trait was validated in the 32-bit Feistel-F context, where the
Feistel XOR across halves compounds diffusion differently; transplanted to a
full-64-bit SPN, 3–4 rounds cannot achieve full diffusion. The parent trait at
fault is the slow-diffusing linear layer, not S1.
(c) **Follow-up:** `rh2_spn4_s1_fastlin` — 4r full-64 SPN, S1, RK64new, but the
linear replaced by a fast-diffusing layer (e.g. x^rotl64(x,17)^rotl64(x,41):
41-bit spread/round ⇒ 4 rounds cover 64 bits), keeping the SPN structure and
key schedule. Directly fixes the identified weakness (diffusion speed), not just
round count (O31/O38 already cover "more rounds" / mixing variants).
**Outcome:** FOLLOW-UP FAILED — S1 LIN FLAG rej=10 (D≈4050/4096) + DIFF FLAG
rej=10. The fast linear FIXED the truncated differentials (output diff now
touches all 64 bits), but a DIFFERENT linear weakness persists. S1's max linear
bias is 0.25 (high for a 4-bit S-box); 4 rounds are insufficient to bring the
linear hull down regardless of diffusion speed. **Refined mechanism:** the SPN
fails for TWO independent reasons — (i) slow diffusion (fixed by fastlin),
(ii) S-box linear bias × insufficient rounds (not fixed). The construction needs
more rounds or a stronger S-box, not just faster diffusion.

### M3. Wide-128 compression — rh_wide128_feist4_nw, rh_wide128_feist5_nw (S1 kill, grouped)

(a) **Signal:** D1: S1 LIN FLAG rej=10 (D≈2195–2260/4096 all keys) + DIFF FLAG
rej=10. D2: LIN PASS (rej=0); DIFF FLAG rej=1 (key 0xaaaaaaaaaaaaaaaa,
worst|z|=4.3) — marginal. The 5th round fixes LIN but not DIFF.
(b) **Mechanism (hypothesis):** Prime suspect is the `out = L' ^ R'` compression
trait. XORing the two 64-bit halves can cancel nonlinear F-terms in linear
approximations, re-exposing relations the Feistel rounds built up; the injective
expansion (halves satisfying B = rotl64(A^c1,13)^c2) also feeds the Feistel a
linearly-structured 128-bit state. Note the collision gate PROVED injectivity
(0 collisions) — the weakness is statistical, not bijectivity. The 4r→5r
improvement (LIN rej=10→0) shows the mechanism is round-count-sensitive, but the
residual DIFF rej=1 implicates the compression specifically.
**Cheapest discriminating experiment:** S1-screen a variant outputting L5 alone
(no compression); if LIN/DIFF collapse, the compression is the culprit; if they
persist, the expansion/round-count is.
(c) **Follow-up:** `rh2_wide128_feist5_nocomp` — identical 128-bit 5r Feistel,
injective expansion, F_64, but out = L5 (single half, no XOR compression). This
IS the discriminating experiment as a candidate: keeps every working trait,
repairs only the implicated compression.
**Outcome:** FOLLOW-UP FAILED — S1 LIN FLAG rej=10 + DIFF FLAG rej=10.
**The compression hypothesis is DISPROVED.** Removing the compression did not
help (indeed D2-compressed had LIN PASS, nocomp has LIN FLAG). The real culprit
is elsewhere: prime suspect shifts to the injective expansion (halves satisfying
B = rotl64(A^c1,13)^c2 feed the Feistel a linearly-structured 128-bit state)
or insufficient Feistel rounds for the 64-bit F. The wide-128 construction's
weakness is not the compression.

### M4. Wide-F fold anomaly — rh_wideF_feist5_nw (S1 marginal kill)

(a) **Signal:** S1 LIN rej=0, DIFF rej=0; marginal screen PB rej=3, RD rej=0
→ verdict FLAG (`round_hyb/s1_rh_wideF_feist5_nw.log`). Mild — no LIN/DIFF
signal.
(b) **Mechanism (unclear):** Prime suspect is the F_wide XOR-fold trait:
F_wide = ((X>>32) ^ (X&0xFFFFFFFF) ^ rk32) compresses 64→32 bits inside F by
XORing halves, which can correlate the output when the halves are related.
But with LIN/DIFF clean and only a mild PB anomaly, this may be a borderline
fluctuation. **Cheapest discriminating experiment:** run S2 + Q1 on wideF; if
clean, the marginal is likely noise and the construction deserves a re-test.
(c) **Follow-up:** deferred pending the discriminating experiment (S2/Q1 below).
If S2/Q1 implicate the fold, `rh2_wideF_feist5_nofold` (return (X>>32)^rk32,
dropping the half-XOR).

### M5. LM skeleton delay — rh_lm_parsplit_nw, rh_lm_chi_nw (S0 gate kill, grouped)

(a) **Signal:** S0 45.5u (P1) / 43.4u (P2) — both ≥40u wide gate → construction
kill, no battery. S1 clean (CAL_PASS, rej=0 all families): NO r13 4r structural
LIN leak at 6r with the new Fs (extends r13's 6r S1-F pass to parsplit-F/chi-F).
(b) **Mechanism:** The LM skeleton (D=L^R pre-XOR, (R^T, D) shuffle) puts more
logic on the critical path than Feistel's simple half-swap; at 6 rounds the
skeleton is structurally ~6–8u slower than the Feistel frontier (37–38u). The F
change (parsplit/chi vs S1) did not close the gap — chi-F saved only ~2u vs
parsplit-F. The delay is inherent to the 6r LM skeleton, not the F.
(c) **Follow-up:** `rh2_lm5_chi` — 5-round LM with chi-F. r13 tested 4r (S1 LIN
kill, structural) and 6r (S1 pass, dominated) with S1-F; 5r with the cheaper
chi-F is untested and might land below 40u while keeping S1-clean. Tests the
round-count gap in the LM re-test series.
**Outcome:** FOLLOW-UP FAILED — S0 37.0u (promising, ties frontier!) but S1 DIFF
FLAG rej=10. 5-round LM diffuses too slowly — consistent with r22 O35 (5r LM
chi-F S2 kill). The 5r gap is now closed: 4r fails S1 LIN (r13), 5r fails S1 DIFF
(this), 6r passes S1 but S0-doomed (P1/P2). The LM skeleton has no viable round
count at this delay budget.

### M6. Parsplit-F × truncation interaction — rh_feist6_parsplit_notr_nw (Q1 kill)

(a) **Signal:** Q1 (N=2^18, fixed key): **sac_z5=7** (mandatory gate: 0 required
for ALL frontier claims), bic_maxcorr=0.2526, bic_meancorr=0.00166,
avalanche_mean=31.998. S1 CAL_PASS (rej=0). S2 borderline: 1 repeat,
max|z|=50.1. S0 36.7u (would-be frontier speed point, now irrelevant).
(b) **Mechanism:** The truncated final round (chi_notr, no linear) leaves the
parsplit-F's output unmixed. The parsplit trait is at fault: its chi16 half
(16 parallel chi gates on the high 16 bits) produces AND-term correlations that
persist to the output when the final linear is dropped. Compare r18's alt-notr
(chi32 final, truncated): bic=0.172, sac_z5=0 — alt-F's full-width chi32 mixes
better post-truncation than parsplit's split chi16/S1. **Parsplit-F × truncation
is a worse interaction than alt-F × truncation.** The S2 borderline (|z|=50.1,
1 repeat vs frontier norm ~11/0) was an early warning.
(c) **Follow-up:** `rh2_parsplit_fm11` (parsplit chassis, fm11 final cure
instead of truncation) — **BUILT 2026-10-03, see M6b below.**

### M6b. fm11 cure decomposes M6 — rh2_parsplit_fm11_nw (Q1 kill)

(a) **Signal:** Q1 (N=2^18, fixed key): **sac_z5=7** (mandatory gate fails),
bic_maxcorr=**0.00967** (was 0.2526 — now under the 0.02 Frontier-Q bar).
S0 39.8u (+3.1u vs base 36.7u — the fm costs MORE here than r19's +1.4u on
alt). S1 CAL_PASS. S2 PASS with a profile **identical** to the base:
1 repeat (delta 0x0000040000000000), max|z|=50.1 (delta 0x0004000000000000).
xcheck 10k/10k, rtlcheck 300/300. Evidence: `round_hyb/s0/s1/s2/q1` logs,
`round_hyb/q1/q1_rh2_parsplit_fm11_nw.json`.
(b) **Mechanism:** the fm11 cure **decomposes M6 into two separable
components**. (1) Output-bit-flip correlations (bic 0.2526): a final-round
mixing problem — cured by fm11, as on the alt family. (2) SAC deviations:
a DIFFERENTIAL-uniformity problem in the alternating parsplit/chi chassis,
not a final-round problem. Proof of separability: the 7 failing
(in_bit, out_bit, z) pairs are **identical to the base's to 2 decimals**
(all L_0 bits 32–50 → R_6 bits 0–27, paired adjacent-bit chi16 signature,
e.g. in38/39→out3 with z=-8.05/+12.39) — the fixed linear fm on F_6's output
permutes but cannot remove differential biases, so S2 and SAC are
fm-neutral. The S2 borderline (bit 38–42 cluster) was the early warning, and
it, too, is unchanged by the fm.
**Design-note correction:** the brief's literal equation `out = y^rotl64(y,11)`
is 2-to-1 (kernel {0, 2^64−1}; 1+t^m is always divisible by t+1 in char 2, so
y^rotl(y,m) is NEVER bijective on 2^k bits) and would break the bijectivity
hard gate. Built r19's actual cure instead: F_6 = y^rotl32(y,11) inside F
(Feistel stays bijective regardless of F).
(c) **Follow-up:** fm07/fm311 (parent's named alternates) are PREDICTED to
also fail SAC — same structural position, and the identical-pairs evidence
shows the fm is SAC-neutral on this chassis, not rotation-amount-sensitive.
NOT BUILT: with O44's r22c at 28.3u the chassis is also uncompetitive on
delay. The real fix must target the differential bias at its source (the
alternating parsplit/chi rounds), not the final round — open design question.

## Evidence locations

- Generator / reference: `round_hyb/gen_rhyb.py`, `round_hyb/models/rhyb.py`
- Candidates: `fast_battery/candidates/rh_*/` (impl.c, rtl.v, model.py, meta.json)
- Bit-exactness: `round_hyb/xcheck/`, `round_hyb/rtlcheck/`
- S0: `round_hyb/s0/`; S1: `round_hyb/s1/`; S2: `round_hyb/s2/`
- Q1: `round_hyb/q1/`; batteries: `round_hyb/battery/`
- Collision gate (D1/D2): `round_hyb/collision_gate.log`
- Pipeline progress: `round_hyb/progress.log`

## Process notes

1. **Two self-test helper bugs caught before generation** (decrypt-side only;
   the encrypt model was correct throughout): (a) `_feistel_decrypt_np`
   evaluated F on the wrong state variable; (b) its final output packed
   (R_0<<32)|L_0 instead of the input convention (L_0<<32)|R_0. Fixed the
   helper; all round-trips pass. Same class re-caught in `_feistel_wideF_dec_np`
   (wrong-half F) — the D3 helper now uses the cleaned state-variable form.
2. **GF(2) matrix-inversion helper bug**: `_gf2_mat_inv` placed the matrix
   in the high bits of the augmented row while pivoting on low bits —
   produced a wrong "inverse" (all 64 basis vectors failed). Fixed the
   half-swap; 300-vector lin64↔inv check green. The lin64 bijectivity
   argument (p(1) = 1 ≠ 0) is independent of the helper.
3. S0-gate for the wide constructions was honored: (pending outcomes).
