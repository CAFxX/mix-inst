# track2-hetstage2 — dense GF-mul-by-constant pool + [CIRC2, MUXD×4], inner-DIFF-SEQ as primary triage

**Track:** 2 (broad screen) · **Owner:** track2-hetstage2 (subagent, lane opened 2026-10-12 ~11:35 CEST, from O131 §4(i), previously ownerless)
**Date:** 2026-10-12 · **Status:** PILOT COMPLETE 9/36 KEEP (seed 0xB803,
adjudicated from `pilot.log` + `pilot_keeps.jsonl` 2026-10-12 ~10:05Z) —
4-gate bar LAUNCHED on the 9 keeps (`gate4.py`, backoff CLEAR load 10.32,
setsid nice-19, workreg `track2-hetstage2`); GHA campaign build in progress.
**Verdict number at close:** O140 (ledger top O139 read 2026-10-12 12:00 CEST).
**Parent verdicts:** O131 (cheap hetero stages KILLED at triage, 0/120; dense-C
dose-response pc 3→5→7: z=5280→250→9.0 with a systematic residual truncated
differential, inner DIFF-SEQ FLAG on both best draws), O132 (8-bit box
structural), O129 (8-bit SPN COST-CLOSED).
**Seed:** 0xB803 (fresh; het8 0xB801, hetstage 0xB802).

## Pilot result (raw-artifact adjudication)

- **Type D/H3 (dense GF, 3×MUXD post): 4/8 KEEP** — pc=16 z=2.4, pc=24 z=2.9,
  pc=32 z=3.5, pc=40 z=3.4 (all inner lin=PASS diff=PASS + fisher n_reject=0).
  Non-monotonic: pc=10/12/20 inner-killed (z=51/62/17), pc=8 inner-PASS but
  fisher-killed (n_reject=2, z=6.1) — the specific C matters, not just density.
  Measured matrix weights lower than the §3 extrapolation (pc=24: wt=1484,
  pc=40: wt=2221) → frame cost ≈ 23–27u: COST-CLOSED on speed, but the
  **mechanism question is answered POSITIVELY** — dense GF pre-diffusion +
  3 MUXD erases the O131 residual.
- **Type R5 [CIRC2, MUXD×4]: 5/12 KEEP** — z=2.3/2.8/3.2/3.2/3.8, all
  inner-PASS + fisher-PASS. The size-axis challenger is ALIVE (~20.0u,
  ~900 cells vs [t6_xorh5_15](../../fast_battery/candidates/t6_xorh5_15/)
  21.8u/5833/17170).
- **Type D/H1, D/H2, sparse controls: 0/16** — all inner-killed. Dense GF
  needs the 3-MUXD post-diffusion (H3); H1/H2 insufficient. Consistent with
  O131's "frame's confusion budget is the MUXD count".
- K1 NOT fired (both types have keeps). K2 route: 4-gate bar → S0.
- Open control question: MU5-324 (5×MUXD) inner/fisher — is R5's CIRC2
  load-bearing? (`gate4.py` runs it as a diagnostic.)
- **ANSWERED 2026-10-12 ~10:10Z:** MU5-324 → inner lin=PASS diff=PASS, fisher
  n_reject=0, z=3.2 — **5×MUXD alone is triage-clean** (z=3.2 vs R5 keeps'
  2.3–3.8). The R5 keeps' CIRC2 is NOT proven load-bearing; the 5-stage MUXD
  frame does the work. R5 is a 5-stage-frame observation, not a hetero-stage
  discovery.

## 4-gate bar interim (2026-10-12 ~10:10Z, raw-artifact adjudication)

- k00 (R5, z=2.29): G3 PASS, bundle bit-exact PASS → **G4 LOW1-REJECT**
  ([Low1/64]FPF/16:all R=+9.3 p=2.6e-6 suspicious; worst_p=2.60e-15).
- k01 (D/H3 pc=16, z=2.41): G3 PASS, bundle PASS → **G4 LOW1-REJECT**
  ([Low1/64]BCFN(2+1,13-9U) R=+47.8 p=7.0e-12 FAIL).
- k02 (R5, z=2.75): **G3 RD-SEQ REJECT** (n_reject=1) → G4 skipped.
- k03–k08 in flight (`gate4.py`, setsid nice-19). Pattern so far: triage
  keeps are falling to the deeper gates — the 4-gate bar is falsifying what
  fisher+inner passed.

## GHA campaign (submitted 2026-10-12 ~10:40Z)

