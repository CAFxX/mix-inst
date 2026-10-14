# Independent statistics review: r7_feist8_s1_1sbox

Reviewer: independent statistics subagent (no contact with other reviewers).
Date: 2026-10-02. Evidence read from raw files, not summaries; one test
re-run performed by the reviewer (S4, new key).

## Scope

Audit the statistical validation (S1–S4) of RV64 `mix` candidate
`r7_feist8_s1_1sbox` (8-round Feistel, F = single S1 S-box layer →
`t ^ rotl7(t) ^ rotl13(t)` → `^ rk32`; val^key whitening; key schedule
`rk_i = rotl64(key,13(i+1)) ^ (i+1)*0x9E3779B97F4A7C15`). Out of scope: S0
delay numbers, synthesis/equivalence/bijectivity (covered by other audits).

## Method

- Read raw: `round7/results/r7_feist8_s1_1sbox/s1_result.json`,
  `audit/s2_k0.log`, `audit/s2_k1.log`, `results/.../s3_k0|k1|k1s3/*.log`,
  `results/.../s4/smallcrush.log`.
- Read methodology sources in full: `fast_battery/src/s1_screen.py`,
  [`lin_diff.py`](../../fast_battery/src/lin_diff.py), [`screen_lindiff.py`](../../screen_lindiff.py), [`screen_cal.py`](../../screen_cal.py) (incl. PB/RD families),
  [`s2_diffprof.c`](../../fast_battery/src/s2_diffprof.c), [`s3_gen.c`](../../fast_battery/src/s3_gen.c), [`s3_practrand.sh`](../../fast_battery/src/s3_practrand.sh), [`s4_smallcrush.c`](../../fast_battery/src/s4_smallcrush.c),
  candidate `impl.c`/`model.py`.
- Recomputed independently: S-box DDT/LAT (max DP = 4/16 = 2^-2), LIN null
  `P(rank<=61)=0.005285` (verified analytically ≈ 0.00528, exact is correct),
  cell counts (448 PB + 20 RD = 468 marginal; 10 LIN + 10 DIFF cells),
  S2 null expectations, detection floors, S1 expected max|z|.
