# track2-hetstage — cheap non-S-box hetero stage pool in the MU5 frame

**Track:** 2 (broad screen) · **Owner:** track2-hetstage (subagent, lane opened 2026-10-12 ~10:15 CEST)
**Date:** 2026-10-12 · **Status:** TERMINAL — VERDICT O131 (2026-10-12 10:49 CEST).
Pilot 0/120 fisher-keeps (seed 0xB802). K1 fired for all three types.
Mechanism: linear hetero stages contribute diffusion but zero confusion —
the frame's confusion budget is the MUXD count (2 MUXD → z~10^3–10^6 via
select-stagnation passthrough; 3 MUXD + dense GF → z~5–9 with a systematic
residual truncated differential, inner DIFF-SEQ FLAG on both best draws).
ANDOR dominated (best z=26k vs GFMUL's 5.1). Cost measured, never binding.
No GHA campaign (conditional on keeps). Next axes in ledger O131 entry.
**Parent verdicts:** O129 (8-bit SPN COST-CLOSED), O132 (single 8-bit hetero box STRUCTURALLY KILLED at triage).
**Seed:** 0xB802 (fresh; het8 used 0xB801).

## 0. Why this axis (the O132 lesson, structural)

O132 killed the single 8-bit hetero *box*: for input deltas 2^k, k≥8 the
low-byte box is TRANSPARENT (identity-box control byte-identical), and the
coverage argument is arithmetic — one 8-bit box covers 1/8 of the 64-bit
delta space, so the frame must be independently DIFF-clean (≥4 MUXD stages,
xorh5 precedent) → box+frame ≈ 30u ≫ 18.6u. **The box ate 10.4u of the
18.6u budget and covered 8 bits.**

The hetero-*stage* concept is validated (t6_xorh5_15: XOR4 stage inside a
MUXD cascade → Frontier S+Q cells/area point). This axis replaces the box
with CHEAP hetero stages that (a) cost 2–8u instead of 10.4u, leaving
7–9u of headroom for diffusion depth, and (b) touch all 64 bits every
application — structurally immune to O132's 1/8-coverage transparency
trap. The thesis: **cheap hetero stages buy stage-depth under the 18.6u
bar; depth buys quality.**

## 1. Frame and stage types

**Frame:** MU5 verbatim — pre-whiten `x ^= k`; stages; final `x ^= rotl(k,13)`.

**Type A — linear circulants** (rotation-XOR mixes):
- A1 `CIRC1`: `x ^= rotl(x,a)`, a odd ∈ 1..63. Rank exactly 63
  (c(z)=1+z^a=(1+z)·u(z), u(1)=1 → kernel {0, all-ones}; a even ⇒ rank ≤ 62,
  draw-gate excludes). **Control arm**: expected to DIFF-die (O127 lesson:
  2-term linear as sole diffusion carrier was DIFF-killed in w3prime2).
  If it keeps here, the frame's MUXD stages carry the nonlinear load and
  ultra-cheap linear suffices — update the thesis.
- A2 `CIRC2`: `x ^= rotl(x,a) ^ rotl(x,b)`, a,b distinct nonzero.
  Draw-gate: rank 64 (bijective; GF(2) elimination on the 64×64 matrix,
  fail-loud). Co-diff criterion: min output weight over weight-2 inputs ≥ 4
  (no sub-4 cancellation; computed at draw time).

**Type B — GF-mul-by-constant** (fixed linear bijections):
- `GFMUL(C)`: x ↦ x ⊗ C in GF(2^64), P(z) = z^64+z^4+z^3+z+1 (irreducible).
  Any C ≠ 0 is a bijection. Draw-gate: popcount(C) ∈ {3,5,7}, deg(C) ≥ 8
  (excludes monomials/shifts and C=1). Density is DIAGNOSTIC, not gated:
  matrix weight recorded per draw; the density thesis is tested
  empirically by the fisher gate across the pc=3/5/7/dense gradient (a
  hard weight gate at avg≥10 would have rejected all pc=3 draws —
  measured gfm3 weight=336 vs gfm7=850, §8).
  **O128/O127 diffusion lessons respected**: the full GF mult (dense P,
  al_w3p_a) is cost-prohibitive as a stage (b2sparse 34.9–35.8u); only
  SPARSE constants are drawn. Numpy impl: precomputed 64×64 bit matrix,
  y_j = parity(x & mask_j) — vectorized, ~64 vector ops per eval.
- Density-control arm: 4 draws with popcount(C) ∈ {24..40} (bypass the
  {3,5,7} gate, documented) — tests whether the gates respond to
  diffusion density as designed.

**Type C — AND-OR mixes** (nonlinear, non-box):
- `ANDOR`: `x ^= (rotl(x,a) & rotl(x,b)) | (rotl(x,c) & rotl(x,d))`,
  a,b,c,d pairwise distinct (fail-loud). Per-bit AO22 + XOR: degree-2,
  full-64-bit coverage every application (anti-O132 by construction).
- Bijectivity NOT required: the x⊕g(x) form is the MUXD precedent
  (t6_b59_47 frontier point is non-bijective per stage); quality is judged
  by the gates, not by stage bijectivity. Diagnostic only: empirical
  distinct-output fraction on 2^16 samples, recorded per draw.

MUXD/XOR4 draw operators verbatim from het8 (`_draw_muxd`, `_draw_xor4`;
s/a/b pairwise-distinct, d free).

## 2. Position thesis

Nonlinear hetero belongs EARLY (het8 position thesis, unrefuted): the
hetero stage's output must be diffused by post-stages; late placement
wastes post-diffusion. Linear hetero (A, B) commutes structurally, but
early placement diffuses the whitened key input soonest — same primary.
- **H1** `[H, MUXD, MUXD]` — primary (14 draws/type).
- **H2** `[MUXD, H, MUXD]` — position control (13 draws/type).
- **H3** `[H, MUXD, MUXD, MUXD]` — xorh5-recipe probe (13 draws/type):
  tests whether a cheap hetero stage substitutes for the XOR4 in the
  DIFF-clean frame recipe (xorh5 = XOR4 + 4×MUXD, 21.8u; here H + 3×MUXD).

Per-type draw budget (≤40, mandate): A: 40 (20 CIRC1 + 20 CIRC2, split
7/7+7/6+6/7 across H1/H2/H3); B: 40 (36 sparse C, popcount 3/5/7 = 12/12/12
across H1/H2/H3, + 4 dense-control draws popcount 24..40 in H1); C: 40.
**Total 120 draws.**
**Type-B H3 is cost-marginal by measurement** ([GFM3, 3×MUXD] ≈ 18.9u,
[GFM7, 3×MUXD] ≈ 21.1u ≥ 18.6u): it runs as a quality-needs-depth
mechanism probe (het8-T4 precedent) — a keep ONLY on B-H3 is mechanism
evidence for COST-CLOSED (speed axis), not a success.

## 3. Cost thesis per type (falsifiable at S0)

**MEASURED** (`stage_cost.py`, pinned yosys 0.69 + abc mini.genlib flow,
dual-analyzer XCHECK, 2026-10-12):

| stage | cells | crit |
|---|---|---|
| muxd (anchor) | 192 | **4.00u** (het8: 3.86u — reproduces within 0.15u) |
| xor4-5t (anchor) | 727 | **5.50u** (het8 DESIGN claimed ~4.0u — **does NOT reproduce**; see note) |
| circ1 (A1) | 64 | **2.00u** |
| circ2 (A2) | 128 | **4.00u** |
| andor (C) | 384 | **3.70u** |
| gfm3 (B, pc=3, C=0x2000000801, matrix wt 336) | 326 | **6.90u** |
| gfm7 (B, pc=7, matrix wt 850) | 870 | **9.10u** |

Frame estimates (isolation sums; S0 arbitrates on the bundle):
- A: H1 [CIRC2+2×MUXD] ≈ 12.0u, H3 ≈ 16.0u; CIRC1 versions ≈ 10.0u/14.0u.
- B: H1 [GFM3+2×MUXD] ≈ 14.9u < 18.6u (3.7u headroom); [GFM7+2×MUXD]
  ≈ 17.1u (thin); B-H3 ≈ 18.9–21.1u — cost-marginal, mechanism probe (§2).
- C: H1 [ANDOR+2×MUXD] ≈ 11.7u, H3 ≈ 15.7u — most headroom.
**Note (anchor discrepancy):** het8's "~4.0u" XOR4 figure does not reproduce
in the pinned flow (5.50u measured). Moot for het8 (died at K1 triage, S0
never ran), but het8's cost thesis arithmetic (10.4+4.0+3.9≈18.3u) was
optimistic — the true figure would have been ≈19.9u. Recorded for the
error-class hunt; this lane's thesis uses measured numbers only.
**Size axis:** t6_b33b is the size point (20.1u); t6_xorh5_15 the
cells/area point (21.8u/5,833/17,170). A cheap-stage frame at ~10–15u
with ≪ 5,833 cells is a size-axis challenger even if it misses 18.6u —
K2 routes accordingly.

## 4. Quality gates (verbatim instruments)

- **Fisher triage** (het8/batch-62 verbatim): KEYS10 (screen_lib KEYS[:10]),
  N=2^18, `diff_cell_logps`, `holm_reject` ALPHA=0.01 → **KEEP iff
  n_reject == 0**.
- **Inner gate (keeps only)** (batch-62 calibration): `screen_lin_diff`
  on 2^17-pair full-range sequential outputs, keys
  0xffffffffffffffff + 0xaaaaaaaaaaaaaaaa →
  lin_verdict==PASS ∧ diff_verdict==PASS.
- Keeps advancing to bundle additionally face the full batch-62 4-gate bar
  (fisher + inner DIFF-SEQ/LIN + RD-SEQ + Low1/64 PractRand-256M prescreen)
  before S0.

## 5. Calibration (fail-loud, pre-pilot)

- **CALIB-1:** b33c and1 → maxworst|z| = 3.3 exact (tolerance 0.05).
- **CALIB-2a:** MU5-324 (5-stage MUXD) → n_reject == 0 (KEEP).
- **CALIB-2b:** linear-4 → n_reject > 0 (REJECT). Non-vacuity.
- **CALIB-3a (draw-gate soundness):** 200 CIRC2 draws → all rank 64;
  200 CIRC1 draws → all rank exactly 63. Fail-loud on any slip.
- **CALIB-3b (GFMUL):** matrix impl == bit-loop reference on 2000 random
  (x, C); gf(x,1)==x; known-answer 2^63⊗2^63 vs hand-reduced
  (x^63+x^62+x^6+x^4+x^3+x per P).
- **CALIB-3c (ANDOR):** bit-exact vs scalar Python reference, 2000 random
  vectors; 200 draws all satisfy pairwise-distinct taps.
- **CALIB-4 (cost):** `stage_cost.py` — MUXD ≈ 3.86u, XOR4 ≈ 4.0u
  (±0.3u; proves the pinned flow is on the het8 scale), then report
  CIRC1/CIRC2/ANDOR/GFM3/GFM7.

## 6. Kill rules (pre-registered)

- **K1:** per type, 0/30+ fisher-keeps across H1–H3 → type KILLED at
  triage (O-entry, mechanism). Per subtype (CIRC1 vs CIRC2): 0/15+ with a
  mechanistic explanation → subtype killed (CIRC1 is the expected-kill
  control; its death confirms the O127 mechanism in this frame).
- **K2:** ≥1 keep → bundle (bit-exact 2000/200 Python-vs-C + 200/200
  iverilog) → S0 (`run_synth.py` authorized path, strict <18.6u, XCHECK
  clean). S0 ≥ 18.6u → COST-CLOSED (speed axis); size-axis fallback ONLY
  if cells ≪ 5,833 (xorh5 cells point); else full kill.
- **K3:** inner gate flags all keeps → KILLED, mechanism recorded.

## 7. Escalation on support

keep → 4-gate bar → bundle → S0 → XCHECK → staged battery S1–S4 → Q1
(sac_z5=0) → **GHA full-pool campaign** (spec, built only on pilot
support): pool = 300 drawn hetero stages of the surviving type(s)
passing draw-gates (JSONL); new tenant `projects/mix-hetstage-search/`
reusing mix-sbox-search `flow/` (validate draw-gates → unit-delay stage
cost, pinned flow → frame fisher triage H1/H2/H3 in numpy → aggregate
keeps); submitted via PAT push (github-pat skill), priority new-leads.
GHA results are leads; PARETO/RETAINED/RTL adjudication stays with the
30m report runs.

## 8. Principled cuts (per-cut justification)

1. **16-bit boxes OFF the table:** O129's per-box floor (≥10.4u for 8-bit)
   extends — a 16-bit box costs ≥ the 8-bit floor while covering 1/4 of
   the delta space per application; the (cost, coverage) ratio is worse
   than the already-killed 8-bit box. No measurement needed.
2. **No 4-bit boxes in this pool:** pool closed 2026-10-10 + cost-terminal
   (POOL_DESIGN.md §2.3); re-screening is not widening.
3. **No dense-constant GF mults:** b2sparse O128 cost-terminal (34.9u);
   only sparse C drawn (this is the co-design, not a blind swap).
4. **Single hetero form per type in the pilot** (no ANDOR+e-term, no
   CIRC4): the pilot tests the base forms; variants are pre-registered
   follow-ups conditional on support.

## 9. Terminal (all types die): O131 draft axes

1. H3-keeps-only signature → reframe around the xorh5 recipe: cheap
   hetero as XOR4-replacement in 5-stage DIFF-clean frames.
2. ANDOR dies on DIFF while CIRC lives → hetero PAIRS: ANDOR+CIRC2 as a
   co-designed compound stage (not independent draws).
3. O132-style structural transparency (identity-hetero control
   byte-identical) → promote the inner gate to primary triage and
   revisit the frame's linear post-stages (batch-62 lesson).

## Appendix: stage-cost calibration (measured 2026-10-12, `cost.log`)

`stage_cost.py` rc=0. gfm3: C=0x2000000801 matrix weight=336 (avg 5.2/col);
gfm7: C=0x1000800200200211 matrix weight=850 (avg 13.3/col).
Per-stage crit (pinned flow): muxd 4.00u, xor4-5t 5.50u, circ1 2.00u,
circ2 4.00u, andor 3.70u, gfm3 7.20u, gfm7 9.40u. Full table in §3.
Anchor check: MUXD reproduces het8's 3.86u within 0.15u (flow on-scale);
XOR4-5t does NOT reproduce het8's ~4.0u claim (5.50u) — discrepancy
recorded in §3, moot for het8 (K1 kill) but relevant to the error-class
hunt: unmeasured cost figures in a DESIGN must be flagged as estimates.
