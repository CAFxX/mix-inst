# GA harness for the RV64 `mix` search — DESIGN

**Date:** 2026-10-03. **Author:** Muse (subagent). **Status:** implemented, validated, running.

## 1. Goal

Evolve `mix` candidates (keyed 64→64-bit, bijective per fixed key, single-cycle
unrolled combinational) over the validated Feistel family **plus Carlo's
almost-zero-overhead step genes** (P-box, XOR-constant, AND/OR-mask), minimizing
(delay, cells, area) under the exact staged battery (S0→S4 + Q1) used by the
manual rounds. The GA never edits [`PARETO.md`](../PARETO.md); it flags archive entries and the
human coordinator verifies from raw logs.

## 2. Genome (JSON, see [`genome.py`](genome.py))

```json
{
  "rounds": 6,
  "tags": ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "chi32v_notr"],
  "pbox_where": "none",
  "pbox_perm": null,
  "const_where": "none",
  "const_fam": null,
  "mask": "none"
}
```

### 2.1 Round-function tags (validated pool — every tag was S0–S2-validated in
some construction in rounds 8–20; no invented F types)

General (any round): `s1_311 s1_713 s1_517 chi_311 chi_713 chi32v_311 chi32v_517
chi32w_311 ps_311`.
Final-round only: `s1_notr chi_notr chi32v_notr chi32w_notr chi_keyin_notr
chi_fm03 chi_fm07 chi_fm11 chi_fm311 chi_fm16 ps_notr`.

Notes:
- `chi` = b_i=a_i^(~a_{i+1}&a_{i+2}); `chi32v` = (1,3); `chi32w` = (3,1).
- `ps_311` = lin(3,11)( chi16(R[31:16]) || S1(R[15:0]) ) ^ rk (r15).
- `chi32w_notr` is a composition of two validated pieces (chi32w nonlinear from
  r20 rounds 2/4 + the final-round truncation pattern); the S1/S2 stages
  re-validate it before it can enter the archive.
- Round keys: the standard affine schedule
  `RK32(k,i) = rotl64(k,13*(i+1)) ^ (i+1)*GOLDEN64` (r7/r8/r9 schedule; key-schedule
  variants were neutral-to-negative — no key-schedule gene).
- Whitening: OFF by construction (r15: +2.1u AND an S1 PB rejection).

### 2.2 P-box gene (free wiring)

- `pbox_where ∈ {none, between64, inF32, replacerot}`.
- `between64`: after each non-final round, the 64-bit state (L,R) passes through
  a fixed 64-bit bit-permutation P64. Bijective (P is a permutation).
- `inF32`: every round's F sees `P32(R)` instead of `R`. Inside F — safe.
- `replacerot`: every round whose tag carries a 2-rotation linear
  `lin(x)=x^rotl(x,a)^rotl(x,b)` instead computes
  `lin'(x)=x^rotl(x,a)^P32(x)` (one rotation swapped for a permutation).
  Rounds without such a linear are unaffected. Inside F — safe.
- Permutation families (fixed tables, `PERM_TABLES` in [`genome.py`](genome.py)):
  - P64: `bitrev64 byteswap64 nibrev64 interleave64 transpose8x8 rot64_16 rot64_32`
  - P32: `bitrev32 byteswap32 nibrev32 interleave32 transpose8x4 rot32_8 rot32_16`
  - `interleave`: out[2i]=in[i], out[2i+1]=in[i+w/2] (perfect shuffle of halves).
  - `transpose8x8`: 8x8 bit-matrix transpose; `transpose8x4`: 8x4 transpose.

### 2.3 XOR-constant gene (inverters only)

- `const_where ∈ {none, round_F, prepost}`, `const_fam ∈ {bit, byte, iota}`.
- `round_F`: round i computes F over `R ^ C_i` (32-bit), breaking round
  self-similarity (slide resistance) at near-zero cost.
- `prepost`: `val ^= C_PRE64` at input, `out ^= C_POST64` at output.
- Families: `bit`: `C_i = 1 << ((i-1) % 32)`; `byte`:
  `C_i = (i * 0x01010101) mod 2^32`; `iota`: low 32 bits of the Keccak-f round
  constants (`0x00000001, 0x00008082, 0x0000808A, 0x80008000, 0x0000808B,
  0x80000001, 0x80008081, …`).
