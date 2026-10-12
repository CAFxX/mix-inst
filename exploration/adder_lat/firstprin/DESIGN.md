# First-Principles Track-3 Designs

Carlo's directive (2026-10-12): "I don't care. I'm sure we can find something suitable
if you keep looking and designing possibly from first principles."

## First-principles restatement

**Goal**: <10u, Fisher LIN+DIFF passing (64 consecutive inputs → ~32 output bits change).

**The real problem**: 6 input bits must influence 32 output bits in <10u, nonlinearly, bijectively.

**Information-theoretic view**: 6 → 12 → 24 → 48 in 3 levels of perfect fanout-2.
It's POSSIBLE in principle. The problem is our gates don't fanout — S-boxes contain
influence (4→4), MUXes reduce it (3→1).

**Stop thinking in rounds. Think in influence propagation.**

## Prior art (what died and why)

- O135: 2-stage designs Fisher-dead (8-bit bottleneck: 6 input bits → ≤2 S-box nibbles).
- O146: 3-stage SPN = 13.0u with whitening. Over budget. XOR cost 1.8-2.0u/level.
- O147: 4-stage hybrid killed by XOR cost correction (4-term = 5.5u, not 2-3u).
- O148: 4-stage MUX2 = 9.4u (UNDER 10u!) but structurally can't diffuse.
- O138: 2.0u MUX2 gate (fastest balanced 3-bit nonlinear).

## The 4 design directions

### Direction 1: Input-dependent MUX routing

64 parallel N:1 MUXes (N=4 or 8). Each MUX's SELECT bits are a nonlinear function
of INPUT bits (not fixed rotations). Each MUX's DATA inputs from diverse positions.

If input bit i changes: alters select bits (nonlinear routing change) AND data bits.
Select logic: `select = (input[a] AND input[b]) XOR input[c] XOR key`.

1-2 level diffusion with massive fanout. Nonlinearity from select, not data path.

### Direction 2: Bit-level Feistel (AND-OR-XOR networks)

S-boxes are not the only nonlinear primitive.
- Stage 1: 64 parallel AND2 — 1u, nonlinear.
- Bijectivity fix: `out[i] = in[i] XOR (in[j] AND in[k])`. This is an involution
  (apply twice = identity) if the AND inputs don't include the target bit.
- It's bijective, nonlinear, and 2-3 levels could suffice.

Essentially 64 parallel bit-level F-functions, XORed back.

### Direction 3: Toffoli / reversible nonlinear gates

Bijectivity is the constraint killing us. Use reversible gates:
- Toffoli (CCNOT): `out[i] = in[i] XOR (in[(i+a)%64] AND in[(i+b)%64])`.
- Bijective (reversible), nonlinear via AND, diffusion via cross-bit AND inputs.
- 2-3 stages: 4-6u. Under budget!

### Direction 4: Fix the 9.4u MUX2

We HAVE a 9.4u design (O148) that's under 10u but can't diffuse. Don't discard — FIX:
- 3-stage MUX2 (7.4u) + 1 diffusion stage (rotation + sparse XOR, ~2u) = 9.4u.
- Test if the diffusion stage fixes the Fisher failure.
- If it works, try Direction 2's bit-Feistel as the diffusion stage.

## Influence propagation analysis (to be filled per direction)

For each design: trace how 6 input bits reach 32 output bits. Count the fanout
at each level. Identify bottlenecks before building.
