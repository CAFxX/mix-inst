# Round 15 — Mixed single/double-F rounds; alt rotation-heterogeneity; key diffusion

**Date:** 2026-10-03. **Frontier after round:**
{r15_feist6_parsplit_nw: 40.7u, r13_feist6_alt_s1chi_nw: 40.1u,
r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u}
— new Pareto point (parallel-split F); no point dominates another.

**Multiplier reference:** 103.5u (re-measured fresh in the pinned Yosys-0.69
flow; S0 bar ≤ 93.15u). All 12 candidates pass S0.

## Families

- **F1** — alt rotation-heterogeneity, 6r: `alt_s713_c311` (odd rounds
  S1-F (7,13), even rounds chi-F (3,11)), `alt_s311_c713` (odd S1-F (3,11),
  even chi-F (7,13)), `alt_2rot` (S1/chi alt; rotmix pair per round-block:
  {1,2} (3,11), {3,4} (7,13), {5,6} (3,11)).
  NOTE: the task's F1(c) ("per-round rotation alternation applied to the
  S1/chi structure") collapses to F1(b) under the natural reading
  (odd rounds are S1, even rounds chi), so (c) was implemented as the
  genuinely distinct rotation-block variant `alt_2rot`.
- **F2** — `alt_wh`: r13 alt structure (odd S1 / even chi, (3,11)) with
  input whitening W = val ^ key before round 1.
- **F3** — mixed single/double-F rounds (unrolled in C and Verilog from a
  shared per-round spec; key indices 1-based C sense):
  `mix5_db3` (5r, round 3 double-F s1x2 keys 3,4; singles [s1,chi,chi,s1]),
  `mix6_db4` (6r, round 4 double-F keys 4,5; singles [s1,chi,s1,s1,chi]),
  `mix5_db24` (5r, rounds 2,4 double-F; singles [s1,chi,s1]),
  `mix6_db34` (6r, rounds 3,4 double-F; singles [s1,chi,s1,chi]).
- **F4** — `parsplit`: 6r, F = lin(3,11)(t) ^ rk with t[15:0] = S1(R[15:0])
  (4 nibbles) and t[31:16] = chi16(R[31:16]) (offsets (1,2) mod 16).
