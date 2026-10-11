# Batch-50 design note — "qLow-stage": minimal-AND bijective quadratic 4-bit S-box repeated stage (track 6, 2026-10-11)

**Status: CO-DESIGN COMPLETE / PRE-PILOT QUEUED.**
(track-6 supervisor incarnation XX, 2026-10-11.)

**Trigger:** batch-49 CLOSED 2026-10-11T17:28Z — Q4 (5 AND monomials,
DU-optimal over the pure-quadratic family) is quality-alive (q4bS4 4/6
KEEP, min z=2.6) but S0 cost-doomed (28.0u vs the 19.3u bar;
7.0u/stage vs the <4.83u/stage 4st budget). The per-stage cost is
schedule-independent (rotations are wires), so the ONLY remaining lever
inside the b45 frame is the S-box's AND structure. The deferred lead
from that verdict — cost-driven quadratic-S-box mining (minimize AND
monomials s.t. bijective + DU≤8) — is this batch's axis, co-designed
below to a construction with a real chance (not a re-run of batch-49).

## The mined S-box QLOW (co-design probe, 2026-10-11)

Two probes were run (both in `batch50/`):

1. **Soft probe** (`probe_lowand.py`): penalty-form anneal, caps K=2/3/4,
   energy = 1000·coll + 64·max(0,AND−K) + DU + LATbias/8 + 32·(S(0)==0),
   3 starts × 10000 steps per K. Result: the penalty landscape is rugged
   — (bijective, DU=8) was reached only by blowing the AND cap
   (K=2→12 ANDs), while AND≤4 stayed at DU=16. Suggestive but not
   conclusive (penalty-landscape luck, not a family statement).

2. **Hard probe** (`probe_lowand_hard.py`): the AND pattern is FIXED to a
   specific set of k pairs (cap holds by construction); the anneal
   optimizes only the linear part (4 components × (1 const + 4 linear +
   k AND-coeffs) bits), energy = 1000·coll + DU + LATbias/8 +
   32·(S(0)==0). Exhaustive over pair-patterns: k=3 → 20 patterns,
   k=2 → 15 patterns, 8000 steps each, deterministic seeds.

**Hard-probe verdict:** pattern 0, the **star** `[x0x1+x0x2+x0x3]`
(all three ANDs share x0), reaches **E=9.0: coll=0, DU=8, LATbias=8,
S(0)=10≠0** — the EXACT quality profile of Q4 (DU=8 is the
pure-quadratic family's empirical floor per b49's 12-start evidence)
with **3 AND monomials instead of 5**. The other 19 k=3 patterns all
stalled at DU=16 (linear-structure trap); the star's shared-variable
geometry is the differentiator (every nonzero input difference keeps at
least one atom's x-dependent derivative alive).

- **QLOW LUT = [10,13,6,15,8,11,4,9,0,1,12,3,2,7,14,5]**
  (fail-loud asserts in `t6_b50_screen.py`: bijective ✓, S(0)≠0 ✓ —
  the b42 hard gate and the b47 discriminator, co-designed per the
  queued lead). Independently verified: bijective, DU=8 exact,
  purely quadratic (Moebius over all 4 output bits, max degree 2),
  exactly 3 distinct AND monomials (x0x1, x0x2, x0x3).
  ANF (derived by Moebius, printed by `gen_b50_bundle.py`):
    y0 = x0
    y1 = 1^x0^x2^(x0&x1)^(x0&x2)^(x0&x3)
    y2 = x0^x1^(x0&x1)^(x0&x2)^(x0&x3)
    y3 = 1^x1^(x0&x1)^(x0&x3)
  Note y0 is purely linear — the S-box as a whole is still bijective
  with DU=8 (differentials are a whole-S-box property); the S1 LIN
  fail-fast (lesson b) is the designated catcher if the linear
  component matters at cascade level.

## Axis
Two arms (pre-whiten `x ^= k`; final `S = cascade ^ rotl(k,13)` — the
b33c/b45/b49 frame; REPLACEMENT stage wiring; the ONLY delta from
q4bS4 (b49) is the S-box):

- **qlowS4** (prize): 4 stages of `stage(x,a,b) = L_{a,b}(QLOW(x))`
  where `L_{a,b}(y) = y ^ rotl(y,a) ^ rotl(y,b)` — b45's 2-rotation tree
  VERBATIM (cheapest nonsingular linear layer per the b48 proof, O45
  class; comparability frame preserved). QLOW applied on 16 contiguous
  4-bit lanes (bits 0..63, full coverage, no passthrough bits).
- **qlowS3** (wall probe): 3 stages of the identical stage form.
  (Rationale: q4bS4 kept 4/6 at triage; if 4st quality survives the
  cheaper S-box, 3st is dead by mechanism (b47/b49) — but a 3st qlowS3
  KEEP at ~3.5u/stage would be a direct frontier challenger, so the
  probe is cheap information.)

Draw constraints (fail-loud asserts): a,b ∈ 1..63, a≠b (b45/b49
verbatim — no mod-4 cut: the ONLY delta from q4bS4 is the S-box;
rank-64 layer premise inherited, assert at import); duplicate
(tag,a,b) stage-tuples re-drawn within a try (b41); draw-loop cap
10000 (b45).

## Cost thesis (measured at S0, not estimated — bar strictly <19.3u)
4st × per-stage budget <4.83u/stage ⟹ frontier viability (19.3u bar,
hyb28_mu5_324). Q4's measured 7.0u/stage decomposes (schedule-
independent) into ~5.8u S-box proper (5 AND monomials + XOR forest) +
~1.2u 2-rot tree. Linear-in-ANDs projection for QLOW's 3 monomials:
~3.5u S-box + ~1.2u tree ≈ **4.7u/stage < 4.83u** — TIGHT but a real
chance (this is the co-design bar the brief demanded: not a re-run of
batch-49, a construction whose cost thesis clears the bar on paper and
is decided by `run_synth.py` measurement on a cost-eligible keep).
3st × <6.43u/stage is the secondary bar only if qlowS4 dies and qlowS3
lives. The S-box cost is decided by S0 measurement, never by the
projection above.

