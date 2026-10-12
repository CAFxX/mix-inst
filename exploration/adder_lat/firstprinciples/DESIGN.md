# First-Principles 3-Stage 64-bit Mapping (fp3)

Carlo's directive (2026-10-12): "forget fisher and just start from basic principles
to build what I asked: set of 64 boolean functions, each depending on all 64 input
bits, maximum NL, maximum degree, minimum latency."

## Design

**Stage function** (3 levels, 8 inputs):
```
out = (a0^a5) ^ (a1&a4) ^ (a2&a7) ^ (a3&a6)
```
- This is the optimal 7-input form `x0^(x1&x4)^(x2&x7)^(x3&x6)` (NL=112) with
  `x0 -> (x0^x5)`, an affine input transform. NL, balance, degree preserved.
- Verified: balanced (128/256), NL=112 (max|W|=32), degree 2.
- Levels: L1 = 3 AND2 + 1 XOR2 (parallel); L2 = 2 XOR2; L3 = 1 XOR2.

**Wiring** (all mod 64):
- Stage 1: `s1[i] = F(x[i], x[i+1], ..., x[i+7])` — local, D1 = 8.
- Stage 2: `s2[i] = F(s1[i], s1[i+8], ..., s1[i+56])` — stride-8, D2 = 64.
  - The 8 Stage-1 dependency sets `{i+8j .. i+8j+7}` are pairwise disjoint,
    covering all 64 inputs.
- Stage 3: `y[i] = F(s2[i], s2[i+1], ..., s2[i+7])` — local, D3 = 64.

**Properties**:
- Each of 64 outputs depends on all 64 primary inputs (verified by transitive fan-in).
- Degree: 2 → 4 → 8.
- Levels: 9 (3+3+3).

## Measurements

| Metric | Result |
|--------|--------|
| S0 | **15.2u** (3220 cells) — under 18.6u Pareto |
| Bijectivity | 0 collisions in 1M random pairs (sampled) |
| 64-input dependence | Verified: all 64 outputs have |D3| = 64 |
| Fisher LIN | **FLAG** (D=4096/4096, logp=-inf) |
| Fisher DIFF | **FLAG** (worst|z|=739994) |

## Analysis

Despite satisfying every first-principles requirement — optimal per-stage NL (112),
degree 8, full 64-bit diffusion, bijectivity, 15.2u — Fisher fails catastrophically
on both LIN and DIFF.

The DIFF worst|z| (739994) is identical to R1's, indicating the same failure mode:
for sequential inputs, only 6 bits vary, and the layered AND/XOR structure cannot
generate sufficient nonlinearity from 6 varying bits spread across a 64-bit datapath.
The AND gates starve (most see constant inputs); the XORs merely permute.

**Conclusion**: Layered compositions of optimal small Boolean functions do not
compose into Fisher-passing 64-bit mappings. Per-stage optimality (NL=112) is
insufficient; the *composition structure* itself is the bottleneck. This corroborates
the DAG-optimizer's structural impossibility finding for layered 2-input-gate DAGs
on Fisher's 6-bit input cubes.

## Artifacts

- [sim.py](sim.py) — numpy-vectorized simulator, dependence verifier, bijectivity tester
- [fp3.v](fp3.v) — Verilog (3 stages, 64 parallel functions each)
- [gen_verilog.py](gen_verilog.py) — Verilog generator
- [fisher_fp3.py](fisher_fp3.py) — Fisher triage script
- [fisher_fp3.json](fisher_fp3.json) — raw Fisher output
- `s0_fp3/` — synthesis workdir (mapped_fp3.v, analyzer cross-check)
