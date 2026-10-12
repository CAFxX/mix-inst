# W3' cost autopsy — why 48u (2026-10-12, from raw artifacts, no new compute)

## Raw numbers

| bundle | cells | area | crit |
|---|---|---|---|
| al_w3p_a | 18,917 | 58,806 | 48.3u |
| al_w3p_b | 18,322 | 57,155 | 50.6u |
| al_w3p_c | 18,119 | 56,361 | 49.0u |
| al_w3p_d | 18,983 | 58,731 | 48.7u |

Source: `adder_lat/w3prime/s0/s0.log` (DUT lines). Four different rotation
schedules, two P constants — S0 spread ±2.5% (noise).

## Structural gate count (from `fast_battery/candidates/al_w3p_a/{model.py,impl.c}`)

Per stage: 2 AND-layers + 1 GF(2^64) constant multiplication.

- **AND layer** `x ^= (rotl(x,a) & rotl(x,b))`: rotations are free in hardware
  (wires). 64× AND2 + 64× XOR2 = **128 gate-equivs**. ×2/stage = 256.
- **GF(2^64) const-mult** `gf_mul(x, P)`: loop over 64 bits; P=0x94d049bb133111eb
  has ~29 set bits → ~29×64 XOR2 (result accumulation) + 64×~5 XOR2 (0x1B
  reduction) ≈ **~2,200 XOR2-equivs**.
- Per stage ≈ 2,450; ×3 stages ≈ 7,350; + key pre/post-whiten ≈ **~7,500
  hand-counted** vs 18,917 yosys cells (2.5× mapping overhead — consistent
  across all four bundles, so the *ratio* is what matters).

**GF diffusion ≈ 85–90% of structural cost. The AND layers — the entire
nonlinearity budget — are ≈10%.** Delay is likewise GF-dominated: per-stage
critical path ≈ AND (2 levels) + GF XOR-tree (~5–6 levels), ×3 stages.

## The decisive fact

**Cost is schedule-independent.** Rotations are wires; the GF multiplier's
cost depends only on popcount(P) (≈29 for all three P constants tried).
Measured S0 across four different schedules: 48.3–50.6u. No schedule in
the d-constrained family can be meaningfully cheaper — the cost floor is
set by the 3 GF multiplications, not by (a,b) choices.

## Consequence for W3'' (recorded here so the co-design is honest)

- **Arm (a) — bigger screen of the same GF form — is REJECTED.** A better
  triage instrument cannot find cheaper schedules because cost does not vary
  with schedule. Quality is already proven (3/4 full battery+Q1 passes); the
  binding constraint is cost, and screening more of the same form is theater.
- **Arm (b) — structural cost variant — has a principled thesis.** The GF
  multiplier is LINEAR (O93: "GF(2^64) multiplication and key XOR are
  linear"). Its S1-LIN role is rank contribution, not nonlinearity. A cheaper
  linear diffusion preserves the nonlinearity budget (d-constrained ANDs,
  3 effective stages) while attacking ~90% of the cost. The S1-LIN rank must
  be RE-PROBED for the variant (mechanism re-check, never assumed), and
  diffusion quality is adjudicated by the Fisher triage + full battery —
  the mechanism doc notes "GF(2^64) carries diffusion" (W3_LIN_MECHANISM.md),
  so weaker diffusion is the explicit risk.
- Pre-registered fallback: if the cheap-linear variant fails the rank probe
  or S1, (b2) sparse-GF (one GF mult at the end, cheap linear between
  stages) is the next structural variant — not screened now.
