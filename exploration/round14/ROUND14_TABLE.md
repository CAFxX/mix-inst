# Round 14 — Exploit the heterogeneity breakthrough

**Date:** 2026-10-03. **Frontier after round: UNCHANGED**
{r13_feist6_alt_s1chi_nw: 40.1u, r9_feist6_rot311_nw: 41.0u,
r8_feist6_s1_1sbox_nw: 42.9u}.

**Multiplier reference:** 103.5u (re-measured fresh in the pinned Yosys-0.69
flow; S0 bar ≤ 93.15u). All 13 candidates pass S0.

## Families

- **F1** — alt variants, 6r: `alt_rev` (odd rounds chi-F, even S1-F — reversed
  order), `alt713` (alt with (7,13) rotmix on both), `alt_chinolin` (chi-F =
  chi32(R)^rk, NO rotmix on chi rounds), `alt_chioff` (chi offsets (i+2,i+3)),
  `alt_rkhi` (S1 rounds standard rk, chi rounds rotating key-half).
- **F2** — 4r lighter-strong-F probes: `chis1l4` = lin(3,11)(chi32(S1(R^rk))),
  `pars1chi` = lin(3,11)(S1(R^rk)) ^ lin(3,11)(chi32(R)).
- **F3** — 5r double-strength-F: lin(S1(lin(S1(R^rkA))^rkB)), 2 keys/round,
  (3,11). Closes the round-strength question; S1 verdict first.
- **F4** — 6r heterogeneous placement: `chi25` (chi-F on rounds {2,5}),
  `chi16` (chi-F on rounds {1,6}).
- **F5** — r9 structure + invertible 64-bit final diffusion
  out = W ^ rotl64(W,a) ^ rotl64(W,b), (a,b) = (13,37) / (7,29).
  p(t) = 1+t^a+t^b, p(1) = 1 (mod 2) -> coprime with (t+1)^64 = t^64+1 ->
  permutation. (Single-term out ^= rotl64(out,r) is NOT bijective — kernel =
  r-periodic vectors — excluded by design.)
- **F6** — `s1chi`: 6r, F = lin(3,11)(chi32(S1(R))) ^ rk (reverse of r13 chi->S1).