- `C_PRE64 = 0x9E3779B97F4A7C15` (golden ratio), `C_POST64 = 0xBF58476D1CE4E5B9`
  (splitmix64 gamma) — both nothing-up-my-sleeve. XOR with a constant is a
  bijection everywhere.

### 2.4 AND/OR-mask gene (cheap nonlinearity — F-INTERNAL ONLY)

- `mask ∈ {none} ∪ {r1_A5, r1_0F, r1_00FF, r1_SP, r1_H2, r2_*, r3_*}` (15 combos):
  `masknl(x) = x ^ ((x >> r) & PAT)`, `r ∈ {1,2,3}`,
  `PAT ∈ {0xAAAAAAAA, 0x0F0F0F0F, 0x00FF00FF, 0x01010101, 0x0000FFFF}`.
- Placement: applied to the **nonlinear layer's output inside F**, before the
  linear/key steps, uniformly across tags:
  - linear tag: `F = lin(masknl(N(R))) ^ rk` (or `lin'` under `replacerot`)
  - notr tag: `F = masknl(N(R)) ^ rk`
  - fm tag: `y = masknl(chi(R)) ^ rk; F = y ^ rotl(y,m)` (fm311 analogous)
  - keyin tag: `F = masknl(chi(R ^ rk))`
  - ps tags: `t = ps_nonlin(R); F = lin(masknl(t)) ^ rk` (ps_notr: no linear)
- **Bijectivity:** every mask placement above is strictly inside F; the Feistel
  round `(L,R) → (R, L^F(R))` is a bijection for *arbitrary* F, so the full
  construction is bijective-per-key by construction. The decoder raises
  `ValueError` on any mask placement outside this set (fail-closed). As a
  runtime backstop, every emitted candidate passes a fixed-key distinctness
  check (2000 random inputs → 2000 distinct outputs); a non-bijective
  construction would fail it. Standalone (non-F) mask transforms are NOT in the
  genome — Carlo's `x ^= ((x>>>r) & MASK)` form with destructive masks is
  excluded by the schema.

### 2.5 Bijectivity proof sketch (whole genome)

Each round is `(L,R) → P?(R, L^F'(R))` where `F'` is F with the inF32/mask/
replacerot/const genes folded in (arbitrary function — no bijectivity needed)
and `P?` is an optional fixed bit-permutation (bijection). Inverse:
un-permute, then `(L',R') → (R'^F'(L'), L')`. Pre/post XORs are bijections.
Composition of bijections is a bijection. ∎

### 2.6 Cost model for the new genes (Sky130 unit-delay flow)

| Gene | Expected delay | Expected cells | Basis |
|---|---|---|---|
| P-box (any) | **~0u** | **~0** | Pure wiring; ABC sees net renaming only. (Real P&R routing is S5 territory.) |
| XOR-const 32b | ~0u (absorbed) worst popcount(c)×1u | ~popcount(c) INV | c_i=0 → wire, c_i=1 → inverter; ABC bubble-pushing usually absorbs. iota: ~8–14 ones. |
| pre/post 64b | ~0u | ~2×popcount | At I/O boundary; absorbed. |
| mask step | **~2u** on masked bit-paths | **~2×popcount(PAT)** | 1 AND2 + 1 XOR2 per 1-bit. A5: ~32 cells; SP: ~16 cells. Real nonlinearity, not free. |

The S0 stage measures the true numbers; the table is only a prior.

## 3. Operators ([`genome.py`](genome.py))

- **Crossover:** single-point on tags (point ∈ 1..min(n1,n2)−1); uniform
  crossover on scalar genes (`pbox_where/perm`, `const_where/fam`, `mask`,
  `rounds` follows the tag list length). Repair: a FINAL tag landing on a
  non-final round is replaced by a random general tag (retry ≤8×, else clone).
- **Mutations** (one per offspring; weights below are normalized by their sum
  0.90): tag swap .22, linear swap .12, truncation toggle .08, keyin flip .04,
  final-mix change .08, round-count ±1 .04, pbox_where .08, pbox_perm .07,
  const_where .05, const_fam .03, mask .09.
  (`none`↔value moves are symmetric; `pbox_perm` draws from the width family
  matching `pbox_where`.)
