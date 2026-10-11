# Round 13 — New F diffusion/topologies

**Date:** 2026-10-03. **Frontier after round:**
{r13_feist6_alt_s1chi_nw: 40.1u, r9_feist6_rot311_nw: 41.0u,
r8_feist6_s1_1sbox_nw: 42.9u} — new speed point (heterogeneous S1/chi).

**Multiplier reference:** 103.5u (re-measured fresh in the pinned Yosys-0.69
flow; S0 bar ≤ 93.15u). All 13 candidates pass S0.

## Families

- **F1** — 4-round Feistel, DOUBLE-STRENGTH F =
  `lin(S1(lin(S1(R^rkA))^rkB))`, two round keys per round
  (rkA=RK32(key,2i-1), rkB=RK32(key,2i)), lin (3,11) and (7,13).
  Hypothesis: a stronger F crosses the 4-round barrier inside ~41u.
- **F2** — chi32 nonlinear layer `b_i = a_i ^ (~a_{i+1} & a_{i+2})`
  (algebraic degree 2, ~3-gate boolean depth, far cheaper than the S1 DNF
  layer), F = lin(3,11)(chi32(R)) ^ rk at 5/6/8 rounds. NOTE: chi over an
  even width is not a permutation — fine, a Feistel F need not be invertible.
- **F3** — chi→S1 hybrid F = lin(3,11)(S1(chi32(R))) ^ rk, 6 rounds.
- **F4** — heterogeneous rounds: `alt` (odd rounds S1-F, even rounds chi-F)
  and `s1x3_chix3` (rounds 1–3 S1-F, rounds 4–6 chi-F), 6 rounds.
- **F5** — Lai-Massey with S1 F, 4r/6r.
- **F6** — key-schedule variants on the r9 structure: `midk`
  (F = lin(3,11)(S1(R) ^ rk), key between S-box and linear) and `rkhi`
  (rk = high32(RK64) on odd rounds, low32 on even rounds).
- **F7** — sandwich F = lin(3,11)(S1(lin(3,11)(R))) ^ rk, 6 rounds.

