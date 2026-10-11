# Wave-11 Notes — COMPLETE, both prongs falsified (2026-10-10 ~03:30Z)

## Design intent
Wave-10 proved the resonance lives in the and6a TRIPLETS (rotation-schedule +
triple-structure), not the subop choice. Wave-11 changed the SCHEDULE STRUCTURE
itself via two prongs, both untested in every track (track-6 LEADS.md checked):

- **Prong A (linear-stage insertion)**: replace 1 of 6 AND stages with pure-linear
  `x ^= ra ^ rb ^ rc`. Hypothesis: linear stage is cheaper (~2.2u) than AND
  (3.35u) AND breaks the AND-differential resonance chain.
- **Prong B (key-linear triplets)**: `x ^= (ra&rb) ^ rk1 ^ rk2` — replace the
  data-linear term rc with two key rotations. Same gate depth as "and" but a
  fundamentally different differential profile (key terms cancel in differentials).

## Triage (triage.py: xcheck + avalanche + mini-diff)
| cand | xcheck | aval_maxdev | zmax | verdict |
|------|--------|-------------|------|---------|
| al_lin6a (lin@idx2) | OK | 0.0243 | 20.4 | **TRIAGE-KILL** (diff resonance at mid position) |
| al_lin6b (lin@idx4) | OK | 0.0135 | 2.9 | TRIAGE-PASS |
| al_lin6c (lin@idx0) | OK | 0.0131 | 3.7 | TRIAGE-PASS |
| al_keylin6a | OK | 0.2861 | 285.2 | **TRIAGE-KILL** (catastrophic) |
| al_keylin6b | OK | 0.2833 | 286.0 | **TRIAGE-KILL** (catastrophic) |
| al_keylin5a | OK | 0.4419 | 448.9 | **TRIAGE-KILL** (catastrophic) |

## S0 (run_synth.py, Yosys 0.69, unit-delay)
| cand | latency | vs frontier (20.1u) | verdict |
|------|---------|---------------------|---------|
| al_lin6b | 21.2u / 5327 cells | +1.1u | **S0 DOMINATED** |
| al_lin6c | 21.7u / 5813 cells | +1.7u | **S0 DOMINATED** |

## Diagnostics (per-stage cost isolation)
| design | S0 | per-stage | finding |
|--------|----|-----------|---------|
| diag_lin6 (6x `x^ra^rb^rc`) | 24.3u | **4.05u** | Linear XOR stage SLOWER than AND stage |
| diag_rot6 (6x `x^ra^rb`) | 21.0u | **3.50u** | Rotation-only also slower than AND |
| al_and6a (6x `x^(ra&rb)^rc`) | 20.1u | **3.35u** | AND stage is cheapest |

## Findings (durable)
1. **"Linear is cheaper" is FALSE in this Yosys flow.** Pure-XOR stages cost
   4.05u/stage, rotation-only 3.50u/stage, both SLOWER than AND-XOR at 3.35u/stage.
   The AND gate is essentially FREE — Yosys/ABC absorbs it while the XOR tree
   dominates the critical path. You cannot buy speed by removing nonlinearity.
2. **The data-linear term rc is LOAD-BEARING for diffusion.** Replacing it with
   key material (keylin) causes catastrophic avalanche failure (meandev 0.28-0.44).
   The rc term is not a mere add-on; it is essential for bit diffusion. (Confirms
   track-6's norc6a "avalanche 23.8 sub-ideal" observation with a stronger kill.)
3. **Linear-stage POSITION matters enormously.** lin@idx2 triage-killed (zmax 20.4)
   while lin@idx0 and lin@idx4 passed (zmax 2.9/3.7). The differential resonance
   is position-sensitive — a mid-cascade linear stage creates a new resonance.
4. **The cascade family is at its Pareto edge.** 6 stages x 3.35u = 20.1u is a
   strong local optimum. Every structural deviation tested (waves 9-11, track-6
   batches 8-24) is slower, quality-dead, or both.

## Wave-12 direction (proposed)
The XOR tree (2 levels for 3-input) is the cost driver, not the AND. New idea:
**twin-AND** `x ^= (ra&rb) ^ (rc&rd)` — TWO ANDs feeding a 3-input XOR tree
(x, p1, p2). Same XOR depth as standard (~3.35u/stage) but 2x nonlinearity per
stage. This is NOT wave-10's dualand (which had a 4-input XOR tree with `^re`,
costing 4.9u/stage). If twin-AND 5-stage is S1/S2-clean, it breaks the 5-stage
DIFF wall via doubled nonlinearity at ~16.8u. Test: 6-stage (quality probe) and
5-stage (floor attack), and6a-derived + fresh quads.

## Artifacts
- gen: `adder_lat/gen_wave11.py` (new "lin"/"keylin" stage types)
- bundles: `fast_battery/candidates/al_{lin6a,lin6b,lin6c,keylin6a,keylin6b,keylin5a}/`
- diagnostics: `fast_battery/candidates/diag_{lin6,rot6}/`
- S0: `adder_lat/s0_results.txt` (RESULT records)
- heartbeat: `adder_lat/supervisor_heartbeat.txt`