## Mechanism question (crisp)
q4bS4's triage finding (4/6 KEEP, min z=2.6) rests on (i) no-zero-corner,
(ii) the S-box's in-lane avalanche (DU=8) feeding (iii) the 2-rot tree's
3-position spread. QLOW keeps (i) (S(0)=10) and (iii) verbatim, and its
in-lane profile is DU=8/LATbias=8 — IDENTICAL to Q4's. **Does the
exact-DIFF quality survive when the S-box's AND structure is thinned
from 5 monomials to the 3-monomial star, holding DU and the linear
layer fixed?** Two sub-mechanisms compete: (a) DU=8 is DU=8 — the
cascade cannot tell the S-boxes apart at the differential level the
triage measures, so quality transfers; (b) the star's shared-x0 geometry
(and y0's pure linearity) concentrates the nonlinearity onto fewer
independent atoms, letting low-weight differentials ride the cascade
(the b43/b44/b46/b47 kill signature). The triage decides. Either way
the verdict is informative: (a) → a cost-viable dense stage exists;
(b) → AND-count is load-bearing for cascade quality, closing the
dense-S-box line on mechanism (not just cost).

**Falsifier:** 0/6 keeps on both arms with min z in the b48-class (≥1e4)
or b47-class (≥1e3) with killkey-0x0 dominance → the thinned S-box's
weakness kills the cascade; axis closed scoped to (4st/3st repeated
QLOW replacement cascade, 2-rot tree, pre-whiten, rotl(k,13)). Any KEEP
→ mechanism alive → synthesis spot-check → pilot.

**The two hard lessons (applied):**
(a) Triage z doesn't rank S0 within a form → S0 on a STRATIFIED keep
    sample spanning the z range (min/median/max-z), never best-z-only.
(b) Exact-DIFF triage is blind to the S1 marginal/inner-DIFF kill → S1
    FAIL-FAST on the FIRST cost-eligible keep (no S0 batching). The S1
    LIN test is the designated catcher for QLOW's linear component y0
    and its correlation-1 relation — measured directly in the fail-fast
    S1, not assumed.

## De-dup (grep-verified 2026-10-11, incarnation XX)
- Minimal-AND / star-pattern quadratic S-box as repeated stage: NEVER
  screened. All S-box-stage screens (b45 chi_3/chi_5, b49 Q4) use
  DU-optimal or dense S-boxes; no batch 19–49 mined or triaged an
  AND-count-constrained S-box. Zero hits for "lowand/QLOW/qlow" outside
  batch50/.
- **fz24_g / fz24_h** (`fused/gen_fused24.py`): 5-stage nibble-chi
  (`nch` = chi_4 per-nibble Keccak-chi) fused forms — the non-bijective
  primitive (b42 proof: 16→12); explicitly NOT the bijective QLOW.
  Stay OPEN as noted in b45, unaffected by this batch.
- Midori/Sb0/Sb1 nibble S-boxes (VERDICT_SCOPE O63): keyed-SPN + P-box
  chassis — no repeated-stage quadratic-bijective cascade.
- All "nibble" hits elsewhere (O34/O37/O39): S-box+P-box SPN chassis —
  no shared mechanism with the replacement-stage cascade.
- b48 cut #6 (fused forms) does not apply: QLOW is a replacement-stage
  S-box (x does not enter the nonlinear op fused with the mask), not a
  fused form.

## Cuts recorded (defensible reason at each cut site)
1. **Penalty-form mining as the family verdict: CUT ON METHODOLOGY.**
   The soft probe's rugged landscape (bijective+DU=8 only by blowing
   the cap) could not distinguish "infeasible" from "unlucky" — replaced
   by the hard probe's exhaustive pattern-fixed search (20+15 patterns),
   which IS the family statement for k≤3. Re-test trigger: none
   (methodology, not a design claim).
