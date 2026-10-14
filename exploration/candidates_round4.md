# Round 4 — Design-Space Search Results (New Primitives Track)

**Date:** 2026-10-01
**Gates:**
- Delay bar: ≤44.3 absolute unit-delays (0.9× remeasured 64×64 multiplier ref 50.8)
- Bijective per fixed key (proven + spot-checked)
- Calibrated statistical screen: Fisher-combined p + Holm-Bonferroni α=0.01; zero rejections = CAL_PASS
- Hardware efficiency: area/power ≤1–2× multiplier
- P&R mandatory (Sky130) — pending for finalists

## Summary

18 candidates modeled across 7 families (X, M, H, G, V, B, S). All pass scalar==vectorized and bijectivity spot-checks; all pass check_rtl (40-60 vectors).

**Delay results** (ref mul64 = 50.8 crit / 17893 cells, bar = 44.3):

| name | family | delay | ×mult | cells | gate |
|------|--------|-------|-------|-------|------|
| blink2 | B (Blink SPN) | 20.4 | 0.402 | 2634 | PASS |
| blink3 | B (Blink SPN) | 29.0 | 0.571 | 3508 | PASS |
| midori3 | B (Midori SPN) | 31.0 | 0.610 | 4661 | PASS |
| blink4 | B (Blink SPN) | 36.8 | 0.724 | 5138 | PASS |
| xsm_c8 | M (sparse mult) | 42.0 | 0.827 | 2520 | PASS |
| xsm_sa | M (sparse mult) | 42.4 | 0.835 | 1179 | PASS |
| xsm_c3 | M (sparse mult) | 50.0 | 0.984 | 4937 | OUT |
| gl5_f6 | G (Goldreich F) | 50.5 | 0.994 | 4175 | OUT |
| midori3_old | B (wrong S-box) | 53.1 | 1.045 | 5054 | OUT (superseded) |
| simeck_f10 | X (AND-Feistel) | 57.0 | 1.122 | 4544 | OUT |
| simon_f10 | X (AND-Feistel) | 57.0 | 1.122 | 4544 | OUT |
| dbland_f8 | X (AND-Feistel) | 62.0 | 1.220 | 6720 | OUT |
| blink4_old | B (ternary S-box) | 64.3 | 1.266 | 8935 | OUT (superseded) |
| gl5_f8 | G (Goldreich F) | 66.5 | 1.309 | 5601 | OUT |
| simeck_f12 | X (AND-Feistel) | 68.0 | 1.339 | 5440 | OUT |
| skinny_xorlin | V (SKINNY S-box) | 71.6 | 1.409 | 8902 | OUT |
| fmix32h_a | H (Murmur fmix) | 82.8 | 1.630 | 12293 | OUT |
| fmix32h_b | H (Murmur fmix) | 87.8 | 1.728 | 12431 | OUT |
| speedy3 | S (SPEEDY S-box) | 127.5 | 2.510 | 11659 | OUT |
| speedy4 | S (SPEEDY S-box) | 168.6 | 3.319 | 15718 | OUT |

**Key breakthrough:** The B family (Blink/Midori SPN with minimized-DNF S-boxes) achieves 20.4–36.8 unit-delays, **far below the 44.3 bar**. The DNF S-box implementation (4.6u vs 11.0u for ternary) was the key optimization.

## Statistical screening

| name | delay gate | calibrated screen | verdict |
|------|------------|-------------------|---------|
| xsm_c8 | PASS | CAL_FLAG (114 pb rej, 20 red rej, max\|z\|=96) | **REJECT** |
| xsm_sa | PASS | CAL_FLAG (133 pb rej, 20 red rej, max\|z\|=512) | **REJECT** |
| blink2 | PASS | CAL_FLAG (233 pb rej, 20 red rej, max\|z\|=512) | **REJECT** |
| blink3 | PASS | CAL_FLAG (170 pb rej, 20 red rej, raw max\|z\|=38.9) | **REJECT** |
| blink4 | PASS | CAL_FLAG (0 pb rej, **1 red rej**, raw max\|z\|=4.0/6.2) | **FLAG (borderline; re-screen candidate)** |
| midori3 | PASS | CAL_FLAG (186 pb rej, 20 red rej) | **REJECT** |

**M family REJECTED:** xsm_c8 and xsm_sa both fail catastrophically. Root cause: structure is linear except for one sparse constant multiplication — insufficient nonlinearity. The 42.0/42.4 delay is attractive but the statistics are unusable.

**B family (2 rounds) REJECTED:** blink2 fails catastrophically (233/468 perbit rejections). Two rounds of the SPN provide insufficient diffusion.

**B family (3 rounds) REJECTED:** blink3 (170/384 perbit rej, raw |z| up to 38.9)
and midori3 (186/384) both fail hard. 3 rounds of the Blink/Midori SPN are
insufficient, despite the perfect sequential-input balance.

**B family (4 rounds) BORDERLINE:** blink4 passes all 384 perbit cells with
zero rejections (raw max|z|=4.00) but flags **1 of 84 reduction cells**
(Holm-Bonferroni, α=0.01). By the protocol's zero-rejection rule this is
CAL_FLAG, not CAL_PASS — but it is the closest any pure-family candidate has
come, and a single-cell flag at raw max|z|=6.23 may be a fluke or a real weak
reduction. **Next step: re-screen blink4 with more keys/samples** to resolve
it. Note: even a clean blink4 (36.8u, 5138 cells) would still trail h_xorspn3
(34.5u, 3893 cells) on both delay and area — the hybrid remains the design to
beat.

