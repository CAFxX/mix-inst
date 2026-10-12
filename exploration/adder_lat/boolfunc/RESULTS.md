# Design B (bipartite thin-Toffoli, E+O) — Results

**Verdict: KILLED by Fisher (diffusion), NOT by cost.** The terminal verdict is
recorded as **O153** in [VERDICT_SCOPE.md](../../VERDICT_SCOPE.md) (the brief
said O149, but O149 was claimed by the D4 lane by write time — per the standing
rule the ledger is the numbering authority; a parallel recovery worker recorded
O153 with Fisher runs on all 5 offset sets, so no duplicate row was added).
Full record: [RESULTS_B.md](RESULTS_B.md).

## 1. Verilog

[boolfunc_b.v](boolfunc_b.v) — 64-bit in/out, parameters A, B (odd).
Stage E: `out[2i] = in[2i] XOR (in[(2i+A)%64] AND in[(2i+B)%64])`, odd bits
passthrough. Stage O: mirror (odd targets, even controls frozen). Each stage is
32 disjoint Toffolis with frozen controls → bijective by construction.
Concrete wrappers: `boolfunc_b_13` (A=1,B=3), `boolfunc_b_17` (1,7),
`boolfunc_b_311` (3,11), plus `boolfunc_b_133` (1,33), `boolfunc_b_335` (3,35)
added for the large-offset follow-up.

## 2. Bijectivity — brute-forced, not assumed

[verify_bij.py](verify_bij.py): n=8 exhaustive (all 256 inputs) for offsets
(1,3), (1,7), (3,11)→(3,3 mod 8) — **0 collisions, PASS**; scalar bit-array
reference == vectorized numpy model on all inputs; n=64 sequential 2^18 outputs
all distinct. **BIJECTIVITY: PASS.**

## 3. S0 — measured via `exploration/run_synth.py` (pinned yosys 0.69, mini.genlib, dual-analyzer XCHECK)

Backoff-gated runner [run_all_b.sh](run_all_b.sh) (cleared-flag single-gate),
all under `nice -n 19`; full log [run_all.log](run_all.log):

| top | cells | area | crit |
|---|---|---|---|
| boolfunc_b_13 | 224 | 512 | **6.2u** |
| boolfunc_b_17 | 224 | 512 | **6.2u** |
| boolfunc_b_311 | 224 | 512 | **6.2u** |

XCHECK clean on all three (analyze.py == analyze2.py); ref mul64 103.5u stable.
**6.2u ≤ 10u → cost gate PASSED** (better than the 7.0u estimate; offset is pure
wiring so all offsets synthesize identically).

## 4. Fisher triage — `lin_diff.screen_lin_diff` verbatim, N=2^18, 10 keys

[screen_b.py](screen_b.py); quick avalanche proxy first, then full Fisher on the
canonical (1,3):

- Avalanche proxy (corrected 64-bit popcount — the first version of
  `popcount_vec` had a `range(6)` bug counting only the low 6 bits; fixed):
  (1,3) mean 2.44 bits/flip, min 1.97; (1,7) 2.44; (3,11) 2.43; (1,33) 2.25;
  (3,35) 2.25. All far below the ~32 needed — the proxy cannot discriminate,
  all offsets are broken the same way.
- **FISHER(1,3): KILL — lin=FLAG (10/10 keys, D=4096/4096, logp=-inf),
  diff=FLAG (10/10 keys, worst|z|=1.48e6), nrej=20.** Measured by the
  backoff-gated runner, `run_all.log` ("FISHER(1,3): KILL lin=FLAG diff=FLAG
  nrej=20").

## 5. Mechanism — sequential-input rank deficiency (offset-independent)

The Fisher screen feeds sequential inputs x<2^18, so only input bits 0..17
vary. Liveness propagation (AND live iff both inputs live; XOR live iff either
live — key-independent since keyed inputs only move the constant) through E→O
gives, for **every** odd (a,b) pair (all 1024 enumerated): at most **45/64**
output bits vary. The LIN family flags rank ≤ 61, so Design B is structurally
Fisher-dead for all odd offsets. Measured live counts: (1,3)=19, (1,7)=19,
(3,11)=22 — consistent with D=4096/4096.

The parent's large-offset hypothesis ("offset 33 makes high target 60's
controls, bits 29/31, vary") is arithmetically wrong: the controls are bits 61
and (60+33)%64=29, both constant under sequential inputs (only bits 0..17
vary). Liveness: (1,33)=18, (3,35)=18 — worse than the small offsets. A
confirmatory full Fisher run on (1,33) was launched (backoff-clear, nice-19);
result: PENDING at write time — appended below when it lands.

## 6. (1,33) confirmatory Fisher result

**FISHER(1,33): KILL — lin=FLAG (10/10 keys, D=4096/4096, logp=-inf),
diff=FLAG (10/10 keys, worst|z|=1480000.0, fisher_logp=-inf), nrej=20.**
Independent run (`screen_b.py 1 33`, backoff-clear, nice-19, completed
2026-10-12). Signature identical to (1,3). The large-offset hypothesis is
falsified with the real instrument, confirming the recovery worker's
`screen_b_large.log` and the O153 mechanism analysis. Liveness bound for
(1,33): 18/64 output bits vary (upper bound; LIN needs rank ≥ 62).
