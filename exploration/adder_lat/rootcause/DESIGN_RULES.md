# Design Rules: Beating the 5-Stage DIFF Wall

**Track 3, 2026-10-10.** Derived from the 5-stage DIFF wall theorem (ROOTCAUSE.md)
plus new experiments (design_rules_exp1.py, s2proxy.py).

## The theorem in one line

For 2-input AND/OR-with-rotation cascades, each stage's AND only randomizes
output bits "touched" by the input difference; after 4 stages the difference
cannot cover all 64 AND-input pairs of a 5th stage (min pair-miss 0.50 vs
0.009 required). **Six stages are the structural minimum for this family.**

## Rule 1 — Difference fan-out determines the wall, not diffusion

The linear skeleton's min-weight is NOT the predictor (falsified: failing
and5xa has weight 32 > passing and6a's 28). The predictor is the **4-stage
prefix's difference uniformity**, measured by:

    U = min_d max_k P[d_4 misses distance-d pair {k, k+d}]

Measured (N=2^16, single-bit deltas):
- and5xa prefix (FAIL): U = 0.50
- and6a-first4 (FAIL as 5-stage): U = 0.498
- fz15_c prefix (PASS): U = 0.295

**Design criterion:** minimize U over the 4-stage prefix. U < 0.009 is
sufficient (by the corollary bound); U in [0.009, ~0.35] is the gray zone
where the bound is loose and direct simulation decides.

## Rule 2 — Triple fan-out beats the wall; double fan-out doesn't

The deterministic difference map of a stage is M = I + R^c (+ R^e...).
- AND-cascade: M = I + R^c (each difference bit fans out to 2 positions)
- 3-term-linear: M = I + R^c + R^e (each difference bit fans out to 3)

The extra fan-out is WHY fz15_c's d_4 is more uniform (U=0.295 vs 0.50).
**Every additional linear term in the stage's deterministic skeleton
multiplies the difference-spreading rate.** This is the fundamental lever.

## Rule 3 — The S2-proxy is predictive; use it as the design loop

**CRITICAL METHODOLOGY FIX (2026-10-10 10:30Z):** v1 proxy used RANDOM x and
was NOT predictive (al_ht51: v1 z=3.4, real S2 z=300.3). diffprof/S1 use
SEQUENTIAL x (0..2^N). Designs can have massive bias on sequential inputs
while looking clean on random (the AND-masking interacts with the
low-Hamming-weight input distribution). **v2 proxy (s2proxy_v2.py) replicates
diffprof exactly: sequential x, dedupe, all 64 single-bit + structured +
nibble deltas.**

Validation (logN=18, sequential x):
| design | v2 proxy max|z| | real verdict |
|---|---|---|
| and5xa | 386.1 | S2 KILL (~118) |
| fz15_c | 10.5 | S2 PASS |

**Design loop:** v2 screen (logN=16, fast) → v2 full (logN=18) → real S2
diffprof (minutes) → S0 (minutes) → GHA S1/S2. NEVER use random-x for
differential screening.

## Rule 4 — Cost budget for sub-20.1u 5-stage

Per-stage S0 (Yosys 0.69): AND = 3.35u, 3-term-linear = 4.5u.
To beat 20.1u with 5 stages:
- 2×t3 + 3×and = 19.05u ✓
- 1×t3 + 4×and = 17.90u ✓
- 3×t3 + 2×and = 20.20u (marginal, needs fast synthesis)

The hetero [t3,and] mixes are the only sub-20.1u 5-stage structures.
Pure t3 (22.5u) and pure and (16.75u, wall-blocked) are both out.

## Rule 5 — Position matters: spread early, mask late

The wall is about the LAST stage's quiet probability. Early stages should
maximize fan-out (t3), late stages provide cheap masking (and). Front-load
the t3 stages: [t3,t3,and,and,and] dominates [and,and,and,t3,t3] because
d_4 uniformity is set by the prefix.

## Rule 6 — The S-box escape hatch (proven)

hyb12_asb5a (5 AND + S-box + L(5,13), 22.3u) is S2-clean: the S-box layer
has a per-nibble quiet condition (4 zero bits), far stricter than a pair.
**Any layer with a stricter-than-pair quiet condition breaks the wall.**
Cost is the issue (S-box layer ~5u); the prize is a sub-20.1u S-box hybrid.

## Rule 7 — What CANNOT work (don't retry)

- Pure 5-stage AND/OR-with-rotation, any schedule (theorem).
- Wider AND pairs / different (a,b) on the same triplets (wave-10: resonance
  is in the triplets, min pair-miss 0.50 for ALL d).
- Removing the AND to "save depth" (wave-11: AND is free, XOR tree dominates).
- 4-stage anything in this family (fz16_a: catastrophic).
- **Higher-degree AND (AND3, x^=(ra&rb&rc)^rd): proxy z=159-174, far worse
  than AND2.** Reason: AND3's "touched" case has residual correlation 0.5
  (E[(-1)^{x_a x_b}] = 0.5 when d_c=1), not balanced like AND2's ≤0.0029.
  **Design principle: the nonlinear op must have BALANCED-touch
  (correlation 0 when the input difference touches it), not just rare-quiet.**
  AND2 is special; higher degree breaks the balance.

## Rule 8 — S-box-first fails; strong layer must be LAST

S-box layer FIRST then AND stages: proxy z=27-57 (worse than pure AND).
The S-box does not "immunize" later stages; the wall applies to whatever
is last. **Position the strongest randomizer at the END** (asb5a: S-box last
works; sbox-first fails). Refines Rule 5.

## Open directions (leads)

1. **Hetero t3/and search** (this track, in progress): 2×t3+3×and at 19.05u
   with proxy z<9. Search running (search5.py).
2. **Cheaper triple fan-out**: is there a <4.5u/stage construction with
   M = I+R^c+R^e? (e.g., sharing XOR terms across stages).
3. **S-box-first**: S-box layer FIRST (strong early d_1), then 4 AND stages.
   The S-box makes d_1..d_4 uniform from the start.
4. **LIN-clean ≠ DIFF-clean** (track-4 dd12 lesson): always check both.

## Files

- `s2proxy.py`: predictive differential z-score screen
- `search5.py`: hetero 5-stage random search
- `design_rules_exp1.py`: U-metric measurement
- `candidates5.json`: top search hits
- `DESIGN_RULES.md`: this document
