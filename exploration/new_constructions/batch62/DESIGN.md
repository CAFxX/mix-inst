# Batch-62 design note — "weakness-gated local": m=1..3 perturbation around the proven-clean basin center, triaged by the failing instruments themselves (track 6, 2026-10-12)

**Status: CO-DESIGNED. Pre-pilot next. Written BEFORE any batch-62 run (2026-10-12 06:15Z).**

## Trigger

Batch-61 COST-TERMINAL 2026-10-12 (O126): the m=1..3 neighborhoods of
t6_b59_47 (18.6u frontier) + t6_b60_27 (18.7u) were exhausted **under
the fisher bar** — 57/57 S0, 3 sub-18.6u keeps (18.3u t6_b61_56,
18.5u t6_b61_24, 18.5u t6_b61_38), ALL killed in the battery on
properties the fisher bar cannot see:
- t6_b61_56: S1-KILLED by the inner calibrated DIFF-SEQ gate
  (CAL_FLAG: rej on keys 0xffffffffffffffff + 0xaaaaaaaaaaaaaaaa,
  worst|z|=4.92 @0xaa) — raw: `fast_battery/results/t6_b61_56/s1_result.json`
- t6_b61_24: S1-KILLED (RD rej=1, ('SEQ','0xffffffffffffffff')) — raw:
  `fast_battery/results/t6_b61_24/s1_result.json`
- t6_b61_38: S1 CAL_PASS, S2 PASS, **S3-KILLED @1GB
  [Low1/64]Gap-16:A R=+21.4 p=1.0e-17** (mild suspicion R=+6.9
  p=3.7e-5 already at 256MB) — raw:
  `fast_battery/results/t6_b61_38/s3_practrand_1GB.log`
  (the 4th Low1/64 PractRand kill in the muxD5f family after t6_b57_0
  O103, t6_b57_6 O111)

Pre-registered re-test trigger (O126): "a narrower co-designed axis
targeting the differential weakness (e.g. screening the perturbation
operator itself against DIFF-SEQ before S0), or a synthesis-path
change." This batch IS that trigger.

## Failure-signature characterization (adjudicated from raw artifacts)

**Which deltas / which structure.** The S3 generator feeds
`mix(i, key)` for sequential i with a fixed key
(`fast_battery/src/s3_gen.c`). The key enters only via XOR
(pre-whiten `x ^= k`, final `x ^= rotl(k,13)`) — affine, so
differentials are key-invariant *except for which input subset the
SEQ range maps to*: k=0 tests inputs [0,2^18); k=0xffffffffffffffff
tests the top region; k=0xaaaaaaaaaaaaaaaa the alternating region.
The DIFF-SEQ kills on structured keys are therefore
**region-dependent truncated-differential structure**: in some input
regions, weight-1 input differentials show detectable low-8-bit output
bias. Mechanism: for the mux gate `g = (s&a)|(~s&b)`, when the select
`s` is stagnant across a differential pair, `g`'s differential is the
differential of `a` (or `b`) alone — a linear passthrough, so the stage
contributes no confusion for that pair. The Low1/64 Gap-16:A failure
(output bit 0 across sequential inputs has non-geometric gap
structure) is the same region-dependent weak confusion visible in the
single-bit stream.

**Why batch-61's triage was blind to it.** b61's screener
(`new_constructions/batch61/t6_b61_screen.py`) used the OUTER
`lin_diff.diff_cell_logps`: 2^16 pairs per delta drawn from the low
input region [0,2^17). The t6_b61_56 kill came from the INNER
`screen_lindiff.screen_lindiff` (2^17 pairs, full [0,2^18) range):
strictly more powerful, and it Holm-rejected 56's structured-key
cells where the outer gate's Fisher logp (-6.43) fell short of the
Holm bar (log(0.001) = -6.91). The triage instrument was weaker than
the battery gate on exactly the failing property. Batch-62 closes
that gap by triaging with the failing instruments themselves.

## The co-designed axis

**Form:** pure-MUXD 5-stage, MU5 frame bit-identical
(`x ^= k` pre-whiten, final `x ^= rotl(k,13)`). The only form that has
ever beaten the frontier; b61's kills were quality kills, not form
kills.

**Base (single, narrower than b61):** t6_b59_47 ONLY — the single
proven S1→S4+Q1-clean basin center (18.6u frontier). t6_b60_27 is
excluded: its m=1..3 neighborhood is exhausted AND its quality beyond
triage is unproven (b60 never batteried it).