All: 32-bit halves, {R,L} output, NO whitening, affine r7/r8/r9 key schedule.
Generator: `round14/gen_r14.py`; reference: `round14/models/r14.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 for all 13. Round-key indexing
uses the (i+2) convention (round-11 lesson); F3 uses (2i+2)/(2i+3) double-key;
alt_rkhi's 1-based-even-round low32 half derived explicitly and matched
300/300 first try.

## S0 (run_synth.py, authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r14_feist6_alt_chinolin_nw | 31.9u | 0.308× | 3,282 | 9,306 | faster+smaller than everything — needs S1 |
| r14_feist4_pars1chi_nw | 37.3u | 0.360× | 6,542 | 18,140 | faster but +44% cells — needs S1 (4r) |
| r14_feist6_alt_rkhi_nw | 40.1u | 0.387× | 4,563 | 13,041 | ties r13 alt exactly — dominated-by-tie |
| r14_feist6_alt_chioff_nw | 40.5u | 0.391× | 4,632 | 13,207 | dominated by r13 alt |
| r14_feist6_alt713_nw | 40.6u | 0.392× | 4,430 | 12,728 | dominated by r13 alt |
| r14_feist6_chi16_nw | 40.9u | 0.395× | 4,815 | 13,383 | dominated by r13 alt |
| r14_feist6_chi25_nw | 41.1u | 0.397× | 4,557 | 13,001 | dominated by r13 alt |
| r14_feist6_chi_s1alt_nw | 41.4u | 0.400× | 4,797 | 13,477 | dominated by r13 alt |
| r14_feist6_r9_outdiff_nw | 43.1u | 0.416× | 5,138 | 14,381 | dominated (+2.1u for final diffusion) |
| r14_feist4_chis1l_nw | 43.2u | 0.417× | 4,560 | 12,536 | dominated |
| r14_feist6_r9_outdiff2_nw | 43.3u | 0.418× | 5,123 | 14,415 | dominated (+2.3u for final diffusion) |
| r14_feist6_s1chi_311_nw | 57.4u | 0.555× | 6,123 | 17,190 | dominated |
| r14_feist5_s1x2_311_nw | 70.6u | 0.682× | 9,151 | 24,468 | dominated |

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r14_feist6_chi_s1alt_nw | **CAL_PASS** | full screen clean |
| r14_feist6_alt713_nw | **CAL_PASS** | full screen clean |
| r14_feist6_alt_chinolin_nw | **FLAG** | LIN PASS, DIFF rej=10 (worst\|z|~29.8) |
| r14_feist6_alt_chioff_nw | **CAL_PASS** | full screen clean |
| r14_feist6_alt_rkhi_nw | **CAL_PASS** | full screen clean |
| r14_feist4_chis1l_nw | **FLAG** | LIN PASS, DIFF rej=1 |
| r14_feist4_pars1chi_nw | **FLAG** | LIN rej=9, DIFF rej=10 |
| r14_feist5_s1x2_311_nw | **CAL_PASS** | full screen clean (dominated; S1 only) |
| r14_feist6_chi25_nw | **CAL_PASS** | full screen clean |
| r14_feist6_chi16_nw | **CAL_PASS** | full screen clean |
| r14_feist6_r9_outdiff_nw | **CAL_PASS** | full screen clean (dominated; S1 only) |
| r14_feist6_r9_outdiff2_nw | **CAL_PASS** | full screen clean (dominated; S1 only) |
| r14_feist6_s1chi_311_nw | **CAL_PASS** | full screen clean (dominated; S1 only) |

10/13 pass S1. The tempting 31.9u/3,282-cell alt_chinolin dies at S1 DIFF;
both 4r lighter-strong-F probes die (one hard, one marginal).

## S2 (differential profiler, N=2^22, 115 deltas, kill threshold 10)

Run for the 6 S1-passing 6r alt variants. All PASS, 0 repeats:

| Candidate | S2 verdict | max\|z\| |
|---|---:|---:|
| r14_feist6_alt713_nw | **PASS** | **3.6** |
| r14_feist6_chi25_nw | **PASS** | 8.0 |
| r14_feist6_alt_rkhi_nw | **PASS** | 10.7 |
| r14_feist6_chi_s1alt_nw | **PASS** | 15.0 |
| r14_feist6_chi16_nw | **PASS** | 20.1 |
| r14_feist6_alt_chioff_nw | **PASS** | 25.9 |

No Q1/S3/S4: nothing is frontier-relevant (all dominated on S0), so no
frontier claim exists to gate.

## Findings (2026-10-03)

**FRONTIER UNCHANGED.** 13 candidates, 10 S1 passes, 6 clean S2s, 0 Pareto
improvements. The r13 alt (S1,chi) at 40.1u survives every variant thrown at it.

1. **chi needs its rotmix.** alt_chinolin (chi-F without rotmix) synthesizes
   at a dream 31.9u/3,282 cells but dies at S1 DIFF (rej=10, worst|z|~29.8).
   The S-box rounds cannot cover chi's weak diffusion alone — the linear
   layer inside the chi round is load-bearing for statistics, not just delay.
2. **S1-first order matters.** Reversed alt (chi on odd rounds) is 1.3u slower
   (41.4u) AND worse differentially (|z|=15.0 vs 10.7): leading with the
   S-box layer both speeds up and cleans up.
3. **alt713 is the differential-cleanliness champion:** S2 |z|=3.6, the
   cleanest 6-round result ever measured (matches r10's alt-rotation 3.6),
   but dominated at 40.6u. Rotation pair controls differentials far more
   than delay.
4. **Rotating key-half on chi rounds is exactly neutral:** 40.1u/4,563/13,041
   — bit-identical S0 numbers to r13 alt — and identical S2 (|z|=10.7).
   Key position inside F moves nothing (key mux off the critical path;
   dedupe confirmed distinct outputs, so this is real, not a tool artifact).
5. **chi placement:** middle {2,5} is cleaner (|z|=8.0) but 0.2u slower than
   edge {1,6} (|z|=20.1). Both dominated.
6. **chi offsets (2,3) lose on both axes:** +0.4u and |z|=25.9 vs 10.7.
   The (1,2) chi is the right one.
7. **4r lighter-strong-F probes both die at S1:** chis1l (DIFF rej=1,
   marginal) and pars1chi (LIN rej=9 + DIFF rej=10, hard). The 4r barrier
   needs the FULL double-S1 F (r13's 56–59u); lighter strong-F doesn't
   cross it. The parallel S1+chi mix is particularly weak.
8. **5r double-F passes S1** — the round-strength question is closed: 5
   rounds with a strong F is statistically fine (the r9/r10/r12 phase
   transition is specific to the single-S1 F). But 70.6u/9,151 cells is
   dominated; no full battery.
9. **r9 + invertible 64-bit final diffusion: pure cost.** +2.1–2.3u and
   +~870 cells for CAL_PASS (unchanged S1). Buying S2 cleanliness with a
   final linear layer is not worth it at these margins. Bijectivity proof
   held (algebraic p(1)=1 + no collisions on 2x200k vectors).
10. **Stacking both nonlinears in one F is delay-expensive:** S1->chi->lin
    at 57.4u (r13's chi->S1 was 57.2u) — heterogeneous ROUNDS beat
    heterogeneous LAYERS.

## Evidence locations

- Candidates: `exploration/fast_battery/candidates/r14_*/`
- S0: `round14/s0/*.log` (RESULT lines; ref mul 103.5u); S1: `round14/s1/*.log`
- S2 logs: `round14/s2_r14_*.log`, progress `round14/s2_progress.log`
- xcheck: `round14/xcheck/` (13/13 PASS 10k/10k); rtlcheck: `round14/rtlcheck/`
  (13/13 PASS 300/300)

## Process notes

1. Tautological self-test assertion caught at write time: gen_r14.py's
   emit() initially asserted `not np.array_equal(O, fn(V,K) ^ 0)` — XOR with
   zero is the identity, so the assertion could never fail. Removed before
   emission. Rule: every self-test assertion must be capable of failing;
   a tautological check is worse than none (it looks like evidence).
2. alt_rkhi's bit-identical S0 numbers to r13 alt (40.1/4,563/13,041) were
   verified as genuine (dedupe showed distinct outputs; the key-half mux is
   off the critical path) rather than assumed to be a caching/tool error.
3. S2 kill threshold verified = 10 at the call site
   (`fast_battery/ref/s2_kill_repeats.txt`).
4. Dedupe: all 13 specs pairwise-distinct by numpy model output before
   generation. No VM reboot this round; per-candidate progress logs were in
   place regardless.