- **F5** — key-diffusion variants on the r13 alt structure, 6r:
  `alt_rkdiff` (rk' = RK32(key,i) ^ rotl32(RK32(key,i+1),8)),
  `alt_rksbox` (rk = sbox_layer32(RK32(key,i))).
- **F6** — `alt_chioff023`: 6r alt, even rounds chi-F with offsets (2,3):
  b_i = a_i ^ (~a_{i+2} & a_{i+3}).

All: 32-bit halves, {R,L} output, NO whitening except alt_wh, affine
r7/r8/r9 key schedule. Generator: `round15/gen_r15.py`; reference:
`round15/models/r15.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 for all 12. Mixed-round key
indices (1-based C sense) bake (j+1) in Verilog via explicit per-round
constants; key-index derivation spot-checked for j=1..8 against numpy.
check_rtl passed 300/300 first try on all novel conventions (unrolled mixed
rounds, rkdiff two-key, rksbox key-through-S-box, whitening, parsplit).

## S0 ([run_synth.py](../run_synth.py), authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r15_feist6_alt_s311_c713_nw | 40.3u | 0.389× | 4,741 | 13,523 | dominated by r13 alt |
| r15_feist6_alt_2rot_nw | 40.3u | 0.389× | 4,683 | 13,399 | dominated by r13 alt |
| r15_feist6_alt_rkdiff_nw | 40.4u | 0.390× | 4,850 | 13,959 | dominated by r13 alt |
| r15_feist6_alt_chioff023_nw | 40.5u | 0.391× | 4,632 | 13,207 | dominated by r13 alt |
| r15_feist6_parsplit_nw | 40.7u | 0.393× | 4,318 | 12,356 | **Pareto-eligible: faster than r9, smaller than r13 alt** |
| r15_feist6_alt_s713_c311_nw | 41.1u | 0.397× | 4,714 | 13,502 | dominated by r13 alt |
| r15_feist6_alt_rksbox_nw | 41.4u | 0.400× | 5,152 | 14,370 | dominated |
| r15_feist5_db3_nw | 41.4u | 0.400× | 4,678 | 12,979 | dominated (S1 FLAG) |
| r15_feist6_alt_wh_nw | 42.2u | 0.408× | 4,854 | 13,957 | dominated (S1 FLAG) |
| r15_feist6_db4_nw | 48.6u | 0.470× | 5,591 | 15,598 | dominated |
| r15_feist5_db24_nw | 49.9u | 0.482× | 5,773 | 15,635 | dominated |
| r15_feist6_db34_nw | 55.3u | 0.534× | 6,550 | 18,075 | dominated |

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r15_feist6_alt_s713_c311_nw | **CAL_PASS** | full screen clean |
| r15_feist6_alt_s311_c713_nw | **CAL_PASS** | full screen clean |
| r15_feist6_alt_2rot_nw | **CAL_PASS** | full screen clean |
| r15_feist6_alt_wh_nw | **FLAG** | LIN PASS, DIFF PASS, marginal PB rej=1 |
| r15_feist5_db3_nw | **FLAG** | LIN PASS, DIFF PASS, marginal RD rej=1 |
| r15_feist6_db4_nw | **CAL_PASS** | full screen clean (dominated; S1 only) |
| r15_feist5_db24_nw | **CAL_PASS** | full screen clean (dominated; S1 only) |
| r15_feist6_db34_nw | **CAL_PASS** | full screen clean (dominated; S1 only) |
| r15_feist6_parsplit_nw | **CAL_PASS** | full screen clean |
| r15_feist6_alt_rkdiff_nw | **CAL_PASS** | full screen clean |
| r15_feist6_alt_rksbox_nw | **CAL_PASS** | full screen clean |
| r15_feist6_alt_chioff023_nw | **CAL_PASS** | full screen clean |

10/12 pass S1. Whitening on the heterogeneous structure flags a marginal
(PB rej=1) — whitening was pure cost before; on the alt structure it also
adds a (marginal) statistical blemish. 5r with one double round passes
LIN/DIFF but flags RD rej=1; 5r/6r with two double rounds pass the full
screen (dominated on delay).

## S2 (differential profiler, N=2^22, 115 deltas, kill threshold 10)

Run for the 7 S1-passing 6r alt-structure designs. All PASS, 0 repeats:

| Candidate | S2 verdict | max\|z\| |
|---|---:|---:|
| r15_feist6_alt_s713_c311_nw | **PASS** | 3.5 |
| r15_feist6_alt_s311_c713_nw | **PASS** | 4.1 |
| r15_feist6_alt_2rot_nw | **PASS** | 6.7 |
| r15_feist6_alt_rksbox_nw | **PASS** | 11.7 |
| r15_feist6_alt_rkdiff_nw | **PASS** | 11.9 |
| r15_feist6_parsplit_nw | **PASS** | 18.6 |
| r15_feist6_alt_chioff023_nw | **PASS** | 25.9 |

parsplit's worst delta is 0x0008000000000000 (|z|=18.6), a single-bit delta
in the low 16 bits of L. 0 repeats everywhere; the kill criterion is on
repeats, so all pass. parsplit's |z| is the highest on the frontier
(r13 alt 10.7, r9 16.5, r8 4.0) — noted, not a kill.

## Q1 (SAC/BIC avalanche, N=2^18, fixed key) — parsplit only

| Candidate | sac_maxdev | sac_z5 | bic_maxcorr | avalanche_mean | verdict |
|---|---|---:|---:|---:|---|
| r15_feist6_parsplit_nw | 0.00480 | 0 | 0.00842 | 31.9997 | **CLEAN** — matches frontier quality |

## Full battery (PractRand 16MB→1GB + SmallCrush) — parsplit only

| Candidate | S3 PractRand | S4 SmallCrush | verdict |
|---|---|---|---|
| r15_feist6_parsplit_nw | 16/64/256MB + 1GB: no FAIL, both key/stride configs | All tests were passed | **BATTERY-PASS** |

## Findings (2026-10-03)

**FRONTIER CHANGE: r15_feist6_parsplit_nw enters as a fourth point.**
6-round Feistel, F = lin(3,11)( S1(R[15:0]) || chi16(R[31:16]) ) ^ rk:
- S0: **40.7u** / 4,318 cells / 12,356 (vs r13 alt 40.1/4563/13041;
  vs r9 41.0/4265/11996)
- S1: CAL_PASS; S2: 0 repeats, max|z|=18.6; Q1: sac_z5=0
- S3: PractRand 1GB clean (both configs); S4: SmallCrush all passed

Pareto check (delay, cells, area): parsplit(40.7, 4318, 12356) vs
r13alt(40.1, 4563, 13041) vs r9(41.0, 4265, 11996) vs r8(42.9, 4133, 11670)
— no point dominates another. parsplit sits between the r13 speed point and
r9: 0.6u slower than r13 alt but 245 fewer cells / 685 less area; 0.3u
faster than r9 but larger. The frontier is now a 4-way tradeoff.
RTL copied to `~/workspace/your_files/mix_rtl_pareto/mix_r15_feist6_parsplit_nw.v`.

1. **Heterogeneous LAYERS inside one F work too.** r14 showed stacking both
   nonlinears in one F costs 57u (S1->chi->lin serial). parsplit instead
   splits the word: S-box on the low 16 bits, chi on the high 16 bits, in
   PARALLEL — one nonlinear depth, not two. 40.7u with fewer cells than any
   other 6r alt design. Parallel-split beats serial-stack.
2. **Rotation heterogeneity inside the alt structure is neutral-to-negative.**
   (7,13)-on-S1/(3,11)-on-chi (40.3u), the reverse (41.1u), and 2-round
   block alternation (40.3u) are all dominated by the uniform (3,11) r13
   alt — and the (7,13) variants are S2-cleaner (3.5/4.1) without buying a
   Pareto position. Rotation pair controls differentials more than delay
   (r10/r14 pattern repeats).
3. **Whitening is still pure cost — and now a blemish.** alt_wh: +2.1u AND
   S1 FLAG (PB rej=1) on the heterogeneous structure. Whitening is closed.
4. **Key diffusion is neutral.** rkdiff (40.4u, |z|=11.9) and rksbox
   (41.4u, |z|=11.7) both pass S1/S2 but are dominated; key position inside
   F moves nothing (r14's rotating-half result generalizes).
5. **Mixed double-F rounds: statistically fine, delay-doomed.** 5r with one
   double round flags RD (rej=1); 5r/6r with two double rounds pass the
   full S1 screen — the round-strength question is fully closed — but at
   48.6–55.3u they are dominated by wide margins. Concentrating strength
   in double rounds cannot beat uniform single rounds on delay.
6. **chi offsets (2,3):** S1-clean, S2 |z|=25.9 (worst of the round), +0.4u
   vs r13 alt. The (1,2) chi stands.

## Evidence locations

- Candidates: `exploration/fast_battery/candidates/r15_*/`
- S0: `round15/s0/*.log` (RESULT lines; ref mul 103.5u)
- S1: `round15/s1/*.log` + `round15/s1_progress.log`
- S2: `round15/s2_r15_*.log`, progress `round15/s2_progress.log`
- Q1: `round15/q1/q1_r15_feist6_parsplit_nw.json`, script `round13/q1_sacbic.py`
- parsplit battery: `fast_battery/results/r15_feist6_parsplit_nw/` +
  `round15/battery_r15_feist6_parsplit_nw.log`
- Frontier RTL: `~/workspace/your_files/mix_rtl_pareto/`

## Process notes

1. Task-spec ambiguity caught before generation: the brief's F1(c) ("per-round
   rotation alternation applied to the S1/chi structure") is identical to
   F1(b) under the natural reading (odd rounds S1, even rounds chi). Rather
   than emit a duplicate (the dedupe gate would have caught it), F1(c) was
   implemented as the genuinely distinct rotation-block variant `alt_2rot`
   ({1,2} (3,11), {3,4} (7,13), {5,6} (3,11)), documented in the model
   docstring. Rule: when a spec collapses to another under the natural
   reading, implement the nearest genuinely distinct variant and document
   the interpretation — never emit a near-duplicate to fill a quota.
2. Mixed-round key indexing: 1-based C key index j bakes (j+1) in Verilog
   via explicit per-round constants (`_rk_v(j)`); derivation spot-checked
   for j=1..8 against numpy in emit(). check_rtl 300/300 first try on all
   four mixed designs.
3. S1 progress-line grep in [run_s1.sh](run_s1.sh) matches CAL_PASS|CAL_FLAG|KILL but the
   script writes "verdict: FLAG" — FLAG verdicts show rc=2 with an empty
   verdict field in the progress log; the per-candidate s1_*.log is
   authoritative. (Cosmetic; logs are complete.)
4. S2 kill threshold verified = 10 at the call site
   (`fast_battery/ref/s2_kill_repeats.txt`).
5. Dedupe: all 12 specs pairwise-distinct by numpy model output before
   generation. Per-candidate progress logs + resume posture kept (no VM
   reboot this round).
