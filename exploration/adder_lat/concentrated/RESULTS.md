# Concentrated XIG — Results (O158)

## Design
f_i(x) = x_i XOR g_i(x), i=0..63.
g_i: 8-input, degree-5, NL=112 (from degree-5 search).
Wiring variants tested for Fisher's 6-bit cubes (LIN) and 18 deltas (DIFF).

## Results

| Variant | S0 | Bijectivity | LIN | DIFF | Verdict |
|---------|----|-------------|-----|------|---------|
| V1: concentrated (bits 0-5) | 9.4u | PASS (10M) | FLAG D=4096/4096 | FLAG 739994 | FAIL |
| V2: balanced (bits 0-17) | — | — | FLAG D=4096/4096 | FLAG 368540 | FAIL |
| V3: diverse ANFs | — | — | FLAG D=4096/4096 | FLAG 461404 | FAIL |

## Analysis

**S0 9.4u** (under 10u), **bijective** (10M/10M), **degree 5**, **NL=112 primitives**.
Yet Fisher fails maximally on LIN (D=4096/4096 = every 6-bit cube rank-deficient).

### Why degree-5 doesn't save us

For f(x)=x⊕g(x) on a 6-bit cube:
- x contributes 6 dimensions.
- g(x) must contribute 58 more (for rank ≥62).
- Each g_i sees ≤8 inputs, of which ≤6 vary.

The 64 g_i outputs are vectors in {0,1}^64. For them to span 58 dimensions,
they must be highly diverse. But:
1. All g_i use similar ANFs (even with term-subset diversity, the structure is similar).
2. Each g_i depends on only 6 varying bits → the space of distinct behaviors is limited.
3. The XIG form f_i = x_i ⊕ g_i means the linear part x_i is *always present*,
   creating a strong linear component that the nonlinear g_i cannot overcome.

### The DIFF clue

V1 DIFF worst|z| = 739994, identical to R1's 739994. V2 (better 0-17 coverage)
improved to 368540. This confirms DIFF is about *input coverage* of the 18
deltas, while LIN is about *rank* on 6-bit cubes. Fixing coverage helps DIFF
but not LIN.

### Fundamental blocker

The DAG-optimizer's conclusion stands: **6 varying bits cannot generate 58
independent nonlinear dimensions through 8-input degree-5 functions in the
XIG form.** The linear x_i term dominates. To beat LIN, we need a construction
where the *nonlinear* part contributes the majority of dimensions, not the
linear part.

This suggests abandoning XIG (f = x ⊕ g) for a fully nonlinear f where *every*
output bit is a strong nonlinear function (no linear passthrough).

## Verdict: O158 TERMINAL

Concentrated degree-5 XIG fails Fisher. The XIG form itself may be the problem:
the linear x_i term guarantees 6 dimensions but caps the nonlinear contribution.

## Artifacts
- `model.py` — Python model with 3 wiring variants
- `conc_xig.v` — Verilog (V1 wiring)
- `s0_conc/` — S0 synthesis (9.4u)
- `fisher_conc.json` — Fisher results (V3)
- `run_fisher.py` — Fisher runner
