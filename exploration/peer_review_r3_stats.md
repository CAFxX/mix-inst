# Peer review — statistical claims for `r3_xorlin_qm` (round-3 winner)

Reviewer: independent statistics track (not the designer).
Date: 2026-10-01. Workspace: [`~/workspace/mix/exploration/`](./) (round4/ untouched).
Design: `r3_xorlin_qm` (V_a) — 4-round SPN, PRESENT S-box as Quine–McCluskey-minimized SOP,
L(x)=x⊕ROTL(x,11)⊕ROTL(x,37), xor key schedule. Only functional change vs
`spn4_xorlin_1137` is the S-box ROM→SOP substitution.

Sources read: [`screen_cal.py`](screen_cal.py), [`run_screen_cal.py`](run_screen_cal.py), [`screen_lib.py`](screen_lib.py) (constants),
[`models/spn4_xorlin_1137.py`](models/spn4_xorlin_1137.py), [`gen_r3.py`](gen_r3.py), [`check_rtl.py`](check_rtl.py), [`qm_sbox.py`](qm_sbox.py),
[`practrand_gen.py`](practrand_gen.py), [`testu01_smallcrush.c`](testu01_smallcrush.c), [`~/workspace/mix/scenarios.md`](../scenarios.md),
[`candidates.md`](candidates.md), `results/*/screen_cal.json`. Verified from installed tool sources:
PractRand `BRank.h`, TestU01 `sknuth_SimpPoker` + `unif01_StripL`.

## Verdicts (one line each)

- **Claim A** (CAL_PASS inherited via bit-identical S-box): **ACCEPT** — the equivalence
  chain is sound and the inheritance logic is valid. Minor strengthening recommended.
- **Claim B** (calibrated screen methodology): **ACCEPT AS SCREENING EVIDENCE** — principled,
  self-aware, and the PASS is corroborated by a dependence-robust secondary check. But the
  "calibrated at α=0.01" headline overstates the rigor (dependence never calibrated,
  coverage partial, controls extreme-point only).
- **Claim C** ("hash-map uniformity OK, not PRNG-grade"): **REJECT as stated** — the battery
  failures are not PRNG aesthetics; they reveal key-independent joint structure in the
  deployment input distribution, in bit regions consumed by supported reductions, at 128×
  the screen's sample size. Recommend differential-profile analysis + larger-N reduction
  tests before final sign-off.

---

## Claim A — Is bit-level S-box equivalence sufficient to inherit the 468-cell result?

### The equivalence chain (verified)

1. The calibrated screen ran on `mix_spn4_xorlin_1137_np` (the vectorized numpy model —
   the only model with the array API `screen_calibrated` requires; scalar≡np cross-checked,
   re-verified 50/50 vectors today).
2. The winner's RTL was checked against **the same** numpy function (`[gen_r3.py](gen_r3.py)::check_equiv`
   → [`check_rtl.py`](check_rtl.py) vs `models.spn4_xorlin_1137.mix_spn4_xorlin_1137_np`): 200/200 random
   vectors (seed 0xBEEF), EQUIV-OK.
