# Batch-29 design note — "muxD5f-324local": m~U{1,2,3} perturbation around the hyb28_mu5_324 winner schedule (track 5, 2026-10-12)

**Status: CO-DESIGNED (incarnation I, 2026-10-12 ~07:45 CEST). Pre-pilot next.**

## Trigger

Track-5 supervisor ownerless 24.5h (heartbeat stale 2026-10-11 05:01:29Z);
the lane idled after the batch-28 cycle landed
[hyb28_mu5_324](../../fast_battery/candidates/hyb28_mu5_324/) on the
frontier (19.3u, S0–S4 + Q1 clean, holds Frontier S cells + area slots).
Track-6's t6_b59_47 basin is exhausted (batch-61 COST-TERMINAL, O126:
m=1..3 neighborhoods of t6_b59_47 + t6_b60_27 exhausted under the fisher
bar). The MU5-324 basin is the only proven-clean region of the MU5
rotation space on track 5 — and it is unexplored.

## The honest axis argument

- **Form:** 5-stage MUXD cascade, MU5 frame bit-identical
  (pre-whiten `x ^= k`, final `x ^= rotl(k,13)`). The ONLY delta from
  batch-28 is the draw operator (local perturbations of the winner
  instead of global draws).
- **Draw operator (fail-loud, batch-59 playbook verbatim, base swapped):**
  base = hyb28_mu5_324 schedule
  `[("MUXD",62,50,55,2),("MUXD",48,58,23,30),("MUXD",44,45,7,40),
  ("MUXD",49,26,32,35),("MUXD",46,51,43,44)]` (from
  `fast_battery/candidates/hyb28_mu5_324/meta.json`). Per try:
  m ~ Uniform{1,2,3} distinct rotation positions (of 20) resampled
  Uniform{0..63}; per-stage s/a/b pairwise-distinctness re-checked on
  resample (b51 cut #10); d free. m≥1 by construction, so exact winner
  rediscovery is impossible (no flag needed).
- **KEEP bar:** n_reject == 0 under Holm-Bonferroni on per-key
  fisher_logp (ALPHA=0.01) — `holm_reject` verbatim, the S1 gate's
  own rule (proven instrument, O96).
- **Cost thesis:** gate-identical to 324 (19.3u); S0 noise across b59
  keeps spanned ~1.8u. Bar STRICTLY <18.6u (current speed point
  [t6_b59_47](../../fast_battery/candidates/t6_b59_47/)) for speed
  eligibility, adjudicated per keep via the authorized
  [run_synth.py](../../run_synth.py) path (ref mul64 103.5u, pinned
  yosys 0.69, XCHECK clean mandatory). Size axis: keeps genuinely
  size-eligible vs t6_b33b (20.1u/5992/19280) escalate on the size
  axis — 324 holds the Frontier S cells + area slots, so a cheaper
  MU5 keep is a size challenger even at ≥18.6u.
- **Quality thesis:** 324 is proven S0–S4 + Q1 (sac_z5=0) clean; 1–3
  position perturbations likely stay in the clean basin — vs global
  draws where quality proved schedule-dependent (O111 Low1/64).
  Exploitation after b28's exploration.
- **Mechanism question (crisp):** does the 324 basin contain a
  schedule cheaper than 18.6u (or a cells/area challenger) that the
  b28 global search missed?

## Cuts (defensible reason at each cut site)

1. **Global re-draws: CUT** — b28 already ran the 40-draw MU5 arm
   (19/40 fisher-keeps); the experiment is done, this is the
   exploitation step.
2. **Wider radius (m>3): DEFERRED** — basin size unknown; small
   radius first is the honest exploitation step. Trigger: pilot 0/80.
3. **Small-delta (±1..3) move operator: DEFERRED** — changing the
   operator AND the base at once would confound; the resample
   operator is proven (b59: 58/80 keeps, 18.5–19.1u finds).
   Trigger: resample-pilot 0/80 or basin cost-verdict.
4. **4-stage: CUT** (O116 family-kill; 5 stages necessary).
5. **MU6 6-stage: CUT for cost** — wall control at ~21–23u, the
   <18.6u bar unreachable by construction.
6. **Hetero/ANDN/OAAND forms: CUT on this lane** — track 6 owns the
   het lines; track 5's MU5 frame is the proven carrier.
7. **Blind/worst-z triage: CUT** (O96; gate-matched bar proven).

## Pre-registered rules

- **Pre-pilot** (12 draws, seed 0xB291): HARNESS CHECK ONLY.
  Calibration must PASS all three gates (fail-loud):
  CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2a MU5-324 n_reject=0;
  CALIB-2b linear-4 n_reject>0. Draws must complete. selftest must
  verify the perturbation operator (200 draws: 1–3 positions differ
  from the 324 base, stages valid, s/a/b distinct, never
  base-identical).
- **Pre-pilot 0/12 → PILOT runs regardless** (12 draws cannot
  adjudicate the basin).
- **GATE-FAIL (vacuous): keeps==n_try and kills==0 → KILL LOUDLY,**
  diagnose.
- **Pilot** (80 draws, seed 0xB292): ≥1 fisher-KEEP → bit-exact
  bundle (gen_b29_bundle.py — keeps carry form="muxD5f",
  base="hyb28_mu5_324") → S0 sweep in z-order (run_synth.py ONLY;
  strict <18.6u speed bar; size-axis escalation vs t6_b33b) →
  XCHECK 10000/10000 mandatory → staged battery S1→S2→S3→S4→Q1
  (sac_z5=0 mandatory). Q1-clearing keep at <18.6u → FRONTIER
  CHALLENGER (PARETO.md + RETAINED.md + RTL mirror update).
  Full-pass-but-dominated → RETAINED.md, no frontier change.
- **Pilot 0/80 → AXIS-KILL** (the 324 m=1..3 basin is exhausted
  under the fisher bar; VERDICT_SCOPE O-entry scoped to the tested
  perturbation radius) → escalate to the deferred small-delta
  operator or close the local axis per evidence.

## Bookkeeping

- Heartbeat: `hybrid/supervisor_heartbeat.txt` every major step;
  workreg `mix-track5-batch29` (heartbeat on schedule).
- Ledger: prepend entry on each terminal verdict; LEADS_LEDGER.md
  never buries a lead.
- Scripts: [hyb_b29_screen.py](hyb_b29_screen.py) (calibrate /
  selftest / pre-pilot / pilot), [gen_b29_bundle.py](gen_b29_bundle.py).
