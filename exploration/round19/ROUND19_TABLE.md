# Round 19 — BIC-fix probes + truncation axis

**Date:** 2026-10-03. **Frontier after round: EXTENDED to two points**
{r18_feist6_alt_notr_nw: 37.9u / 4,119 / 11,621,
 r19_feist6_alt_notr_chioff13_nw: 37.4u / 4,149 / 11,820}.
Neither dominates the other (chioff13 is 0.5u faster but 30 cells / 199 area
larger). Both carry the documented BIC blemish class (unmixed final chi).

**Multiplier reference:** 103.5u (pinned Yosys-0.69 flow; S0 bar ≤ 93.15u).
All 10 candidates pass S0.

## Families (all 6r Feistel, no whitening, affine r7/r8/r9 key schedule)

- **A. BIC-fix probes** — notr structure, round 6 F gets cheap final mixing:
  - `fm03`: F_6 = (chi32(R)^rk) ^ rotl32(chi32(R)^rk, 3)
  - `fm07`: same with rotl 7
  - `fm11`: same with rotl 11
  - `fm311`: F_6 = rotl32(chi32(R),3) ^ rotl32(chi32(R),11) ^ rk
- **B. Truncation axis**:
  - `notr5`: r13 alt with round 5's linear ALSO dropped (F_5 = S1(R)^rk;
    round 6 F = chi32(R)^rk) — S1-gated probe, expected harmful.
  - `ps_notr`: parsplit-F (r15) with round 6's linear dropped.
  - `r9_notr`: r9 structure with round 6's linear dropped (F_6 = S1(R)^rk).
  - `chioff13`: notr + chi offsets (1,3) on rounds 2,4 (round 6 unchanged).
  - `notr_517`: notr with (5,17) rotmix on the 5 surviving linears.
- **A+B combo** (added mid-round on Q1 evidence): `chioff13_fm03` — rounds
  2,4 chi(1,3), F_6 = (chi32(R)^rk)^rotl32(chi32(R)^rk,3).

Generator: `round19/gen_r19.py`; reference: `round19/models/r19.py`.
Structural note: all are plain balanced Feistel with an arbitrary F —
bijective in val for fixed key regardless of F; no novel topology.
One generator bug caught by structural RTL review before the battery: the
generic round if-chain emitted a stray `end` before `else if` (unbalanced
block); fixed, all 9+1 RTLs parse in iverilog.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 for all 10 — first try, including
the rk-baking fm rounds (round-key indexing (i+2) convention held).

## S0 (run_synth.py, authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r19_feist6_alt_notr5_nw | 34.9u | 0.337× | 4,028 | 11,580 | tempting — S2-gated |
| r19_feist6_alt_notr_chioff13_nw | 37.4u | 0.361× | 4,149 | 11,820 | faster than notr — full battery |
| r19_feist6_alt_notr_517_nw | 38.4u | 0.371× | 4,320 | 12,285 | dominated by notr |
| r19_feist6_alt_notr_fm07_nw | 38.8u | 0.375× | 5,053 | 14,320 | dominated (BIC fix, Q1-gated) |
| r19_feist6_alt_notr_fm11_nw | 39.3u | 0.380× | 4,877 | 13,748 | dominated (BIC fix, Q1-gated) |
| r19_feist6_alt_notr_fm311_nw | 39.5u | 0.382× | 4,467 | 12,769 | dominated (BIC fix, Q1-gated) |
| r19_feist6_ps_notr_nw | 39.5u | 0.382× | 3,905 | 10,994 | dominated |
| r19_feist6_alt_notr_chioff13_fm03_nw | 39.5u | 0.382× | 4,848 | 13,891 | dominated (BIC fix, Q1-gated) |
| r19_feist6_alt_notr_fm03_nw | 39.8u | 0.385× | 4,572 | 12,943 | dominated (BIC fix, Q1-gated) |
| r19_feist6_r9_notr_nw | 39.9u | 0.386× | 3,960 | 11,039 | dominated |

## S1

| Candidate | S1 verdict |
|---|---|
| all 10 | **CAL_PASS** (zero rejections, all four families) |

10/10 pass S1 — including the 34.9u notr5. S1's screen does not see the
notr5 differential breakage (see S2).

