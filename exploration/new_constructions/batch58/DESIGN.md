# Batch-58 design note — "muxD4f": 4-stage pure-MUXD cascade with fisher-matched triage (track 6, 2026-10-12)

**Status: CO-DESIGNED (incarnation XXXIV, 2026-10-12 ~04:10 CEST). Pre-pilot next.**

## Trigger

Batch-57 CLOSED 2026-10-12 (O115): the fisher-matched triage on global
pure-MUXD 5-stage draws (80 draws, 13/80 keeps) yielded exactly one
frontier point — t6_b57_8 at 19.2u (S1→S4 + Q1 clean, sac_z5=0). 13/13
ranks terminal: 9 S0-doomed (19.3–20.7u), 3 quality-killed (rank 2 at S1;
ranks 0/6 at S3), 1 frontier. The global-5-stage-draw axis is exhausted
as an experiment (its EV is spent, not the 64^20 space).

Mechanism evidence constraining the next axis (O111): 2 of the 3
S1-S3-tested cost-eligible 5-stage keeps died at S3 in the Low1/64
PractRand family (rank 0: [Low1/64]Gap-16:A; rank 6: [Low1/64]FPF/16).
Pure-MUXD cascades show a repeatable S3 weakness in Low1/64; the
frontier schedule is the exception, not the rule. Any fewer-stage
variant is strictly weaker mixing — S3 is where its risk concentrates.
This is a flagged risk, not a kill: the triage + staged battery
adjudicate it empirically.

## The honest axis argument (options evaluated against evidence)

