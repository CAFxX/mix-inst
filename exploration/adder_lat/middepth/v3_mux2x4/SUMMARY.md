# V3 4-stage MUX2 network — Worker V3 summary (2026-10-12)

## Verdict: TERMINAL (O148)

4-stage MUX2 network is **cost-eligible (9.4u < 10u)** but **structurally incapable
of Fisher-passing diffusion**. Extends O135 to the MUX2-network primitive class.

## Measured results

| Gate | Result |
|---|---|
| S0 pure 64×MUX2 stage | **2.0u** (64 MUX2 cells; confirms O138) |
| S0 1-stage + key xors | 5.2u (ABC maps to 384 NOR2 + 64 XOR2) |
| S0 full 4-stage (+key xors, muxd2.v convention) | **9.4u** (1408 cells) — UNDER 10u |
| Fisher base (verbatim `screen_lin_diff`, 10 keys) | LIN FLAG D=4096/4096 rej=10; DIFF FLAG \|z\|~1e6 rej=10 |
| Control MU5-324 | lin=PASS diff=PASS (harness valid) |
| ~20 wiring variants (focused/graded) | ALL fail LIN+DIFF |
| 3-stage MUX2 + 2-term linear (task fallback) | LIN/DIFF FLAG |
| Avalanche (base) | 4.2 bits mean |

## Structural mechanisms

**DIFF (counting bound):** 64 MUX2/stage = 192 input slots; each slot propagates a
single-bit flip w.p. ≤1/2 → E[flips] ≤1.5×/stage for ANY wiring (slots conserved).
1.5^4 ≈ 5-bit avalanche ceiling vs ~25+ needed. No pattern escapes.

**LIN (diffusion, not nonlinearity):** 64 consecutive outputs vary only 6 input bits;
base has 54/64 outputs CONSTANT across LIN blocks (rotation cones miss low-6).
Even 64/64-varying wirings are rank-deficient.

## Files

- [v3_model.py](v3_model.py) — bit-exact vectorized model (verified vs scalar)
- [gen_v3.py](gen_v3.py) / [gen_v3_focus.py](gen_v3_focus.py) — Verilog generators
- [v3_fisher.py](v3_fisher.py) — verbatim Fisher triage
- [v3_focus.py](v3_focus.py), [v3_sweep.py](v3_sweep.py), [v3_sweep2.py](v3_sweep2.py), [v3_sweep3.py](v3_sweep3.py) — wiring variants
- [v3_calib.py](v3_calib.py) — avalanche calibration
- `s0_stage1.log`, `s0_v3x4.log`, `s0_pure1.log`, `fisher_base.log`, `fisher_BASE.json`, `control.log`

## Re-test trigger

A ≤2u nonlinear gate with >2×/stage confusion growth, or a feedthrough
mechanism costing <1u.
