# sub10 DESIGN: <10u (ideally <8u) mixer

## Target
Carlo 2026-10-12: **<10u strict, ideally <8u** (1/10th of 83u S0 adder). Current frontier 18.6u.

## Cost model (measured, S0 flow)
- NAND2/NOR2: 1.0u | AND2: 1.5u | XOR2/XNOR2/MUX2: 2.0u
- 16× Midori Sb0 (4-bit, DU=4 NL=4): **3.0u**, 179 cells
- 16× PRESENT S-box: 6.0u (has XOR2 on crit path — rejected for this budget)
- 2-stage MUXD (t6_b59_47 stages): **9.6u**, 2086 cells

## What failed (with evidence)
1. **2-round 4-bit SPN** (S-P-S, Midori Sb0 + PRESENT P-box): Fisher CATASTROPHIC
   (LIN D=4096/4096, DIFF |z|=1.48e6). 2 rounds insufficient for diffusion.
   Avalanche mean 2.1 bits (need ~32).
2. **2-stage / 3-stage MUXD** (t6_b59_47 constants): Fisher FLAG both.
   5-stage passes; 2-3 stage constants were optimized for 5r, not 2r.
3. **6-level NAND network**: saturates (bias), not bijective. No 2-input
   function is both balanced and nonlinear.

## Live hypothesis: 2-stage MUXD with 2-round-optimized constants
- Cost: 9.6u measured (t6_b59_47 stages). <10u bar is feasible.
- The t6_b59_47 constants were selected for 5-round security. For 2 rounds,
  we need constants maximizing diffusion in just 2 rounds — a different
  optimization target.
- Screen: 200 random 2-stage MUXD, Fisher triage verbatim.
  - If ≥1 KEEP: synthesize to verify <10u, then S0 bar <10u strict, battery.
  - If 0/200: the 2-stage MUXD form is insufficient → try 2-stage with
    different structure (e.g., wider MUX, added XOR layer) or record
    terminal.

## Escalation (pre-registered)
1. Screen N=200, Fisher triage. Bar: ≥1 KEEP.
2. Synthesize keeps via run_synth.py. Bar: <10u strict.
3. S0 via run_synth.py (ref mul64 103.5u). Bar: <10u strict.
4. Battery: S1 (Fisher LIN+DIFF), S2, S3, S4 + Q1 (sac_z5=0, BIC).
5. If a keep passes all with <10u: new track-3 frontier, update PARETO.md.

## Fallbacks (if 2-stage MUXD fails)
- 3-stage MUXD with aggressive ABC optimization (may fit <12u, not <10u —
  would need bar relaxation by Carlo).
- Return to S-box SPN with 3 rounds of ultra-shallow (2u) S-boxes (none found yet).
- Record terminal O-number with mechanism.

## Gate levels (Carlo's steer)
Count gate levels, not rounds. 2-stage MUXD: MUX(2u) + XOR(2u) + XOR(2u) = 6u
per stage nominal, 9.6u measured for 2 stages (ABC cross-stage opt).
Target: ≤5 XOR-levels (10u) or ≤10 NAND-levels.
