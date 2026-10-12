# Decomposition design: f_i = l_i ⊕ n_i (O149 track)

## Goal

64 Boolean functions f_1..f_64, each 64→1 bit, such that F(x)=(f_1(x),..,f_64(x))
is bijective, Fisher LIN+DIFF passing, total depth <10u (target <8u).

## Decomposition

Write each function as:

    f_i(x) = l_i(x) ⊕ n_i(x)

- **l_i**: linear (XOR of input bits). The 64 l_i form L: {0,1}^64→{0,1}^64,
  a bijective linear map. Designed for **diffusion + bijectivity**.
- **n_i**: nonlinear, 2-level AND-XOR. The 64 n_i are **arbitrary** — no
  bijectivity constraint. Designed for **nonlinearity (LIN resistance)**.

The two dimensions are solved **independently**, then XOR-combined.

## Depth analysis (no added levels)

L and N are computed **in parallel**:

```
x ──┬──► L (XOR trees) ──┐
    │                     ├──► XOR ──► F(x)
    └──► N (AND-XOR) ────┘
```

- depth(L) = 2 XOR levels (weight-3 pattern) ≈ 3.6u
- depth(N) = 1 AND level + 2 XOR levels ≈ 1.0 + 3.6 = 4.6u
- merge = 1 XOR level ≈ 1.8u
- **total = max(3.6, 4.6) + 1.8 = 6.4u** < 10u ✓ (headroom for <8u tuning)

The merge XOR overlaps with N's output XOR tree: f_i is just a wider XOR
of (L terms + N AND-terms). No sequential penalty.

## Bijectivity

F(x) = L(x) ⊕ N(x), L invertible linear.

Apply L^{-1}: H(x) := L^{-1}(F(x)) = x ⊕ L^{-1}(N(x)) =: x ⊕ G(x).

- F bijective ⟺ H bijective (L^{-1} is a bijection).
- H is in XIG form. G = L^{-1}∘N is nonlinear (linear ∘ nonlinear).
- **Test, don't prove**: SAT-encode F, query ∃x≠y: F(x)=F(y).
  UNSAT ⟹ bijective. 64-bit, ~6 levels — feasible for modern SAT.

Sufficient-condition fallback (if SAT is slow): choose N "small" (sparse,
low-degree) so H is a perturbation of identity; generic perturbations of
identity over GF(2)^n are permutations with high probability.

## Task 1: L — linear, bijective, diffusive (independent)

Circulant matrices over GF(2): t^64+1 = (t+1)^64 (char 2).
A rotation pattern p(t) gives invertible circulant ⟺ gcd(p, (t+1)^64)=1
⟺ p(1)=1 ⟺ **p has odd weight**.

- Weight-3: l_i = x_i ⊕ x_{i+a} ⊕ x_{i+b}. 2 XOR levels (3.6u). Invertible
  for any (a,b). Optimize (a,b) for diffusion.
- Weight-5: 3 XOR levels (5.4u). Only if weight-3 diffusion insufficient.

Diffusion metric: for Fisher, 6 consecutive input bits must affect ~32
output bits. Compute for candidate (a,b): min over 6-bit windows of the
number of output positions with odd dependency count. Target ≥ 24.

Deliverable: (a,b) offsets, branch number, diffusion table, Verilog for L.

## Task 2: n_i — nonlinear, arbitrary (independent)

n = XOR of k AND2 terms (2 levels). No bijectivity needed — maximize
nonlinearity (minimize max absolute Walsh coefficient / linear bias).

- k=4 (8 inputs): AND 1u + XOR4 3.6u = 4.6u.
- k=8 (16 inputs): AND 1u + XOR8 5.4u = 6.4u. Only if k=4 LIN-insufficient.
- One pattern, rotated across i (or per-i optimized if time permits).

Input selection: each n_i takes 8 (or 16) inputs from diverse positions.
Pattern must ensure every input bit feeds ≥4 different n_j (for DIFF).

Deliverable: AND-pairing pattern, Walsh spectrum / max bias, Verilog for N.

## Task 3: combine

f_i = l_i ⊕ n_i. S0 measure (<10u gate). SAT bijectivity. Fisher
`lin_diff.screen_lin_diff` verbatim if bijective.

## Verdicts

O149: this decomposition track (parent).
O150+: Task 1 / Task 2 / Task 3 outcomes.
