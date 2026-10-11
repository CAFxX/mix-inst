# h_xorspn3 — TestU01 SmallCrush + Dieharder results (2026-10-01)

Model: `mix_h_xorspn3_s` from `round4/models/r4_hybrid.py`
(xorshift64 pre-diffusion + 3-round SPN with S1 S-box + Midori M).
C port in `testu01_hx.c` / `gen_dh.c`, verified against the Python model on
12 reference values (keys 0x123456789ABCDEF0 and 0x0, vals 0..5) — all match.

Input distribution for ALL runs: sequential 64-bit counter values
(val = 0, 1, 2, ...), i.e. hash output stream, not a PRNG stream.

## TestU01 SmallCrush 1.2.3

Key 0x123456789ABCDEF0 (ran twice, deterministic):
14/15 pass. Only sknuth_SimpPoker flagged: chi2=70.62/19dof, p=7.3e-8
(N=1, n=400000, r=24, d=64, k=64). All other p-values in [0.09, 0.84].

Key 0x0: 15/15 pass, incl. SimpPoker chi2=35.47/19dof, p=0.01.
=> SimpPoker deviation is key-dependent, far milder than r3_xorlin_qm's p<1e-300.

Logs: smallcrush_key1.log, smallcrush_key0.log

## Dieharder 3.31.1, full battery

Tooling: dieharder is the Debian package dieharder 3.31.1.4-1.1build1
(bin + libdieharder3t64 + libgsl27). It does NOT survive rootfs rebuilds
(machine rebooted twice mid-task, binary gone each time); reinstall from
/var/cache/apt/archives/*.deb (RV-backed, survives reboots).
Correct invocation for raw binary files is `-g 201`, NOT `-g 202`
(-g 202 = formatted ASCII; man page is explicit). This resolves both the
round-3 "not found" note and the -g 202 confusion.

Data: hx_key1_200MB.bin (209715200 bytes = 52428800 uint32, key
0x123456789ABCDEF0, sequential). Log: dieharder_key1.log (98 rows).

Result: 88 PASSED, 7 WEAK, 3 FAILED — but all 3 FAILEDs are proven
file-rewind artifacts (see below), and 4 of the 7 WEAKs are on
rewind-heavy tests.

FAILEDs (all rewind artifacts, each re-verified rewind-free -> PASS):
- marsaglia_tsang_gcd p=0.00000004 (38 in-test rewinds; test needs 2e9
  uints from a 52.4M-uint file). Rerun -d 17 -t 200000, 0 rewinds:
  p=0.4165 / 0.9609 PASS (dieharder_gcd_notrewound.log)
- rgb_lagged_sum ntup 19 p=0.00000000 (38 rewinds). Rerun -t 10000,
  0 rewinds: p=0.604 PASS (dh_lagsum19_t10k.log)
- rgb_lagged_sum ntup 24 p=0.00000004 (47 rewinds). Rerun -t 10000,
  0 rewinds: p=0.787 PASS (dh_lagsum24_t10k.log)

WEAKs:
- diehard_squeeze p=0.00399756, diehard_sums p=0.00231708 — 0 in-test
  rewinds, clean.
- diehard_opso p=0.00030671 (~10 rewinds), diehard_oqso p=0.00003398
  (~12 rewinds), rgb_bitdist ntup 11 p=0.99934968 (~63 rewinds),
  rgb_lagged_sum ntup 15 p=0.00053352 (~38 rewinds),
  marsa_gcd row 1 p=0.00306608 (38 rewinds) — rewind-tainted.

Battery tail (individual runs, key1 data, rewind-free):
- rgb_lagged_sum ntup 25-32: all PASS (p 0.16-0.96)
- rgb_kstest p=0.256 PASS; dab_bytedistrib p=0.0926 PASS (t=10M rerun,
  0 rewinds: p=0.645 PASS); dab_dct p=0.144 PASS;
  dab_filltree p=0.664/0.278 PASS (t=5M rerun, 0 rewinds: p=0.018/0.312);
  dab_filltree2 p=0.428/0.797 PASS; sts_monobit p=0.890 PASS;
  sts_runs p=0.518 PASS.

Genuine anomaly — dab_monobit2 (block-monobit over block sizes 2^k words):
"too perfect" bit balance, high-side p-values, reproduces across keys:
- key1, 200MB, default (1 rewind): p=1.00000000 FAILED
- key1, 600MB (hx_key1_600MB.bin), default, 0 rewinds: p=0.99994418 WEAK
- key0, 300MB (hx_key0_300MB.bin), default, 0 rewinds: p=0.99999987 FAILED
- smaller t (1M/5M/20M): p=0.55/0.38/0.64 PASS
sts_monobit (single block size) is clean (p=0.89), so this is specific to
the multi-block-size aggregation. Worth a follow-up (e.g. control run of
monobit2 on SplitMix64/urandom with sequential inputs).

## Environment notes
- /tmp is a 512MB tmpfs AND gets cleaned while the machine runs; also the
  VM rebooted twice during this task, wiping /tmp and /usr/bin/dieharder.
  All durable artifacts are in this directory (workspace, persistent).
- The 600MB/300MB data files are kept (hx_key1_600MB.bin, hx_key0_300MB.bin)
  for re-verification.
