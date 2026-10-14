# Peer review — round-4 hybrid candidate `h_xorspn3` (consolidated finalist battery)

**Design:** `round4/rtl/flat2/r4_h_xorspn3.v` — xorshift64 pre-diffusion +
3-round SPN (S1 4-bit S-box + Midori almost-MDS binary matrix + nibble shuffle),
key-whitened. **Date:** 2026-10-01.
**Coordinator:** this report consolidates seven independent workers (gates/synthesis
re-verification, pipeline, PractRand, TestU01, differential characterization,
P&R, screen-methodology diagnosis), plus coordinator remediation and new
measurements. It follows the structure of [`peer_review_r3.md`](../peer_review_r3.md).

**Bottom line: `h_xorspn3` is DISQUALIFIED as a finalist.** It genuinely passes
both hard gates — delay 34.5u reproduced to the digit (0.679× a freshly
re-measured 50.8u multiplier reference, 9.8u under the 44.3 bar), CAL_PASS
reproduced (0/448 per-bit + 0/20 reduction Holm rejections at α=0.01),
bijectivity proved structurally and empirically, 1-cycle pipeline verified —
and it even posted the best silicon number yet (0 DRC, 4.95ns GR+parasitic STA,
0.39× the multiplier). But PractRand rejects it decisively (BRank FAIL at the
first logged 16MB checkpoint, R=+3008 → +9306 at 256MB, key-independent) and
the differential profile shows catastrophic full-64-bit joint structure
(~41,900 output-difference repeats at N=2²², probability ~2⁻¹³,
key-independent, confirmed in two implementations). The screen passed it
because all 468 cells are marginal or small-window statistics — blind by
construction to full-word joint linear structure. A screen-methodology
diagnosis with prototyped fixes is included (§3); `r3_xorlin_qm` remains the
standing winner.

## Design specification

`x = xorshift64(val ^ key)` with `x^=x>>12; x^=x<<25; x^=x>>27`; then 3 rounds
of `{ x ^= rk[i]; x = shuffle(midori_M(sbox16(x))) }`; `out = x ^ rk[3]`.
`rk[i] = rotl64(key,13(i+1)) ^ ((i+1)*0x9E3779B97F4A7C15)`.
S1 = [0,1,2,4,3,8,F,C,9,5,B,6,7,E,D,A] (THF/Blink, DU=4, max|W|=8 optimal).
Midori M per 4-nibble column: `out_j = parity(all 4) ^ in_j` (rank 64,
involutory). Shuffle `_PERM=[0,10,5,15,14,4,11,1,9,3,12,6,7,13,2,8]`
(`y_nibble[i]=x_nibble[PERM[i]]`).
Model: `round4/models/r4_hybrid.py` (`mix_h_xorspn3_s` scalar,
`mix_h_xorspn3_np` numpy).

---

## 1. Findings by severity

### Critical

- **C1 [batteries] — PractRand FAIL, decisive, key-independent. DISQUALIFYING.**
  `RNG_test stdin64`, sequential inputs (deployment distribution), PractRand 0.96:
  BRank(12) FAIL at the first logged checkpoint (16MB, R=+3008), growing
  monotonically to R=+9306 (p≈6e-8413) at 256MB. Key 0x0 repeats the signature
  (R=+5868 at 64MB). Secondary failures concentrate in the low-4-bit fold and
  grow monotonically: [Low4/64]Gap-16:A R=+498.7 (p=1.3e-392), B R=+367.0
  (p=1.6e-331), FPF/16:all R=+84.2 (p=1.7e-78) at 256MB. Comparison:
  r3_xorlin_qm failed BRank only at 256MB (R=+622…+754) — h_xorspn3 fails at
  least 16× earlier in stream length with 12× the terminal R-score. Logs:
  [`exploration/hx_practrand/run1_key1234.log`](../hx_practrand/run1_key1234.log), [`run2_key0.log`](../hx_practrand/run2_key0.log).