- **Guided mutation** (§10): 30% of offspring are produced by the
  diagnosis-driven operator reading a recent failure annotation; 70% by the
  random operators above (plus crossover).
- **Dedupe:** fingerprint = sha256(canonical genome JSON ‖ model outputs on 64
  fixed vectors). Checked against every evaluated genome *and* all seeds before
  any synthesis. (Existing rule: pairwise-distinct model outputs.)

## 4. Fitness — staged (see [`evaluate.py`](evaluate.py))

Multi-objective: minimize (delay, cells, area) from S0 ([`s0_delay.py`](../fast_battery/src/s0_delay.py),
authorized path, dual-analyzer agreement inside).

- **Emit** → build C harnesses → **xcheck** 10k vectors C-vs-Python (gate).
- **Stage A (S0):** kill if rc≠0, delay > 93.15u (0.9×103.5 hard bar), or the
  point is **dominated by BOTH Pareto archives** on all three axes → discard,
  no statistics burned. (A candidate that is S-dominated but could extend the
  Q frontier survives — see the two archives below.)
- **Stage B (S1):** [`s1_screen.py`](../fast_battery/src/s1_screen.py) (absolute outdir). Kill on rc≠0 (honors every
  kill field incl. `cal_verdict`).
- **Stage C (S2):** `diffprof` N=2^22, 115 deltas. Parse the summary line; kill
  if `max_repeats ≥ 10` **or `max|z| > 40`** (structural rule from the
  notr5/drop4 "fast number, broken design" class — formal PASS is not enough).
- **Archives (two):** a Stage-C survivor enters **Archive S** (provisional) if
  not S-dominated, and **Archive Q** (provisional) if not Q-dominated →
  **Stage D:** S3 PractRand 1GB ×2 configs, S4 SmallCrush, Q1 SAC/BIC. Any
  fail → evicted from both, logged dead. Pass → confirmed; Q membership
  additionally requires `bic ≤ 0.02` (evicted from Q otherwise, kept in S).
  The log flags Frontier-S/Q candidacy **without editing [PARETO.md](../PARETO.md)**.

## 5. Selection ([`ga.py`](ga.py))

(μ+λ), μ=20, λ=12. Nondomination rank on (delay, cells, area) for S0-evaluated
individuals (S1/S2 kills rank below all survivors); crowding-distance tiebreak;
truncation to μ (elitist). Generation 0 = seeds (below).

## 6. Seeding ([`seed.py`](seed.py))

