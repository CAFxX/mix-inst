# Round 12 — Linear/diffusion structure inside F; F cost reduction

**Date:** 2026-10-02/03. **Frontier after round: UNCHANGED**
{r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u}.

**Multiplier reference:** 103.5u (re-measured fresh in the pinned Yosys-0.69
flow; S0 bar ≤ 93.15u). All 10 candidates pass S0.

## Families

- **F1** — 5 rounds + 3-rotation linear `lin(a,b,c) = x^rotl(x,a)^rotl(x,b)^rotl(x,c)`
  (same 2-XOR tree depth as 2-rotation). Re-attacks the 5-round phase transition.
- **F2** — partial S-box F: S1 on low 16 bits only → full `lin(3,11)` → ^rk32,
  at 6/7/8 rounds. Halves S-box cost/round; tests cheaper-F/more-rounds.
- **F3** — 3-rotation linear at 6 rounds: does better diffusion/round buy
  cleaner S2 at ~41u?
- **F4** — heterogeneous: `lin16(x) = x ^ rotl32(x,3) ^ rot16half(x,7)`
  (each 16-bit half rotated by 7 within itself), 6 rounds.

All: balanced Feistel, 32-bit halves, {R,L} output, NO whitening, affine
r7/r8/r9 key schedule. Generator: `round12/gen_r12.py`; reference:
`round12/models/r12.py`. C↔model 10,000/10,000 and RTL↔model 300/300 for all
10 (round-key indexing uses the (i+2) convention per the round-11 lesson).

## S0 (run_synth.py, authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r12_feist6_s1half311_nw | 37.3u | 0.360× | 2,871 | 8,437 | faster+smaller than r9 — needs S1 |
| r12_feist5_lin31125_nw | 38.9u | 0.376× | 4,566 | 12,768 | faster than r9 — needs S1+Q1 |
| r12_feist5_lin31119_nw | 39.3u | 0.380× | 4,372 | 12,224 | faster than r9 — needs S1+Q1 |
| r12_feist5_lin3711_nw | 39.5u | 0.382× | 4,775 | 13,274 | faster than r9 — needs S1+Q1 |
| r12_feist5_lin71319_nw | 39.9u | 0.386× | 4,552 | 12,726 | faster than r9 — needs S1+Q1 |
| r12_feist6_s1_16rot_nw | 41.6u | 0.402× | 4,041 | 11,402 | dominates r8 on (delay,cells,area) — needs S1 |
| r12_feist7_s1half311_nw | 42.5u | 0.411× | 3,441 | 10,145 | dominates r8 on (delay,cells,area) — needs S1 |
| r12_feist6_lin3711_nw | 46.7u | 0.451× | 5,445 | 15,301 | dominated by r9 |
| r12_feist6_lin71319_nw | 46.8u | 0.452× | 6,060 | 16,796 | dominated by r9 |
| r12_feist8_s1half311_nw | 47.0u | 0.454× | 4,489 | 13,017 | dominated by r9 |

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r12_feist5_lin3711_nw | **FLAG** | LIN rej=9 |
| r12_feist5_lin31119_nw | **FLAG** | LIN rej=9 |
| r12_feist5_lin71319_nw | **FLAG** | LIN rej=9 |
| r12_feist5_lin31125_nw | **FLAG** | LIN rej=9 |
| r12_feist6_s1half311_nw | **FLAG** | LIN rej=10, DIFF rej=10 |
| r12_feist7_s1half311_nw | **FLAG** | LIN/DIFF pass; marginal PB rej=4 |
| r12_feist8_s1half311_nw | **CAL_PASS** | full screen clean |
| r12_feist6_lin3711_nw | **FLAG** | LIN rej=9 |
| r12_feist6_lin71319_nw | **FLAG** | LIN rej=9 |
| r12_feist6_s1_16rot_nw | **FLAG** | LIN rej=10, DIFF rej=10 |

## Full battery (sole S1 survivor)

**r12_feist8_s1half311_nw**: S0a xcheck 10k/10k ✓, S0 47.0u ✓, S1 CAL_PASS ✓,
**S2 KILL** — `delta=0x0000000000080000` (single bit in the high 16 bits, the
nibbles that bypass the S-box) gives **70 repeats** (kill threshold 10,
`ref/s2_kill_repeats.txt` verified = 10 at the call site); companion delta
`0x0000000000040000` has max|z|=20.1. Structural: input differences confined
to the non-S-box half do not get enough nonlinear diffusion even at 8 rounds.

## Findings

1. **The 5-round phase transition is robust.** All four 3-rotation-linear
   5-rounders fail the LIN screen with rej=9 — the same signature as every
   prior 5-round attempt. Stronger per-round linear diffusion does not cross
   the transition. F1 closed.
2. **Cheaper-F/more-rounds does NOT beat the optimum.** Partial S-box needs
   8 rounds to pass S1 (6r fails LIN+DIFF outright, 7r fails marginal PB),
   and at 8r it is slower (47.0u) than 6r full-S-box (41.0u) — then dies at
   S2 on exactly the structural weakness the design invites (differences
   avoiding the S-box). F2 closed as a frontier direction.
3. **The 3-rotation linear is worse on both axes.** At 6r it synthesizes
   SLOWER (46.7–46.8u vs 41.0u for 2-rotation — the 4-term XOR tree does not
   map to the expected 2-XOR depth) AND fails the LIN screen (rej=9) where
   lin(3,11) passes. The 2-rotation (3,11) remains the optimal linear layer.
   F3 closed.
4. **16-bit-half rotation mixing fails structurally** (LIN rej=10, DIFF
   rej=10) despite an attractive 41.6u/4,041-cell S0 that would have
   dominated r8. Heterogeneous linear layers of this form are out. F4 closed.
5. **Frontier unchanged.** No round-12 candidate survives S1+S2. The two
   frontier points stand: r9_feist6_rot311_nw (41.0u, speed) and
   r8_feist6_s1_1sbox_nw (42.9u, size/quality).

## Evidence locations

- `round12/gen_r12.py`, `round12/models/r12.py`
- `round12/s0/` (per-candidate run_synth.py logs), `round12/s0_progress.log`
- `round12/s1/` + `round12/s1_<cand>.log`, `round12/s1_progress.log`
- `round12/xcheck/` (C↔model 10k), `round12/rtlcheck/` (RTL↔model 300)
- `round12/battery_r12_feist8_s1half311_nw.log`; S2 detail in
  `fast_battery/results/r12_feist8_s1half311_nw/s2.out`
- Candidates: `fast_battery/candidates/r12_*/` (impl.c, rtl.v, model.py, meta.json)

## Process notes

- Round-key indexing used the (i+2) convention from the round-11 lesson;
  check_rtl passed 300/300 on all 10 first try — no off-by-one.
- S2 kill threshold verified = 10 at the call site
  (`fast_battery/ref/s2_kill_repeats.txt`).
- Dedupe: all 10 specs pairwise-distinct by numpy model output before
  generation.
- Infra: first rtlcheck run failed (iverilog not on PATH in the fresh
  session); re-ran with the sky130/micromamba PATH export. No design impact.
