# Round 4 — HYBRID Track Results (Heterogeneous Compositions)

**Date:** 2026-10-01
**Direction:** Actively explore hybrids/cross-combinations of primitives, not just
pure-family candidates.

**Gates (same as main track):**
- Delay bar: ≤44.3 absolute unit-delays (0.9× remeasured 64×64 multiplier ref 50.8)
- Bijective per fixed key (structural proof + spot-check)
- Calibrated statistical screen: Fisher-combined p + Holm-Bonferroni α=0.01; zero rejections = CAL_PASS
- Pipelinable, 1 result/cycle; area ≤1–2× multiplier

## 🏆 Winner: h_xorspn3

**xorshift64 pre-diffusion + 3-round SPN** (S1 S-box + Midori M + ShuffleCell)

| metric | value | gate |
|--------|-------|------|
| Delay | 34.5 (0.679× mult) | ✅ 9.8u under bar |
| Cells | 3893 (0.218× mult) | ✅ |
| Calibrated screen | **CAL_PASS** (0/468 rej) | ✅ |
| Bijectivity | structural + 600k spot-check | ✅ |
| Raw screen | max\|z\|=4.36 (FLAG→calibrated PASS) | n/a |

**Composition:** `xorshift64(val^key)` → 3× `(xor rk, 16×S1-DNF, Midori M, ShuffleCell)` → whitening.
The xorshift* multiply is replaced by a 3-round SPN (per the direction's
"xorshift* where the multiply constant is replaced by an SPN" — 3 rounds were
needed; 2 rounds failed with 146 rejections).

**Why it works:** xorshift provides cheap, provably-bijective pre-diffusion
(~6u); the SPN rounds supply the nonlinearity (S1) and strong mixing (Midori
M). The combination reaches statistical cleanliness at 3 SPN rounds while
staying 9.8u under the delay bar.

## Candidate table (all 10 hybrids)

| name | composition | delay | ×mult | cells | delay gate | calibrated | verdict |
|------|-------------|-------|-------|-------|------------|------------|---------|
| h_sandwich2 | S1 + triangular-χ + rotl, 2rd SPN | 18.9 | 0.372 | 2388 | PASS | FLAG (310 rej) | REJECT |
| h_xorspn | xorshift + 2rd SPN(S1+Midori) | 25.9 | 0.510 | 2942 | PASS | FLAG (146 rej) | REJECT |
| h_sandwich3 | S1 + triangular-χ + rotl, 3rd SPN | 26.5 | 0.522 | 3683 | PASS | FLAG (310 rej) | REJECT |
| h_clmulspn | clmul(odd) + S1 + rotl, 2rd SPN | 34.2 | 0.673 | 3580 | PASS | FLAG (303 rej) | REJECT |
| **h_xorspn3** | **xorshift + 3rd SPN(S1+Midori)** | **34.5** | **0.679** | **3893** | **PASS** | **CAL_PASS (0 rej)** | **🏆 WINNER** |
| h_chifeist6 | cyclic-χ as F, 6rd Feistel | 37.0 | 0.728 | 3168 | PASS | FLAG (310 rej) | REJECT |
| h_heterofeist | Feistel, alternating S1-F / χ-F, 6rd | 40.3 | 0.793 | 3344 | PASS | FLAG (310 rej) | REJECT |
| h_laimassey | Lai-Massey + 16-bit mult F, 3rd | 47.5 | 0.935 | 9324 | OUT | — | REJECT |
| h_multspn | 64b mult(odd) → 2rd SPN | 65.8 | 1.295 | 12409 | OUT | — | REJECT |
| h_spnmult | 2rd SPN → 64b mult(odd) squeeze | 67.2 | 1.323 | 13630 | OUT | — | REJECT |

All 10: scalar==vectorized OK; bijectivity spot-check OK (600k samples, no
collisions); RTLCHECK 40/40 PASS.

## Composition notes

- **h_sandwich2/3**: Blink S1 S-box inside a triangular χ-like layer sandwich
  (`S1 → tchi64 → ROTL13`). tchi64 is *provably* bijective by back-substitution
  (y[i]=x[i]^((~x[i+1])&x[i+2]), top 2 bits pass through). Fast (9.5u/round)
  but the triangular χ diffuses too weakly upward — 3 rounds still fail.
- **h_chifeist6**: χ-like nonlinear layer as the F-function of a 6-round
  Feistel (F need not be bijective in Feistel). Fails: χ-F is too weak even at
  6 rounds.
- **h_multspn / h_spnmult**: single masked 64-bit multiply (odd constant)
  feeding / fed by 2 SPN rounds. REJECT on delay: the 64-bit constant
  multiplier alone is ~40u in this flow — the multiply dominates and blows
  the bar before the SPN even starts.