- Re-ran SmallCrush myself with a **different key** (`0x9E3779B97F4A7C15`;
  team's key presumed `0x123456789ABCDEF0`, not recorded in their log):
  built from [`s4_smallcrush.c`](../../fast_battery/src/s4_smallcrush.c) + candidate `impl.c` with
  `-DGOLDEN_OUT=0x9433380721f156b2` (golden = Python model `mix(0,
  0x123456789ABCDEF0)`; bit-exact sanity check passed, i.e. C↔Python agree).
  Log: `audit/s4_smallcrush_key9e37.log`.

## Findings

### MAJOR-1 — S1 "honest FWER ≤ 0.04" is overstated: within-cell Fisher combination is liberal under dependence

The claim rests on Holm (α=0.01) in each of 4 families + union bound. Holm
needs *valid* per-cell p-values. Three of the four families Fisher-combine
*dependent* p-values inside each cell: PB combines 64 per-bit p-values from
the same N outputs; RD combines 9 reduction p-values from the same S; DIFF
combines 18 delta p-values from overlapping input sets. The team's own
[`screen_cal.py`](../../screen_cal.py) docstring admits Fisher "assumes independence, so as an exact
test it is liberal under dependence; it is used here as the prescribed
calibrated screening heuristic." A procedure that is *admitted* liberal
cannot support the word "honest". Only the LIN family (single exact binomial
p per cell) has rigorous per-family error control. The dependence-robust
Bonferroni-on-max secondary is reported but does not drive the verdict.

Impact on this candidate: none for the verdict itself — zero rejections in
all families, and the robust secondary is also clean (raw worst per-bit
|z| = 4.5078 vs null-expected max ≈ 4.53 over 28,672 tests: exactly
null-like). But the FWER sentence in `s1_result.json` (`"fwer":
"<=0.04 (alpha=0.01 x 4 families)"`) should read "heuristic, ≤0.04 under
within-cell independence".

### MAJOR-2 — Search multiplicity: the FWER bound is per-candidate, the search tested 17 candidates

`round7/results/` contains 17 candidates. Each was screened at per-candidate
FWER ≤ 0.04 (heuristic, see MAJOR-1). P(≥1 false CAL_PASS among 17) ≈
1 − 0.96^17 ≈ 50%. The leader is then *selected* as the fastest survivor —
post-selection inference the FWER framework does not cover. No multiplicity
correction across the design search is applied anywhere. This does not
invalidate this candidate's clean data, but "CAL_PASS at FWER ≤ 0.04" must
not be read as "4% chance this survivor is a false positive of the search".

### MAJOR-3 — Latent orchestrator bug: inner LIN/DIFF kill signal is dropped

[`s1_screen.py`](../../fast_battery/src/s1_screen.py) runs LIN/DIFF via [`lin_diff.py`](../../fast_battery/src/lin_diff.py) for the verdict, but
`screen_calibrated()` *re-runs* LIN/DIFF via a *different implementation*
([`screen_lindiff.py`](../../screen_lindiff.py)) as its early-kill gate. The two implementations differ:
different pair sets (lin_diff uses 2^16 pairs for deltas 2^0..2^16 vs 2^17
in screen_lindiff) and different p-transforms (normal approx vs
Wilson-Hilferty). If the inner gate flags, `screen_calibrated` returns
`cal_rejected_perbit=[]`, `cal_rejected_red=[]`, `s1_kill=True`,
`cal_verdict="CAL_FLAG"` — and [`s1_screen.py`](../../fast_battery/src/s1_screen.py) **ignores** `s1_kill` and
`cal_verdict`, sees two empty rejection lists, and can emit **CAL_PASS**.
The kill path was not taken for this candidate (both implementations pass),
so this did not fire — but a borderline candidate could be misreported as
CAL_PASS. Fix: check `res_marg["s1_kill"]`/`cal_verdict` in the verdict, and
deduplicate to a single LIN/DIFF implementation.

### MAJOR-4 — S2 kill threshold (1000 repeats) is arbitrary and ~7 orders of magnitude above the null

S2's `kill_repeats` defaults to 1000. Under the null, per (delta,key):
E[repeats] = C(2^21,2)/2^64 ≈ 1.2e-7; P(≥1 repeat) ≈ 1.2e-7; over all 148
(delta,key) tests P(any repeat) ≈ 1.8e-5. **A single repeat anywhere is
already overwhelming evidence of structure**, yet the screen tolerates up to
999. It killed h_xorspn3 (41,889 repeats) but would PASS a candidate with
500 repeats — statistically damning, verdict PASS. This candidate has 0
repeats so the verdict stands, but the threshold must be tied to the null
(e.g. kill on ≥1, or ≥5 for margin), not a round number.

### MAJOR-5 — S2 delta set is not S-box-driven; 5 of the 10 worst S-box input diffs untested as single-nibble deltas

I computed the S1 S-box DDT: max DP = 4/16 = 2^-2, attained by input diffs
{0x2,0x3,0x5,0x6,0x8,0x9,0xA,0xC,0xD,0xF} (all except 0x1,0x4,0x7,0xB,0xE,
which have max count 2). The S2 set covers single-nibble deltas 0x1–0x8
(weight-1) plus 0x3,0x5,0x9 (weight-2 list) — **missing 0x6, 0xA, 0xC, 0xD,
0xF as isolated nibble deltas**, i.e. half of the S-box's own worst-case
input differences. Also missing: rotation-aware structured deltas matched to
the `rotl7/rotl13` linear layer (e.g. 0xAAAAAAAAAAAAAAAA,
0x0F0F0F0F0F0F0F0F; only 0xF0F0F0F0F0F0F0F0 present), and deltas exercising
high input bits of *x* (S2 uses x ∈ [0,2^22) only). The delta list
("historically-suspicious first") is generic, not derived from this design's
differential structure. For an S-box design the differential screen should
be DDT-driven. (Cosmetic: 0x400 and 0x4000000 are tested twice — duplicated
in the weight-1 loop.)

### MAJOR-6 — What "zero repeats at N=2^22" actually rules out (interpretation bound)

Two readings, very different answers:
- (a) Per-pair repeat probability: 0 observed → 95% upper limit
  3/C(2^21,2) ≈ 1.4e-12 ≈ **2^-39.4**. N=2^22 is *more* than enough here
  (2^-32 would need only N≈2^19).
- (b) A *specific* differential (δ→Δ) with probability q: the repeat
  statistic needs E[repeats] ≈ 2^41·q² ≳ 3, i.e. **q ≳ 2^-20**. Ruling out a
  2^-32 differential via full-output repeats would need N ≈ 2^33 —
  infeasible. The low-8-bit χ² floors at q ≳ 2^-11 (truncated), per-bit flip
  bias at ε ≳ 2^-9.

So S2 rules out *catastrophic* differentials (h_xorspn3's q≈2^-13 class),
not 2^-32-level ones. "S2: PASS, zero repeats" must not be paraphrased as
"no differential weakness exploitable at 2^-32". S2 is an early-kill screen;
the actual differential-security argument (trail bounds — see gap G1) does
not exist yet. Related: only 2 keys tested (0x0, 0x123456789ABCDEF0); no
weak-key or related-key analysis (M9 acknowledged as remaining).

### MINOR-1 — S1 DIFF docstring overstates its data: 2^16 pairs, not 2^17, for deltas 2^0..2^16

`lin_diff.diff_cell_logps` uses `xs=arange(2^17)`, `keep = xs < xs^2^k` →
2^16 unordered pairs for k≤16 (2^17 only for k=17). Docstring claims
"deduped 2^17 pairs each". The code normalizes by the actual `npairs`, so the
χ² is valid; power is just half the documented data for those deltas.

### MINOR-2 — S3 stage-verdict logic: FAIL-only grep misses "unusual"/"suspicious" and vacuous stages

- [`s3_practrand.sh`](../../fast_battery/src/s3_practrand.sh) kills only on `grep -q "FAIL"`. PractRand's intermediate
  tiers ("unusual", "mildly suspicious", "suspicious") never kill. Instance:
  `s3_k1s3/s3_practrand_16MB.log` shows `Gap-16:A  R= -4.3  p=1-4.4e-4
  unusual` ("...and 146 test result(s) without anomalies"). Assessment:
  order 10–25% chance under the null of seeing ≥1 "unusual" in 147 tests, and it vanished at
  32MB+ ("no anomalies in 159") — benign fluctuation, not a defect. But the
  team's summary "no anomalies in 227 tests" is true only of the final 1GB
  stage; the 16MB "unusual" is undisclosed.
- `s3_k1/s3_practrand_16MB.log` contains **zero test results**
  ("error reading from file" immediately — RNG_test saw EOF with no data;
  generator .err empty). The stage is vacuous; the script passed it anyway
  because no "FAIL" string appeared. 16MB coverage for k1 is recovered only
  via the 1GB run's 16MB report line. The script should assert each stage
  emitted test results (and use `pipefail` — the generator's exit status is
  currently invisible).

### MINOR-3 — S3/S4 config coverage is thin

S3: 2 keys × strides {1, 3-on-k1-only}; missing stride 2, key=0×stride=3,
more keys, nonzero/high counter starts, PractRand expanded set (core only).
S4: team's `smallcrush.log` does not record which key was used (provenance
gap). My re-run adds key 0x9E3779B97F4A7C15 → 15/15 pass, min p-value 0.09
(`audit/s4_smallcrush_key9e37.log`), golden bit-exact check passed.

### MINOR-4 — Cosmetic/robustness nits

- `bonf_logp` in [`lin_diff.py`](../../fast_battery/src/lin_diff.py) is "capped later" per comment but never
  capped: `s1_result.json` contains positive log-p values (0.148, 0.262,
  0.503). Not used in any verdict; fix the comment or the cap.
- S1 LIN's most extreme cell: D=36/4096, logp=-5.86, key
  0x9D79627A793D16E5 — sits just above the Holm boundary (log(0.01/10) =
  -6.91). Correctly not rejected; under the null P(min-of-10 ≤ this) ≈ 1%.
  Thin margin — a repeat LIN run on fresh keys/offset would be the natural
  falsifying experiment; not required, but noted.
- No p-hacking evidence found for this candidate (single `s1_result.json`;
  code mtimes 21:20 precede the 22:14 run; no backup/rerun artifacts), but
  there is also no run provenance (who ran what, when, with which binary) —
  worth adding for a production gate.

## What the battery does NOT cover (skeptic's list before production)

- **G1 — No differential/linear trail analysis.** The battery is purely
  statistical and blind below q≈2^-20 (full) / 2^-11 (truncated-8-bit) /
  linear-bias ≈2^-9. The evidence a 64-bit finalizer actually needs — best
  differential trail probability via MILP/SAT over the 8-round Feistel,
  active-S-box lower bound, branch number of `t ^ rotl7(t) ^ rotl13(t)`,
  best linear trail bias — does not exist. (Raw material is good: S-box max
  DP 2^-2, max |LAT| bias 2^-3; but no trail was ever bounded.)
- **G2 — No related-key / weak-key analysis.** Key schedule is
  rotl64-xor-multiply; related-key differentials untested. M9 multi-key
  hash-DoS chaining is acknowledged as remaining — it is a real gap, not a
  formality, for a keyed hash under adversarial keys.
- **G3 — Fixed keys everywhere.** S1's 10 keys, S2's 2 keys, S3's 2 keys,
  S4's 1–2 keys are constants. No random-key sampling to catch
  key-dependent weak classes (KEY-SWEEP in S1 is a gross 64-key monobit
  check only).
- **G4 — PractRand/SmallCrush see sequential-counter streams only.** No
  adversarial input distributions; S1 covers input *shapes* and S2 covers
  *differentials* but both at N≤2^22 depth.
- **G5 — No full SAC/BIC avalanche matrix at depth** (only per-bit |z|
  summaries, which are clean: S2 max|z| 3.6/3.8 vs null-expected ≈4.1).
- **G6 — Dieharder not run** (binary lost in VM reboot per project notes);
  no TestU01 BigCrush, no PractRand beyond 1GB / expanded set.
- **G7 — Bijectivity** rests on the structural Feistel argument (sound) +
  20k explicit inverse vectors (thin but the structural argument carries
  it); **1-result/cycle** verified on 64 vectors in iverilog (thin sample
  for a pipeline claim, out of statistics scope — noted for completeness).

## Verdict: APPROVE-WITH-FINDINGS

The candidate's **data** is clean everywhere I could check independently:
S1 zero rejections across all 488 cells (448 PB + 20 RD marginal + 10 LIN + 10 DIFF) (raw worst |z| exactly null-like),
S2 zero repeats on 148 (delta,key) tests at N=2^22, S3 1GB PractRand clean
on 3 configs (one benign "unusual" at 16MB, vanished with more data), S4
SmallCrush 15/15 on the team's key and, by my own re-run, on a second key
(min p=0.09). No p-hacking evidence for this candidate.

The **methodology** needs the fixes above before its claims can be quoted
at face value — most importantly: de-liberalize or relabel the FWER claim
(MAJOR-1), account for search multiplicity (MAJOR-2), fix the dropped
inner-kill signal (MAJOR-3), tie the S2 kill threshold to the null
(MAJOR-4), and drive S2 deltas from the S-box DDT (MAJOR-5). And the
**interpretation** must stay inside what was measured: the battery rules
out gross statistical defects and catastrophic differentials (q ≳ 2^-20);
it says nothing about 2^-32-level differentials — that requires the
cryptanalytic trail work in G1, which is the single biggest missing piece
before any production claim.
