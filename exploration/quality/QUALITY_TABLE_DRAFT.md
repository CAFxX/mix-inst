# Quality Battery Results — 8 Pareto Candidates

**Date:** 2026-10-02 | **Key:** 0x123456789ABCDEF0 (all Q2/Q3) | **Machine:** 2-core, max 2 concurrent pipelines

## Table 1 — Q1 Avalanche (SAC/BIC), N=2^18, fixed key

| Candidate | sac_maxdev | sac_meandev | sac_z5 | bic_maxcorr | bic_meancorr | avalanche_mean |
|---|---|---|---|---|---|---|
| r7_feist8_s1_1sbox | 0.0035 | 0.0008 | 0 | 0.0092 | 0.0016 | 32.0011 |
| r7_feist8_r311 | 0.0042 | 0.0008 | 0 | 0.0091 | 0.0016 | 31.9996 |
| r7_feist8_spn_nw | 0.0037 | 0.0008 | 0 | 0.0088 | 0.0016 | 31.9995 |
| r7_feist8_r517 | 0.0037 | 0.0008 | 0 | 0.0088 | 0.0016 | 32.0012 |
| r6_feist8_spn | 0.0035 | 0.0008 | 0 | 0.0084 | 0.0016 | 31.9993 |
| r7_feist8_rksimple | 0.0039 | 0.0008 | 0 | 0.0092 | 0.0016 | 31.9995 |
| r7_feist8_rkcheap | 0.0037 | 0.0008 | 0 | 0.0086 | 0.0016 | 31.9995 |
| r7_feist8_gift | 0.0038 | 0.0008 | 0 | 0.0093 | 0.0016 | 31.9997 |

**Verdict Q1:** All 8 candidates essentially identical and excellent. sac_z5=0 across the board (no |z|>5 cells). Differences in sac_maxdev/bic_maxcorr are noise-level. Q1 does NOT discriminate.

## Table 2 — Q2 Reductions Battery (6 seq × 8 red = 48 cells/candidate)

**Sequences:** s1=1, s8=8, s256=256, s4k=4096, s64k=65536, s4g=2^32 (v=i*stride; pow2 strides pin low input bits)
**Reductions:** low8, low16, low32, high32, xor32 (pow2, full-width) | lemire1e9p7, mod1e9p7, mod1000 (non-pow2)
**PractRand:** 1GB/cell or first FAIL. stdin (byte/16-bit), stdin32 (32-bit).

### 2a. Power-of-2 reductions (discriminating)

| Candidate | s1 | s8 | s256 | s4k | s64k | s4g |
|---|---|---|---|---|---|---|
| (per seq: low8/low16/low32/high32/xor32) | | | | | | |
| r7_feist8_s1_1sbox | ... | ... | ... | ... | ... | ... |
| r7_feist8_r311 | ... | ... | ... | ... | ... | ... |
| r7_feist8_spn_nw | ... | ... | ... | ... | ... | ... |
| r7_feist8_r517 | ... | ... | ... | ... | ... | ... |
| r6_feist8_spn | ... | ... | ... | ... | ... | ... |
| r7_feist8_rksimple | ... | ... | ... | ... | ... | ... |
| r7_feist8_rkcheap | ... | ... | ... | ... | ... | ... |
| r7_feist8_gift | ... | ... | ... | ... | ... | ... |

### 2b. Non-power-of-2 reductions (non-discriminating — see artifact note)

All candidates FAIL@BCFN on lemire1e9p7, mod1e9p7, mod1000 across all 6 sequences.
**Control:** splitmix64 (known-good) also FAILs BCFN identically → reduction artifact (top bits structurally zero in [0,p) range), NOT a candidate defect. These cells reported for completeness, excluded from ranking.

## Table 3 — Q3 Endurance (full 64-bit, sequential, 32GB cap)

| Candidate | endurance_bytes | endurance_GB | failing_test |
|---|---|---|---|
| r7_feist8_s1_1sbox | ... | ... | ... |
| r7_feist8_r311 | ... | ... | ... |
| r7_feist8_spn_nw | ... | ... | ... |
| r7_feist8_r517 | ... | ... | ... |
| r6_feist8_spn | ... | ... | ... |
| r7_feist8_rksimple | ... | ... | ... |
| r7_feist8_rkcheap | ... | ... | ... |
| r7_feist8_gift | ... | ... | ... |

## Ranking Note

(TBD after Q2/Q3 complete)