`hetstage2-screen-20261012`, commit
[e77a0f5a](https://github.com/CAFxX/fanout/commit/e77a0f5aaa6be78fd0fc9c4db91a9be14cfb6a8e)
to CAFxX/fanout@main (PAT targeted push, 10 files). 8 shards, est ~240
GHA-min, priority new-leads, image
`ghcr.io/cafxx/fanout-mix-sbox-search:latest` (reused — python+numpy+scipy;
no new image build). Tenant `projects/mix-hetstage2-search/`: driver +
verbatim eval port (`hetstage2_eval.py`, copied from the VM pilot, never
reimplemented) + vendored `lin_diff.py`/`screen_lib.py` + 300-draw pool
(150 dense-GF H1/H3 pc 8..40 seed 0xB804 + 150 R5) + canary (9 pilot keeps
bit-exact + try53 inner-FLAG). **Local canary GREEN** (all 9 keeps reproduce
to z±0.01; kill replay FLAGs) before submit. Results are leads; the
4-gate→S0→battery→Q1 chain stays local.

## 0. Why this axis (the O131 residual)

O131 closed the cheap-hetero line: 2 MUXD + hetero → z~10^3–10^6 (select-stagnation
passthrough); 3 MUXD + dense GF pre-diffusion → z~5–9, but the inner DIFF-SEQ gate
(the batch-62 instrument that killed t6_b61_56) FLAGged both best draws (try 53
dense/H1: lin=FLAG diff=FLAG; try 78 sparse/H3: lin=PASS diff=FLAG, rej on 9–10/10
keys) — a systematic residual truncated differential. The z~5 residual is
*localizable*: a pre-diffusion quality question, not a frame-capacity question.
The batch-62 lesson: the inner gate is the instrument that sees it — so this lane
runs the inner gate **first**, as the primary triage, on a **dense** GF pool that
extends the measured pc 3→5→7 dose-response into 8→40. The question is binary:
does any dense C erase the residual (inner PASS)? Nothing in the muxD5f frame
family except t6_b59_47 itself has ever inner-PASSed — a PASS would be a genuine
quality signal, cost to be arbitrated by S0 afterwards.

The O131 §4(ii) deeper guidance (hetero stage with HIGHER confusion-per-u than
MUXD, co-designed structured taps, not a cheaper one) is the standing direction;
this lane tests the (i) axis, which is the pre-registered experiment the dense
dose-response gradient points at.

## 1. Frame and draw types

**Frame:** MU5 verbatim — pre-whiten `x ^= k`; stages; final `x ^= rotl(k,13)`.

**Type D — dense GF-mul-by-constant** (primary axis):
- `GFMUL(C)`: x ↦ x ⊗ C in GF(2^64), P(z) = z^64+z^4+z^3+z+1 (irreducible).
  Any C ≠ 0 bijects. Draw: pc(C) stratified across **{8,10,12,16,20,24,32,40}**
  (one per value per H1/H3; H2 position-control draws from {12,16,24,32}),
  deg(C) ≥ 8, fail-loud. Matrix weight recorded per draw (wt ≈ 117×pc measured
  on pc=3 (336) and pc=7 (850)).
- Sparse controls: 4 draws pc ∈ {3,5,7,5} — the O131 gradient anchors; an inner
  FLAG here with the reordered gate order must reproduce the O131 signature
  (diagnostic, not a surprise).

**Type R5 — [CIRC2, MUXD×4]** (second sub-axis, size-axis challenger):
- New template T5: `[CIRC2(a,b), MUXD×4]` — CIRC2 + four MUXD (MUXD/_draw_muxd
  verbatim from het8). Cost anchor ≈ 4.00u + 4×4.00u = **~20.0u, ~900 cells**
  (circ2 128 + 4×192 = 896). This is the xorh5 recipe (XOR4 + 4×MUXD = 21.8u)
  with the cheapest measured hetero stage substituted: if inner-clean, it
  Pareto-challenges [t6_xorh5_15](../../fast_battery/candidates/t6_xorh5_15/)
(21.8u/5833/17170)
  on delay AND cells AND area. 12 draws. NOT a blind swap: CIRC2 was the only
  type-A survivor (best z=1121 vs CIRC1's 13k), and the 4-MUXD cascade is the
  DIFF-clean frame recipe — this is the co-designed combination of the two
  strongest hetstage fragments.

**Templates:** H1 `[H, MUXD, MUXD]`, H2 `[MUXD, H, MUXD]`, H3 `[H, MUXD×3]`
(hetstage verbatim), T5 `[CIRC2, MUXD×4]`.

**Draw budget (≤40, mandate):** D-H1 8 + D-H3 8 + D-H2 4 + sparse-ctrl 4 + R5 12
= **36 draws**.

## 2. Gates (reordered — the batch-62 lesson)

1. **Primary: inner-DIFF-SEQ** (`screen_lin_diff`, batch-62/hetstage verbatim
   instrument: N=2^18 sequential outputs, keys 0xffffffffffffffff +
   0xaaaaaaaaaaaaaaaa, LIN+DIFF Holm α=0.01). Runs **FIRST** on every draw;
   a draw inner-kills iff `diff_verdict != PASS` (lin recorded for diagnosis).
2. **Secondary: fisher triage** (het8 verbatim: KEYS10, N=2^18, diff_cell_logps,
   holm_reject α=0.01). Runs only on inner-PASS draws (compute order; the keep
   bar is the conjunction, so this loses nothing).
3. **Keep bar (pre-registered):** inner lin==PASS ∧ diff==PASS ∧ fisher
   n_reject==0. Both verdicts recorded in keeps JSONL.

**Cost bar:** S0 strict **<18.6u** (frontier speed point
[t6_b59_47](../../fast_battery/candidates/t6_b59_47/)) or Pareto-relevant on
cells/area vs [t6_b33b](../../fast_battery/candidates/t6_b33b/) (20.1u/5992/19280);
**>30u is COST-CLOSED** for this frame, no escalate.

## 3. Cost thesis (pre-registered, falsifiable at S0)

Measured anchors (O131 §3, pinned yosys 0.69 + abc mini.genlib, dual-analyzer):
circ2 **4.00u**, muxd **4.00u**, gfm3 (wt 336) **6.90u**, gfm7 (wt 850) **9.10u**.
Interpolation: cost(GF pc) ≈ 6.90 + (wt−336)×0.00428, wt ≈ 117×pc:

| pc | est. GF cost | H1 ≈ GF+8u | H3 ≈ GF+12u | status |
|---|---|---|---|---|
| 8 | ~9.5u | ~17.5u | ~21.5u | H1 eligible (thin) |
| 10 | ~10.5u | ~18.5u | ~22.5u | H1 marginal |
| 12 | ~11.5u | ~19.5u | ~23.5u | over bar → size-axis |
| 16 | ~13.5u | ~21.5u | ~25.5u | mechanism probe |
| 24 | ~17.5u | ~25.5u | ~29.5u | mechanism probe |
| 32 | ~21.5u | ~29.5u | ~33.5u | mechanism probe |
| 40 | ~25.5u | ~33.5u | ~37.5u | COST-CLOSED (>30u) |

Honest pre-registration: **pc≥12 is expected COST-CLOSED on speed** — the lane's
value is the quality question (does dense C inner-PASS?) plus the size-axis
comparison for pc≤12 H1 keeps. R5 ≈ 20.0u: speed-closed by construction,
**size-axis challenger by design** (vs 5833/17170 cells/area of xorh5_15).
Keeps route: 4-gate bar (fisher + inner + RD-SEQ + Low1/64 PractRand-256M
prescreen, batch-62 verbatim) → bundle (bit-exact 2000/200 Python-vs-C +
200/200 iverilog) → S0 ([run_synth.py](../../run_synth.py) authorized path) → XCHECK → staged
battery S1–S4 → Q1 (sac_z5=0).

## 4. Calibration (fail-loud, pre-pilot)

- **CALIB-1:** b33c and1 → maxworst|z| = 3.3 exact (tol 0.05). Reuse.
- **CALIB-2a:** MU5-324 → fisher n_reject == 0 (KEEP). Reuse.
- **CALIB-2b:** linear-4 → fisher n_reject > 0 (REJECT). Non-vacuity.
- **CALIB-3 (draw-gate soundness):** 200 dense-C draws → all pc in the allowed
  stratified set, deg(C) ≥ 8; 50 CIRC2 draws → rank 64 ∧ minw2 ≥ 4.
- **CALIB-4 (cost anchor):** [stage_cost.py](../hetstage/stage_cost.py) (hetstage's,
  verbatim) — MUXD
  ≈ 3.86–4.00u proves the pinned flow is on-scale; report CIRC2 + GF(pc=12)
  as new anchors.
- **CALIB-5a (NEW, positive):** t6_b59_47
  ([BASE_47](../../new_constructions/batch62/t6_b62_screen.py)) →
  inner lin==PASS ∧ diff==PASS (batch-62 CALIB-3a).
- **CALIB-5b (NEW, negative — RNG replay):** replay hetstage seed 0xB802 pilot
  RNG verbatim → try 53 (dense C, H1) and try 78 (sparse pc=5, H3) stages →
  inner diff_verdict != PASS on both (reproduces the O131 FLAG; proves the new
  primary gate sees what killed hetstage).
- **CALIB-5c (gate order):** the harness evaluates inner FIRST on every draw;
  fisher only on inner-PASS draws (log asserts the order).

Selftest (pre-calib): CIRC2 bit-exact vs scalar; GFMUL matrix == independent
carryless bit-loop reference on 30 random C (the transpose-class bug that the
hetstage selftest caught+fixed — re-verified here, not assumed); distributivity;
gf(x,1)==x; draw-gate soundness 800/800; inner smoke shape.

## 5. Kill rules (pre-registered)

- **K1:** Type D: 0/20+ inner-PASS draws across H1–H3 → **type D KILLED at the
  new primary gate** (O-entry; mechanism: the residual is irreducible by
  GF pre-diffusion at any density — strengthens O131's "diffusion but zero
  confusion" claim). Type R5: 0/12 inner-PASS → R5 killed (xorh5-recipe
  substitution thesis dead).
- **K2:** ≥1 keep → 4-gate bar → bundle → S0. S0 ≥ 18.6u → COST-CLOSED (speed);
  size-axis fallback ONLY if cells ≪ 5,833 (xorh5_15 cells point) AND delay
  ≤ 21.8u AND area < 17,170; else full kill.
- **K3:** inner flags all keeps' companions too (i.e. zero inner-PASS across
  both types) → terminal verdict, mechanism recorded.

## 6. Escalation on support (conditional, built only if pilot keeps ≥1)

GHA full-pool campaign (per [POOL_DESIGN.md](../POOL_DESIGN.md) §8 submit
pattern, PAT push path): pool = 300 drawn GF stages (pc stratified 3..40,
draw-gates fail-loud), new tenant `projects/mix-hetstage2-search/` (proposed)
reusing
[`flow/`](https://github.com/CAFxX/fanout/tree/main/projects/mix-sbox-search/flow)
from mix-sbox-search: validate draw-gates → unit-delay stage cost
(pinned flow) → frame inner-DIFF-SEQ primary triage H1/H3 in numpy →
aggregate inner-PASS → cost-eligible (≤18.6u frame estimate) fisher triage →
keeps. GHA results are leads; PARETO/RETAINED/RTL adjudication stays with the
30m report runs.

## 7. Principled cuts (per-cut justification)

1. **No sparse-only pool:** O131 tested pc 3/5/7 (0/36 inner-PASS); re-running
   the sparse gradient is not widening — only 4 sparse controls as anchors.
2. **No ANDOR in this pool:** O131 type C KILLED at triage (0/40, best z=26k,
   dominated 4 orders of magnitude below GFMUL's 5.1) — re-drawing it is not
   a new axis. The ANDOR-with-co-designed-taps form stays in the ledger as the
   O131 §4(ii) follow-up (confusion-per-u direction), a DIFFERENT lane.
3. **No CIRC1:** expected-kill control in O131 (0/20, rank-63 linear) —
   mechanism confirmed; re-running it tests nothing new.
4. **Single hetero form per frame in the pilot:** no GF+CIRC2 compounds —
   the pilot tests the base forms; compounds are pre-registered follow-ups
   conditional on support (either type keeps).
5. **pc capped at 40:** pc=40 H1 is already ~33.5u > 30u COST-CLOSED line;
   denser C is a mechanism probe with no possible escalation — a principled
   upper cut, not a sample.

## 8. Terminal axes (if K1/K3 fires — draft)

1. **Confusion-per-u co-design** (O131 §4(ii) guidance): ANDOR with co-designed
   structured taps, or ANDOR+CIRC2 compound stages — the hetero stage must
   contribute confusion, not just cheaper diffusion.
2. **R5-kill signature:** if [CIRC2, MUXD×4] inner-dies, the xorh5 recipe's
   XOR4 is load-bearing (not substitutable by a cheaper hetero) — record as
   a scoped verdict.
3. **Dense-C inner-PASS without cost viability:** if a dense C inner-PASSes
   but S0 > 30u, the quality axis is proven viable and the cost axis becomes
   the new problem (cheaper dense-GF circuits? composite structure?) —
   recorded as an open lead with the PASS evidence.