2. **k=2 S-boxes as the batch-50 stage: CUT ON MEASUREMENT (hard
   probe).** 15/15 patterns stall at DU=16 (linear-structure trap);
   none reach bijective+DU≤8. The k=2 corner is closed. Re-test
   trigger: a new k=2 family (non-quadratic) — different axis.
3. **Non-star k=3 patterns: CUT ON MEASUREMENT (hard probe).** 19/19
   non-star patterns stall at DU=16; only the x0-star reaches DU=8.
   The star geometry is load-bearing, not incidental. Re-test trigger:
   none within the quadratic family (exhaustive).
4. **LP-optimal-class (cubic) S-boxes as repeated stages: CUT ON FAMILY
   SCOPE** (inherited from b49 cut #3 — cubic = more AND levels,
   abandons the cost thesis; the quadratic axis tests the cheap end
   first). Re-test trigger: QLOW axis dies AND a cost-viable cubic
   S-box is mined (different axis, different lead).
5. **5st/6st qlow: CUT on measured-cost projection** (5×~4.7 ≈ 23.5u >
   19.3u; b45's 6st-cut precedent). Re-test trigger: 4st keeps AND
   measured per-stage < 3.86u.
6. **Per-stage round key: CUT on measured cost** (b8 het5a 5.0u/stage
   rk-bearing cost dominance; b45/b46/b47/b49 precedent).
7. **Fused forms (x entering the nonlinear op): CUT on evidence** (b8
   fchi6a S1-killed z 47k–160k; t6_fmaj6a difference-contraction kill).
8. **mod-4 rotation cut: NOT applied.** Deliberate non-minimal
   comparability: the ONLY delta from q4bS4 is the S-box; a≠b is the
   only draw constraint (b45/b49 verbatim).
9. **LIN proxy triage: N/A** (b39–b49 precedent: DIFF-only triage for
   rotation cascades; S1 LIN gates escalation — and here it is
   load-bearing, since y0's linearity must be measured).
10. **Pre-pilot 3-draw short-cuts per arm: CUT.** ~6 draws/arm is the
    pre-registered minimum for a verdict with any discriminating power
    (b49 precedent).

## Pipeline (b33 playbook + lessons)
1. Calibration: and1/b33c must reproduce z=3.3 (fail-loud;
   `t6_b50_screen.py calibrate`). The b33c schedule is copied verbatim
   from `batch47/t6_b47_screen.py` so the z=3.3 reproduction is exact.
2. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Pre-pilot: ~6 draws/arm
   (seeds 0xB501 block: qlowS4 0xB501, qlowS3 0xB502). Keeps → JSONL
   per-try appended immediately (b39). Fail-loud draw-loop cap 10000
   (b45). Duplicate stage-tuples re-drawn (b41). QLOW asserts
   (bijective, S(0)≠0) fail-loud at import.
3. Pre-registered pre-pilot verdict rules (see next section).
4. Escalation on any KEEP: bundle gen bit-exact 2000/2000 → S0 via
   `run_synth.py` (bar strictly <19.3u MEASURED, XCHECK clean — ref
   mul64 103.5u) on a STRATIFIED keep sample (lesson a) → S1 FAIL-FAST
   on the FIRST cost-eligible keep (lesson b) → survivors staged
   battery S1→S2→S3→S4→Q1 (round13/q1_sacbic.py; sac_z5=0 mandatory for
   any Frontier-S claim).

## Pre-registered pre-pilot verdict rules
- 0 keeps both arms with min z ≥1e3 (b47-class) or ≥1e4 (b48-class) with
  killkey-0x0 dominance → **KILL LOUDLY**: the thinned S-box's weakness
  kills the cascade (mechanism (b) confirmed); axis closed scoped to the
  tested construction; no pilot; no S0. Next lead per the widen
  directive (never stop silently).
- 0 keeps with min z < 100 (near-misses) → NOT catastrophe →
  **PILOT** (2×40 draws): the mechanism is alive enough to deserve the
  full pre-registered pilot; ~1h CPU during backoff is justified
  information gain.
- ≥1 KEEP on either arm → **mechanism alive → synthesis spot-check on
  one schedule** (cost thesis: S-box+tree <4.83u/stage at 4st, else
  cost-doomed → retained as evidence, closed) → PILOT.
- Pre-pilot 0 kills at all (all keeps — GATE-FAIL) → harness vacuous
  (script exits 2) → fix the harness, no verdict.

## Pilot wiring (pre-registered, launched after pre-pilot adjudication)
- Scripts: `batch50/t6_b50_screen.py` (LUT-filled, asserts pass),
  runner pattern `batch47/run_b47.sh` (backoff-poll ≤12h, setsid launch,
  tag track6/b50-pilot).
- 2×40 draws: qlowS4 seed 0xB503, qlowS3 seed 0xB504.
- Escalation: any pilot KEEP → bundle gen bit-exact 2000/2000 → S0
  stratified (bar <19.3u) → S1 fail-fast → staged battery.
- All arms dead → axis closed (VALID scoped kill); next axis per the
  widen directive.

## Backoff / launch log
- 2026-10-11 17:32–17:55 CEST: co-design probes (soft + hard) under
  backoff-CLEAR (load 8.4–9.2); hard probe k=3 decisive at pattern 0.
- 2026-10-11 17:43:45Z: pre-pilot LAUNCHED via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b50-prepilot`
  (wrapper `run_b50_prepilot.sh`: backoff-poll ≤12h → calibration
  fail-loud → qlowS4 6 draws seed 0xB501 → qlowS3 6 draws seed 0xB502 →
  keeps to `prepilot_keeps.jsonl`; logs `prepilot.log`,
  `prepilot_calibrate.log`). At launch load=14.57 → wrapper correctly
  waiting on backoff (starts the 12 draws when clear). Calibration
  pre-verified PASS (b33c z=3.3 exact) before launch.
- 2026-10-11 18:08 CEST: PILOT LAUNCHED by the 18:01 report run (the
  18:05 adjudication had TRIGGERED it but the cron timed out before
  launch) via `setsid agentwork-launch.sh --nice 19 --tag
  track6/b50-pilot` (new wrapper `run_b50_pilot.sh`: backoff-poll ≤12h
  → calibration fail-loud → qlowS4 40 draws seed 0xB503 → qlowS3 40
  draws seed 0xB504 → keeps to `pilot_keeps.jsonl` → "PILOT COMPLETE";
  logs `pilot.log`, `pilot_calibrate.log`). At launch backoff ENGAGED
  (1 frozen process, shedder draining) → wrapper correctly
  backoff-polling (pid 106091); proceeds autonomously when clear.