- **Archive:** every candidate from rounds 6–20 satisfying ALL of: S0 numbers
  parsed from the round table; S1 `CAL_PASS`; S2 `PASS` with `max_repeats < 10`
  **and** `max|z| ≤ 40` (the structural rule — excludes the notr5/drop4 "fast
  number, broken design" class even when the formal verdict passed); S3/S3b/S4
  rc=0; Q1 `sac_z5 == 0`. **No re-synthesis**: fitness comes from the logs.
  Non-genome-expressible designs (e.g. r18 palk's palindromic key schedule)
  seed the archive only, flagged `genome: null`.
- **Population:** the expressible subset, each **bit-exact validated**
  (`decode_np(genome)` vs the checked-in `model.py` on ≥1k vectors; mismatch →
  archive-only), plus Carlo's hand-built cheap-layer seeds:
  1. `hand_const_iota`: chioff13all tags + `round_F`/`iota` constants.
  2. `hand_replacerot`: chioff13all tags + `replacerot`/`transpose8x4`.
  3. `hand_between64`: chioff31 tags + `between64`/`interleave64`.
  4. `hand_mask`: chioff13all tags + `mask=r2_A5`.
  5. `hand_prepost`: fm07 tags + `prepost` constants.
  Random genomes fill to μ=20.

## 7. Concurrency (`[evaluate.py](evaluate.py)::polite_wait`)

Never >2 heavy pipelines system-wide. Before each heavy stage, count distinct
*foreign* (non-`ga_g*`) candidate names with live
`yosys|s1_screen|s0_delay|RNG_test|diffprof|sc_|practrand` processes; if ≥2,
sleep 300 and re-check. (Round 21 runs concurrently.)

## 8. Checkpointing & logging

- `ga/state/checkpoint.pkl` after every evaluation and generation: population,
  archive, fingerprint set, RNG state, generation, wall-clock start, stats.
  Resume: `python3 ga/ga.py --resume`.
- `ga/state/STOP`: presence stops the loop cleanly at the next checkpoint.
- `ga/GA_LOG.md`: append-only, dated — generation summaries, archive
  movements, kills with construction-scoped reasons, frontier-candidacy flags.
- 48h wall-clock budget from first start (persisted).

## 10. Analytical failure analysis ([`evaluate.py`](evaluate.py), [`ga.py`](ga.py))

The battery is a diagnostic instrument, not a black-box oracle. Every
statistical death is recorded with three fields (`[evaluate.py](evaluate.py)::annotate`):

1. **Failing signal** — the precise mechanism: which stage; S1 family rejection
   lists (LIN/DIFF/PB/RD with counts); S2 summary (`max_repeats`, `max|z|`,
   and every single-bit spike delta with its |z|); S3/S4 which config/test;
   Q1 `sac_z5` / `bic_maxcorr`.
2. **Mechanistic hypothesis** (`[evaluate.py](evaluate.py)::hypothesize`) — a rule-based,
   construction-scoped diagnosis, explicitly labeled HYPOTHESIS. Current rules:
   - S1 LIN-heavy → linear-hull trail through the rotation pairs
     → `guided_linear`
   - S1 DIFF → weak nonlinear layer/chi offsets → `guided_nonlinear`
   - S1 PB/RD only → round self-similarity/slide structure → `guided_const`
   - S2 many single-bit |z| spikes → mid-round diffusion collapse (the class
     S1's marginal screen is blind to) → `guided_diffusion`
   - S2 repeat-count kill → round-count phase transition → `guided_rounds_up`
   - S3 PractRand → residual structure: MORE nonlinearity needed, not more
     linear mixing → `guided_nonlinear`
   - Q1 bic high → unmixed final nonlinear layer (the known notr blemish
     class) → `guided_finalmix` (the measured y^rotl(y,m) cure)
   - Q1 sac → avalanche failure → `guided_diffusion`
3. **Suggested fix** — a guided-mutation op name (`[ga.py](ga.py)::guided_mutate`).

- **Failure-annotated archive** (`state.failures`): every dead individual
  stores its annotation plus its genome and gene-pattern tags
  (`[evaluate.py](evaluate.py)::gene_pattern`: truncation tags, per-tag family counts,
  pbox/const/mask genes, round count).
- **Association table** (`state.assoc`): `(failure_stage, gene_pattern_tag) →
  count`, snapshotted into [GA_LOG.md](GA_LOG.md) each generation. Over time this shows
  which gene patterns correlate with which failure modes (e.g. "S2: chi_notr
  on final + many spikes"), letting the search learn mechanisms, not just
  fitness values. New hypotheses graduate to `hypothesize` rules when they
  survive several independent confirmations.
- **Guided mutation** (`[ga.py](ga.py)::guided_mutate`, 30% of offspring): picks a
  recent death (uniform among the last 25), reads its `suggested_fix`, and
  applies the targeted edit to that dead genome (falling back to a random
  mutation if the edit is inapplicable or invalid). 70% stay random/crossover
  to keep diversity.

Guardrails: a guided edit that fails schema validation falls back to random
mutation (never an invalid genome); hypotheses are labeled as hypotheses in
the log; verdicts stay scoped to the tested construction (AGENTS.md /
[VERDICT_SCOPE.md](../VERDICT_SCOPE.md) rules).

## 11. Validation of the harness itself ([`test_ga.py`](test_ga.py))

- Permutation tables are true permutations (bijective) — numpy vs independent
  bit-loop reference.
- C/RTL P-box emission matches the numpy tables (via xcheck on a perm-heavy
  genome + S0's netlist-equivalence check).
- `decode_np` of the 3 required seeds (r20 chioff13all, r20 chioff31, r19 fm07)
  matches checked-in models bit-exactly on 1k vectors.
- Crossover/mutation always yield schema-valid genomes (fuzz 500×).
- Archive domination logic on a synthetic set (incl. edge: equal points).
- Checkpoint save/load round-trip preserves RNG state.
- Every test is capable of failing (mutation-tested logic: e.g. a corrupted
  table must fail the permutation test).
