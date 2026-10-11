# Track 3 Wave-9 Design Notes (2026-10-09)

## Wave-8 Failure Analysis

Wave-8 tested "avalanche-aware" schedules (18 distinct rotations) for AND cascades.
The methodology transferred from chi but FAILED for AND:
- al_and6h (19.2u): S1 DIFF FLAG (rej=4, worst|z|=6.8)
- al_and6i (19.8u): S1 DIFF FLAG (rej=10, worst|z|=64.7) — catastrophic
- al_and6j: triage kill (avalanche 0.0855)

**Root cause hypothesis: rotation danger zones.**

| Candidate | Danger rotations (/18) | S1 result |
|-----------|----------------------|-----------|
| al_and6a (PASS) | 2 | CAL_PASS |
| al_and6h | 6 | FLAG (rej=4) |
| al_and6i | 5 | FLAG (rej=10) |

Danger zones:
- **[28,36]**: near 32 (half-word). `rotl(x,32)` has order 2 (apply twice = identity).
  Creates structural symmetries exploitable by differential trails.
- **>= 54**: near 64 (= 0). Rotations like 57, 58 are `rotr(x,7)`, `rotr(x,6)` —
  small rotations in the other direction. Mixing small positive and small negative
  rotations creates short cycles.

al_and6a's rotations: max 41, avoids 32 and near-64 entirely.
Wave-8 H: includes 32, 53, 57, 58. Wave-8 I: includes 32, 30, 33, 35, 54, 55.

## Wave-9 Design Principles

1. **Danger-zone-free**: no rotations in [28,36], none >= 54.
2. **Progressive structure**: early stages use small AND-pair differences (dense local
   nonlinearity), later stages use larger differences (diffusion).
   al_and6a diffs: 1, 12, 8, 14, 12, 22 (starts small, grows).
3. **XOR rotation c incommensurate** with AND-pair (a,b): avoid c near a, b, or |a-b|.

## Wave-9 Results

### Triage (avalanche N=20k, mini-diff N=2^18, 12 deltas)

| Candidate | aval_maxdev | zmax | Verdict | Notes |
|-----------|-------------|------|---------|-------|
| al_and9a | 0.0170 | 9.8 | KILL (marginal) | Just over 9.0 bar |
| al_and9b | 0.0141 | 6.5 | PASS | |
| al_and9c | 0.0137 | 4.4 | PASS | |
| al_and9d | 0.0122 | 3.6 | PASS | Best triage |
| al_and9e | 0.0252 | 17.3 | KILL | Small-XOR hypothesis FALSIFIED |
| al_and5xa | 0.0705 | 60.2 | KILL | 5-stage barrier HOLDS |
| al_and5xb | 0.1319 | 130.1 | KILL | 5-stage barrier HOLDS |
| al_andor9a | 0.0151 | 9.3 | KILL (marginal) | |
| al_andor9b | 0.0134 | 6.0 | PASS | OR-heavy works |

**Findings:**
- 5-stage barrier HOLDS even with danger-zone-free co-design (60-130 zmax).
  5 stages insufficient for AND cascades, period.
- Small-XOR hypothesis FALSIFIED: keeping XOR rotations small (3,5,7,9,11)
  hurts diffusion (zmax=17.3). XOR needs to be large for spreading.
- OR-heavy (4/6 stages OR) passes triage — OR is viable in AND cascades.

### S0 (run_synth.py, Yosys 0.69, pinned flow)

| Candidate | Delay | Cells | vs frontier |
|-----------|-------|-------|-------------|
| al_and9b | **19.8u** | 6113 | Ties 6-stage floor |
| al_andor9b | **19.8u** | 6162 | Ties 6-stage floor |
| al_and9c | 20.1u | 5891 | Ties al_and6a |
| al_and9d | 20.1u | 6027 | Ties al_and6a |

Two candidates at the 19.8u floor. If either is S1-clean, it ties the speed
record (chi6b, chi6c, ornot6c, and6b all at 19.8u but S1-FLAGGED).

### Next

- GHA campaign `al-wave9-s1s2-20261009` submitted (4 shards, S1+S2).
- Local S1 running for al_and9b (early signal).
- If S1-clean at 19.8u: S3/S4/Q1 for frontier challenge.
- If all FLAG: wave-10 needs new ideas (fewer stages won't work, 19.8u is floor).