## S2 (N=2^22, 115 deltas, kill threshold 10 — verified `10` at ref file)

| Candidate | S2 verdict | max\|z\| | repeats |
|---|---|---:|---:|
| r19_feist6_alt_notr_fm03_nw | **PASS** | 10.7 | 0 |
| r19_feist6_alt_notr_fm07_nw | **PASS** | 10.7 | 0 |
| r19_feist6_alt_notr_fm11_nw | **PASS** | 10.7 | 0 |
| r19_feist6_alt_notr_fm311_nw | **PASS** | 10.7 | 0 |
| r19_feist6_alt_notr_chioff13_fm03_nw | **PASS** | 11.2 | 0 |
| r19_feist6_alt_notr_chioff13_nw | **PASS** | 11.2 | 0 |
| r19_feist6_alt_notr_517_nw | **PASS** | 4.7 | 0 |
| r19_feist6_ps_notr_nw | **PASS** | 18.6 | 0 |
| r19_feist6_r9_notr_nw | **PASS** | 16.5 | 0 |
| r19_feist6_alt_notr5_nw | **PASS (formal) / BROKEN (structural)** | **477.4** | 1 |

notr5: formal PASS (repeats=1 < 10) but systematic single-bit differential
spikes |z| = 165–477 across many deltas (e.g. 0x0000001000000000: 477.2,
0x0001000000000000: 477.4). Dropping the round-5 S1 linear destroys diffusion;
the 34.9u number is a "fast number, broken design" (r17 premix class).
**notr5 is dead for the frontier.** The identical |z|=10.7 across all four fm
variants (== notr's 10.7) shows the worst delta lives in the shared rounds
1–5; ps_notr reproduces r15 parsplit's 18.6 and r9_notr reproduces r9's 16.5
— dropping the final linear changes nothing differentially there.

## Q1 (SAC/BIC, N=2^18, fixed key, same script/procedure as r13/r18)

| Candidate | sac_z5 | sac_maxdev | bic_maxcorr | avalanche_mean |
|---|---|---:|---:|---:|
| r19_feist6_alt_notr_fm03_nw | 0 ✓ | 0.00446 | **0.00844** | 32.0002 |
| r19_feist6_alt_notr_fm07_nw | 0 ✓ | 0.00446 | **0.00805** | 32.0001 |
| r19_feist6_alt_notr_fm11_nw | 0 ✓ | 0.00446 | **0.00976** | 32.0003 |
| r19_feist6_alt_notr_fm311_nw | 0 ✓ | 0.00446 | **0.00882** | 32.0000 |
| r19_feist6_alt_notr_chioff13_fm03_nw | 0 ✓ | 0.00359 | **0.00860** | 32.0002 |
| r19_feist6_alt_notr_chioff13_nw | 0 ✓ | 0.00376 | 0.14217 (blemish) | 31.9998 |
| r13_feist6_alt_s1chi_nw (control) | 0 ✓ | 0.00446 | 0.00800 | 31.9999 |

Reference: r18 notr bic_maxcorr = 0.17247. The control reproduces r13's 0.00800
exactly — procedure is stable across rounds.

**Objective A: ACHIEVED scientifically, missed on delay.** A single extra
XOR+rotation on the final round's output (y ^ rotl(y,m), m ∈ {3,7,11}, or the
two-rotation variant) brings bic_maxcorr from 0.172 back to the 0.008–0.0098
family norm on all five tested structures. The blemish mechanism is confirmed:
it is the unmixed final chi output, and cheap final mixing cures it. Cost:
+0.9–1.9u and +350–930 cells — none of the five reaches the ≤38.5u bar, so no
fm variant enters the frontier (all dominated by notr on implementation axes).

## S3 / S4 (chioff13 only — the one frontier-relevant candidate)

| Candidate | S3 PractRand | S4 SmallCrush |
|---|---|---|
| r19_feist6_alt_notr_chioff13_nw | 1GB clean, both configs (sequential + golden-stride, 4 stages each, no FAIL) | rc=0, BATTERY-PASS |

## Frontier decision

