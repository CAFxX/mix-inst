# Batch-60 design note — "basin-depth": wider-radius perturbation search around the two new winners (track 6, 2026-10-12)

**Status: CO-DESIGNED (track-6 supervisor, 2026-10-12 ~03:45Z). Pre-pilot next.**

## Trigger

Batch-59 TERMINAL 2026-10-12 (O117/O118): the muxD5f-local axis
(m~Uniform{1,2,3} around t6_b57_8) produced TWO frontier points —
t6_b59_47 at 18.6u (speed point, m=2 from the winner) and t6_b59_0 at
19.1u (m=1). S0 cost spread across the basin is wide (18.5–20.3u);
the cheapest draw (18.5u, t6_b59_7) was a marginal S1 kill. The
basin contains sub-18.6u schedules; the question is whether it
contains a sub-18.6u QUALITY-CLEAN one.

## The honest axis argument

b59 established: (a) the winner's basin is broad (72.5% pilot keep
rate) and quality-clean (2/2 full battery passes on tested
challengers, 1 marginal S1 kill); (b) the two NEW winners are
proven-clean basin centers at different basin locations (47 is
d=2 from t6_b57_8, 0 is d=1); (c) S0 cost is noisy across the
basin (18.5–20.3u) — sampling more of it is the honest way to find
cheaper clean schedules.

- **Form:** 5 stages of full MUXD, MU5 frame bit-identical
  (pre-whiten `x ^= k`, final `x ^= rotl(k,13)`). The ONLY delta
  from b59 is the draw operator (wider radius, two bases).