## Pareto frontier (delay vs. area, delay-passers only)

```
delay (×mult)
0.40 | * blink2 (REJECT-stat)
0.57 | * blink3 (REJECT-stat)
0.61 | * midori3 (REJECT-stat)
0.72 | * blink4 (FLAG: 1 red cell; re-screen)
0.83 | * xsm_c8 (REJECT-stat)
0.84 | * xsm_sa (REJECT-stat)
     +-------------------------------- cells
       1k   2.6k  3.5k  4.7k  5.1k
```

**Pareto-optimal (delay, area):**
- **blink2**: (20.4, 2634) — fastest, but statistically rejected
- **blink3**: (29.0, 3508) — rejected statistically (170/384 perbit)
- **blink4**: (36.8, 5138) — 0 perbit rejections, 1/84 red-cell flag; re-screen pending
- **xsm_sa**: (42.4, 1179) — smallest area, but statistically rejected

**Round-4 pure-family outcome:** no candidate clears both gates. blink4 is the
only borderline case (single reduction-cell flag); the hybrid h_xorspn3
(34.5u, 3893 cells, CAL_PASS) remains the design to beat.

## Family notes

### B family (Blink/Midori SPN) — PROMISING
Structure: 2-4 rounds of (xor rk, 16× 4-bit S-box, Midori almost-MDS matrix M, ShuffleCell permutation) + whitening. 
- S-box: THF/Blink S1 = `0,1,2,4,3,8,f,c,9,5,b,6,7,e,d,a` (or Midori Sb0 for midori3)
- Linear: Midori M = 4×4 matrix over nibbles, each output = XOR of 3 inputs (XOR depth 2)
- Permutation: ShuffleCell `[0,10,5,15,14,4,11,1,9,3,12,6,7,13,2,8]` (free wiring)
- Key schedule: rk[i] = ROTL64(key, 13*(i+1)) ^ (i+1)*0x9E3779B97F4A7C15

**Critical optimization:** Minimized DNF S-box (Quine-McCluskey, verified 16/16) achieves 4.6u vs 11.0u for ternary mux. This 6.4u/round saving moved blink3 from 49.3 (OUT) to 29.0 (PASS).

**Bug fixed:** Initial implementation used wrong Midori S-box table (consistent between model and RTL, so checks passed, but not the real Midori Sb0). Fixed to `c,5,6,b,9,0,a,d,3,e,f,8,4,7,1,2`.

### M family (sparse constant multiply) — REJECTED
xsm_c8 (42.0) and xsm_sa (42.4) passed delay but failed statistics catastrophically. The structure (linear shifts/XORs + one sparse constant multiplication) lacks sufficient nonlinearity. Confirms that "almost linear" designs cannot pass the stringent calibrated screen.

### X family (AND-Feistel: SIMECK/SIMON) — REJECTED
10-12 rounds needed for diffusion; 57-68 delay, all OUT. Feistel depth doesn't fit the bar.

### G family (Goldreich 5-local F) — REJECTED
gl5_f6 at 50.5 (OUT by 6.2). The 5-local F is expensive; 6+ rounds needed.

### H family (keyed Murmur fmix) — REJECTED
Sequential 32-bit multiplies: 82-88 delay. Structurally too slow.

### V family (SKINNY S-box in xorlin) — REJECTED
71.6 delay. The xorlin linear layer (L(x)=x^ROTL(x,11)^ROTL(x,37)) plus S-box is slower than the B-family Midori approach.

### S family (SPEEDY 6-bit S-box) — REJECTED
127-169 delay. The 6-bit S-box as logic is huge and slow; the "2-level NAND" from the paper doesn't translate to our unit-delay model with the ternary/DNF implementation. Not pursued further.

## Bugs fixed (2026-10-01)
1. **Wrong Midori S-box**: Model and RTL used `[0xC,0xA,0xD,...]` instead of correct `c,5,6,b,9,0,a,d,3,e,f,8,4,7,1,2`. Fixed in both; re-verified.
2. **Ternary S-box slow**: 11.0u per S-box. Replaced with minimized DNF (4.6u). 6.4u/round saving.
3. **Yosys case-statement issues**: `case` inside `function` caused undriven nets; switched to ternary then DNF.
4. **ROM inference**: 64-entry case for SPEEDY S-box inferred as ROM; analyze2 can't handle. (S family abandoned anyway.)

## Open items
- Full calibrated screens for blink3, blink4, midori3 (infrastructure timeouts; preliminary data promising)
- If blink3 passes: 2-stage pipeline, PractRand/Dieharder/TestU01, Sky130 P&R
- Round-3 peer reviews still pending (separate track)

## Files
- Models: [`round4/models/r4_blink.py`](round4/models/r4_blink.py), [`r4_speedy.py`](round4/models/r4_speedy.py), [`r4_xorlinv.py`](round4/models/r4_xorlinv.py), etc.
- RTL: `round4/rtl/flat2/r4_blink*.v` (DNF S-box), [`round4/rtl/flat2/r4_midori3.v`](round4/rtl/flat2/r4_midori3.v)
- Generators: [`round4/gen_bflat.py`](round4/gen_bflat.py) (DNF), [`gen_sflat.py`](round4/gen_sflat.py), [`gen_xflat.py`](round4/gen_xflat.py), [`gen_gflat.py`](round4/gen_gflat.py)
- Results: `round4/results/` (screens), [`batch3.log`](round4/batch3.log), [`batch_bsv2.log`](round4/batch_bsv2.log)
