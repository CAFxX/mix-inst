# Round 8 — Pareto-frontier search (2026-10-02)

Target: beat `r7_feist8_s1_1sbox` — 56.5u (0.546×), 6,063 cells, area 17,098.
Multiplier reference re-measured fresh in this round's pinned flow: **103.5u**
(cells 12,645, area 35,323). S0 bar: ≤ 0.9 × 103.5 = 93.15u.

Metrology note: `run_synth.py` (default ABC) and `s0_delay.py` (no-dretime
script) agree exactly on the leader (56.5u/6063/17098). Battery S0 numbers
are quotable.

## Candidates

| Candidate | Structure | S0 delay | Cells | Area | Stage reached | Kill reason / notes |
|---|---|---:|---:|---|---|---|
| r8_feist6_s1_1sbox | 6r, F=S1x1+lin713, white | 43.7u | 4,744 | 13,387 | S4 PASS | Full S0–S4. 0.422×. Q1 PASS (noise floor). |
| r8_feist7_s1_1sbox | 7r, F=S1x1+lin713, white | 50.2u | 5,452 | 15,421 | S4 PASS | Full S0–S4. 0.485×. Q1 PASS (noise floor). |
| r8_feist6_s1_1sbox_nw | 6r, F=S1x1+lin713, no white | 42.9u | 4,133 | 11,670 | S4 PASS | Full S0–S4. 0.414×. Fastest+smallest so far. Q1 PASS (noise floor). |
| r8_feist7_s1_1sbox_nw | 7r, F=S1x1+lin713, no white | 48.6u | 5,192 | — | S1 kill | LIN FLAG (DIFF passed). |
| r8_feist8_s1_1sbox_nw | 8r, F=S1x1+lin713, no white | 56.0u | | — | S1 kill | LIN/DIFF passed; marginal RD rej=1. Whitening matters at 8r. |
| r8_feist6_r311 | 6r, F=S1+lin311+S1, white | 64.1u | 6,163 | 17,182 | S4 PASS | Full S0–S4 but slower than leader (56.5u). |
| r8_feist6_r517 | 6r, F=S1+lin517+S1, white | 65.5u | 6,444 | 17,638 | S4 PASS | Full S0–S4 but slower than leader (56.5u). |
| r8_feist8_midori | 8r, F=S1+MidoriMC(2col), white | 57.2u | 5,891 | — | S1 kill | LIN FLAG + DIFF FLAG (rej=10/10, |z|~1.5M). |
| r8_feist6_midori | 6r, F=S1+MidoriMC(2col), white | 43.2u | 4,231 | — | S1 kill | LIN FLAG + DIFF FLAG (rej=10/10, |z|~1.5M). |
| r8_feist6_s1_alt | 6r, alternating F (1sbox/2sbox), white | 55.0u | 5,436 | 15,095 | S4 PASS | Full S0–S4. 0.531×. Q1 PASS (noise floor). |
| r8_feist4_s1_3sbox | 4r, F=S1+lin+S1+lin+S1, white | 68.2u | 6,724 | 17,865 | S4 PASS | Full pass but slower than leader. |
| r8_feist6_pbox | 6r, F=S1x1+lin713 + P32 on new R, white | 43.5u | 4,544 | 12,929 | S4 PASS | Full S0–S4 (RTL gen bug fixed, re-run). 0.420×. Q1 PASS (noise floor). |
| r8_ufeist16_48_f2 | 8r uFeistel 16/48, F=S1+fold+lin16+S1 | 101.6u | 6,302 | — | S0 kill | 0.982× > 0.9 bar. ufeist16/48 hopeless on delay. |

## Bit-exactness

- C vs Python (xcheck, 10k vectors): 13/13 PASS.
- RTL vs Python (check_rtl, 300 vectors): 13/13 PASS (pbox re-verified after fix).
- S0 mapped-netlist equivalence (1000 vectors): per battery log.

## Pareto frontier

Standing (pre-round-8): { r7_feist8_s1_1sbox: 56.5u, 6063 cells, 17098 }.
**Round-8 changes: THE PARETO POINT MOVED.** New leader: **r8_feist6_s1_1sbox_nw —
42.9u (0.414× multiplier), 4,133 cells, area 11,670** (6r Feistel,
F = S1 S-box layer → x^rotl32(x,7)^rotl32(x,13) → ^rk32, no input whitening).
Dominates the old leader on all three axes (24% faster, 32% fewer cells,
32% less area).

Evidence for the new leader:
- S0: 42.9u ≤ 93.15u bar (0.414× of 103.5u ref, same pinned flow); cells 4133,
  area 11670; mapped-netlist equivalence 1000/1000 vectors.
- S1: CAL_PASS (LIN PASS, DIFF PASS, marginal PB rej=0 RD rej=0).
- S2: differential early-kill PASS (no repeats above threshold).
- S3: PractRand PASS to 1 GB (key=0x123456789ABCDEF0 stride=1, and
  key=0x0 stride=0x9E3779B97F4A7C15).
- S4: TestU01 SmallCrush 15/15 PASS.
- Q1 spot check (SAC/BIC, N=2^18, fixed key): sac_z5=0, sac_maxdev=0.003792,
  sac_meandev=0.000780, bic_maxcorr=0.008037, bic_meancorr=0.001556,
  avalanche_mean=31.9991 — at noise floor, indistinguishable from the old
  leader's Q1 (0.0035/0/0.0092/32.0011).
- Bit-exactness: C↔Python 10,000/10,000; RTL↔Python 300/300.

Other new full-pass sub-56.5u candidates (S0–S4 + Q1 at noise floor):
- r8_feist6_pbox: 43.5u (0.420×), 4544 cells, 12929 area. Q1: 0.003830/0/0.008664/32.0018.
- r8_feist6_s1_1sbox: 43.7u (0.422×), 4744 cells, 13387 area. Q1: 0.003365/0/0.008742/32.0010.
- r8_feist7_s1_1sbox: 50.2u (0.485×), 5452 cells, 15421 area. Q1: 0.003529/0/0.008573/32.0008.
- r8_feist6_s1_alt: 55.0u (0.531×), 5436 cells, 15095 area. Q1: 0.003170/0/0.008911/32.0011.

Non-Pareto full passes: r8_feist6_r311 64.1u, r8_feist4_s1_3sbox 68.2u.
r8_feist6_r517 finished 65.5u (dominated).