- **Draw operator (fail-loud):** per try, base ~ Uniform{t6_b59_47,
  t6_b59_0}; m ~ Uniform{2,3,4} distinct rotation positions (of 20)
  resampled Uniform{0..63}; per-stage s/a/b pairwise-distinctness
  re-checked on resample (b51 cut #10); d free. m>=2 by
  construction, so exact base rediscovery is impossible.
- **Base schedules (verbatim from fast_battery/candidates/*/model.py):**
  - t6_b59_47: [("MUXD",17,22,10,55),("MUXD",63,62,49,57),
    ("MUXD",29,39,35,6),("MUXD",9,4,44,36),("MUXD",5,54,31,34)]
  - t6_b59_0:  [("MUXD",17,22,10,55),("MUXD",63,62,49,41),
    ("MUXD",29,39,35,6),("MUXD",9,4,49,36),("MUXD",5,54,31,34)]
- **KEEP bar:** n_reject == 0 under Holm-Bonferroni on per-key
  fisher_logp (ALPHA=0.01) — `holm_reject` verbatim, the S1 gate's
  own rule. Fisher-matched triage is the proven instrument (O96);
  worst-z triage stays CUT.
- **Cost thesis:** identical gate count; S0 noise 18.5–20.3u
  measured across b59 keeps. Bar STRICTLY <18.6u for speed
  contention; S0 adjudicates per keep (run_synth.py, ref mul64
  103.5u, pinned yosys 0.69, XCHECK clean).
- **Quality thesis:** both bases are proven S1→S4+Q1 clean
  (sac_z5=0, BIC-clean); 2–4-position perturbations likely stay in
  the clean basin. Exploitation continues after b59's success.
- **Mechanism question (crisp):** does the proven-clean winner
  basin contain a sub-18.6u schedule that survives the full battery?

## Triage discussion: the S2 max|z| signal

t6_b59_47 passed S2 with max|z|=138.1 vs 89.6 for t6_b59_0. Both
pass the formal S2 gate (0 repeats); the worst-delta margin is
thinner for 47. This is recorded as a SIGNAL, not a kill and not a
gate: no evidence links triage-z or S2 max|z| to later kills
(t6_b59_7 died at S1 with triage z=2.53; 47 passed everything with
triage z=3.18). Batch-60 records per-keep (triage_z, S2 max|z|)
pairs for the keeps that reach S2, to test whether the two
correlate. Adding an unvalidated S2-margin gate would be an
unjustified cut — the gate stays fisher-matched.

## Cuts (defensible reason at each cut site)

1. **m=1 around the two bases: CUT** — every 1-position neighbor
   of t6_b59_47 is a ≤3-position neighbor of t6_b57_8
   (d(t6_b57_8,47)=2, triangle inequality:
   d(t6_b57_8,x) ≤ 2+1 = 3), and likewise for t6_b59_0 (d=1 →
   ≤2); both lie inside b59's already-sampled perturbation space
   (92 draws). Re-sampling m=1 is mostly re-draw of b59's space,
   not new territory. m∈{2,3,4} reaches d∈{4,5,6} from the
   original winner — genuinely new territory.
2. **Wider radius (m>4): DEFERRED** — start 2–4 (basin size at
   d≥4 unknown; one radius step at a time is the honest
   exploitation sequence). Trigger: pilot 0/80 → widen or close.
3. **Perturbing around t6_b57_8 directly at wider radius: CUT** —
   redundant with the two bases' reach (m∈{2,3,4} around 47
   covers d∈{0..6} from the original winner; around 0 covers
   d∈{0..5}); sampling the same territory from a third base is
   not new territory, it's re-weighting.
4. **Global re-draws: CUT** (b57 exhausted the experiment).
5. **4-stage: CUT** (O116 family-kill).
6. **mux3f (dropped d-tap): DEFERRED** — trigger: basin-depth
   axis-kill (pilot 0/80 or no sub-18.6u cost-eligible keep).
7. **Hetero forms AND3/ANDN/OAAND: CUT** (postmortem_hetcascade;
   no reshuffle). **XOR4-hetero: NOT CUT** — the queued xorh5 lead
   is being adjudicated in parallel (own pilot); its verdict
   decides whether it becomes a batch, not this axis.
8. **h0-neighborhood / Q1-tail: DEFERRED** (b57; trigger unmet).
9. **Blind/worst-z triage: CUT** (O96; gate-matched bar proven).
10. **key-fold: CUT** (O83 — systematic differential bias +5.6u).
11. **6-stage/chi/S-box forms: CUT** (measured cost floors;
    QLOW 24.6/25.7u O88).

## Pre-registered rules

- **Pre-pilot** (12 draws, seed 0xB601): HARNESS CHECK ONLY.
  Calibration must PASS all three gates (fail-loud):
  CALIB-1 and1/b33c z=3.3 EXACT; CALIB-2a MU5-324 n_reject=0;
  CALIB-2b linear-4 n_reject>0 (negative control fires).
  selftest must verify the two-base perturbation operator (200
  draws: base ∈ {47,0}, 2–4 positions differ from the chosen base,
  stages valid, s/a/b distinct, never base-identical). 1-draw
  smoke PASS.
- **Pre-pilot 0/12 → PILOT runs regardless** (12 draws cannot
  adjudicate the basin).
- **GATE-FAIL (vacuous): keeps==n_try and kills==0 → KILL LOUDLY,**
  diagnose.
- **Pilot** (80 draws, seed 0xB602): ≥1 fisher-KEEP → bit-exact
  bundle (`gen_b57_bundle.py` verbatim — keeps carry form="muxD5f",
  5 stages; output recorded to disk) → S0 (run_synth.py ONLY;
  strict <18.6u for speed contention; ties at 18.6u recorded as
  size-chain candidates) → cost-eligible keeps escalate in z-order
  → staged battery S1→S2→S3→S4 → Q1 (sac_z5=0 mandatory). A
  Q1-clearing keep at <18.6u → FRONTIER CHALLENGER (chain stops).
- **Pilot 0/80 → AXIS-KILL** (the 2–4 basin around both winners is
  exhausted under the fisher bar; VERDICT_SCOPE O-entry scoped to
  the tested bases and radius) → escalate to deferred mux3f, or to
  xorh5 if its pilot kept.
- **Per-keep S2-margin recording:** every keep reaching S2 gets
  (triage_z, S2 max|z|) recorded in the battery log for the
  correlation study. No gate change.

## What a full pass at <18.6u means

A keep that clears S0 STRICTLY <18.6u, S1→S4, and Q1 sac_z5=0
becomes the new Frontier S+Q speed point (PARETO.md + notes,
RETAINED.md, RTL `your_files/mix_rtl_pareto/mix_t6_b60_*.v`
generator-verbatim, O-entry). The chain stops at the first such
challenger (b59 precedent); remaining cost-eligible keeps go to a
size chain.

## Bookkeeping

- Heartbeat: `new_constructions/batch60/heartbeat.txt` every ~20 min.
- CHECKPOINT.md: sibling; resume instructions inside.
- Ledger: prepend entry on each terminal verdict; VERDICT_SCOPE.md
  O-entry (O119+) scoped to tested configs.
- workreg: track6-batch60 (exists; heartbeat on state changes).
