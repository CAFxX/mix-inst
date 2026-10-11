# Wave-10 Notes — COMPLETE, all candidates terminal (2026-10-10 ~01:15Z)

## Design intent
Wave-9 (danger-zone-free progressive AND) was falsified. Wave-10 tried two NEW directions:
- **Prong A (dual-AND)**: 5/6-stage `x ^= (ra&rb)^(rc&rd)^re` — the 5/6-stage dual was NEVER tried
  before (only dualand4 was killed at triage). dualand5a/b, dualand6a.
- **Prong B (heterostage on known-clean triplets)**: het6a [and,or] and het6b [and,chi]
  alternating on the KNOWN-CLEAN and6a triplets — resonance control for wave-9's broad-elevation
  differential bias. Both 20.4u (+0.3u vs frontier 20.1u).

## S0 (run_synth.py, Yosys 0.69, unit-delay)
| cand | latency | note |
|------|---------|------|
| dualand5a | 24.7u | floor attack FAILS on speed: 4.9u/stage |
| dualand5b | 24.4u | same |
| dualand6a | 28.7u | dominated-class quality probe |
| het6a | 20.4u | +0.3u vs frontier |
| het6b | 20.4u | +0.3u vs frontier |

All triage-PASS (xcheck OK, aval 0.012–0.017, zmax 2.9–4.5).

## S1/S2 (GHA al-wave10-s1s2-20261009, run 37990749152, 6/6 shards success; and6a canary healthy)
- dualand5a: **S1 FLAG** — CAL_FLAG with zero PB/LIN/DIFF/RED rejections (calibration kill)
- dualand5b: **S1 FLAG** — DIFF rej=2
- dualand6a: **S1 FLAG** — PB rej=2
- het6a: S1 CAL_PASS; S2 tool-PASS (max_repeats=0, max|z|=148.9)
- het6b: S1 CAL_PASS; S2 tool-PASS (max_repeats=0, max|z|=112.3)

**Dual-AND family: S1-dead.** All three dead at S1, including the 6-stage.

## S2 raw-log adjudication (local, nice-10, diffprof N=2^22, key 0x123456789abcdef0, kill_repeats=10)
Same protocol as wave-9 kills. Kill bar: ornot6 killed 33/115 deltas |z|>9; al_and9d killed
34/115 (max|z|=64.4); chi6k killed 49/115 (max|z|=195.3).

- **al_het6a: S2 KILLED** — 43/115 deltas |z|>9, max|z|=148.9 @ delta 0x0001000000000000 (bit48),
  0 full repeats. Local max matches GHA tool's 148.9 exactly.
- **al_het6b: S2 KILLED** — 48/115 deltas |z|>9, max|z|=112.3 @ bit48, 0 full repeats.

GHA tool "PASS" verdicts overridden by raw log (tool verdicts are leads, not verdicts).

## Findings
1. **Resonance-control hypothesis falsified.** Building heterostages on known-clean and6a triplets
   does NOT fix the systematic differential bias. The bias persists (max at bit48 for both het6a/b,
   43–48/115 deltas) despite the triplet structure being S2-clean under chi.
2. **The resonance lives in the and6a triplets, not the subop choice.** Changing the subop
   (and/or vs and/chi) did not move the needle — both die with the same high-bit-delta signature.
   This is the sharpest new signal from wave-10: the (rotation-schedule, triple structure) combination
   resonates regardless of which chi-like subop occupies each slot.
3. **Dual-AND (4.9u/stage) is worse than single-AND cascade (3.35u/stage).** The floor attack fails:
   two AND-pairs per stage costs ~1.5u/stage extra with no quality gain — all three S1-dead.
4. The 20.1u al_and6a remains the only fully-validated (S0–S4+Q1) design at the frontier.
   Every sub-20.5u AND-family construction tested to date has failed S1 or S2.

## Wave-11 direction (open, needs new ideas — do NOT repeat wave-9/10)
- The triplet-schedule resonance is the binding constraint, not subop choice. New directions must
  change the schedule structure itself (different triplet composition, non-triplet stage
  structure, or non-cascade architecture entirely).
- Non-AND, non-cascade families (cf. track-6's `noncascade_structures` lead) are the genuinely
  unexplored space for this track.
- Re-test triggers: a new <4u/stage function family; a schedule with fundamentally different
  differential-elevation profile.

## Artifacts
- gen: `adder_lat/gen_wave10.py`; models: `adder_lat/models.py`
- bundles: `fast_battery/candidates/al_{dualand5a,dualand5b,dualand6a,het6a,het6b}/`
- GHA: campaign `al-wave10-s1s2-20261009` (run 37990749152, commit 3a819536)
- local S2: `adder_lat/s2_al_het6a.log`, `s2_al_het6b.log`
- ledger: `LEADS_LEDGER.md` rows 155–159 (terminal), 332–336 (wave-10 NEW)
- heartbeat: `adder_lat/supervisor_heartbeat.txt`
