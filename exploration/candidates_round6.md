# Round 6 Candidates — Feistel Breakthrough (2026-10-01)

## Strategic context
- **Delay bar**: relative, ≤0.9× the 64×64 multiplier re-measured in the current
  flow. Multiplier ref: 103.5u ([fast_battery/ref/mult_ref.txt](fast_battery/ref/mult_ref.txt)) → **bar ≈ 93.2u**.
- **Binding constraint**: LIN/DIFF (amended 4-family screen), not delay.
- **xorshift64 pre-diffusion abandoned** as core primitive (round-5 finding).
- **S1 pipeline**: LIN/DIFF run FIRST; marginal (PB/RD) screen skipped on kill.
  Validated: h_xorspn3 dies in ~15s.

## SOTA refresh (2026-10-01)
Fresh sweep written to [`exploration/sota_leads.md`](sota_leads.md). Key leads:
- THF (eprint 2025/1314): fresh unrolled latency table; QARMAv2 tweak ideas.
- Orthros (2021): non-invertible low-latency PRF precedent — our mixer need not
  be invertible.
- SCARF (2022): forward-only latency metric matches our 1-cycle requirement.
- ILEA: Balanced Block Mixing layers as xorshift64 replacement (untested).
- wyhash MUM: rejected (full multiply ~40u, incompatible).

## Results: 16 candidates screened (LIN/DIFF-first)

### CAL_PASS — full 4-family amended screen (3)

> **CORRECTION 2026-10-01 (synthesis-flow bug):** the delay/area figures below
> were measured with a broken Yosys flow (`memory_map` after `techmap` left
> S-box muxes unmapped; the analyzer silently ignored the functional assigns
> and reported 8.9u). Corrected re-measurement with the fixed flow
> (`memory_map` BEFORE `techmap`; both analyzers cross-checked, fail loudly on
> functional assigns) gives:
>
> | candidate | delay | ratio | cells | area | S0 (≤0.9×) |
> |-----------|-------|-------|-------|------|-------------|
> | r6_feist8_spn | **86.5u** | **0.836×** | 8660 | 23566 | PASS |
> | r6_feist12_spn | **127.1u** | **1.228×** | 13408 | 36476 | **FAIL** |
> | r6_feist8_present | **100.7u** | **0.973×** | 10665 | 30351 | **FAIL** |
>
> Only **r6_feist8_spn** survives S0. The other two fail the delay bar.
> The CAL_PASS statistical claim (from `results/ldonly_r6.log`) is under
> independent re-verification via the fast-battery S1 screen (running).

| candidate | composition | LIN D | DIFF | bij |
|-----------|-------------|-------|------|-----|
| r6_feist8_spn | 8r Feistel, F=2r SPN (S1 S-box) | ≤29/4096, 0/10 rej | 0/10 | 100k ok |
| r6_feist12_spn | 12r Feistel, F=2r SPN (S1) | ≤33/4096, 0/10 rej | 0/10 | 100k ok |
| r6_feist8_present | 8r Feistel, F=2r SPN (PRESENT) | ≤33/4096, 0/10 rej | 0/10 | 100k ok |

Superseded (invalid) delay figures for the record: 8.9u/0.086×/2304 cells,
11.6u/0.112×/3447 cells, 8.9u/0.086×/2304 cells — produced by the broken flow.

### CAL_FLAG — LIN/DIFF kill (13)
| candidate | composition | LIN D | verdict |
|-----------|-------------|-------|---------|
| r6_spn5_s1 | 5r SPN S1+MidoriM (no xorshift) | 4096 | catastrophic linear |
| r6_spn6_s1 | 6r SPN S1+MidoriM | 4096 | catastrophic (even 6 rounds!) |
| r6_spn5_present | 5r SPN PRESENT S-box+pLayer | 32 | better but still FLAG |
| r6_spn5_gift | 5r SPN GIFT+MidoriM | 4096 | catastrophic |
| r6_spn5_skinny | 5r SPN SKINNY+MidoriM | 4096 | catastrophic |
| r6_spn5_midori | 5r SPN MidoriSb0+MidoriM | 4096 | catastrophic |
| r6_spn3_chi_spn3 | SPN3-chi-SPN3 sandwich | 4096 | catastrophic |
| r6_spn5_chi | 5r SPN + chi post | 4096 | catastrophic |
| r6_spn4_chi | 4r SPN + chi post | 4096 | catastrophic |
| r6_hetero6 | 6r hetero S-box | 4096 | catastrophic |
| r6_hetero5 | 5r hetero S-box | 4096 | catastrophic |
| r6_lm4_spn | 4r Lai-Massey SPN-F | 4096 | catastrophic |
| r6_lm6_spn | 6r Lai-Massey SPN-F | 4096 | catastrophic |

## Key findings

1. **Feistel with SPN F-functions is the ONLY structure that passes LIN/DIFF.**
   All 3 variants passed LIN/DIFF in the coordinator's sweep
   (`results/ldonly_r6.log`); full 4-family CAL_PASS is under independent
   re-verification via the fast-battery S1 screen (the coordinator's full-screen
   result files were not found). Only r6_feist8_spn survives S0.