3. The S-box substitution is exact by construction: the QM minimizer enumerates prime
   implicants of the on-set only (implicants can't cover off-set points) and covers all
   minterms — verified 0/64 bit-nibble mismatches (16 inputs × 4 bits, exhaustive).
   V_a changes nothing else.
4. The screen is deterministic given the function (seeded keys, fixed scenarios), so
   functional equivalence ⇒ identical screen result — the transfer is exact, not approximate.

**Verdict: ACCEPT.** For inheriting a *statistical* result, this evidence is proportionate.
A combinational bug affecting a measurable fraction of inputs would be caught by 200 random
vectors with near-certainty; the only logic change is provably exact.

### Findings

- **[minor] A1 — Composition/wiring rests on 200 random vectors, not proof.** The 64-combo
  proof covers one S-box instance in isolation; nibble wiring, round structure, and key
  schedule rely on the 200-vector spot check. Residual risk (a difference confined to a
  tiny input region, e.g. exactly the screen's structured inputs) is paranoid but nonzero.
  Cheap fix: add directed vectors covering screen inputs (SEQ 0..2^18−1 under key 0 costs
  nothing — they're enumerable) or re-run a subsample of the calibrated screen's SEQ/PTR-j8
  cells against the RTL netlist.
- **[minor] A2 — The batteries are inherited too, via a weaker link.** PractRand used the
  numpy model directly (fine — same argument as above), but TestU01 used a C
  reimplementation ([`testu01_smallcrush.c`](testu01_smallcrush.c)) with **no recorded cross-validation** against the
  numpy model. It matches by inspection (round keys, S-box table, rotations all agree), and
  PractRand corroborates the qualitative failure, so a spurious artifact is unlikely — but
  the cross-check is a 5-minute job and should exist before the battery results are quoted
  as properties of the winner.
- **[info] A3 — "Bit-identical ⇒ identical distribution" is the right argument**, and the
  designer applied it consistently (screen + PractRand + TestU01 all run on the predecessor
  function). No objection to the logic, only to the strength of the full-function evidence
  (A1/A2).

---

## Claim B — The calibrated screen methodology

Mechanics (confirmed by reading code + rerunning numbers): per (scenario,key) cell, 64
per-bit two-sided normal p-values → Fisher χ²(128); per (SEQ|PTR-j8,key) cell, 9 reduction
p-values → Fisher χ²(18); Holm–Bonferroni per family at α=0.01 (448 + 20 = 468 cells);
CAL_PASS ⇔ zero rejections. N=2^18 per cell, 10 keys (8 fixed + 2 random), +128×64 key sweep.

### Findings

- **[major] B1 — Fisher under dependence: disclosed, but never calibrated.** The docstring
  is honest ("NOT independent… liberal under dependence… used as the prescribed calibrated
  screening heuristic"). Two problems remain:
  1. The "calibration" self-test (500 null cells → 0 rejections) was run under **independence**
     — i.e., it validated the machinery exactly where the assumption holds, not where it is
     violated. The size distortion under realistic bit-dependence is unquantified.
  2. Assessment of impact: for the *observed PASS*, liberality cuts in the reassuring
     direction — a test that rejects too easily still rejected nothing across 468 cells.
     And the dependence-robust secondary check (Bonferroni on max|z|, valid under arbitrary
     dependence) corroborates: all scenario-level p > 0.01 (minimum 0.0327 on
     DESC-j=2^64−1; next 0.0518 on POW2-2^16). So the PASS conclusion stands, but the
     nominal "FWER controlled at 0.01" is not literally established. State it as a
     heuristic screen with corroboration, not a calibrated level-α test.
- **[major] B2 — Coverage vs [`scenarios.md`](../scenarios.md) is partial; "468 cells" overstates it.**
  The catalog says "every finalist must pass all of these." Gaps in the calibrated run:
  1. **Keys:** 8 fixed + **2** random vs catalog's "≥32 pseudorandom keys". The 128×64
     key-sweep partially compensates (per-bit over the key axis) but with n=64 it is coarse.
     Key-robustness is central for a keyed finalizer — a weak-key class at ~10% frequency
     would likely be missed.
  2. **Reductions only on SEQ and PTR-j8**, not every scenario; Lemire X∈{10,1000,2^32} vs
     11 catalog values (missing 2^64−1 and small X∈{2,3,5,7}); mask m∈{8,32} vs 11 values;
     mod y∈{7,1000} vs 5 values.
  3. **Scenarios not run:** GRAY, UPSTREAM (splitmix-fed input), BYTE-REP, SPARSE-HD,
     PTR-RAND, SMALL-INT, MPOW2 c=9, most POW2 strides (k∈{7,9–15,17–31,33–47,49–63}).
  4. No Small-N chi-square (catalog §E); no explicit adversarial-regression cells (§F).
  The docstring's "IDENTICAL protocol/scenario catalog as screen_lib.screen" is true but
  circular — `screen_lib.screen` is the *quick* screen, not the catalog. Document the delta
  explicitly instead of letting "468 cells" imply full-catalog coverage.
- **[major] B3 — Validation controls are extreme-point only.** Negative control (keyed
  SplitMix64 → CAL_PASS 0/0) shows no false positive on an excellent mixer; positive
  controls (lane4_s1_const, hyb_sp4b_121: CAL_FLAG 311/20; spn5_present etc. similar) show
  gross-defect sensitivity. Neither probes the **moderate-defect regime** where a winner
  actually lives. The synthetic self-tests (single-bit z=20 must reject; 8×z=5 must reject)
  help but assume independence. Missing: a borderline positive control (e.g., a 3-round or
  deliberately weakened variant) to locate the screen's real detection threshold.
- **[minor] B4 — Two Holm families ⇒ overall FWER ≤ 0.02, not 0.01.** Holm is run separately
  on the per-bit family (448 cells) and reduction family (20 cells), each at α=0.01; the
  "reject if either rejects" rule doubles the budget. (Holm needs no cross-cell independence —
  that part is genuinely solid.) Fix by stating per-family control or using α=0.005/family.
- **[minor] B5 — Fisher dilution blinds the screen to isolated single-bit bias (disclosed,
  but in tension with [scenarios.md](../scenarios.md)).** Verified numerically: one bit at |z|=6 among 63 null
  bits → Fisher combined p≈0.013 ≫ Holm threshold 2.2e-5 → **no rejection** (the self-test
  even asserts "expect not rejected"). So the calibrated rule cannot see an isolated
  ~0.6%-bias bit at N=2^18. Practical impact is small (a sub-1% single-bit bias is irrelevant
  to bucketing; the reduction family covers consumed paths), and the Bonferroni-on-max|z|
  secondary check mitigates it — but [scenarios.md](../scenarios.md) §F explicitly wants per-bit monobit to
  catch single-bit biases "that pooled tests dilute," and Fisher reintroduces exactly that
  dilution. Keep the secondary check as a co-equal gate, not informational-only.
- **[info] B6 — The raw→calibrated override was the right call.** Raw verdict was FLAG
  (per-bit max |z|=4.05 @ DESC-j=2^64−1). Expected false flags under the null across
  28,672 bit-tests at |z|≥4.05: **≈1.47** (computed). The raw bar had no multiplicity
  control and its single flag is exactly what the null predicts. Replacing it with a
  multiplicity-controlled rule is statistically principled, not result-shopping.

Net: the methodology is thoughtful and self-aware (the caveats are in the docstring, not
hidden), the PASS is corroborated by a dependence-valid check, and the raw-bar override is
justified. It is good *screening* evidence — not a proof, and not full-catalog coverage.

---

## Claim C — Battery failures: "hash-map uniformity OK, not PRNG-grade"

### What the tests actually measure (verified from installed sources)

- **PractRand BRank**: fills binary matrices from the raw output bitstream, computes GF(2)
  ranks, scores the rank distribution. Rank deficiency ⇔ systematic **linear dependencies**
  among output bits (within/across consecutive outputs). Reported R is a standardized score
  (|R|≳5 already null-impossible); **R=+622…+754 at 256MB** is hundreds of sigma out —
  a deterministic structural linear relation, not a borderline p-value.
- **TestU01 SmallCrush SimpPoker** (`sknuth_SimpPoker(gen,res,1,400000,24,64,64)`, confirmed
  in `bbattery.c`): 400k "hands" of 64 cards; each card = `unif01_StripL(gen,24,64)` = bits
  **[7:2] of each 32-bit output half** (verified in `unif01.c`: fractional part of u·2^24 ×64),
  i.e. the **low-bit region** — bits [7:2] and [39:34] of each hash. Counts distinct values
  per hand, χ² vs the occupancy null. **p<1e-300** ⇒ the joint distribution of low bits
  across consecutive outputs is catastrophically non-uniform in occupancy structure.
- Both failures **systematic across 2 keys**; input was the sequential counter stream
  h(0),h(1),… (PractRand: 2^25 hashes; TestU01: 12.8M hashes).

### Findings

- **[major] C1 — Sequential input IS the deployment distribution; the "PRNG" framing is
  wrong.** [scenarios.md](../scenarios.md) lists SEQ as the canonical case ("ordered integer keys, counters").
  The PractRand/TestU01 stream h(0),h(1),h(2),… is literally the hash sequence a table
  computes for keys 0,1,2,…. A structural defect in consecutive-output joint distribution is
  in the use case's direct path — not an artificial PRNG scenario the design can disclaim.
- **[major] C2 — The failures are structural, key-independent, and in reduction-consumed
  bits.** The low-bit occupancy catastrophe (SimpPoker) sits exactly where `out & (2^m−1)`
  reductions read. BRank's linear-dependency signal is consistent with strong
  linear/differential structure through 4 rounds (PRESENT S-box max linear correlation 2^−1;
  4-round trails at ~2^−4 are easily visible in 2^31 bits). Key enters only via xors, so
  differential properties are **key-independent by construction** — "trusted per-map seed"
  ([scenarios.md](../scenarios.md)'s rationale for scoping out differential analysis) does **not** neutralize
  key-independent differentials. An attacker can analyze the public 4-round structure
  offline, find high-probability low-weight differentials, and force output *relations*
  (hence bucket collisions under mask reduction) without knowing the key. CAL_PASS's
  N=2^18 *marginal* tests cannot rule this out. No exploit was demonstrated — the
  differential profile was never computed — but the battery magnitudes make "cannot bite"
  an assertion without evidence.
- **[major] C3 — 128× sample-size mismatch: the screen lacks power where the batteries
  found signal.** Batteries: ~2^25 hashes. Screen cells: N=2^18. The screen's marginal
  mask-8/Lemire tests passing at N=2^18 does not imply the low-bit region is clean at
  battery scale — the tests differ in power by two orders of magnitude. Before finalizing
  any uniformity claim, re-run the mask/Lemire reduction cells at N=2^24–2^25 on SEQ/PTR.
- **[minor] C4 — "12-round SPN passes BRank" is diagnostic only, and unlogged.** It supports
  the rounds-deficiency diagnosis, but no run log was found in the workspace — record it or
  re-run. It doesn't resolve anything (12 rounds fail latency at 1.51×).
- **[minor] C5 — TestU01 C-model cross-validation missing** (see A2). Corroborated by
  PractRand-on-numpy-model, so low risk, but close the loop.
- **[info] C6 — Dieharder is NOT installed** (verified: `which dieharder` empty, no
  /usr/bin/dieharder), contradicting the project note claiming "Dieharder 3.31.1 was
  installed at /usr/bin/dieharder". The note is stale — fix it. Given two batteries already
  fail catastrophically, Dieharder would add little; don't block on it.
- **Counterpoints (honesty):** (i) CAL_PASS remains genuine positive evidence for *marginal*
  uniformity under the tested reductions at N=2^18 — the batteries bound its meaning, they
  don't overturn it; non-adversarial workloads at tested scale look fine. (ii) No practical
  collision-forcing attack was demonstrated; exploitability magnitude is unquantified.
  (iii) "Winner criteria didn't include PractRand/TestU01" is true of the selection rule but
  circular as a defense — the adequacy of the criteria is precisely what's under review.

### Verdict on Claim C: REJECT as stated.

"4 rounds achieves hash-map uniformity but not PRNG-quality randomness" mischaracterizes
the evidence twice: the failing input distribution **is** the hash-map input distribution,
and the failing bit region **is** consumed by supported reductions. The accurate statement:
"4 rounds achieves *marginal* uniformity under the tested reductions at N=2^18, but exhibits
strong key-independent linear/differential joint structure across consecutive outputs,
detectable at 2^25 samples, whose adversarial implications (collision-forcing via public
differentials) were not analyzed." The latency-vs-randomness tradeoff is real, but
"Pareto-optimal for the stated hash-map requirements" presumes the requirements (as
operationalized by CAL_PASS) capture the threat model — the batteries suggest they don't,
at least not at adversarial scale.

---

## Recommendations (priority order)

1. **Compute the differential profile** (directly quantifies C2): measure
   P(h(i)⊕h(i⊕δ) ∈ S) for low-weight δ (especially δ=1) over ≥2^24 samples; check whether
   any (δ_in → low-bit δ_out pattern) has probability ≫ 2^−6. This decides whether the
   battery failures are a practical collision-forcing risk or a non-exploitable curiosity.
2. **Re-run mask/Lemire reduction cells at N=2^24–2^25** on SEQ and PTR-j8 (addresses C3).
3. **Close the Claim A loop cheaply** (A1/A2/C5): directed screen-input vectors in
   `check_rtl`, plus a numpy-vs-C cross-check for the TestU01 model.
4. **Documentation fixes:** correct the Dieharder note (C6); state FWER as per-family or
   halve α (B4); write down the explicit delta between the calibrated run and
   [scenarios.md](../scenarios.md) (B2); promote the Bonferroni-on-max|z| check to a co-equal gate (B5).
5. **Add a moderate positive control** for the screen (B3) — e.g., a 3-round variant — to
   locate the real detection threshold before the next winner is declared on CAL_PASS alone.

## Severity-ordered finding list

- critical: (none)
- major: B1 (Fisher dependence uncalibrated), B2 (partial catalog coverage),
  B3 (extreme-point-only validation), C1 (sequential = deployment distribution),
  C2 (key-independent joint structure in reduction-consumed bits),
  C3 (128× sample-size/power mismatch)
- minor: A1 (composition evidence = 200 vectors), A2/C5 (C model unvalidated),
  B4 (FWER 0.02 not 0.01), B5 (Fisher dilution vs [scenarios.md](../scenarios.md) intent),
  C4 (12-round diagnostic unlogged)
- info: A3, B6, C6