- **C2 [differential] — catastrophic full-64-bit differential structure.**
  N=2²² deduped sequential pairs × 72 deltas × 2 keys, C profiler bit-exact
  1500/1500 vs the Python model: **57/72 deltas flagged at both keys**
  (r3: 40/37); full-64-bit output-difference repeats up to **41,889/41,916**
  for δ=0x400, key-independent — differentials at probability ~2⁻¹³ where ~0
  are expected. Confirmed in the independent numpy implementation (bit-exact
  dx 3000/3000; repeat phenomenon reproduced). Raw tables:
  `round4/results/r4_h_xorspn3/`.

### Major

- **M1 [batteries] — TestU01 SmallCrush SimpPoker FAIL (p=7.3e-8); 14/15 pass.**
  Fresh C port (`round4/testu01_h_xorspn3.c`), bit-exact sanity vs Python model
  (`f(0,0x1234…)=0x726ecd2eeb1fb24f`, `f(0,0)=0xe8aa0581be8e17cc`), key
  0x123456789ABCDEF0, TestU01 1.2.3. Less extreme than r3's p<1e-300 but a
  clear fail (outside [0.001, 0.999]).
- **M2 [methodology] — the calibrated screen is blind by construction to the
  defect that killed the candidate.** All 468 cells are marginal (per-bit) or
  small-window (mask8/mask32, 1-D lemire/mod projections). A GF(2)-linear
  dependency spread over all 64 bits and across consecutive outputs is
  invisible to every cell: marginalization destroys the evidence. Measured:
  all contiguous 8/16/32-bit sub-windows full-rank; no exact global bit
  relation; max |corr(in_a,out_b)| = 0.0085 (null 0.0088). S1 itself is
  cryptographically optimal (max|W|=8, DU=4, degree 3) — this is a
  construction-level linear-hull weakness (3-round SPN + linear pre-diffusion
  on the counter distribution), not a component flaw. Short-range temporal:
  64 consecutive outputs span 55.9 dims (null 63.2; r3 62.7; splitmix64 63.1).
- **M3 [differential] — the truncated-differential picture is MIXED, not
  uniformly worse than r3.** Per-output-bit flip bias max|z| 38–39 (δ=0x3)
  vs r3's 222; low-8-bit χ² ≤ 5018 (δ=2⁶³) vs r3's ~29000; pairwise low-8-bit
  collision-forcing advantage ≤1.10× (r3: ≤1.25×). The catastrophic axis is
  specifically the full-64-bit differentials (C2), which r3 barely exhibits
  (12 repeats).
- **M4 [reporting] — PractRand "16KB first failure" unevidenced; corrected.**
  The worker's 16KB/32KB/64KB rows came from memory of a killed pre-reboot run;
  the durable log's first checkpoint is 16MB. "Four orders of magnitude" was
  overstated — honest: ≥16× earlier stream length, 12× terminal R-score.

### Minor

