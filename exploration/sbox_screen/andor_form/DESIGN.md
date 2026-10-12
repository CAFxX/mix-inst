# track2-andor-form — ANDOR form WITH LINEAR BYPASS TAP (O141 re-test trigger)

**Track:** 2 (broad screen) · **Owner:** track2-andor-form (subagent, lane
opened 2026-10-12 ~13:10 CEST, from O141 §8 re-test trigger)
**Date:** 2026-10-12 · **Status:** TERMINAL — pilot COMPLETE 0/36 KEEP
(2026-10-12 ~13:28 CEST / 11:28:32Z, adjudicated raw from `pilot.log`).
**Verdict number at close:** O144 (ledger top O143 re-read 2026-10-12
~13:50 CEST at write time; O142 reserved for the batch-62 S0 verdict).
**Parent verdicts:** O141 (ANDOR+structured taps KILLED 0/36 at inner gate;
tap geometry exonerated; Boolean function f exonerated — max|W|=6, NL=5,
normalized 0.625 > MUX 0.5; the stage-as-wired ceiling: no linear bypass
tap, all-probabilistic 3/8 differential spread, 1/16 output bias),
O131 §4(ii) (hetero stage needs HIGHER confusion-per-u than MUXD 4.0u, not
merely cheaper).
**Seed:** 0xB805 (fresh; struct 0xB804, hetstage2 0xB803).

## Pilot result (raw-artifact adjudication, 2026-10-12 ~13:28 CEST)

**0/36 KEEP** (seed 0xB805; `pilot.log`: "0/36 KEEP (inner_kills=36
fisher_kills=0)"). Every draw inner-killed (lin=FLAG diff=FLAG); 0
fisher-kills. Per family best-z: B/H3 4396.2, B/H1 368540.5, X/H3 5397.6,
X/H1 182813.6, Y/H3 306.3, Y/H1 110264.1. K1 fired: the form change is
KILLED at the primary gate.

**Mechanism learning:**
1. The bypass tap does NOT fix the ceiling. B/H3 best 4.4k is the same
   order as the old form's H3 best (7.0k, O141) — guaranteed linear
   diffusion is not sufficient; the ceiling is in the AND-OR differential
   structure, not the missing linear path.
2. The uniformity+nonlinearity axis moves the needle: Y (bent, NL=6,
   uniform 1/2) 306 vs B (f, NL=5, 3/8) 4396 vs X (balanced, NL=4,
   uniform) 5398. Bent uniform-response is ~14x better than f-with-bypass
   — but still inner-FLAG'd at 0/36, 2+ orders from keep-like.
3. H3 >> H1 in every family (~2 orders) — O131's "confusion budget =
   MUXD count" once more.
4. Balanced-isn't-free, confirmed empirically: X (5.4k) did not beat B
   (4.4k), matching the pre-pilot analysis (both balanced options drop
   NL 5→4).

No 4-gate bar was run (mandate: conditional on keeps ≥1; there were
none). No GHA campaign. Artifacts: `pilot.log`, `t8_andor_form_screen.py`,
`run_pilot.sh`, `backoff_poll_pilot.out`, `CHECKPOINT.md`.
Workreg `track2-andor-form` → done.

## 0. The thesis: the form change, concretely

O141's re-test trigger names a FORM change — "linear bypass tap,
bias-free variant" — never more tap draws. This lane tests exactly that.

### 0.1 Family B — ANDOR with linear bypass tap (PRIMARY thesis)

`ANDORB(a,b,c,d,e)`: `y_i = x_i ^ f(x_{i+a},x_{i+b},x_{i+c},x_{i+d}) ^
x_{i+e}`, `f(p,q,r,s)=(p&q)|(r&s)` (O131/O141-verbatim f).

**Which variable is L, and why (mandate question):** `L = x_{i+e}` with
`e` a DISTINCT fifth tap, `e ∉ {0,a,b,c,d}`. Three candidates, one
survives:

1. `L = x_i` — vacuous: cancels the feedthrough term.
2. `L = x_{i+a}` (one of f's taps) — the guaranteed flip lands on bit
   `j+a`, a bit f ALREADY flips (probabilistically). The deterministic
   contribution is real (flip prob → 1) but the differential spread does
   not widen: no new affected bit.
3. `L = x_{i+e}`, e distinct — adds a NEW deterministically-flipped bit
   `j+e` (rotl convention: `rotl(x,e)[i] = x[(i−e) mod 64)`, so input bit
   j lands in output bit j+e — verified empirically: delta j=10 flips
   bits {10, 17} deterministically for e=7). The guaranteed differential floor grows 1 → 2 bits
   (feedthrough j + bypass j+e). This is EXACTLY MUXD's skeleton
   (`y_i = x_i ^ m(...) ^ x_{i+d}`: feedthrough j + d-tap j−d) with f's
   stronger per-bit function (NL 5 vs MUX NL 2) in place of the MUX core.
   This is the co-design: replicate the guaranteed-diffusion property
   ANDOR lacks, keep the Boolean function O141 exonerated.

**Mechanism grounding (measured, not asserted):** single-stage
single-bit-delta avalanche, 4096 random x, fixed key, quadrant taps
(experiment 2026-10-12, recorded in CALIB-8):

| stage | mean flipped bits / 64 deltas | analytic expectation |
|---|---|---|
| old ANDOR | 2.50 | 1 + 4×3/8 = 2.5 ✓ |
| **ANDORB** | **3.50** | 1 + 1 + 4×3/8 = 3.5 ✓ |
| MUXD | 3.50 | 1 + 1 + 3×1/2 = 3.5 ✓ |

The bypass moves ANDOR's diffusion floor from 2.5 to exactly MUXD's 3.5 —
the "no linear bypass tap" weakness (O141 §0.2.1) is removed by
construction, and the "all-probabilistic spread" (O141 §0.2.2) gains a
deterministic bit. What remains for the pilot to decide: whether f's
superior per-bit nonlinearity (NL 5 vs 2) converts the matched diffusion
floor into a confusion-per-u ADVANTAGE over MUXD (O131 §4(ii) bar).

### 0.2 The bias-free question — analyzed, then split into two families

O141 §0.2.3: f has weight 7/16. Marginal stage output is unbiased
(feedthrough), so the bias that matters is structural: f fires 7/16 of
the time and its differential response is uniformly weak (3/8 on all four
inputs vs the 1/2 ideal). Exact truth-table analysis of candidate
replacement functions (2026-10-12):

| function | weight | NL | max\|W\| | flipP (p,q,r,s) | E[flips] | gate cost |
|---|---|---|---|---|---|
| f=(p&q)\|(r&s) | 7 | 5 | 6 | 3/8 ×4 | 1.50 | 2 AND+OR2 |
| g1=f\|(p&r) | **8** | 4 | 8 | .5,.25,.5,.25 | 1.50 | 3 AND+OR3 |
| g2=f⊕NOR4(p,q,r,s) | **8** | 4 | 8 | 1/2 ×4 | 2.00 | 2 AND+OR2+NOR4+XOR |
| g4=(p&q)^(r&s)^p | 6 | **6** | **4** | 1/2 ×4 | 2.00 | 2 AND+2 XOR |

Findings:

- **Balanced is not free.** Both balanced options (g1, g2) drop NL 5→4
  and max|W| 6→8. g1 is additionally rejected outright: its flipP is
  position-dependent (1/4 corners are weak spots the SEQ gates would
  find) — recorded, not run.
- **g2 = f⊕NOR4** (weight 8, uniform 1/2 differential response, E=2.0):
  the honest bias-free variant. **Family X** = `x ^ g2 ^ x_e`.
  Pre-registered tradeoff: balance + uniform response vs NL 5→4. The
  pilot adjudicates whether uniformity beats raw nonlinearity.
- **g4 = (p&q)^(r&s)^p** (bent: NL=6/max|W|=4 OPTIMAL for 4 vars,
  uniform 1/2, E=2.0, weight 6 — bias −2/16): the other corner.
  **Family Y** = `x ^ g4 ^ x_e`. Pre-registered tradeoff: maximal
  nonlinearity + uniform response vs worse marginal bias. (Bent ⇒
  |W(0)|=4 ⇒ weight 6 or 10 always; bias-free+bent is impossible in 4
  vars — no free lunch, recorded.)

Stage-level avalanche (same experiment as §0.1): X and Y both 4.00 mean
flips (1+1+2.0) — ABOVE MUXD's 3.50. So X/Y attack weaknesses 1+2+3
together; B attacks 1+2 with f's NL intact.

### 0.3 Falsifiable theses (pre-registered)

- **Quality thesis (primary):** ≥1 inner-PASS (lin=PASS ∧ diff=PASS) on
  B/H3 within 10 draws; B/H3 maxworst|z| < 1,000 (old-form H3 best:
  R 7.0k, Q 46.8k, P 37.0k — all inner-killed). If B/H3 inner-kills with
  z in the thousands, the bypass did NOT fix the ceiling → terminal
  verdict with mechanism (the ceiling is in f's differential structure,
  not the missing linear path).
- **Uniformity thesis (secondary):** X/Y maxworst|z| ≤ B's on H3
  (uniform 1/2 response + E=2.0 beats f's 3/8 corners).
- **Cost thesis (measured at S0, estimates flagged):** B ≈ 4.3–4.7u,
  X ≈ 5.0–5.5u, Y ≈ 4.0–4.5u (ESTIMATES — the xor4-5t lesson: unmeasured
  figures are flagged, never trusted). Frame H1 ≈ 12–14u, H3 ≈ 16–19u —
  cost-eligible vs 18.6u by construction. Per O131 §4(ii) the binding bar
  is confusion-per-u > MUXD, not cost.

## 1. Frame and draw types

**Frame:** MU5 verbatim — pre-whiten `x ^= k`; stages; final
`x ^= rotl(k,13)`. Templates H1 `[F, MUXD, MUXD]`, H3 `[F, MUXD×3]`
(hetstage verbatim, F = the new-form stage).

**Tap geometry:** (a,b,c,d) quadrant-spread Q-style (O141's geometric best
case, inherited — geometry was exonerated as the binding constraint, so
the pilot holds it fixed at the best case); **e drawn free** from
`[1,64) \ {a,b,c,d}` (least-tuned choice for the bypass position; a
structured e would confound the form question).

**Draw budget (≤40, mandate):** B/H3 10 + B/H1 6 + X/H3 6 + X/H1 4 +
Y/H3 6 + Y/H1 4 = **36 draws**.

**Draw gates (fail-loud):** a∈[1,16), b∈[16,32), c∈[32,48), d∈[48,64);
e∈[1,64), e∉{a,b,c,d}; all asserts fire on violation.

## 2. Gates (batch-62 lesson: inner-DIFF-SEQ primary)

1. **Primary: inner-DIFF-SEQ** (`screen_lin_diff`, batch-62/hetstage2
   verbatim: N=2^18 sequential outputs, keys 0xffffffffffffffff +
   0xaaaaaaaaaaaaaaaa, LIN+DIFF Holm α=0.01). Runs FIRST on every draw;
   inner-kill iff `diff_verdict != PASS` (lin recorded).
2. **Secondary: fisher triage** (het8 verbatim: KEYS10, N=2^18,
   diff_cell_logps, holm_reject α=0.01).
3. **Keep bar (pre-registered):** inner lin==PASS ∧ diff==PASS ∧ fisher
   n_reject==0.

Keeps route (conditional): 4-gate bar — G3 RD-SEQ (batch-62 verbatim) +
bit-exact bundle (emitter + new forms, 2000 vectors × 3 keys Python-vs-C)
+ **G4 Low1/64 PractRand-256M with the 2026-10-12 parser rule: ANY
PractRand FAIL is a real detection** + MU5-324 control.

## 3. Cost thesis (pre-registered — MEASURED at S0, estimates flagged)

§0.3 estimates; S0 via [run_synth.py](../../run_synth.py) (authorized
path) is the falsifier, conditional on keeps ≥1. Cost bar: S0 strict
**<18.6u**, or Pareto-relevant on cells/area vs
[t6_xorh5_15](../../fast_battery/candidates/t6_xorh5_15/)
(21.8u/5833/17170).

## 4. Calibration (fail-loud, pre-pilot — harness non-vacuity is mandatory)

- **CALIB-1:** b33c and1 → maxworst|z| = 3.3 exact (tol 0.05). Reuse.
- **CALIB-2a:** MU5-324 → inner lin==PASS ∧ diff==PASS ∧ fisher
  n_reject==0 (KEEP). Positive control.
- **CALIB-2b:** linear-4 → fisher n_reject > 0 (REJECT). Negative control.
- **CALIB-5a:** t6_b59_47 → inner lin==PASS ∧ diff==PASS. Reuse.
- **CALIB-6:** seed-pinned O131-verbatim random-tap ANDOR H3 draw → inner
  diff_verdict != PASS (reproduces the O131 kill; gate sees old failure).
- **CALIB-7:** 500 5-tap draws per family → quadrants hold, e distinct
  nonzero (draw-gate soundness).
- **CALIB-8 (NEW, mechanism):** single-stage avalanche (4096 x, fixed
  key, §0.1): mean flips old 2.50±0.10, B 3.50±0.10, X 4.00±0.10,
  Y 4.00±0.10, MUXD 3.50±0.10 — proves the harness implements the
  intended forms AND the bypass determinism (for B: bit j+e flips on ALL
  4096 xs for every delta j — asserted exactly).
- **CALIB-9 (NEW, function properties):** truth-table asserts —
  f: wt=7 NL=5 flipP=3/8×4; g2: wt=8 NL=4 flipP=1/2×4; g4: wt=6 NL=6
  flipP=1/2×4. Guards against a wrong-function bug (independent of the
  harness's vectorized implementation).
- **Selftest (pre-calib):** ANDORB/ANDORX/ANDORY bit-exact vs scalar (50
  draws × 3 families); draw-gate soundness; inner gate smoke; H1/H3
  template shape.

## 5. Kill rules (pre-registered)

- **K1:** 0/36 inner-PASS across B/X/Y → **form-change KILLED at the
  primary gate** → terminal verdict: the ANDOR ceiling is in f's
  differential structure even with guaranteed linear diffusion; neither
  the bypass (B) nor balance+uniformity (X) nor maximal nonlinearity (Y)
  fixes it. Mechanism recorded; O-entry in VERDICT_SCOPE.md.
- **K2:** ≥1 keep → 4-gate bar → bundle → S0. S0 ≥ 18.6u → COST-CLOSED
  (speed); size-axis fallback ONLY if cells ≪ 5,833 AND delay ≤ 21.8u
  AND area < 17,170; else full kill.
- **K3 (family-level):** B dies but X or Y keeps → the bias/uniformity
  axis was binding, not the bypass — recorded as the mechanism learning.

## 6. Escalation on support (conditional, built only if pilot keeps ≥1)

GHA full-pool campaign (per [POOL_DESIGN.md](../POOL_DESIGN.md) §8 submit
pattern, PAT push path; GHA minutes unlimited, public repo): pool of
B/X/Y draws (H1/H3), new tenant `projects/mix-andor-form-search/`
(proposed) reusing the sbox-search flow image; gates = draw-gate
validation → unit-delay stage cost (pinned flow) → frame inner-DIFF-SEQ
primary triage → cost-eligible (≤18.6u frame estimate) fisher triage →
keeps. GHA results are leads; PARETO/RETAINED/RTL adjudication stays
local.

## 7. Principled cuts (per-cut justification)

1. **No H2 template:** hetstage showed no positional rescue; H3 gives the
   hetero stage maximum MUXD post-diffusion (best chance), H1 tests the
   pre-diffusion position. H2 adds draws, not information.
2. **No g1 (`f|(p&r)`) family:** balanced but NL 5→4 AND
   position-dependent flipP (1/4 corners) — dominated by X on uniformity
   and by B on NL; running it would confound the balance question with a
   known-weak differential structure.
3. **No 2-bypass variant in the pilot:** MUXD has exactly one bypass;
   the pilot tests the minimal form change. Two-bypass is a recorded
   follow-up axis conditional on B being close-but-not-quite.
4. **e drawn free, not structured:** the least-tuned choice; a
   structured e would confound the form-change question with a new
   geometry thesis (O141 closed the geometry axis).
5. **No old-form R control draws:** the old form is killed 0/36 (O141);
   CALIB-6's pinned draw is the control. Draws are spent on the new
   forms.
6. **No compounds** (ANDORB+GF, ANDORB+CIRC2): the pilot tests the base
   form; compounds are conditional follow-ups.
