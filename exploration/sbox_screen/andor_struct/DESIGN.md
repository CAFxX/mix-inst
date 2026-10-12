# track2-andor-struct — ANDOR with co-designed structured taps, inner-DIFF-SEQ primary triage

**Track:** 2 (broad screen) · **Owner:** track2-andor-struct (subagent, lane
opened 2026-10-12 ~12:35 CEST, from O131 §4(ii), previously ownerless)
**Date:** 2026-10-12 · **Status:** TERMINAL — pilot COMPLETE 0/36 KEEP
(2026-10-12 ~10:51Z, adjudicated raw from `pilot.log`).
**Verdict number at close:** O141 (ledger top O140 re-read 2026-10-12 12:55
CEST at write time).
**Parent verdicts:** O131 (type C ANDOR-with-random-taps KILLED at triage
0/40, best z=26k, dominated 3–4 orders of magnitude below dense-GF's 5.1;
"weak confuser AND weak diffuser"), O140 (hetstage2 terminal: dense GF +
3 MUXD erases the fisher residual but dies at PractRand BCFN/Gap/FPF —
hetero contribution still < a 4th MUXD; re-test trigger names exactly this
lane: "hetero stage with higher confusion-per-u than MUXD (O131 §4(ii):
ANDOR with co-designed structured taps, or a new hetero family)").
**Seed:** 0xB804 (fresh; hetstage2 0xB803, hetstage 0xB802, het8 0xB801).

## Pilot result (raw-artifact adjudication, 2026-10-12 ~10:51Z)