**Draw operator (b59/b61 verbatim — the failure was the bar, not the
operator):** m ~ Uniform{1,2,3} distinct rotation positions (of 20)
resampled Uniform{0..63}; per-stage s/a/b pairwise-distinctness
re-checked on resample (b51 cut #10); d free. b61 proved this
operator finds sub-18.6u schedules (18.3/18.5/18.5u).

**KEEP bar — the co-design (all four gates must pass, in cost order):**
1. **Fisher triage** (proven instrument): n_reject == 0 under
   Holm-Bonferroni (ALPHA=0.01) on per-key DIFF fisher_logp
   (outer `lin_diff.diff_cell_logps` + `holm_reject` verbatim).
2. **Inner DIFF-SEQ + LIN gate** (`screen_lindiff.screen_lindiff`,
   the exact gate that killed t6_b61_56): zero Holm rejections
   across the 10 calibrated keys on SEQ outputs. (~23s/keep)
3. **RD-SEQ reduction gate** (the cell class that killed t6_b61_24):
   9 reduction tests (`screen_cal._reduction_logps`) on SEQ outputs
   × 10 keys, Fisher-combined per key, Holm-rejected across keys;
   zero rejections.
4. **Low1/64 PractRand prescreen at 256MB** (battery key
   0x123456789abcdef0, `s3_practrand.sh` pattern: 4GB stream piped to
   `RNG_test stdin64 -tlmax 268435456`, fail-loud `length=` guard):
   REJECT on any `[Low1/64]` line with FAIL or "suspicious"
   (p < 1e-3). t6_b61_38 showed mild suspicion (p=3.7e-5) at 256MB →
   would have been rejected here. (~65s/keep)

Only keeps passing all four are bundled (bit-exact 2000/2000 C-vs-Python
+ 500/500 screener-vs-bundle) → S0 (`run_synth.py`, strict <18.6u, ref
mul64 103.5u, XCHECK) → cost-eligible keeps escalate in z-order →
staged battery S1→S2→S3→S4 → Q1 (sac_z5=0 mandatory). A Q1-clearing
keep at <18.6u → FRONTIER CHALLENGER (O127+, PARETO/RETAINED/RTL
update per chain rules).

**Why this is a NEW axis, not a re-run of the exhausted one:** O126's
kill is explicitly scoped "as a search axis **under the fisher
bar**". The (operator, bar) pair here is new: a narrower single
proven-clean base × a bar that IS the property failed on (the failing
instruments themselves). The old verdict cannot transfer because the
bar tests a different property — this is the pre-registered re-test
trigger, not a repeat. A blind rotation re-draw with the same fisher
bar would be marked KILLED-INVALID per standing order; this is its
opposite.

## Cuts (each with its defensible reason)

1. **Form pure-MUXD 5-stage MU5:** only form beating the frontier;
   kills were quality, not form. (O117/O118)
2. **Single base t6_b59_47:** only proven-clean basin center;
   narrower per the re-test trigger; t6_b60_27's neighborhood
   exhausted + quality unproven.
3. **m=1..3 operator unchanged:** proven to find sub-18.6u schedules;
   the failure was the bar.
4. **S0 bar strict <18.6u:** only sub-frontier schedules can
   challenge it.
5. **No battery without S0 eligibility:** S0 is the cheap gate
   relative to the full battery.
6. **No structural (non-screen) perturbation bias:** without a proven
   structural criterion, biasing the draw operator toward e.g.
   select-tap positions would be a blind swap. The screen IS the
   co-design. (Diagnostic: per-keep select-activity metrics are
   recorded to build evidence for a future structural axis —
   leads-ledger entry.)

## Pre-registered rules

- **Pre-pilot** (12 draws, seed 0xB621): HARNESS CHECK ONLY.
  Calibration must PASS all gates (fail-loud):
  CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2a MU5-324 n_reject=0;
  CALIB-2b linear-4 n_reject>0;
  CALIB-3a t6_b59_47 inner screen_lindiff CAL_PASS (positive control);
  CALIB-3b t6_b61_56 inner screen_lindiff CAL_FLAG with rej on
  0xffffffffffffffff + 0xaaaaaaaaaaaaaaaa (negative control — the
  exact kill reproduced);
  CALIB-3c t6_b61_24 inner screen_lindiff CAL_PASS (passed DIFF;
  its kill was RD — the gate must not over-reject);
  CALIB-3d t6_b61_24 RD-SEQ REJECT (negative control for gate 3);
  CALIB-4a t6_b61_38 Low1/64 prescreen REJECT at 256MB (negative
  control — mild suspicion p=3.7e-5 must trip the p<1e-3 rule);
  CALIB-4b t6_b59_47 Low1/64 prescreen PASS (positive control);
  CALIB-4c t6_b57_0 Low1/64 prescreen REJECT (failed at 16MB).
  Draws must complete. selftest must verify the perturbation operator
  (200 draws: 1–3 positions differ from t6_b59_47, stages valid,
  s/a/b distinct, never base-identical).
- **Pre-pilot 0/12 → PILOT runs regardless** (12 draws cannot
  adjudicate the basin).
- **GATE-FAIL (vacuous): keeps==n_try and kills==0 → KILL LOUDLY,**
  diagnose.
- **Pilot** (80 draws, seed 0xB622): ≥1 four-gate KEEP → bit-exact
  bundle (gen script adapted from b61 — keeps carry form="muxD5f",
  5 stages) → S0 (run_synth.py ONLY; strict <18.6u) → cost-eligible
  keeps escalate in z-order → staged battery S1→S2→S3→S4 → Q1
  (sac_z5=0 mandatory). A Q1-clearing keep at <18.6u → FRONTIER
  CHALLENGER (O127+, PARETO/RETAINED/RTL update).
- **Pilot 0/80 → AXIS-KILL** (the weakness-gated basin is empty under
  this bar; O-entry scoped to the tested base+bar) → escalate to the
  next co-designed axis (synthesis-path change per O126, or a
  select-activity structural axis from the diagnostics).
- **Backoff-gated** (cleared-flag single-gate pattern; fail-loud only
  if cleared==0), **nice -n 19** via agentwork-launch.sh + setsid,
  draw-loop fail-loud cap 10000, **never two workers on one
  candidate**.

## Bookkeeping

- Heartbeat: `new_constructions/batch62/heartbeat.txt` every ~20 min.
- CHECKPOINT.md: sibling; resume instructions inside.
- Ledger: prepend entry at lane start and on each terminal verdict;
  VERDICT_SCOPE.md O-entry (O127+) scoped to tested configs.
- Workreg: track6-batch62 (active); track6-batch61 stays done.
