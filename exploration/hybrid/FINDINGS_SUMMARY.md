# Track 5 (Hybridization) — Findings Summary

**Date:** 2026-10-09 (supervisor respawn after ~20:35Z VM reboot)
**Frontier:** al_and6a 20.1u (S0–S4 + Q1 all PASS, BIC-clean)

## Terminal findings (batches 6–10)

1. **Inter-stage P-boxes HURT the al_and6a construction** (batch-6, 3 candidates, all S1-FLAG).
   The rotation triplets are a delicate sequence co-design; inserting a permutation
   between stages disrupts the diffusion pattern and CREATES linear/differential
   weaknesses. The chi_pbox_diffuse.py metric (spread score 43 vs 29 baseline) is
   MISLEADING here: it measures dependency spread, not statistical quality.
   Spread ≠ security. Verdict scoped to inter-stage placement.

2. **Even a single P-box at the cascade midpoint hurts** (batch-8, S1-FLAG DIFF rej=3).
   The sequence co-design is fragile — any inter-stage permutation disrupts it.
   **P-box-between-stages direction: EXHAUSTED** (4 candidates, all FLAG).

3. **6 stages are necessary for the AND-cascade family** (batch-7): 5-stage 3-input
   AND (degree 3 per stage) still S1-FLAGGED (LIN rej=2, DIFF rej=10). Per-stage
   strength does not compensate for depth. The 5-stage barrier holds.

4. **MAJ3 is too expensive per stage** (batch-9): 25.8u at 6 stages — dominated.

5. **The 3u/stage structure `x ^= (ra&rb)^rc` is load-bearing for security** (batch-10):
   restructured `x ^= ra ^ (rb&rc)` (2u/stage, S0 19.8u) creates a linear trail
   via the `ra` term (D=252/4096 on key=0). Parallelism and security are in
   tension here.

**Conclusion:** al_and6a (20.1u, 6-stage) is at a strong local optimum within the
AND-cascade family. Beating 20.1u requires changing WHERE diffusion comes from,
not tweaking the cascade — batch-11 tests the one unexplored placement: a final
diffusion layer AFTER all stages (never tried; batch-6 only tested between-stages).

## What batch-11 tests (launched 2026-10-09 ~20:55Z)

- **hyb11_and5_finalPL** (S0 19.9u — beats frontier by 0.2u): 5-stage al_and6a
  triplets + final P(37,1) + L(5,13). Hypothesis: a strong final diffusion layer
  compensates for the 6th AND stage. S1/S2 on GHA (`hyb11-s1s2-20261009`).
- **hyb11_and6_finalPL** (S0 23.0u, control): final layer on the frontier design;
  tests whether the final layer breaks quality.
- **hyb11b_andSPN_p27** (S0 28.8u): batch-5B reconstruction (lost in restart) —
  4-round SPN skeleton (proven batch-3 core: rk[i]=rotl(k,13*(i+1))^RC[i]) with
  the AND stage as the nonlinear layer replacing the S-box.
- **hyb11c_chiSPN_p27 / _p43** (S0 28.7u / 29.4u): batch-5C reconstruction —
  chi-SPN with SPN-co-designed P(27,1) vs chi-metric pick P(43,1).

Abandoned micro-direction (documented, not buried): a 4-bit AND-XOR S-box of
form y_i = x_i ^ (literal & literal) was prototyped for 5B; the full literal-AND
space (1.68M, exhaustive) yields ddt=16 structurally (single-bit input
differences propagate with probability 1). Two-AND-term form also ddt=16.
The 64-bit cascade-stage NL avoids this trap entirely.

## Open / deferred

- Direction (c) from the respawn brief: Q1 already PASS for the full S2-clean
  trio (cd1×2 2026-10-07, cd2_p_a43b7 + hyb5_casc8_p43 2026-10-09, all BIC-clean).
  S3/S4 remain infra-blocked (canary pipe — DO NOT re-race). Nothing to launch.
- Direction (a) P-box co-designed FOR chi/maj3 cascades: substantially covered
  by batch-5 (chi8/chi6 + P-box, all S1-FLAGGED on single-bit PB extreme keys)
  and batch-6 (metric falsified for AND). Not re-run without a new metric.

## Files

- Generator: `hybrid/codesign/gen_batch11.py`
- Bundles: `fast_battery/candidates/hyb11_*` (bit-exact: model vs C 5/5 vecs,
  RTL vs model 16/16, meta goldens match, rtl_top present)
- GHA campaign: `hyb11-s1s2-20261009` (5 shards, S1+S2), repo commit `148a5e3a`,
  bundles VERIFIED PRESENT 21/21 via API tree read