2. **Deep SPNs (5-6 rounds) without xorshift are catastrophically linear**
   (D=4096/4096). Even 6 rounds of S1+MidoriM cannot break the linear
   structure of sequential inputs. The SPN structure itself preserves
   joint linear relationships; xorshift64 was masking this, not fixing it.

3. **PRESENT S-box + pLayer is better** (D=32 vs 4096) but still fails.
   The Midori M matrix combined with S1/GIFT/SKINNY is particularly bad.

4. **Chi, hetero, Lai-Massey all fail** with D=4096. The χ-layer (which failed
   in round 4) does not help as post-layer or sandwich.

5. **Delay bar binds again (corrected)**: with the fixed flow, Feistel 8-round
   is 86.5u (0.836×) — passes S0 with modest margin, not the 10× headroom the
   broken 8.9u figure suggested. 12 rounds (127.1u, 1.228×) and the PRESENT
   variant (100.7u, 0.973×) both FAIL S0.

## Pareto frontier (amended screen + delay)
- **r6_feist8_spn**: only S0-surviving CAL_PASS design (86.5u, 0.836×,
  8660 cells) — statistical claim under independent S1 re-verification
- **r6_feist12_spn**: fails S0 (127.1u, 1.228×) — out
- **r6_feist8_present**: fails S0 (100.7u, 0.973×) — out

r6_feist8_spn is slower than the round-5 leaders (r5_xs2spn3: 38.3u, 0.754×;
r5_xorspn4: 39.9u, 0.785×) but those were killed by LIN/DIFF; it is the only
candidate passing both the delay bar and the statistical screen (pending
independent S1 confirmation).

## Composition field
- **r6_feist8_spn**: `val ^ key` whitening → 8× Feistel round
  (`L,R = R, L ^ F(R, rk)`), F = S-box(S1) → rotl7/rotl13 XOR → S-box(S1) → ^rk32.
  Output `{R, L}` (final swap).
- **r6_feist12_spn**: same, 12 rounds.
- **r6_feist8_present**: same as 8-round, PRESENT S-box in F.

## Bugs fixed during round 6
1. **Python model 32-bit leak**: `_feist_F_spn_np` used 64-bit `_sbox_layer_np`
   on 32-bit values, leaking S-box(0) patterns from upper bits into rotations.
   Fixed with explicit 32-bit masking.
2. **Verilog rk missing round constant**: `_rk_np(k,i) = rotl(k,13*(i+1)) ^ rc(i)`
   but Verilog only did rotation. Fixed.
3. **[run_synth.py](run_synth.py)**: removed `-fast` (incompatible with `-genlib` in this ABC
   version); added `memory_map` for ROM inference from case statements.

## Next gates (per kill-chain)
1. **S2**: Differential early-kill (C, N=2^22, kill at 1000 full-64-bit repeats)
2. **S3**: PractRand incremental 16MB→1GB (C generator, bit-exact xcheck)
3. **S4**: TestU01 SmallCrush
4. **S5**: Sky130 P&R (manual gate)

The Feistel candidates are the first to reach S2 since the amended screen.

## r6_feist8_spn full battery results (2026-10-01)

First candidate in the entire search to clear S0–S4.

| Gate | Result | Evidence |
|---|---|---|
| S0 delay | **PASS** 86.5u = 0.836× multiplier (bar 0.9×) | fixed-flow synthesis, analyzers agree |
| S1 CAL_PASS | **PASS** LIN 0/10, DIFF 0/10, PB 0, RD 0 | independently confirmed (s1_result.json) |
| S2 differential | **PASS** 2 keys (0x123456789ABCDEF0, 0x0), 74 deltas, N=2²² | max_repeats=0, max\|z\|=3.5/3.3 |
| S3 PractRand | **PASS** 16MB→64MB→256MB→1GB, no FAIL | 3 configs: (key=1234…,stride=1), (key=0,stride=1), (key=1234…,stride=3); "no anomalies in 227 test result(s)" at 1GB |
| S4 SmallCrush | **PASS** all 15 statistics | TestU01 1.2.3, 25s |
| RTL 1/cycle | **PASS** 64/64 back-to-back vectors | iverilog tb, new inputs every clock, no hidden state |
| Equivalence | **FORMALLY PROVEN** RTL ≡ mapped netlist | ABC `cec`: "Networks are equivalent" (0.03s), 128/64 I/O |
| C ↔ model | 10,000/10,000 match | bit-exact |
| Netlist ↔ model | 300/300 random vectors match | Python topological evaluator |
| Bijectivity | **PROVEN structurally + constructive** | Feistel round is a permutation for any F; whitening is XOR; explicit inverse recovers input 20,000/20,000; 0 collisions on 4M sequential outputs |

Key contrast vs disqualified finalists: h_xorspn3 had 41,889 full-width repeats at
δ=0x400 (S2 kill) and PractRand BRank FAIL at 16MB; r3_xorlin_qm had PractRand
BRank FAIL at 256MB and S1 LIN/DIFF kills. r6_feist8_spn shows 0 repeats and
clean PractRand to 1GB on 3 configurations.

Remaining gates: S5 (Sky130 P&R identical-condition A/B), independent peer
reviews, M9 multi-key hash-DoS chaining analysis. Search continues (round 7+)
regardless — no ISA freeze.