**0/36 KEEP** (seed 0xB804; `pilot.log`: "0/36 KEEP (inner_kills=36
fisher_kills=0)"). Every draw inner-killed (lin=FLAG diff=FLAG); the
fisher triage also catastrophically rejected all 36 (n_reject=10,
maxworst|z| 7.0k–1.48M). Per family best-z: Q/H1 380k, Q/H3 46.8k,
P/H1 720k, P/H3 37.0k, R/H1 461k, **R/H3 7.0k** — the random control's
best draw beats both structured families. Q/H3 < Q/H1 and P/H3 < P/H1
(the extra MUXD post-diffusion helps, O131's "confusion budget = MUXD
count" again) but 4+ orders of magnitude from the bar. K1 fired:
structured-tap ANDOR is KILLED at the primary gate — tap geometry was
NOT the binding constraint. The O131 §4(ii) lead is CLOSED as drawn;
its re-test trigger (§8) names a form change, never more tap draws.
No 4-gate bar was run (mandate: conditional on keeps ≥1; there were
none). Artifacts: `pilot.log`, `t8_andor_struct_screen.py`,
`gate4_andor.py` (built, unrun — conditional).

## 0. The thesis: what "co-designed structured taps" means and why it could win

O131's thesis: a single hetero stage can't beat pure-MUXD because its
marginal contribution is < another MUXD. The search needs a hetero stage
with HIGHER confusion-per-u than MUXD. The concrete form named: ANDOR
with co-designed structured taps (not random taps) in the MU5 frame.

### 0.1 The ANDOR stage, exactly

`ANDOR(a,b,c,d)`: `y = x ^ ((rotl(x,a) & rotl(x,b)) | (rotl(x,c) & rotl(x,d)))`
— per output bit i: `y_i = x_i ^ f(x_{i+a}, x_{i+b}, x_{i+c}, x_{i+d})`
with `f(p,q,r,s) = (p&q)|(r&s)` (hetstage verbatim). Cost 3.70u measured
in the pinned flow (O131 §3) — cheaper than MUXD's 4.00u.

### 0.2 What the Boolean function itself buys — and what it doesn't

Computed 2026-10-12 (Walsh spectrum, exact): `f` has max|W| = 6, weight 7
(bias +1/16 toward 1), NL = 5 of 4 variables (max 6). The MUX function
`m(s,a,b)` has max|W| = 4, NL = 2 of 3 (optimal). Normalized: ANDOR-f
NL/2^{n-1} = 5/8 = 0.625 vs MUX 2/4 = 0.5 — **the Boolean function is NOT
the weak link**; per bit it is more nonlinear than the MUX core. O131's
"weak confuser" is therefore a statement about the *stage as wired*, not
about `f`. The wiring weaknesses are derivable:

1. **No linear bypass tap.** MUXD: `y_i = x_i ^ m(x_{i+s},x_{i+a},x_{i+b}) ^
   x_{i+d}` — the `d` tap is a guaranteed linear diffusion path: a
   single-bit input delta flips ≥1 extra output bit *deterministically*.
   ANDOR has all four taps inside `f` — its entire differential spread is
   probabilistic.
2. **All-probabilistic differential spread.** Input Δ = e_j affects output
   bits {j−a, j−b, j−c, j−d} (plus the feedthrough bit j). Each affected
   AND-OR bit flips iff the delta'd AND input's partner = 1 AND the other
   AND = 0: probability (1/2)(3/4) = **3/8** per bit, expected 1.5 flipped
   bits, *zero guaranteed*. MUXD: 3 nonlinear-affected bits at prob ~1/2
   (expected 1.5) PLUS 1 guaranteed linear bit.
3. **Output bias 1/16.** `f` has weight 7/16. The bias interacts with
   sequential-input structure (the SEQ-based gates sweep low-bit patterns).
4. **Random tap geometry can cluster and correlate the spread.** This is
   the ONLY one of the four that tap structure can fix — and it is this
   lane's thesis.

### 0.3 The structured-tap thesis (the co-design)

With random 4-tap draws, the four differentially-affected output bits
{j−a, j−b, j−c, j−d} can cluster in a narrow window, and — worse — the
*flip conditions* for those bits share variables when taps are close
(e.g. taps {3,5}: the flip condition of bit j−3 involves x_{j+2}, and of
bit j−5 involves x_j itself — overlapping conditions correlate the four
flip events). Correlated, clustered differentials are exactly what the
SEQ-based gates (fisher DIFF on sequential inputs, inner DIFF-SEQ) detect.

**Family Q — quadrant-spread taps (primary thesis):** draw
a ∈ {1..15}, b ∈ {16..31}, c ∈ {32..47}, d ∈ {48..63}. By construction
each output bit's AND-OR sees the full word: the four affected bits are
spread across four 16-wide windows, and the flip conditions draw on
decorrelated variable sets. This maximizes per-bit support width and
minimizes inter-bit differential correlation — the geometric best case
for the AND-OR function. Per-cut justification: every random draw that
clusters is provably narrower than every Q draw; Q excludes the
clustering failure mode by construction rather than by luck.

**Family P — paired ± taps (secondary thesis):** taps {a, −a, b, −b}
mod 64, a,b ∈ {1..31}, a ≠ b. The differential spread becomes symmetric:
Δ = e_j affects {j, j−a, j+a, j−b, j+b} — a balanced ± pattern. Tests
whether symmetric spread (vs Q's decorrelated spread) is what the gates
reward. Distinctness: a≠b, neither 0 nor 32 ⇒ all four distinct mod 64.

**Family R — random-tap replay (control, NOT a thesis):** O131-verbatim
random 4 distinct taps. Expected: inner-REJECTED (reproduces the O131
kill at the new primary gate; proves the gate sees the old failure).
If R inner-passes while Q/P die, the data says geometry is irrelevant
and the draw count was the story — recorded as such.

### 0.4 Honest pre-registration of what taps CANNOT fix

Structured taps address weakness 4 only. Weaknesses 1–3 (no linear
bypass, 3/8 all-probabilistic spread, 1/16 bias) are intrinsic to the
ANDOR form. The pilot's binary question: **is tap geometry the binding
constraint?** If Q/P inner-pass where R dies → YES, geometry was binding,
the intrinsic weaknesses are survivable in the MU5 frame, and the lead is
real (escalate: wider pool, bias/form variants as follow-up axes). If all
three families die → the ANDOR form's confusion-per-u ceiling is below
MUXD regardless of tap geometry → TERMINAL for this axis, with a precise
mechanism (not "unlucky draws"). The re-test trigger then names a *form*
change (linear bypass tap, bias-free variant), never more tap draws.

## 1. Frame and draw types

**Frame:** MU5 verbatim — pre-whiten `x ^= k`; stages; final
`x ^= rotl(k,13)`. Templates H1 `[H, MUXD, MUXD]`, H3 `[H, MUXD×3]`
(hetstage verbatim). ANDOR is the hetero stage H.

**Draw budget (≤40, mandate):** Q/H1 8 + Q/H3 8 + P/H1 6 + P/H3 6 +
R/H1 4 + R/H3 4 = **36 draws**.

**Draw gates (fail-loud):**
- Q: a∈[1,16), b∈[16,32), c∈[32,48), d∈[48,64); assert quadrants hold.
- P: a,b ∈ [1,32), a≠b; taps (a, −a mod 64, b, −b mod 64); assert 4
  distinct, none 0.
- R: 4 distinct taps from 64 (O131 `_draw_andor` verbatim).

## 2. Gates (batch-62 lesson: inner-DIFF-SEQ primary)

1. **Primary: inner-DIFF-SEQ** (`screen_lin_diff`, batch-62/hetstage2
   verbatim: N=2^18 sequential outputs, keys 0xffffffffffffffff +
   0xaaaaaaaaaaaaaaaa, LIN+DIFF Holm α=0.01). Runs **FIRST** on every draw;
   a draw inner-kills iff `diff_verdict != PASS` (lin recorded).
2. **Secondary: fisher triage** (het8 verbatim: KEYS10, N=2^18,
   diff_cell_logps, holm_reject α=0.01). Runs on every draw (compute order;
   keep bar is the conjunction).
3. **Keep bar (pre-registered):** inner lin==PASS ∧ diff==PASS ∧ fisher
   n_reject==0.

Keeps route (conditional): 4-gate bar — G3 RD-SEQ (batch-62 verbatim) +
bit-exact bundle (C emitter + ANDOR, 2000 vectors × 3 keys Python-vs-C) +
**G4 Low1/64 PractRand-256M prescreen with the 2026-10-12 parser rule:
ANY PractRand FAIL (not just Low1-family) is a real detection**
(per `new_constructions/batch62/t6_b62_screen.py` eval_low1); fail-loud if
RNG_test never reaches 256MB. MU5-324 control runs in the 4-gate bar
(load-bearing diagnostic, hetstage2 verbatim).

## 3. Cost thesis (pre-registered, falsifiable at S0 — MEASURED, not estimated)

Measured anchors (O131 §3, pinned yosys 0.69 + abc mini.genlib,
dual-analyzer): andor **3.70u**, muxd **4.00u**. Frame cost ≈
H1: 3.70+8.00 = **~11.7u**; H3: 3.70+12.00 = **~15.7u** — cost-eligible
vs the 18.6u frontier speed point
([t6_b59_47](../../fast_battery/candidates/t6_b59_47/)) by construction,
with S0 via [run_synth.py](../../run_synth.py) (authorized path) as the
falsifier. Cautionary anchor (O131): xor4-5t measured 5.50u vs het8's
~4.0u figure — unmeasured figures are estimates; **every cost claim in
this lane is measured or flagged**.
Cost bar: S0 strict **<18.6u**, or Pareto-relevant on cells/area vs
[t6_xorh5_15](../../fast_battery/candidates/t6_xorh5_15/)
(21.8u/5833/17170).

## 4. Calibration (fail-loud, pre-pilot — harness non-vacuity is mandatory)

- **CALIB-1:** b33c and1 → maxworst|z| = 3.3 exact (tol 0.05). Reuse.
- **CALIB-2a:** MU5-324 → inner lin==PASS ∧ diff==PASS ∧ fisher
  n_reject==0 (KEEP). **Positive control: must PASS all gates.**
- **CALIB-2b:** linear-4 → fisher n_reject > 0 (REJECT). **Negative
  control: must be REJECTED.**
- **CALIB-5a:** t6_b59_47 → inner lin==PASS ∧ diff==PASS (batch-62
  CALIB-3a verbatim).
- **CALIB-6 (NEW, draw-level negative):** a seed-pinned O131-verbatim
  random-tap ANDOR H3 draw → inner diff_verdict != PASS (reproduces the
  O131 kill at the new primary gate; proves the gate sees the old
  failure mode).
- **CALIB-7 (NEW, structured draw-gate soundness):** 500 Q draws → all
  taps in the four quadrants, 4 distinct; 500 P draws → ± pairing valid,
  4 distinct, none 0.
- **Selftest (pre-calib):** ANDOR bit-exact vs scalar (50 draws, the
  hetstage check verbatim); Q/P draw-gate soundness; inner gate smoke.

## 5. Kill rules (pre-registered)

- **K1:** 0/32 structured (Q+P) inner-PASS draws → **structured-tap ANDOR
  KILLED at the primary gate** → terminal verdict: tap geometry was NOT
  the binding constraint; the ANDOR form's confusion-per-u ceiling is
  below MUXD. Mechanism recorded (§0.4).
- **K2:** ≥1 keep → 4-gate bar → bundle → S0. S0 ≥ 18.6u → COST-CLOSED
  (speed); size-axis fallback ONLY if cells ≪ 5,833 AND delay ≤ 21.8u
  AND area < 17,170; else full kill.
- **K3:** zero inner-PASS across all three families → terminal verdict,
  mechanism recorded.

## 6. Escalation on support (conditional, built only if pilot keeps ≥1)

GHA full-pool campaign (per [POOL_DESIGN.md](../POOL_DESIGN.md) §8 submit
pattern, PAT push path; GHA minutes unlimited, public repo): pool of
structured-tap ANDOR draws (Q/P families, H1/H3), new tenant
`projects/mix-andor-struct-search/` (proposed) reusing the sbox-search
flow image; gates = draw-gate validation → unit-delay stage cost (pinned
flow) → frame inner-DIFF-SEQ primary triage → cost-eligible (≤18.6u
frame estimate) fisher triage → keeps. GHA results are leads;
PARETO/RETAINED/RTL adjudication stays local. (The cancelled
hetstage2-screen-20261012 tenant pattern is the template.)

## 7. Principled cuts (per-cut justification)

1. **No H2 template:** hetstage showed no positional rescue (C type died
   3–4 orders of magnitude from the bar on H1, H2, and H3 alike); H3
   gives the hetero stage maximum MUXD post-diffusion (best chance), H1
   tests the pre-diffusion position. H2 is the interpolation — adds
   draws, not information.
2. **No Boolean-function variants in the pilot** (e.g. `(a&b)^(c&d)`,
   6-tap bias-reduced forms): the lead names *structured taps*, not a new
   function. Function variants are pre-registered follow-up axes
   conditional on structured-tap support — running them now would
   confound the geometry question.
3. **No compounds** (ANDOR+GF, ANDOR+CIRC2): the pilot tests the base
   form; compounds are conditional follow-ups.
4. **R capped at 8:** the random form is already killed (O131, 0/40);
   the 8 R draws are controls, not a re-screen.

## 8. Terminal axes (if K1/K3 fires — draft)

1. **Form change, not more taps:** the re-test trigger names a different
   ANDOR *form* — a linear bypass tap (MUXD-style guaranteed diffusion),
   or a bias-free variant — never another tap-geometry draw.
2. **New hetero family:** per O140's re-test trigger, any hetero family
   with a derivable confusion-per-u advantage over MUXD.