- **h_clmulspn**: carry-less multiply (odd C, GF(2)-linear bijection) + S1
  S-box + rotation, 2 rounds. clmul is cheap (~10u) but 2 rounds insufficient.
- **h_laimassey**: Lai–Massey with 16-bit multiplier F-functions
  (F(z)=(z_lo*C1)^(z_hi*C2)^ROTL(z,9)) wrapped in xor-linear structure,
  3 rounds. 47.5u — just over the bar; the 32-bit F is too heavy.
- **h_xorspn / h_xorspn3**: xorshift* state update with the multiply replaced
  by a 2-round (fails, 146 rej) / 3-round (**passes**) SPN. The winner.
- **h_heterofeist**: Feistel halves with different F-functions per round
  (even rounds: S1 S-box layer; odd rounds: cyclic χ). Fails like chifeist6 —
  the χ rounds drag it down.

## Pareto delta (hybrid track vs. round-4 best, updated 13:57)

Round-4 pure-family screens are now complete (2026-10-01 13:57): blink3
REJECT (170 pb rej), midori3 REJECT (186 pb rej), blink4 FLAG with a single
red-cell rejection (0/384 perbit rej, raw max|z|=4.0/6.2 — borderline,
re-screen candidate).

```
delay (u)   hybrid                          round-4 pure
 18.9       h_sandwich2 (REJECT-stat)        —
 25.9       h_xorspn (REJECT-stat)           —
 26.5       h_sandwich3 (REJECT-stat)        —
 29.0        —                               blink3 (REJECT-stat)
 31.0        —                               midori3 (REJECT-stat)
 34.2       h_clmulspn (REJECT-stat)         —
 34.5       h_xorspn3 🏆 (CAL_PASS)          —
 36.8        —                               blink4 (FLAG: 1 red cell)
 37.0       h_chifeist6 (REJECT-stat)        —
 40.3       h_heterofeist (REJECT-stat)      —
```

**Delta:** The hybrid track produced the **first and still only candidate to
clear both hard gates** (h_xorspn3: 34.5u + CAL_PASS). Even if blink4's single
red-cell flag proves a fluke on re-screen, h_xorspn3 beats it on both delay
(34.5 vs 36.8) and area (3893 vs 5138 cells).

## Key lessons

1. **2 rounds is never enough** for the calibrated screen, regardless of
   primitive cleverness (sandwich, clmul, xorshift+SPN all fail at 2 rounds).
2. **χ-like layers are weak mixers** here: triangular χ (even 3 rounds +
   S-boxes) and cyclic-χ Feistel (6 rounds) both fail catastrophically.
   The χ nonlinearity is too "thin" (quadratic, low diffusion per round).
3. **64-bit multiplies blow the delay bar** (~40u for the multiplier alone).
   Multiplier hybrids are structurally incompatible with ≤44.3 unless the
   multiply is 16/32-bit or the SPN is 0-1 rounds (which then fails stats).
4. **xorshift + SPN is the sweet spot**: xorshift gives ~6u of provable
   bijective pre-diffusion; 3 SPN rounds finish the job at 34.5u total.
5. **DNF S-boxes remain critical**: all SPN hybrids reuse the 4.6u
   Quine-McCluskey-minimized S1.

## Bugs fixed (hybrid track)
1. **Midori M nibble mapping**: my generator computed `y[4c+i] = XOR of
   three *including* self` instead of *excluding* self. Caught by check_rtl
   mismatch; fixed to match the model (`out[i] = parity ^ in[i]`).
2. **iverilog `for`-loop part-selects**: unrolled Midori M explicitly.
3. **Wrong clmul constant parity**: `0xA5..A5 ^ 0x1` is even; fixed to
   `0xA5A5A5A5A5A5A5A7` (odd, bijective).
4. **Screen verdict key**: `screen_calibrated` returns `cal_verdict`, not
   `cal_pass` — my launcher printed REVIEW for a true CAL_PASS; the log's
   `calibrated: CAL_PASS (rej 0, 0)` is authoritative.

## Files
- Models: `round4/models/r4_hybrid.py` (numpy + scalar, self-test on run)
- RTL: `round4/rtl/flat2/r4_h_*.v` (10 files, flat unrolled)
- Generator: `round4/gen_hflat.py`
- Batch: `round4/run_batch_h.py`, `round4/batch_h.log`
- Screens: `round4/results/screen_h_*.log`

## Open items
- h_xorspn3 → finalist battery: 2-stage pipeline, PractRand/Dieharder/TestU01,
  Sky130 P&R (same as round-3 finalist protocol)
- blink4 re-screen with more keys/samples (single red-cell flag to resolve;
  currently CAL_FLAG by the zero-rejection rule)
- Multiplier hybrids could be revisited with 32-bit multiplies if the
  64-bit cost remains prohibitive
