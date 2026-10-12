# XIG: Direct Bijective Construction via x_i ⊕ g_i

**Date:** 2026-10-12
**Status:** Design phase — Carlo approved the approach.

## The construction

Define 64 Boolean functions:
**f_i(x) = x_i ⊕ g_i(x)** for i = 0..63.

Where each g_i is a 2-3 level AND-XOR network that does NOT use x_i (or uses it in a way that preserves the argument below).

The full map: F(x) = (f_0(x), f_1(x), ..., f_63(x)).

## Bijectivity argument

**Claim:** If the g_i are "generic" nonlinear functions, F is bijective.

**Reasoning:**
Consider F(x) = x ⊕ G(x), where G(x) = (g_0(x), ..., g_63(x)).

For F to be non-bijective, ∃ x≠y with F(x) = F(y), i.e., x ⊕ G(x) = y ⊕ G(y).

Let d = x ⊕ y (nonzero). Then the condition becomes:
G(x ⊕ d) ⊕ G(x) = d.

This says d is a **linear structure** of G: the derivative of G in direction d is constant (equal to d).

**Key theorem** (from vectorial Boolean function theory): A randomly chosen nonlinear G has no linear structures with overwhelming probability. Specifically, if each g_i is a "generic" nonlinear Boolean function, the probability that G has a linear structure decreases exponentially with the number of functions.

**Practical consequence:** We don't prove bijectivity — we TEST it:
1. **Random sampling** (fast filter): Test N random pairs (x, y). If F(x) = F(y) for x≠y → not bijective.
2. **SAT check** (definitive): Encode the miter circuit M(x,y) = [x≠y] ∧ [F(x)=F(y)]. If UNSAT → bijective.

If a specific offset pattern yields collisions, we tweak the pattern. The theory guarantees generic patterns work.

## Influence analysis (for Fisher diffusion)

**Fisher requirement:** 6 consecutive input bits changing → ~32 output bits change.

**Influence propagation in XIG:**
- f_i(x) = x_i ⊕ g_i(x).
- If input bit j changes:
  - f_j changes directly (via x_j term) — 1 output.
  - f_i changes for every i where g_i depends on x_j — up to (number of g_i using x_j) outputs.

**Design goal:** Each input bit x_j should appear in ~8 different g_i functions.

Then: 6 input bits changing → each affects ~8 outputs → up to 48 output influences. With overlaps, expect ~32 distinct outputs changing. **Sufficient for Fisher.**

**Critical:** The g_i must use DIVERSE input positions. If g_i only uses nearby bits, diffusion is local. Use offsets like {1,2,4,8,16,32} to spread influence across the full 64-bit word.

## Variant specifications

### Variant A: 2-level, 8 inputs per g_i

g_i = (a&b) ⊕ (c&d) ⊕ (e&f) ⊕ (g&h)

- 8 distinct input bits, paired into 4 AND2 terms, XORed together.
- **Cost:** AND2 (1u) + XOR4-tree (2 XOR levels = 3.6u) + final XOR with x_i (1.8u) = **6.4u**.
- **Degree:** 2 (from AND).
- **Influence:** Each g_i depends on 8 inputs. Each input appears in ~8 g_j (if offsets designed well).

### Variant B: 2-level, 16 inputs per g_i

g_i = XOR of 8 AND2 terms (16 distinct inputs).

- **Cost:** AND2 (1u) + XOR8-tree (3 XOR levels = 5.4u) + final XOR (1.8u) = **8.2u**.
- **Degree:** 2.
- **Influence:** Each g_i depends on 16 inputs. Better diffusion than A, but higher cost.

### Variant C: 3-level, degree 4

g_i = ((a⊕b)&(c⊕d)) ⊕ ((e⊕f)&(g⊕h))

- Each AND term takes XORs of 2 bits. 8 inputs total, degree 4.
- **Cost:** XOR (1.8u) + AND (1u) + XOR2 (1.8u) + final XOR (1.8u) = **6.4u**.
- **Degree:** 4 (higher nonlinearity than A/B).
- **Influence:** 8 inputs per g_i, but the XOR pre-layer mixes them first.

## Offset patterns (for input selection)

For g_i, select inputs from positions (i + offset) mod 64.

**Pattern P1 (diverse):** offsets = {1, 3, 7, 15, 31, 45, 53, 59}
- Mix of small and large jumps. Avoids clustering.

**Pattern P2 (powers of 2):** offsets = {1, 2, 4, 8, 16, 32, 48, 56}
- Structured, ensures each input bit is used.

**Pattern P3 (random):** Randomly chosen offsets, different per variant.
- Tests the "generic" hypothesis.

**Constraint:** g_i should NOT use x_i (to keep the bijectivity argument clean). If offsets include 0, shift them.

## Cost summary

| Variant | g_i levels | Total cost | Degree | Inputs/g_i |
|---------|------------|------------|--------|------------|
| A       | 2          | 6.4u       | 2      | 8          |
| B       | 2          | 8.2u       | 2      | 16         |
| C       | 3          | 6.4u       | 4      | 8          |

All under 10u. Variant A and C are the most promising (lowest cost).

## Testing pipeline

For each (Variant, Pattern) combination:
1. **Generate Verilog** for the 64 functions.
2. **S0 measure** using `run_synth.py`. Kill if >10u.
3. **Bijectivity test:**
   - a. Random sampling: 10M pairs. If collision → not bijective, try next pattern.
   - b. SAT check (for survivors): Encode miter, check UNSAT.
4. **Fisher triage** (only if bijective): `lin_diff.screen_lin_diff` verbatim.
5. **Escalate** (only if Fisher passes): Standard battery.

## Success criteria

- **Minimum:** At least one (Variant, Pattern) that is <10u, bijective, and Fisher-passing.
- **Stretch:** Multiple variants passing, allowing Pareto optimization.

## Open questions

1. Is degree 2 (Variants A/B) sufficient for Fisher LIN? The 18.6u frontier uses MUX (degree 2) but with 5 rounds. Single-layer degree 2 might not suffice.
2. Does the "generic g_i" bijectivity argument hold for structured offsets (P1/P2)? Or do we need random (P3)?
3. Can we push to 1-level g_i (just AND terms, no XOR tree) for even lower cost?
