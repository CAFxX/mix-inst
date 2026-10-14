# Round 7 results — Feistel F-axis + key-schedule axis (r6_feist8_spn family)

Date: 2026-10-01. All numbers measured on the shared 2-CPU box unless noted.
Reference for S0: mul64 crit=103.5u, area=35323 (re-measured per flow); bar = 0.9x.

## Verdicts

| candidate | F linear / key schedule | S0 delay (ratio) | S1 | S2 | S3 | S4 | bijectivity | verdict |
|---|---|---|---|---|---|---|---|---|
| r7_feist8_r311 | `x^rotl32(x,3)^rotl32(x,11)` / r6 schedule | 84.3u (0.814x), 8218 cells | CAL_PASS (0/468 marg, 0/10 LIN, 0/10 DIFF) | PASS (maxrep 0, max\|z\| 3.7) | PASS 16M→1G | PASS 15/15 | 200k/200k inv | **SURVIVES** |
| r7_feist8_r517 | `x^rotl32(x,5)^rotl32(x,17)` / r6 schedule | 86.3u (0.834x), 8652 cells | CAL_PASS (0/468, 0/10, 0/10) | PASS (maxrep 0, max\|z\| 3.5) | PASS 16M→1G | PASS 15/15 | 200k/200k inv | **SURVIVES** |
| r7_feist8_rksimple | r6 linear / `rk=rotl64(k,13(i+1))` (no const) | 87.4u (0.844x), 8510 cells | CAL_PASS (0/468, 0/10, 0/10) | PASS (maxrep 0, max\|z\| 4.1) | PASS 16M→1G | PASS 15/15 | 200k/200k inv | **SURVIVES** |
| r7_feist8_rkcheap | r6 linear / `rk=k^(i+1)*G` (no rot) | 87.4u (0.844x), 8552 cells | CAL_PASS (0/468, 0/10, 0/10) | PASS (maxrep 0, max\|z\| 4.0) | PASS 16M→1G | PASS 15/15 | 200k/200k inv | **SURVIVES** |
| r7_feist8_mid32 | 32-bit Midori almost-MDS / r6 schedule | n/a (killed at S1) | **KILLED**: LIN rej=10/10, DIFF rej=10/10 | — | — | — | n/a (decomposes) | **KILLED** |

Details:
- **S0**: via [`run_synth.py`](../run_synth.py) only; [analyze.py](../../synth/analyze.py) == [analyze2.py](../analyze2.py) cross-check passed for all 4.
  All 4 beat r6 (86.5u/0.836x): r311 is fastest at 84.3u (0.814x).
- **S1**: amended 4-family screen, 10 keys. All 4 survivors: PB rej=0, RD rej=0, LIN rej=0, DIFF rej=0.
  Per-candidate logs: `results/<name>/s1_result.json`, `s1_stdout.log`.
- **S2**: diffprof, key 0x123456789abcdef0, N=2^22, 74 deltas, kill threshold 1000 repeats.
  All 4: max_repeats=0. Logs: `results/<name>/s2.log`.
- **S3**: PractRand stdin64, 16MB→64MB→256MB→1GB, key 123456789abcdef0, stride 1. All 4: no FAIL.
  Logs: `results/<name>/s3.log` (+ `s3/` per-stage logs).
- **S4**: TestU01 SmallCrush, key 123456789abcdef0, golden `mix(0,key)` checked at startup.
  All 4: "All tests were passed" (15/15). Logs: `results/<name>/s4.log`.
- **C↔Python**: xcheck 10k/10k PASS for all 4 (`results/<name>/xcheck.log`).
- **RTL**: iverilog 24/24 vectors PASS vs Python model for all 4 (incl. mid32 — its kill is design, not bug).
- **Bijectivity**: structural (8-round Feistel + XOR whitening = permutation for any F) PLUS
  explicit C inverse (`fast_battery/src/s5_invert.c`, `#include`s the shipped impl.c):
  200,000 random (val,key) round-trips + 24 edge vectors x 4 keys, 0 failures, all 4.
- **Linear-layer bijectivity**: GF(2) rank 32/32 for r311, r517, mid32, r6-linear (import-time guard in [models/r7c.py](models/r7c.py)).

## Kill: r7_feist8_mid32

Full report: `results/r7_feist8_mid32/KILL_REPORT.md`.
Root cause: the 32-bit Midori layer is column-local (two independent 4-nibble columns, one per
16-bit half), so F splits into two independent 16-bit functions and the 8-round Feistel
decomposes into two independent 32-bit ciphers concatenated. Evidence: rank of 64 consecutive
outputs = 33 (vs 63 for r311); hi16 of each half pairwise affine-equal (496 relations);
input deltas 2^16/2^17 -> identically-zero low-8-bit output diffs (logp ~ -1e11/-1e12).
Follow-up lead (untested): an 8-nibble single-column Midori adaptation would not split lanes.

## Golden outputs (mix(0, 0x123456789abcdef0)) — verified by S4 startup checks

- r311: `a2b59c577b47c976`
- r517: `d03b74f8ad53c5a6`
- rksimple: `ef6c02d754d1d9c8`
- rkcheap: `f5b8cd8ba5062b5f`

## Notes

- rksimple: k=0 -> all round keys 0 (weak-key structure); rkcheap: round keys differ only by
  known constants (related-key structure). Neither affects the fixed-key battery; flag for
  any future multi-key / related-key analysis.
- r311 vs r517: both rotl-XOR linears; r311 slightly faster (84.3u vs 86.3u) and smaller
  (8218 vs 8652 cells). No statistical daylight between them at this battery depth.
- Environment: 2 VM reboots during the run; all /tmp binaries rebuilt after each; all result
  logs live under `results/<name>/` (persistent workspace).
