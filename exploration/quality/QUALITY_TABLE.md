# Quality Battery Results — 8 Pareto Candidates

**Date:** 2026-10-02 | **Key:** 0x123456789ABCDEF0 (all Q2/Q3) | **Machine:** 2-core, max 2 concurrent pipelines
**Work dir:** [`~/workspace/mix/exploration/quality/`](./)

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

**Q1 verdict:** All 8 essentially identical and excellent. `sac_z5=0` everywhere (no |z|>5 cells out of 4096). Differences are noise-level. **Q1 does not discriminate.**

## Table 2 — Q2 Reductions Battery (6 sequences × 8 reductions = 48 cells/candidate)

**Sequences** (v = i × stride): s1=1, s8=8, s256=256, s4k=4096, s64k=65536, s4g=2³².
Power-of-two strides pin low input bits (aligned-data pathology); s4g is the critical 32-bit-half test.
**Reductions:** low8, low16, low32, high32, xor32 (pow2, full-width) · lemire1e9p7, mod1e9p7, mod1000 (non-pow2).
**PractRand:** 1 GB/cell or first FAIL. `stdin` (byte/16-bit), `stdin32` (32-bit). Key fixed.

### 2a. Power-of-2 reductions — 1 GB PASS in every cell (240/240)

| Candidate | s1 | s8 | s256 | s4k | s64k | s4g |
|---|---|---|---|---|---|---|
| r7_feist8_s1_1sbox | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |
| r7_feist8_r311 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |
| r7_feist8_spn_nw | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |
| r7_feist8_r517 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |
| r6_feist8_spn | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |
| r7_feist8_rksimple | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |
| r7_feist8_rkcheap | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |
| r7_feist8_gift | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 | PASS×5 |

(each PASS×5 = low8/low16/low32/high32/xor32 all "no anomalies in 227 tests" at 1 GB)

### 2b. Non-power-of-2 reductions — FAIL@BCFN in every cell (144/144), NON-DISCRIMINATING

All 8 candidates FAIL PractRand BCFN (p=0, R>+99999) on lemire1e9p7, mod1e9p7, mod1000 across all 6 sequences.
**Control experiment:** splitmix64 (known-good PRNG) reduced via `x % 1000000007` FAILs BCFN identically.
**Mechanism:** values in [0, 10⁹+7) use only 30 of 32 bits; top bits structurally zero → BCFN detects it.
**Conclusion:** reduction artifact, NOT a candidate defect. Excluded from quality ranking. (See [`CONTROL_NOTE.md`](CONTROL_NOTE.md).)

**Q2 verdict:** On the discriminating (pow2) reductions, all 8 candidates are perfect across all 6 stride sequences, including the s4g low-half-stuck critical test. **Q2 does not discriminate.**

## Table 3 — Q3 Endurance (full 64-bit output, sequential, 32 GB cap, stdin64)

| Candidate | endurance_bytes | endurance_GB | failing_test |
|---|---|---|---|
| r7_feist8_s1_1sbox | 34359738368 | 32.0 | 32GB clean |
| r7_feist8_r311 | 34359738368 | 32.0 | 32GB clean |
| r7_feist8_spn_nw | 34359738368 | 32.0 | 32GB clean |
| r7_feist8_r517 | 34359738368 | 32.0 | 32GB clean |
| r6_feist8_spn | 34359738368 | 32.0 | 32GB clean |
| r7_feist8_rksimple | 34359738368 | 32.0 | 32GB clean |
| r7_feist8_rkcheap | 34359738368 | 32.0 | 32GB clean |
| r7_feist8_gift | 34359738368 | 32.0 | 32GB clean |

**Q3 verdict:** All 8 candidates clean through 32 GB (≈2⁴³ bytes, PractRand "no anomalies" at every doubling from 64 MB to 32 GB). **Q3 does not discriminate.**

## Ranking Note

**Best on each axis:** Tie — all 8 candidates are statistically indistinguishable on Q1 (avalanche), Q2 (reductions), and Q3 (32 GB endurance).

**Quality-based reordering vs delay Pareto:** **None.** The quality battery confirms the delay-Pareto ranking stands:
the fastest candidate (r7_feist8_s1_1sbox, 56.5u = 0.546×) is quality-equivalent to all 7 others on every measured axis.
No candidate shows any statistical weakness at 1 GB reductions (6 stride sequences × 5 pow2 reductions),
32 GB endurance, or SAC/BIC avalanche (N=2¹⁸, zero |z|>5 cells).

The non-pow2 reduction FAILs are a test-setup artifact (proven by splitmix64 control), not a candidate signal.

**Files:** Q1 JSONs `q1_<name>.json` · Q2 logs `q2_<name>_<seq>_<red>.log` (384 cells) · Q3 logs `q3_<name>.log` ·
generators [`q_gen_reduce.c`](q_gen_reduce.c), [`q_avalanche.c`](q_avalanche.c) · parsers [`parse_q2.py`](parse_q2.py), [`parse_q3.py`](parse_q3.py) · control note [`CONTROL_NOTE.md`](CONTROL_NOTE.md).