**(a) Re-run global muxD5f with a new seed — CUT.** b57 ran this exact
experiment. Repeating it is the dominated comparator: same instrument,
same space, diminishing returns (1 frontier / 80 draws). The axis's
question ("does the gate-matched instrument find better-than-324 MUXD
schedules?") is answered: yes, once (t6_b57_8).

**(b) muxD5f-local: perturb t6_b57_8's Q1-clearing schedule — DEFERRED,
principled ordering.** Valid axis (exploit the proven-clean basin), but
at equal quality risk a full stage drop dominates it on cost thesis
(~3.8u vs synthesis-noise hunting around 19.2u). Re-test trigger: if
muxD4f is quality-dead (4 stages insufficient), local exploitation of
the 5-stage winner becomes the next axis.

**(c) mux3f: drop the d-tap (5 stages of x ^= mux(...)) — CUT for b58.**
Weaker cost thesis than dropping a whole stage (the no-rc precedent:
dropping an XOR saves ~0.3u total — Yosys absorbs XORs — vs ~3.86u for
a stage). Deferred trigger: muxD4f quality-dead AND 5-stage local
stalled.

**(d) h0-neighborhood / Q1-tail lottery — DEFERRED.** b57 cut (a)
reasons stand unchanged: ~1% S1-clear yield for AND3-hetero (each Q1
candidate costs ~100 S1 screens); cost headroom vs the new frontier is
now 0.1u (h0 19.1u vs 19.2u — worse than before); every known
avalanche-tail cure costs +0.9–1.9u. Re-test trigger unchanged: a
principled SAC-tail mechanism for AND-in-cascade, not a schedule
lottery.

**(e) Hetero stage forms (AND3/ANDN/OAAND) — CUT.** Postmortem:
three independent kills (S1-differential, triage-absence, cost-floor).
The hetero family is exhausted. Do NOT reshuffle
(postmortem_hetcascade.md).

**(f) 6-stage MUXD — CUT.** Measured cost thesis 6 × 3.86u ≈ 23u ≥
19.2u: dominated on cost before quality is even asked.

**(g) Per-stage key folding — CUT.** al_chi6k evidence: S2 systematic
differential bias from the fold AND +5.6u cost.

**(h) chi / AND / maj / S-box homogeneous forms — CUT.** Measured cost
floors: chi ~5.4–5.77u/stage, andor ~4.9u/stage, maj ~4.9u/stage, Q4
7.0u/stage. None has a sub-19.2u cost thesis.

**(i) Blind / worst-z triage — CUT (stays replaced).** O96 measured:
blind to fisher-aggregated deviations. The gate-matched bar is the
proven instrument (O97: n_reject=0 reproduces the S1 per-bit DIFF gate
bit-for-bit).

**Selected axis: muxD4f — the fisher-matched instrument on 4-stage
pure-MUXD.** The instrument is proven; it has never been pointed at the
4-stage MUXD space (grep-verified: all holm_reject screens are 5-stage
or hetero). This is a genuinely new construction family (new stage
count of the frontier form), orthogonal to the closed hetero family.

## Axis: muxD4f

- **Form:** 4 stages of full MUXD
  `x ^= mux(rotl(x,s),rotl(x,a),rotl(x,b)) ^ rotl(x,d)`,
  pre-whiten `x ^= k`, final `x ^= rotl(k,13)` — bit-identical frame
  to hyb28_mu5_324 and t6_b57_8. The ONLY delta from the frontier is
  the stage count (5 → 4) plus the rotation schedule (drawn fresh).
- **Draw constraints (fail-loud):** MUX stages s,a,b pairwise
  distinct (b51 cut #10 degeneracy proof); d free; duplicate
  stage-tuples re-drawn within a try (b41); draw-loop cap 10000
  (b45 fail-loud pattern).
- **KEEP bar:** n_reject == 0 under Holm-Bonferroni on per-key
  fisher_logp (ALPHA=0.01) — `holm_reject` verbatim from b55/b57,
  the S1 per-bit DIFF gate's own rule.
- **Measured cost thesis:** MUXD stage 3.86u (324 measured); 4 stages
  ≈ 15.4u — strictly <19.2u with >3u margin even under the observed
  ±1u synthesis noise. Bar STRICTLY <19.2u; S0 adjudicates per keep
  (run_synth.py, ref mul64 103.5u, pinned yosys 0.69, XCHECK clean).
  This is measured-component reasoning (b56/b57 precedent), not
  projection.
- **Mechanism question (crisp):** is 5 the minimal MUXD stage count
  for full S+Q quality, or does 4 suffice? Either outcome is
  informative: a Q1-clearing 4-stage keep moves the frontier ~3.8u;
  0/80 keeps is a family-level verdict (4 MUXD stages insufficient
  for the fisher bar) that bounds the design space.
- **Flagged risk (not a cut):** the O111 S3-Low1/64 mechanism — 5
  stages are already marginal for some schedules; 4 stages are weaker
  mixing, so S3 is the risk concentration point. The staged battery
  adjudicates it; no pre-judgment.

## Cuts (defensible reason at each cut site)

1. **Global 5-stage re-draws: CUT** (see (a) — experiment exhausted).
2. **muxD5f-local perturbation: DEFERRED** (see (b) — principled
   ordering by cost-thesis strength).
3. **mux3f (dropped d-tap): CUT for b58** (see (c) — dominated cost
   thesis; deferred trigger recorded).
4. **h0-neighborhood / Q1-tail: DEFERRED** (see (d) — trigger unmet).
5. **Hetero forms: CUT** (see (e) — postmortem closed; no reshuffle).
6. **6-stage MUXD: CUT** (see (f) — cost-dominated).
7. **Per-stage key folding: CUT** (see (g) — al_chi6k evidence).
8. **chi/AND/maj/S-box homogeneous: CUT** (see (h) — cost floors).
9. **Blind/worst-z triage: CUT** (see (i) — instrument proven).

## Pre-registered rules

- **Pre-pilot** (12 draws, seed 0xB581): HARNESS CHECK ONLY.
  Calibration must PASS all three gates (fail-loud):
  CALIB-1 and1/b33c z=3.3 EXACT (harness sanity);
  CALIB-2a MU5-324 (5-stage) n_reject=0 (bar sanity vs known-good);
  CALIB-2b linear-4 (4× `x ^= rotl(x,s)`, same frame) n_reject>0
  (negative control — the gate fires on garbage).
  Draws must complete.
- **Pre-pilot 0/12 keeps → WEAK-SIGNAL flag, PILOT runs regardless.**
  (Unlike b57's vacuity reading: at 4 stages, 0/12 is plausible real
  signal that the bar is too strict for the stage count — the pilot
  confirms or refutes at 80 draws.)
- **GATE-FAIL (vacuous): keeps==n_try and kills==0 → KILL LOUDLY,**
  diagnose (the fisher bar would be vacuous, contradicting b55/b57).
- **Pilot** (80 draws, seed 0xB582): ≥1 fisher-KEEP → bit-exact
  bundle (`gen_b58_bundle.py`: C-vs-Python 2000/2000 +
  screener-vs-bundle 500/500, output recorded to disk) → S0
  (run_synth.py ONLY; strict <19.2u) → cost-eligible keeps escalate
  in z-order → staged battery S1→S2→S3→S4 (run_fast_battery.sh,
  stops at first kill) → Q1 (sac_z5=0 mandatory) on any S4 survivor.
  A Q1-clearing keep at <19.2u → FRONTIER CHALLENGER.
- **Pilot 0/80 → FAMILY-KILL verdict** (4 MUXD stages insufficient
  for the fisher bar; VERDICT_SCOPE O-entry scoped to the tested
  4-stage construction) → escalate to the deferred muxD5f-local
  axis. Form verdict only after the pilot adjudicates.
- **324-analog:** no exact-schedule rediscovery flag applies at 4
  stages (the 5-stage frontier schedule cannot be redrawn). Any keep
  matching a b57 keep's first 4 stages is logged `[SCHEDULE-OVERLAP]`
  for honesty but adjudicated normally.

## Bookkeeping

- Heartbeat: `new_constructions/batch58/heartbeat.txt` every ~20 min.
- CHECKPOINT.md: this file's sibling; resume instructions inside.
- Ledger: prepend entry on each terminal verdict; VERDICT_SCOPE.md
  O-entry (O116+) scoped to tested configs.