- **m1** [batteries] Dieharder not run: `/usr/bin/dieharder` was present
  earlier today (verified 43312 bytes) but the VM rebooted twice and /usr is
  ephemeral; reinstall blocked (apt lists locked by another process, package
  not locatable). Low signal given two decisive battery failures (same
  rationale as r3's m1).
- **m2** [process] The TestU01/Dieharder worker completed with no captured
  handoff and /tmp was wiped by a reboot; SmallCrush was re-run by the
  coordinator from scratch (fresh C port, bit-exact sanity) — results above
  are the coordinator's, not the worker's.
- **m3** [P&R] Post-DRT STA in this OpenROAD build falls back to wireload
  (no `estimate_parasitics -detailed_routing`); `report_area`/`report_drc`
  absent (worked around via [`post.tcl`](pnr/post.tcl) + DRT logs). GR+parasitic STA is the
  apples-to-apples number.

### Info (no action)

- Gates reproduced exactly: delay 34.5u / 3893 cells / area 10826 (analyzers
  agree; multiplier reference re-measured 50.8u/17893 cells in the same run);
  CAL_PASS 0/448+0/20 (915s fresh run; raw worst |z| 4.36 per-bit / 2.56
  reduction — same as the reference log); bijectivity structural (S1 a
  permutation, shuffle a permutation, Midori M GF(2)-rank 64 and involutory,
  xorshift64 steps triangular ⇒ invertible by back-substitution) + empirical
  (RTL≡model 200/200, 200k random vals → 200k distinct outputs at 2 keys,
  full-construction inverse round-trip 180,000/180,000).
- Pipeline PASS: 1-cycle latency, 1 result/cycle after fill, 128/128 golden
  vectors (4 keys × 32 sequential), valid tracking incl. bubbles/drain;
  adversarial true-2-cycle variant fails the unmodified testbench (149 errors).
  Files: `round4/rtl/mix_h_xorspn3_pipe{v,_adv,_tb}.v`.
- P&R (completed before the stand-down redirect): h_xorspn3 Yosys→Sky130
  synth 1305 cells; full detailed route at DIE 260 / 24.94% util → **0 DRC
  violations**, GR+parasitic STA **4.9534 ns** (key[19]→out[9]), 69.2 µW;
  mul64_64 (reused 9639-cell netlist) 12.5632 ns (reproduces r3's 12.56 to 4
  sig figs); add64 reproduced clean (0 DRC, 9.5912 ns, 305 instances).
  **Mixer-vs-multiplier: 0.39×** — the best silicon ratio yet (r3: 0.47×).
  Corner TT/100C/1.8V, virtual-clock flow, OpenROAD v2.0 / Yosys 0.69 /
  Sky130A c6d73a35. Netlists + notes: `round4/pnr/` ([RESULTS.md](pnr/RESULTS.md),
  [synth_h_xorspn3.v](pnr/synth_h_xorspn3.v)). Moot for the verdict, valuable as flow validation.
- blink4 (cheap extra): the single flagged reduction cell (SEQ, key=0xAA,
  mask-m=8, |z|=6.23 at N=2¹⁸) does NOT reproduce at 4× samples —
  6.23 → 4.08 → 2.26 (a real bias would √N-scale to ~8.8/~12.5); six other
  keys ≤1.80. Statistical artifact; resolved with the caveat that |z|=6.23
  is a strong single event deserving an offset-varied follow-up if blink4
  ever becomes a finalist.

---

## 2. Remediation performed (coordinator, 2026-10-01)

| # | Action | Evidence |
|---|--------|----------|
| 1 | PractRand first-failure claim corrected to log-evidenced 16MB (M4) | `hx_practrand/run1_key1234.log:8` |
| 2 | TestU01 SmallCrush re-run from scratch (worker handoff lost): fresh C port, bit-exact sanity vs Python model, key 0x123456789ABCDEF0 | `round4/testu01_h_xorspn3.c`, `/tmp/hx_sc.log` (14/15, SimpPoker 7.3e-8) |
| 3 | Screen-methodology diagnosis: blindness mechanism characterized, two new cell families prototyped and measured against h_xorspn3 / r3_xorlin_qm / splitmix64 | §3 below |
| 4 | Dieharder discrepancy resolved: binary wiped by VM reboots, reinstall blocked — documented as open, low-signal (m1) | §4 |
| 5 | P&R stood down after disqualification; completed numbers preserved | `round4/pnr/RESULTS.md` |

---

## 3. Screen-methodology diagnosis and round-5 amendment

**Blindness mechanism.** The 468-cell screen measures only 1-D or small-window
statistics. h_xorspn3's defect is joint GF(2)-linear structure spread across
the full 64-bit word and across consecutive outputs. The 448 per-bit cells test
only marginals (genuinely uniform — confirmed clean at N=2²⁴); reduction cells
are 1-D scalar projections or ≤16-bit windows (all measured full-rank). Nothing
probes joint structure across consecutive outputs or input→output differentials.
Fisher-combination dependence (r3's M7) is NOT the cause: the 64 per-bit
p-values are genuinely null, and Fisher of nulls is null regardless of
dependence — purely a coverage issue.

**Prototyped detection (N=2¹⁸, key 0x123456789ABCDEF0, sequential):**

| Cell | h_xorspn3 | r3_xorlin_qm | splitmix64 (null) | cost |
|---|---|---|---|---|
| 64×64 rank, deficient-count z (rank≤61, null p=0.005285 exact) | **+885** (4096/4096) | **+32** (170/4096) | +0.5 (26/4096) | 0.8 s |
| 64×64 rank, N=2²⁰ | **+1770** (16384/16384) | **+73.6** | — | 3.8 s |
| 256×256 rank, mean-rank z | **−1062** | **−297** | — | 0.6 s |
| Truncated-diff: low-8-bit χ², 18 weight-1 deltas, Fisher log₁₀(p) | **−20.2** (worst z +7.2) | −inf (worst z +47.4) | −0.0 | 0.075 s/key |

The rank cell catches both the catastrophic (hx) and the weak (r3) linear
structure; the truncated-differential cell catches both differential
profiles. Both reuse the already-computed SEQ outputs — no extra hashing.

**Round-5 screen amendment (concrete proposal).** Add two Holm families
(α=0.01 each), SEQ × 10 keys:
- **Family LIN (linear bound):** per cell, 4096 matrices of 64×64 (rows = 64
  consecutive outputs); D = #{rank ≤ 61}; null D ~ Binomial(4096, 0.005285)
  exact; per-cell p = upper tail. Bound: no detectable GF(2)-linear
  dependency at N=2¹⁸.
- **Family DIFF (differential bound):** per cell, 18 weight-1 deltas 2⁰…2¹⁷,
  deduped 2¹⁷ pairs; low-8-bit χ² → two-sided normal p; Fisher-combine the 18
  p-values per cell, Bonferroni-on-max as dependence-robust secondary.
  Bound: no detectable truncated-differential structure at N=2¹⁸.
- **Verdict:** CAL_PASS iff zero Holm rejections across all four families
  (PB, RD, LIN, DIFF). Honest FWER ≤ 0.04 (was ≤0.02 — state it).
- Cost: ~9 s/candidate. M7's missing scenarios (GRAY/UPSTREAM/…) remain unrun.

---

## 4. Remaining open items

1. **Dieharder** (m1) — environmental; reinstall when apt is free. Low signal.
2. **Round-5 screen amendment** (§3) — implement LIN/DIFF families before the
   next search round; re-screen r3_xorlin_qm under the amended screen (its
   rank-cell z=+32 at N=2¹⁸ needs a verdict under the new bound).
3. **M7 screen-coverage delta** — GRAY/UPSTREAM/BYTE-REP/SPARSE-HD/PTR-RAND/
   SMALL-INT scenarios and ≥32-key coverage still never run for any candidate.
4. **Adversarial analysis of r3_xorlin_qm's differential structure** (r3 M9) —
   unchanged: multi-way hash-DoS chaining unanalyzed.
5. **h_xorspn3 files** — pipeline RTL, TestU01 C model, P&R netlists, PractRand
   logs, differential tables all preserved (see §5); the design is a useful
   negative example (fastest silicon, worst linear structure).

## 5. Verdict

`h_xorspn3` passes every gate the search defined — delay (34.5u, 0.679×, 9.8u
margin), calibrated screen (0/468), bijectivity (proved + empirical),
1-cycle pipeline, clean detailed route at 0.39× the multiplier in Sky130 —
and is still **rejected**: PractRand BRank fails at 16MB (R=+3008 → +9306)
and full-64-bit differentials repeat ~41,900× where ~0 are expected. The
3-round SPN + linear xorshift pre-diffusion leaves construction-level linear
structure that marginal/small-window screens cannot see. Its lasting
contributions: (a) proof that the delay bar has real headroom (34.5u vs 44.3),
(b) the screen-blindness diagnosis and the concrete LIN/DIFF round-5
amendment, (c) a validated P&R flow producing 0-DRC routes. `r3_xorlin_qm`
remains the standing winner — Pareto-optimal for the non-adversarial
hash-map use, with its own known battery failures and differential profile.
