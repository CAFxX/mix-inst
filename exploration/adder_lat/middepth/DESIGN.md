# MID-DEPTH DESIGN — 3-stage and 4-stage sub-10u exploration (track-3, 2026-10-12)

## Mandate (Carlo's critique)

We tested 2-stage (Fisher-dead, O135) and 5-stage (18.6u, too slow) but NEVER 3-stage or 4-stage.
That's the gap. This document scopes the missing middle.

## Cost model (measured, not estimated)

| Stage type | Per-stage cost | Source |
|---|---|---|
| 4-bit S-box (Midori Sb0) | 3.0u | O135 Prong B measurement |
| MUXD stage (5-round family) | ~3.7u | 18.6u / 5 stages |
| MUXD stage (2-stage) | ~4.8u | 9.6u / 2 stages (sub10/muxd2.v) |
| 4-term rotl-xor linear | ~2-3u | w4term DESIGN.md (2 XOR levels) |
| L32 linear | 8.5u | O139 Prong A — TOO EXPENSIVE, excluded |
| MUX2 gate | 2.0u | O138 Prong B — fastest balanced 3-bit gate |

## Budget analysis

**3-stage:**
- 3 × S-box (3.0u) = 9.0u + linear layers (~1u) = ~10u. BORDERLINE.
- 3 × MUXD (3.7u) = 11.1u. OVER BUDGET (unless stages compress).
- S-box + MUX + S-box = 3.0 + 3.7 + 3.0 = 9.7u + linears. VERY TIGHT.

**4-stage:**
- 4 × MUX2 (2.0u) = 8.0u + interconnect. FITS with margin.
- 4 × S-box (3.0u) = 12.0u. OVER BUDGET.
- Mixed 2×S-box + 2×MUX2 = 6.0 + 4.0 = 10.0u. BORDERLINE.

**Key insight:** The MUX2 gate at 2.0u is the enabler. 4 MUX2-based stages = 8.0u leaves 2u for
interconnect/diffusion. The 4-bit S-box at 3.0u is too expensive for 4 stages but viable for 3.

## Variants to explore

### V1: 3-stage SPN (4-bit S-box)
Structure: S-box → linear → S-box → linear → S-box → linear (final).
Linear options: 4-term rotl-xor (DIFF-clean), PRESENT P-box (wiring only), rotation-XOR.
- S0 first. If >10u, kill. If ≤10u, Fisher-triage.

### V2: 3-stage MUXD (fresh rotations)
Structure: 3 MUX stages, rotations drawn fresh (NOT the 5-round ones — those were optimized
for 5-round security, 2-stage got 0/200).
Stage form (from t6_b59_47 family):
  `g = (rotl(x,s) & rotl(x,a)) | (~rotl(x,s) & rotl(x,b)); x = x ^ g ^ rotl(x,d)`
- S0 first (expect ~11u — may need stage compression). Fisher-triage if ≤10u.

### V3: 4-stage MUX2 network
Structure: 4 stages of parallel MUX2 gates (2.0u each), wide/parallel per Carlo's steer.
Each stage: 64 parallel MUX2, select bits from key + input.
- Target: 8.0u + interconnect < 10u. Fisher-triage.

### V4: 4-stage hybrid
Options:
- S-box → MUX2 → S-box → MUX2 (3.0+2.0+3.0+2.0 = 10.0u, borderline)
- MUX2 → 4-term linear → MUX2 → 4-term linear (2.0+2.5+2.0+2.5 = 9.0u)
- S-box → 4-term → MUX2 → 4-term (3.0+2.5+2.0+2.5 = 10.0u, borderline)

## Escalation rules (pre-registered)

1. S0-measure the STAGE first. If stage > budget/stages, kill the variant before building.
2. Build full candidate, S0-measure. If >10u strict, kill (no Fisher).
3. If ≤10u, Fisher-triage with `lin_diff.screen_lin_diff` verbatim.
4. If Fisher passes, bundle + battery per standard gates (S1→S4, Q1).
5. Record verdict in VERDICT_SCOPE.md (O140+).

## Dual-measurement calibration (2026-10-12, from synth/DUAL_MEASURE.md)

Real silicon targets (all measured):
- Sky130 HD adder: 2.0943 ns | HS adder: 1.4428 ns (HS 31% faster, 30% more area)
- t6_b59_47 (18.6u): 0.4993 ns (HD), 0.3790 ns (HS) — HS 24% faster

Re-expressed <10u/<8u goals:
- HD: <0.252 ns (<10u-equiv), <0.202 ns (<8u-equiv)
- HS: <0.174 ns (<10u-equiv), <0.139 ns (<8u-equiv)

**Protocol:** Keep using unit-delay S0 for screening (fast, ratios hold — HD within 12%).
For any candidate that passes Fisher AND is under 12u unit-delay, ALSO run
`synth/run_synth_hs.py` for the HS number. The HS flow is Carlo's "optimized layout."

The gap is ~2× in HD, ~2.2× in HS. HS headroom (24-31%) helps but doesn't close it alone.

## Positive artifacts to reuse

- 2.0u MUX2 gate (Prong B, O138)
- 4-term linear DIFF-clean (w4term, O134)
- MUXD stage structure from t6_b59_47 (but fresh rotations)
- `lin_diff.screen_lin_diff` from `fast_battery/src/`
- `run_synth.py` for S0
