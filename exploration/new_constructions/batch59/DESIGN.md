# Batch-59 design note — "muxD5f-local": perturbation search around the t6_b57_8 winner schedule (track 6, 2026-10-12)

**Status: CO-DESIGNED (incarnation XXXIV, 2026-10-12 ~04:15 CEST). Pre-pilot next.**

## Trigger

Batch-58 FAMILY-KILL 2026-10-12 (O116): 0/92 fisher-keeps at 4 stages
(pre-pilot 0/12 minz=3045.9; pilot 0/80 minz=1053.2). 5 stages are
necessary for random-draw search under the fisher bar. The b58
pre-registered escalation fires: the deferred muxD5f-local axis.

## The honest axis argument

b57 (global 5-stage draws, 80 draws, 13 keeps) yielded exactly one
frontier point: t6_b57_8 at 19.2u, proven S1→S4 + Q1 clean
(sac_z5=0). Of the other cost-eligible keeps, 3/4 died at S1/S3 —
quality is schedule-dependent and the winner's basin is the only
proven-clean region of the space. The local axis exploits it: draw
schedules as small perturbations of the winner and re-screen with
the gate-matched instrument.

- **Form:** 5 stages of full MUXD, MU5 frame bit-identical
  (pre-whiten `x ^= k`, final `x ^= rotl(k,13)`). The ONLY delta from
  b57 is the draw operator (local perturbations instead of global
  draws).
- **Draw operator (fail-loud):** base = t6_b57_8 schedule
  `[("MUXD",17,22,10,55),("MUXD",63,62,49,41),("MUXD",29,39,35,6),
  ("MUXD",9,4,44,36),("MUXD",5,54,31,34)]` (from
  `fast_battery/candidates/t6_b57_8/model.py`). Per try: m ~
  Uniform{1,2,3} distinct rotation positions (of 20) resampled
  Uniform{0..63}; per-stage s/a/b pairwise-distinctness re-checked
  on resample (b51 cut #10); d free. m≥1 by construction, so exact
  winner rediscovery is impossible (no flag needed).
- **KEEP bar:** n_reject == 0 under Holm-Bonferroni on per-key
  fisher_logp (ALPHA=0.01) — `holm_reject` verbatim, the S1 gate's
  own rule.
- **Cost thesis:** identical gate count to t6_b57_8; S0 noise range
  18.9–20.7u measured across b57 keeps. Bar STRICTLY <19.2u; S0
  adjudicates per keep (run_synth.py, ref mul64 103.5u, pinned yosys
  0.69, XCHECK clean).
- **Quality thesis:** the winner is proven S1→S4+Q1 clean;
  1–3-position perturbations likely stay in the clean basin — vs
  global draws where 3/4 cost-eligible keeps died at S1/S3 (O111
  Low1/64 mechanism). Exploitation after b57's exploration.
- **Mechanism question (crisp):** does the Q1-clean winner's
  schedule basin contain cheaper schedules the global search missed?

## Cuts (defensible reason at each cut site)

1. **Global re-draws: CUT** (b57 exhausted the experiment; b58 (a)).
2. **Wider radius (m>3): DEFERRED** — start 1–3 (basin size unknown;
   small radius first is the honest exploitation step). Trigger: if
   the pilot is 0/80, widen the radius or close the local axis.
3. **4-stage: CUT** (O116 family-kill).
4. **mux3f (dropped d-tap): DEFERRED** — trigger: local-axis kill.
5. **Hetero forms: CUT** (postmortem_hetcascade; no reshuffle).
6. **h0-neighborhood / Q1-tail: DEFERRED** (b57 (a); trigger unmet).
7. **Blind/worst-z triage: CUT** (O96; gate-matched bar proven).

## Pre-registered rules

- **Pre-pilot** (12 draws, seed 0xB591): HARNESS CHECK ONLY.
  Calibration must PASS all three gates (fail-loud):
  CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2a MU5-324 n_reject=0;
  CALIB-2b linear-4 n_reject>0. Draws must complete. selftest must
  verify the perturbation operator (200 draws: 1–3 positions differ
  from winner, stages valid, s/a/b distinct, never winner-identical).
- **Pre-pilot 0/12 → PILOT runs regardless** (12 draws cannot
  adjudicate the basin).
- **GATE-FAIL (vacuous): keeps==n_try and kills==0 → KILL LOUDLY,**
  diagnose.
- **Pilot** (80 draws, seed 0xB592): ≥1 fisher-KEEP → bit-exact
  bundle (`gen_b57_bundle.py` verbatim — keeps carry form="muxD5f",
  5 stages; output recorded to disk) → S0 (run_synth.py ONLY; strict
  <19.2u) → cost-eligible keeps escalate in z-order → staged battery
  S1→S2→S3→S4 → Q1 (sac_z5=0 mandatory). A Q1-clearing keep at
  <19.2u → FRONTIER CHALLENGER.
- **Pilot 0/80 → AXIS-KILL** (the winner's 1–3 basin is exhausted
  under the fisher bar; VERDICT_SCOPE O-entry scoped to the tested
  perturbation radius) → escalate to deferred mux3f or close the
  mux line per evidence.

## Bookkeeping

- Heartbeat: `new_constructions/batch59/heartbeat.txt` every ~20 min.
- CHECKPOINT.md: sibling; resume instructions inside.
- Ledger: prepend entry on each terminal verdict; VERDICT_SCOPE.md
  O-entry (O117+) scoped to tested configs.