All: 32-bit halves, {R,L} output, NO whitening, affine r7/r8/r9 key schedule.
Generator: `round13/gen_r13.py`; reference: `round13/models/r13.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 for all 13. Round-key indexing
uses the (i+2) convention (round-11 lesson); F1 additionally uses
(2i+2)/(2i+3) for its two keys/round — check_rtl passed 300/300 first try on
all novel conventions (double-key, rotating key-half, mid-key, Lai-Massey).

## S0 (run_synth.py, authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r13_lm4_s1_311_nw | 31.0u | 0.300× | 2,785 | 7,951 | faster+smaller than r9 — needs S1 |
| r13_feist5_chi311_nw | 34.0u | 0.329× | 3,548 | 10,175 | faster+smaller than r9 — needs S1 |
| r13_feist6_alt_s1chi_nw | 40.1u | 0.387× | 4,563 | 13,041 | faster than r9 — needs S1+Q1 |
| r13_feist6_chi311_nw | 40.9u | 0.395× | 4,883 | 13,688 | faster than r9 — needs S1+Q1 |
| r13_feist6_s1x3_chix3_nw | 41.0u | 0.396× | 4,285 | 12,127 | ties r9 delay, larger — dominated |
| r13_feist6_s1_rkhi311_nw | 41.6u | 0.402× | 4,410 | 12,341 | dominated by r9 |
| r13_lm6_s1_311_nw | 45.6u | 0.441× | 4,684 | 13,415 | dominated by r9 |
| r13_feist6_s1_midk311_nw | 50.3u | 0.486× | 5,192 | 14,268 | dominated by r9 |
| r13_feist8_chi311_nw | 52.4u | 0.506× | 6,171 | 17,810 | dominated by r9 |
| r13_feist4_s1x2_311_nw | 56.2u | 0.543× | 6,920 | 18,576 | dominated by r9 |
| r13_feist6_chis1_311_nw | 57.2u | 0.553× | 5,841 | 16,230 | dominated by r9 |
| r13_feist4_s1x2_713_nw | 58.6u | 0.566× | 6,868 | 18,525 | dominated by r9 |
| r13_feist6_sandw311_nw | 59.7u | 0.577× | 7,127 | 20,109 | dominated by r9 |

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r13_feist4_s1x2_311_nw | **CAL_PASS** | full screen clean |
| r13_feist4_s1x2_713_nw | **CAL_PASS** | full screen clean |
| r13_feist5_chi311_nw | **FLAG** | DIFF rej=10 |
| r13_feist6_chi311_nw | **CAL_PASS** | full screen clean |
| r13_feist8_chi311_nw | **CAL_PASS** | full screen clean |
| r13_feist6_chis1_311_nw | **CAL_PASS** | full screen clean |
| r13_feist6_alt_s1chi_nw | **CAL_PASS** | full screen clean |
| r13_feist6_s1x3_chix3_nw | **CAL_PASS** | full screen clean |
| r13_lm4_s1_311_nw | **FLAG** | LIN rej=10 |
| r13_lm6_s1_311_nw | **CAL_PASS** | full screen clean |
| r13_feist6_s1_midk311_nw | **CAL_PASS** | full screen clean |
| r13_feist6_s1_rkhi311_nw | **CAL_PASS** | full screen clean |
| r13_feist6_sandw311_nw | **CAL_PASS** | full screen clean |

11/13 pass S1. The 4-round phase transition is CROSSED: both double-strength-F
4-rounders pass the full screen (the 5-round single-S1 barrier from r9/r10/r12
does not apply to a stronger F).

## S2 (differential profiler, N=2^22, 115 deltas, kill threshold 10)

| Candidate | S2 verdict | max\|z\| | repeats |
|---|---|---:|---:|
| r13_feist4_s1x2_311_nw | **PASS** | 3.7 | 0 |
| r13_feist4_s1x2_713_nw | **PASS** | 3.8 | 0 |
| r13_feist6_chi311_nw | **PASS** (repeats) | **86.5** | 0 |
| r13_feist8_chi311_nw | **PASS** | 3.8 | 0 |
| r13_feist6_chis1_311_nw | **PASS** | 3.7 | 0 |
| r13_feist6_alt_s1chi_nw | **PASS** | 10.7 | 0 |
| r13_feist6_s1x3_chix3_nw | **PASS** | 23.2 | 0 |
| r13_lm6_s1_311_nw | **PASS** | 4.1 | 1 |
| r13_feist6_s1_midk311_nw | **PASS** | 16.7 | 0 |
| r13_feist6_s1_rkhi311_nw | **PASS** | 16.9 | 0 |
| r13_feist6_sandw311_nw | **PASS** | 3.7 | 1 |

## Q1 (SAC/BIC avalanche, N=2^18, fixed key) — for frontier-relevant candidates

| Candidate | sac_maxdev | sac_z5 | bic_maxcorr | avalanche_mean | verdict |
|---|---|---:|---:|---:|---|
| r13_feist6_alt_s1chi_nw | 0.00446 | 0 | 0.00800 | 32.00 | **CLEAN** — matches frontier quality |
| r13_feist6_chi311_nw | 0.0214 | **57** | 0.0232 | 31.98 | **REJECT** — avalanche fails |
| r9_feist6_rot311_nw (control) | 0.0037 | 0 | 0.0085 | 32.00 | script validation OK |

The Q1 script (`round13/q1_sacbic.py`) reproduces the known r9 baseline
(sac_z5=0), so chi6's 57 z5-cells are real. 6-round chi has a systematic
avalanche/differential weakness (S2 |z|=86.5 on single-bit deltas; Q1
sac_z5=57) despite passing S1's marginal screen — S1's PB family tests
marginals, not single-bit-flip avalanche. **Chi at 6 rounds is rejected for
the frontier on quality.** (8-round chi is S2-clean at |z|=3.8 but dominated
at 52.4u.)

## Full battery (PractRand 16MB→1GB + SmallCrush)

| Candidate | S3 PractRand | S4 SmallCrush | verdict |
|---|---|---|---|
| r13_feist6_alt_s1chi_nw | 16/64/256MB + 1GB: no FAIL (199/227 tests) | All tests were passed | **BATTERY-PASS** |
| r13_feist6_chi311_nw | not run (Q1 reject) | — | rejected on avalanche |

## Findings (2026-10-03)

**FRONTIER CHANGE: r13_feist6_alt_s1chi_nw takes the speed point.**
6-round Feistel with heterogeneous F — odd rounds S1-F (S1→rotmix(3,11)→^rk),
even rounds chi-F (chi32→rotmix(3,11)→^rk), no whitening:
- S0: **40.1u** / 4,563 cells / 13,041 (vs r9 41.0u / 4,265 / 11,996)
- S1: CAL_PASS (zero rejections, all four families)
- S2: PASS, 0 repeats, max|z|=10.7 (r9: 16.5)
- Q1: sac_z5=0, sac_maxdev=0.00446, bic_maxcorr=0.00800 (matches frontier)
- S3: PractRand 1GB clean; S4: SmallCrush all passed

Pareto check (delay, cells, area): alt(40.1, 4563, 13041) vs
r9(41.0, 4265, 11996) vs r8(42.9, 4133, 11670) — no point dominates another,
so the frontier grows to three points: **alt = new speed point**,
r9 = middle, r8 = size/quality. The 0.9u gap is deterministic ABC output on
different netlists, not measurement noise (same flow, same multiplier ref).
RTL copied to `~/workspace/your_files/mix_rtl_pareto/mix_r13_feist6_alt_s1chi_nw.v`.

1. **Heterogeneous nonlinear layers beat homogeneous ones on delay.**
   Alternating (S1, chi) at 40.1u is faster than all-S1 (41.0u) AND all-chi
   (40.9u), while matching all-S1 quality. The chi rounds are cheap
   (~3-gate depth vs S-box layer) and the S1 rounds supply the avalanche
   that pure chi lacks (see 2). No adverse S1/chi interaction.
2. **Pure chi needs help with avalanche at 6r.** r13_feist6_chi311_nw passes
   S1's marginal screen but fails Q1 avalanche (sac_z5=57, sac_maxdev=0.0214)
   with S2 |z|=86.5 on single-bit deltas. S1's PB family tests marginals,
   not single-bit-flip avalanche — Q1 is now a mandatory gate for any
   frontier claim, not just 4r/5r. (8r chi is S2-clean at |z|=3.8 but
   dominated at 52.4u.)
3. **The 4-round barrier is crossed with a stronger F** (process notes §1:
   both 4r double-S1 pass full S1 + clean S2 at |z|~3.7/3.8) — but dominated
   on delay (56–59u). Statistical result, not a Pareto one.
4. **Lai-Massey: D-invariance bug caught by S0; even fixed, dominated.**
   (see process notes)
5. **Key-schedule variants neutral-to-negative** (mid-key 50.3u, rotating
   half 41.6u, both S1-pass but dominated).
6. **Sandwich diffusion costs** (59.7u, S1-pass, dominated).

## Evidence locations

- Candidates: `exploration/fast_battery/candidates/r13_*/`
- S0: `round13/s0/*.log` (RESULT lines; ref mul 103.5u); S1: `round13/s1/*.log` + `round13/s1_progress.log`
- S2 logs: `round13/s2_r13_*.log`, progress `round13/s2_progress.log`
- Q1: `round13/q1/q1_*.json`, script `round13/q1_sacbic.py`
- alt battery: `fast_battery/results/r13_feist6_alt_s1chi_nw/` + `round13/battery_r13_feist6_alt_s1chi_nw.log`
- Frontier RTL: `~/workspace/your_files/mix_rtl_pareto/`

## Process notes

1. **The 4-round barrier is crossed with a stronger F.** Both double-strength-F
   4-rounders pass the FULL S1 screen (zero rejections in all four families)
   and are S2-clean (0 repeats, max|z| = 3.7/3.8 — cleaner than either
   frontier point). The 5-round phase transition observed in r9/r10/r12
   applies to the single-S1 F, not to 4 rounds as such. Cost: 56–59u, so
   dominated on delay — but the statistical result reframes the round-count
   question as F-strength-dependent. (4r claims would still need sac_z5=0;
   not pursued — dominated.)
2. **Pure chi fails avalanche at 6r; Q1 is now mandatory for frontier claims.**
   r13_feist6_chi311_nw passes S1's marginal screen but Q1 shows sac_z5=57
   (S2 |z|=86.5 on single-bit deltas). S1's PB family tests marginals, not
   single-bit-flip avalanche — a screen-shaped hole. Rule: any frontier
   claim now requires Q1 sac_z5=0 regardless of round count.
3. **Heterogeneous (S1,chi) rounds: no adverse interaction.** The alternating
   design is S2-clean (|z|=10.7), Q1-clean, PractRand/SmallCrush-clean —
   the S1 rounds fully compensate chi's avalanche weakness.
4. **Lai-Massey: D-invariance bug caught by S0; even fixed, dominated.**
   The naive LM round L'=R^t, R'=L^t preserves D = L^R across rounds — every
   round's F sees the same input, a degenerate single-F-layer design.
   S0 caught it (5.5u/578 cells for 4r; ABC correctly shared the single F).
   The synthesis number was TRUE for the (degenerate) design, not a tool
   bug. Fixed with orthomorphism σ(L,R)=(R,L^R): L'=R^t, R'=L^R
   (bijectivity proved by round-trip inverse test, 2 keys × 2000 vectors).
   Even fixed, 4r LM fails S1 LIN (rej=10) — the linear half R'=D leaks;
   6r passes S1 but is dominated at 45.6u. Family closed.
   Rule: for any non-Feistel topology, prove by hand that the round
   function's inputs actually change across rounds (trace D or the F input
   for 2 rounds symbolically) BEFORE generating RTL; add an invertibility
   round-trip self-test for novel topologies.
5. **Key-schedule variants neutral-to-negative.** Key-between-S-box-and-linear
   (50.3u) and rotating key-half (41.6u) both pass S1 but are dominated;
   neither buys delay or quality over the standard key position.
6. **Sandwich diffusion costs.** lin→S1→lin at 6r passes S1 but costs 59.7u —
   diffusion before AND after the S-box is pure delay cost at 6r.
7. **VM reboot mid-round (2026-10-03 ~00:29).** The machine rebooted during
   the S2 queue (5/11 done) and the chi6 S3 battery, killing all detached
   queues despite setsid/nohup. Toolchain (~/tools, micromamba) survived
   intact. Recovery: S2 resumed for the 6 remaining candidates
   (`run_s2_resume.sh`); completed S2 results (5) were on persistent disk
   and kept. Lesson: on this VM, treat every long queue as rebootable —
   keep per-candidate progress logs so a resume script can pick up exactly
   the unfinished set. (Same class as the round-9 session-reaping lesson,
   one level up: detach from the session AND checkpoint per candidate.)
8. Round-key indexing: the novel (2i+2)/(2i+3) double-key convention, the
   rotating key-half, and the mid-key variant all passed check_rtl 300/300
   first try — the (i+2) derivation discipline from r11 generalizes.
9. S2 kill threshold verified = 10 at the call site
   (`fast_battery/ref/s2_kill_repeats.txt`).
10. Dedupe: all 13 specs pairwise-distinct by numpy model output before
    generation.
11. chi32 even-width non-permutation documented in the model; Feistel F needs
    no invertibility.
