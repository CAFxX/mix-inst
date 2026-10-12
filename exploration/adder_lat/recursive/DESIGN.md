# Recursive `(a⊕b)⊕(c&d)` — Design Document

Carlo's idea (2026-10-12): apply the optimal 4-input 2-layer function recursively 3 times.

## The Math

**Primitive**: `f(a,b,c,d) = (a⊕b)⊕(c&d)`
- 2 levels: L1 (XOR2, AND2 parallel), L2 (XOR2).
- 3.6u (1.8 + 1.8). NL=4 (optimal for balanced 4-input, proven).
- Degree 2. Balanced.

**Recursive composition** (3 stages, 64 parallel per stage):

| Stage | Degree | Max inputs/output | Levels | Cumulative u |
|-------|--------|-------------------|--------|--------------|
| 1 | 2 | 4 | 2 | 3.6u |
| 2 | 4 | 16 | 4 | 7.2u |
| 3 | 8 | 64 | 6 | 10.8u |

Degree 8 ≥ 5 (satisfies XIG LIN bound!). 64 inputs/output (full diffusion possible!).

## The Bijectivity Problem

Three stages of parallel 4→1 functions are **not automatically bijective** 64→64.

**Options:**
1. **XIG per stage**: `y_i = x_{p(i)} ⊕ g_i(...)`. Adds 1 level/stage → 9 levels total → 16.2u. **Over budget.**
2. **Prove specific wiring bijective**: Hard in general.
3. **Test and adjust**: Build with structured wiring, test 10M pairs. If bijective, proceed. If not, try different wiring.

**Plan**: Start with option 3. Use wiring that maximizes disjointness:
- Stage 1: output i takes inputs (i, i+16, i+32, i+48) with roles (a,b,c,d) = (i, i+16, i+32, i+48).
  - Actually, for `(a⊕b)⊕(c&d)`: a,b go to XOR; c,d go to AND.
  - Wiring: a=i, b=i+16, c=i+32, d=i+48 (mod 64).
- Stage 2: output i takes 4 Stage-1 outputs with disjoint input sets.
  - Stage-1 output j depends on {j, j+16, j+32, j+48}.
  - For Stage-2 output i to have 16 distinct inputs, need j1,j2,j3,j4 such that their 4-sets are disjoint.
  - j, j+16, j+32, j+48 are disjoint? {j,j+16,j+32,j+48} vs {k,k+16,k+32,k+48}: disjoint iff j≠k mod 16.
  - So take j = i, i+1, i+2, i+3 (mod 16, plus high bits to make 64).
  - Simpler: Stage-2 output i takes Stage-1 outputs (i, i+4, i+8, i+12) — need to verify disjointness.
- Stage 3: Similar.

**If structured wiring fails bijectivity**, try random wirings. If none work, fall back to proving or XIG.

## Designs

### R1: 3-stage `(a⊕b)⊕(c&d)`
- Expected: 10.8u, degree 8, 64 inputs/output.
- Risk: Over 10u budget. Bijectivity unproven.

### R2: 3-stage `(a&b)⊕c` (cheaper)
- Primitive: 2 levels, 3 inputs, 2.8u (1.0 AND + 1.8 XOR).
- 3 stages: 8.4u, degree 8, up to 27 inputs/output (3^3).
- Lower input count but under budget with margin.

## Test Plan

1. Python simulator for fast bijectivity testing (10M pairs).
2. If bijective: generate Verilog, run S0.
3. If S0 <10u (R1) or <9u (R2): run Fisher `lin_diff.screen_lin_diff`.
4. Record verdict in VERDICT_SCOPE.md.

## Results (2026-10-12)

### R1 Hierarchical — O157 TERMINAL

**Wiring** (Carlo's hierarchical, guarantees 64-input coverage):
- Stage 1: out[i] = (x[i]^x[i+1]) ^ (x[i+2]&x[i+3])
- Stage 2: out[i] = (s1[i]^s1[i+16]) ^ (s1[i+32]&s1[i+48])
- Stage 3: out[i] = (s2[i]^s2[i+4]) ^ (s2[i+8]&s2[i+12])

**Verified:**
- All 64 Stage-3 outputs depend on ALL 64 inputs (by construction, verified via input-set computation).
- Bijective: 0 collisions in 500k random pairs.
- S0: 9.8u (1984 cells) — UNDER 10u!

**Fisher:** FLAG on both.
- LIN: D=4096/4096 (maximum failure).
- DIFF: worst|z|=739994.3.

**Mechanism:** Despite degree 8 and full input dependence, the recursive XOR structure creates linear relations that persist on sequential inputs. The (a⊕b)⊕(c&d) form has too much XOR — the nonlinear AND terms cancel or don't activate sufficiently for the 6-bit cube. Degree alone is insufficient; the *structure* matters.

### R2 — Not pursued

Initial bijectivity test with structured wiring showed collisions (5 in 200k). Given R1's catastrophic Fisher failure despite superior parameters (degree 8, 64 inputs), R2 (degree 8, 27 inputs) was deprioritized per task instructions ("prioritize R1").
