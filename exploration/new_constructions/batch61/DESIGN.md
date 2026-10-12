# Batch-61 design note — "local2": m=1..3 perturbation around the two best points (track 6, 2026-10-12)

**Status: CO-DESIGNED. Pre-pilot next.**

## Trigger

Batch-60 TERMINAL 2026-10-12 (O120): the wider-radius (m~U{2,3,4})
basin-depth axis found NO sub-18.6u schedule (best 18.7u t6_b60_27,
49/49 S0, zero under the strict bar). Remaining unexplored territory:
(a) the m=1 ring around the t6_b59_47 frontier point (b60 covered
m=2..4 around it), and (b) the d≤3 neighborhood of t6_b60_27 — the
b60 keep set contains only t6_b60_27 itself within d≤4 (45/49 within
d≤8), so its immediate neighborhood is unexplored, not proven narrow.

## Cuts (each with its defensible reason)

1. **Form: pure-MUXD 5-stage, MU5 frame bit-identical** (pre-whiten
   `x ^= k`, final `x ^= rotl(k,13)`). Reason: the only form that has
   ever beaten the frontier (19.2 → 19.1 → 18.6u, O117/O118); every
   other form is closed (hetero-AND S1-DIFF wall, ANDN triage-dead,
   OAAND cost, muxD4f 0/80, xorh5 cost O119).
2. **KEEP bar: n_reject == 0 under Holm-Bonferroni (ALPHA=0.01) on
   per-key fisher_logp — `holm_reject` verbatim.** Reason: the proven
   instrument (O96); worst-z is blind to what the S1 gate kills on.
3. **Two bases: t6_b59_47 (18.6u frontier, full-battery clean) +
   t6_b60_27 (18.7u, best b60 keep).** Reason: the two best known
   points; both proven quality-clean at the fisher bar. Schedules
   verbatim from `fast_battery/candidates/t6_b59_47/model.py` and
   `new_constructions/batch60/bundle_t6_b60_27.log`.
4. **Draw operator: base ~ Uniform{47, 60_27}; m ~ Uniform{1,2,3}
   distinct rotation positions (of 20) resampled Uniform{0..63}.**
   Reason: the batch-59 playbook verbatim — b59's m=1..3 found
   18.5–19.1u; b60's m=2..4 found nothing under 18.6u. Covers the
   unexplored m=1 ring around t6_b59_47 and the unexplored d≤3
   neighborhood of t6_b60_27. NOT widened preemptively: the b60 data
   shows t6_b60_27's neighborhood unexplored, not narrow; the pilot
   adjudicates.
5. **Per-stage s/a/b pairwise-distinctness re-checked on resample.**
   Reason: b51 cut #10, carried over — degenerate stages are a
   known confound.
6. **d free.** Reason: b59/b60 used d free; constraining it would be
   an unjustified cut.
7. **S0 bar: strict <18.6u (the frontier).** Reason: only a schedule
   cheaper than the frontier can challenge it; anything at/above is
   dominated by construction.
8. **No battery without S0 eligibility.** Reason: S0 is the cheap
   gate; the battery is expensive. Same rule that correctly skipped
   batteries for all of b60.

## Pre-registered rules

- **Pre-pilot** (12 draws, seed 0xB611): HARNESS CHECK ONLY.
  Calibration must PASS all three gates (fail-loud):
  CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2a MU5-324 n_reject=0;
  CALIB-2b linear-4 n_reject>0. Draws must complete. selftest must
  verify the perturbation operator (200 draws: 1–3 positions differ
  from chosen base, stages valid, s/a/b distinct, never base-identical,
  both bases drawn).
- **Pre-pilot 0/12 → PILOT runs regardless** (12 draws cannot
  adjudicate the basin).
- **GATE-FAIL (vacuous): keeps==n_try and kills==0 → KILL LOUDLY,**
  diagnose.
- **Pilot** (80 draws, seed 0xB612): ≥1 fisher-KEEP → bit-exact
  bundle (gen script adapted from b57/b59 — keeps carry form="muxD5f",
  5 stages) → S0 (run_synth.py ONLY; strict <18.6u) → cost-eligible
  keeps escalate in z-order → staged battery S1→S2→S3→S4 → Q1
  (sac_z5=0 mandatory). A Q1-clearing keep at <18.6u → FRONTIER
  CHALLENGER (O121+, PARETO/RETAINED/RTL update).
- **Pilot 0/80 → AXIS-KILL** (the m=1..3 neighborhoods of both best
  points are exhausted under the fisher bar; O-entry scoped to the
  tested radii) → escalate to the next co-designed axis.

## Bookkeeping

- Heartbeat: `new_constructions/batch61/heartbeat.txt` every ~20 min.
- CHECKPOINT.md: sibling; resume instructions inside.
- Ledger: prepend entry on each terminal verdict; VERDICT_SCOPE.md
  O-entry (O121+) scoped to tested configs.
