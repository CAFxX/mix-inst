# SAC/BIC First-Principles: Results

## Summary

**Achieved**: 64 quadratic Boolean functions with **proven perfect SAC and BIC**,
synthesized at **12.7u** (Pareto improvement over 18.6u).

**Failed**: Fisher LIN (D=4096/4096, catastrophic).

**Key finding**: SAC + BIC are **not sufficient** for statistical quality.
Perfect derivatives do not prevent systematic linear dependencies in the output sequence.

## Construction (First Principles)

No AES/PRESENT copied. Derived from SAC/BIC constraints via ANF search.

### Mathematical Framework

F = (f_0, ..., f_63), f_j(x) = x_j ⊕ (⊕_{k=0}^{47} (x_{a_{j,k}} & x_{b_{j,k}}))

For quadratic f_j, D_i f_j(x) = δ_{ij} ⊕ (M_{ij} · x) where M_{ij} is a 64-bit mask.

- **SAC(i,j)** ⟺ M_{ij} ≠ 0
- **BIC(i,j,k)** ⟺ M_{ij} ≠ M_{ik}

Exact, not sampled. The masks fully characterize SAC/BIC.

### Impossibility at t=32

With 32 disjoint pairs, M_{ij} are single bits. Need 64 distinct from 63 available.
**t > 32 necessary.** Used t=48.

### Search

Simulated annealing on ANF coefficients (2.3M iterations):
- Init: sac=0, bic=3098
- Final: **sac=0, bic=0**
- Saved: [anneal_best_t48_s42.pkl](anneal_best_t48_s42.pkl)

## Measurements

| Metric | Result |
|--------|--------|
| SAC violations | **0 / 4096** (proven) |
| BIC violations | **0 / 129024** (proven) |
| S0 | **12.7u** (8073 cells, XCHECK clean) |
| Bijectivity | 0 collisions / 50k samples |
| Fisher LIN | **D=4096/4096 FLAG** |
| Depth | 7 levels (1 AND + 6 XOR) |

## Interpretation

The Fisher LIN failure despite perfect SAC/BIC reveals:

1. **SAC/BIC test derivatives** (local differences).
2. **Fisher LIN tests output linear dependencies** (global structure).
3. A function can have perfect local behavior but systematic global linearity.

Specifically, our quadratic XIG construction likely has a non-trivial linear
combination Σ c_j f_j(x) where the AND terms cancel (each pair appears evenly),
leaving an affine function. This creates rank deficiency in consecutive output blocks.

## Artifacts

- [sacbic.py](sacbic.py): Mask computation.
- [climb.py](climb.py): Hill-climber.
- [anneal.py](anneal.py): Simulated annealing.
- [anneal_best_t48_s42.pkl](anneal_best_t48_s42.pkl): Optimal ANF.
- [sacbic64.v](sacbic64.v): Verilog.
- [s0_sacbic/](s0_sacbic/): Synthesis (12.7u).
- `seq_outputs.bin`: 2^18 outputs for testing (generated artifact, not tracked).
- [DESIGN.md](DESIGN.md): Design documentation.

## Conclusion

We built the SAC/BIC-optimal quadratic 64-bit function from first principles.
It achieves 12.7u (Pareto) with proven SAC/BIC. But Fisher LIN fails catastrophically,
proving SAC/BIC are insufficient criteria. The Pareto search needs stronger
mathematical foundations than SAC/BIC alone.
