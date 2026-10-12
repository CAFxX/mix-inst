# Track-3 Boolean Function Designs (6-level)

Carlo's intuition (2026-10-12): "the true lower bound must be a Boolean function with 6 levels."

## Goal

64→64 bijective mapping as a flat 6-level Boolean circuit:
- Nonlinear (AND/OR for LIN resistance)
- Diffusive (6 input bits → ~32 output bits for Fisher)
- Bijective (one-to-one)
- Fast (<10u; 6 levels ≈ 9u at ~1.5u/level)

## Critical correction from firstprin workers (2026-10-12)

The naive 64-parallel Toffoli `S(x)[i] = x[i] XOR (x[(i+a)] AND x[(i+b)])` is **NOT bijective**.
Explicit collision: `S(0^64) = S(1^64) = 0^64`.

**Root cause**: The Toffoli involution proof requires control bits to be frozen (not targets).
In the parallel stage, every bit is both a target and a control. The proof does not transfer.

**Repair (adopted)**: Bipartite / alternating-parity Toffoli.
- Partition by parity. Offsets `a, b` odd.
- Stage E: even targets, odd controls (frozen). `out[2i] = in[2i] XOR (in[2i+a] AND in[2i+b])`, `out[2i+1] = in[2i+1]`.
- Stage O: odd targets, even controls (frozen). Mirror.
- Each stage is 32 disjoint Toffolis with frozen controls → bijective (own inverse).

**Cost correction**: AND2=1.5u, XOR2=2.0u (mini.genlib). Toffoli stage = 3.5u (not 2.8u).
E+O full round = 7.0u. 3 stages = 10.5u (over budget).

## Influence propagation analysis

### Design B (bipartite thin-Toffoli, 2 stages = E+O = 7.0u)

Stage E forward influence of input bit `p`:
- `p` even: `out[p]` only (as target; even bits never controls in E).
- `p` odd: `out[p]` (passthrough) + `out[p-a]`, `out[p-b]` (even targets via AND).

After E+O (full round):
- Even bit `p`: influences `out[p]` (E target), then in O, `p` is a control for odd targets `p+a`, `p+b`.
- Odd bit `p`: influences `out[p]` (E passthrough), `out[p-a]`, `out[p-b]` (E targets), then in O, `p` is a target.

**Worst case**: 6 consecutive input bits. If they're all even, after E they affect only 6 outputs.
In O, each even bit is a control for 2 odd targets → 6×2 = 12 odd outputs (conditional on AND).
Total after E+O: ~6 (direct) + ~12 (via AND) = 18 outputs. **Below the 32 needed.**

**Conclusion**: 2-stage thin-Toffoli likely insufficient for Fisher. Need fatter ANDs or more stages.

### Design A (fat-Toffoli, 2 stages)

`x[i] ^= (x[i+1]^x[i+2]^x[i+3]^x[i+4]) & (x[i+5]^x[i+6]^x[i+7]^x[i+8])`

But this is the NAIVE form (not bipartite) → **not bijective**. Must use bipartite version:
- Stage E (even `i`): `out[2i] = in[2i] XOR (XOR of 4 odd bits) AND (XOR of 4 other odd bits)`.
- All AND inputs are odd (frozen in E) → bijective.

Influence per stage: output depends on 1 + 4 + 4 = 9 inputs.
After 2 stages (E+O): 9×9 = 81 (capped at 64). **Sufficient in principle.**

Cost: XOR4 = 2 XOR levels = 4.0u. AND2 = 1.5u. XOR2 = 2.0u.
Per stage: 4.0 (XOR4) + 1.5 (AND) + 2.0 (XOR) = 7.5u. Two stages = 15.0u. **Over budget.**

**Conclusion**: Fat-Toffoli is too slow. Killed by cost.

### Design C (bit-Feistel)

From firstprin/d2: the naive per-bit form is NOT an involution. The D2 worker has a proof
and sweep data (av2 ~14.3 after 2 rounds). 

Feistel structure: Split 64 → L,R (32 bits).
Round: `L' = L`, `R' = R XOR F(L)`, then swap.
`F` can be ANY function (not necessarily bijective) → the round is bijective.

If `F` is a 2-level AND-XOR network:
- `F(L)[i] = (L[a] AND L[b]) XOR (L[c] AND L[d]) XOR ...`
- Cost per F: AND (1.5u) + XOR (2.0u) = 3.5u.
- 2 rounds: 7.0u + swap (wiring). Under 10u!

Influence: After 1 round, R depends on L (via F). After 2 rounds (with swap), both halves depend on both.
- 6 input bits in L: after R1, R affected. After swap, L' = R (affected). After R2, R' = L' XOR F(R) — both affected.
- The AND gates in F provide nonlinearity. The cross-bit wiring in F provides diffusion.

**This is the most promising.** Bijective by Feistel structure, no bipartite constraint needed.

## The three builds

### Build 1: Design B (bipartite thin-Toffoli, E+O)
- Verilog: `boolfunc_b.v` (64-bit, parameters a,b odd).
- S0: expect ~7.0u.
- Fisher: expect FAIL (influence ~18 < 32). But MEASURE, don't assume.

### Build 2: Design C (bit-Feistel, 2 rounds)
- Verilog: `boolfunc_c.v` (64-bit, F = AND-XOR network).
- S0: expect ~7.0u.
- Fisher: influence analysis suggests it might pass. MEASURE.

### Build 3: Design A-repaired (bipartite fat-Toffoli, IF B and C fail)
- Only if B and C both fail. The cost (15u) is over, but try a "medium-fat" version:
  - XOR2 instead of XOR4: `x[2i] ^= (x[a]^x[b]) & (x[c]^x[d])`.
  - Cost: 2.0 + 1.5 + 2.0 = 5.5u/stage. Two stages = 11.0u. Still over.
  - **Likely killed by cost. Build only if B/C show promise but need more diffusion.**

## Verdicts to record

- O149: Design B (bipartite thin-Toffoli) — S0 + Fisher.
- O150: Design C (bit-Feistel) — S0 + Fisher.
- O151: Design A (fat-Toffoli) — cost-killed or measured, if built.