**r19_feist6_alt_notr_chioff13_nw ENTERS.** 37.4u / 4,149 / 11,820 with full
evidence: S0 (authorized path), S1 CAL_PASS, S2 0 repeats max|z|=11.2,
Q1 sac_z5=0, PractRand 1GB clean both configs, SmallCrush passed.
vs r18 notr (37.9 / 4,119 / 11,621): −0.5u, +30 cells, +199 area — a genuine
tradeoff, no domination either way. **Caveat (not hidden):** bic_maxcorr =
0.14217, same blemish class as notr's 0.172 (unmixed final chi on round 6;
rounds 2,4 use the chi(1,3) variant with full linear). Sub-threshold on all
gates; consistent with notr's documented status.

Frontier is now two points: {r18 notr, r19 chioff13}. RTL package updated:
`~/workspace/your_files/mix_rtl_pareto/` now holds both.

## Findings (scoped per VERDICT_SCOPE.md)

1. **The BIC blemish is curable for ~1u.** y ^ rotl(y,m) on the final round's
   output restores bic_maxcorr to 0.008–0.0098 on all five tested structures
   (fm03/07/11/311 on notr, fm03 on chioff13). Mechanism confirmed: unmixed
   final chi output. None reaches ≤38.5u (38.8–39.9u), so the cure stays off
   the frontier — but a future BIC gate now has a known-cost fix.
2. **Dropping round 5's (S1) linear is differentially fatal.** notr5's 34.9u
   passes S1 and formally passes S2, but |z| hits 477 on single-bit deltas —
   the S-box round's linear is load-bearing for diffusion, not just delay.
   Truncation is safe only on the final chi round (O15 refined: round-6
   truncation works in alt; round-5 truncation breaks it).
3. **chi(1,3) on rounds 2,4 of notr: 0.5u faster, same blemish.** chioff13
   (37.4u) inherits the unmixed-final-chi BIC blemish (0.142 vs notr's
   0.172) — the variant changes rounds 2,4, the blemish lives in round 6.
4. **(5,17) on notr: S2-cleanest of the round (|z|=4.7)** but dominated at
   38.4u. Rotation pairs move differentials far more than delay (consistent
   with r10/r14).
5. **Final-linear truncation is differentially neutral elsewhere too:**
   ps_notr reproduces parsplit's |z|=18.6, r9_notr reproduces r9's |z|=16.5
   — but both are dominated on delay (39.5u/39.9u), so truncation only pays
   in the alt structure.
6. **S1 is blind to the notr5 breakage class.** notr5 passed all four S1
   families yet has |z|=477 differentials — same screen-shape hole as the
   r13 chi6 avalanche case (S1 marginals vs single-bit-flip structure). S2's
   |z| column, not just its repeat count, is load-bearing for frontier
   claims.

## Evidence locations

- Candidates: `exploration/fast_battery/candidates/r19_*/`
- S0: `round19/s0/*.log` (RESULT lines; ref mul 103.5u); S1: `round19/s1/*.log`
- S2 logs: `round19/s2_r19_*.log`, progress `round19/progress.log`
- Q1: `round19/q1/q1_*.json` (script: `round13/q1_sacbic.py`, same procedure)
- chioff13 battery: `round19/battery_r19_feist6_alt_notr_chioff13_nw.log`
- Frontier RTL: `~/workspace/your_files/mix_rtl_pareto/`

## Process notes

1. Generator bug caught by structural RTL review before the battery: the
   generic round if-chain emitted a stray `end` before `else if`
   (unbalanced block). Fixed; all 10 RTLs parse in iverilog. (Same class as
   the r8 cross-process read — review the emitted RTL, not just the
   generator.)
2. The fm rounds bake rk32 into `t` (y = chi^rk before the extra rotation),
   so V_RK_STD runs before the round if-chain and the tail conditionally
   skips ^rk32 on fm rounds. xcheck/rtlcheck passed 10k/300 first try on the
   novel convention.
3. Mid-round 10th candidate (chioff13_fm03) added on Q1 evidence: the fastest
   structure × the BIC fix. 39.5u — the combination doesn't beat fm07's
   38.8u; recorded, dominated.
4. S2 kill threshold verified = 10 at the ref file
   (`fast_battery/ref/s2_kill_repeats.txt`).
5. Dedupe: all 10 specs pairwise-distinct by numpy model output before
   generation. r19 notr-family cross-checked bit-identical to r18's notr
   model before emission.
6. No VM reboot this round; per-candidate progress logs + resume scripts in
   place regardless.
