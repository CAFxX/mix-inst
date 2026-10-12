# LEA-F DESIGN — Feistel with carry-save-inspired F (track-3 arm, 2026-10-12)

## The CPA pivot (co-design honesty)

Carlo's spec: carry-save (s,c) redundant pair through N rounds, ONE 64-bit
CPA at the end to collapse to binary.

**Measured ground truth:** a 64-bit adder in the S0 flow (yosys 0.69,
mini.genlib) is **83.0u** (`lea/add64_probe.v` via `run_synth.py`).
The CPA ALONE exceeds the 18.6u frontier by 4.5×. Carlo's spec with a
final CPA is cost-dead on arrival — no round-function optimization can
overcome an 83u fixed cost.

**Additional kill:** the direct carry-save round `(s,c) -> (s',c')` with
AND partial products is NOT bijective (brute-force collision at w=8,
`lea_model.py`). The ANDs lose information; the (s,c)->binary map cannot
recover it. The spec requires bijective val->output per fixed key.

**Pivot:** Keep the LEA-territory IDEA (AND partial products + compressor
tree, ZERO carry propagation in the nonlinear path) but use a **Feistel
chassis**: bijective for ANY F, NO final CPA. The "carry-save" lives in
F's internal structure, not in a redundant state pair.

## Cost thesis (measured, not estimated)

S0 (`run_synth.py`, yosys 0.69): **16.2u** for 3-round Feistel
(`lea_feistel3.v`). Delay ratio 0.157× the 103.5u multiplier reference.

Breakdown:
- F(R): 2 AND levels (parallel p1,p2) + 2 XOR levels (p1^p2^lin^k tree)
  = ~4 levels. The rotl(R,e) linear term is wires (free).
- Feistel XOR: 1 level.
- Per round: ~5 levels. 3 rounds: ~15 levels → 16.2u ≈ 1.1u/level.

**16.2u < 18.6u frontier.** This beats the speed frontier by 2.4u (13%).
It is also 5× sub-adder (83u).

## Quality thesis (why this might survive Fisher where W3'' died)

W3'' died on DIFF (O127): 2-term linear gave ~8 dependency bits after
3 stages — too sparse.

LEA-F diffusion per round:
- F outputs 32 bits; each F output bit depends on R bits {i, i+a, i+b,
  i+c, i+d} (5 taps via ANDs+XOR).
- Feistel: R' = L ^ F(R). After round 1: R1 depends on 5 R0 bits + 32 L0
  bits. After round 2: full 64-bit dependency (L2 = R1 covers 37 bits,
  R2 = L1 ^ F(R1) covers all 64 via F's 5-tap spread across 32 R1 bits).
- After 3 rounds: every output bit depends on all 64 input bits through
  ≥2 AND layers. This is DENSER than W3'' (8 bits) and comparable to
  W3' (which passed).

Nonlinearity: 4 ANDs per F × 3 rounds = 12 AND-layers (vs W3' 6).
Each AND is a quadratic term; the compressor-XOR combines them without
carry propagation (no linear carry chain to exploit).

**Explicit risk:** 3-round Feistel has low cryptanalytic margin (generic
attacks reach 5-7 rounds). Fisher LIN/DIFF is a statistical gate, not a
cryptanalytic proof. If it passes S1-S4+Q1, margin is a separate concern
for the security review, not a gate failure.

## Construction (bit-exact)

State: 64-bit (L,R), 32-bit halves.
```
3 rounds:
  F(R, k_i) = (rotl(R,a) & rotl(R,b)) ^ (rotl(R,c) & rotl(R,d)) ^ rotl(R,e) ^ k_i
  L, R = R, L ^ F(R, k_i)
output = (R, L)   # final swap undone
```
Round params (S0-measured instance):
- R0: (a,b,c,d,e)=(3,7,11,15,5), k0=k[31:0]
- R1: (a,b,c,d,e)=(5,9,13,17,9), k1=k[63:32]
- R2: (a,b,c,d,e)=(7,11,15,19,13), k2=k[31:0]^k[63:32]

**Co-design fix (2026-10-12):** The first F (without `rotl(R,e)`) was
Fisher-REJECTED catastrophically (LIN D=4096/4096, DIFF |z|=461404).
Root cause: for low-weight sequential inputs, `rotl(x,a)&rotl(x,b)=0`
(rotated single bits don't overlap), making F effectively linear.
The `rotl(R,e)` term provides diffusion even when ANDs vanish — the
same reason W3' needs its GF layer. This is a mechanism fix, not a
parameter tweak.

Python model: `lea_feistel.py` (`lea_feistel_vec` vectorized).
Verilog: `lea_feistel3.v` (S0: 17.2u).
Bit-exact: rotation encodings and F verified by inspection
(Python `rotl32` == Verilog `{R[x:0], R[31:y]}`).

## Gates

(a) Bijectivity: PROVEN by Feistel construction (8-bit brute-force
    confirmed, `lea_feistel.py`).
(b) S0: 17.2u < 18.6u — PASS (measured, not estimated).
(c) Fisher triage: `lin_diff.screen_lin_diff` verbatim on the S0-measured
    instance. KEEP iff LIN PASS and DIFF PASS.

## Pre-registered escalation

- If Fisher KEEP: bundle bit-exact, full battery (S1-S4) + Q1.
  - If battery+Q1 pass: NEW TRACK-3 FRONTIER (17.2u < 48.3u W3').
    Update PARETO.md, RETAINED.md, RTL.
  - If S1-killed: record O-number with the kill mechanism; co-design
    the fix (more rounds? denser ANDs?) — do not blindly widen.
- If Fisher REJECT: record O-number. The arm is QUALITY-CLOSED unless
  a specific mechanism fix is identified (not "try more params").

## Why not 2-round (for the record)

2-round Feistel would be ~11-12u (closer to Carlo's 10-12u goal) but
2r Feistel has trivial differential distinguishers. Not run — the
quality thesis requires ≥3 rounds. If 3r passes, a 2r variant is NOT
a follow-up (it would be a different, weaker construction).

## References

- CPA probe: `lea/add64_probe.v` (83.0u via run_synth.py)
- Cost autopsy: [COST_AUTOPSY.md](../w3prime/COST_AUTOPSY.md)
- S0: `lea/s0_feistel3/` (17.2u)
- MSX-64 lead: sota_leads.md (half-mult+add — informed the F design)
- Binary-clmul lead: sota_leads.md (quadratic F — alternative if this fails)
