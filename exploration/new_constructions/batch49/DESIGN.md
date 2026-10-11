# Batch-49 design note — "q4-stage": bijective quadratic 4-bit S-box repeated stage (track 6, 2026-10-11)

**Status: PRE-PILOT LAUNCHED / AWAITING ADJUDICATION.**
(track-6 supervisor incarnation XIX, 2026-10-11.)

**Trigger:** batch-48 CLOSED 2026-10-11T12:44Z (1-XOR linear layer provably
singular for every rotation; 2 XORs is the linear-layer cost floor; dense
chi-stage line fully cost-closed — the S-box is the only remaining
per-stage lever; chi_4 non-bijective per b42 proof, chi-specific). The
queued lead: a BJECTIVE QUADRATIC 4-bit S-box as a repeated stage — never
screened (de-dup below).

## The mined S-box Q4 (mining completed 2026-10-11)
`batch49/anneal_q4_fast.py`: simulated annealing over the pure-quadratic
ANF family (4×11 binary params per S-box: constant + 4 linear + 6 quadratic
terms per component), 12 starts × 25000 steps, seeds 0xB492–0xB49D,
per-start checkpointed to `mine_q4_fast.starts.jsonl` (deterministic
resume; survived two silent miner deaths — 13:04Z session-teardown and
13:42Z unknown — plus backoff-gated wrapper `run_b49_mine.sh`).
Objective: energy = 64·coll + DU + LATbias/8 (collisions dominant, then
DU, then LAT bias). De-duped pre-anneal: LP-optimal 16 classes
(`verify_lp.py`, DU=4/LATbias=4) are NOT purely quadratic (component
degrees {2,3} or {3}); random-quadratic ANF 0/200000 bijective (CUT ON
MEASUREMENT — bijectivity too rare in the quadratic family for blind
screening); triangular quadratic construction CUT ON MEASUREMENT (1024
cores all DU=16; proof: x0 enters linearly).

**Mining verdict (12/12 starts checkpointed):** BEST energy=9.0, coll=0,
DU=8, LATbias=8 (miner units; = max |LAT entry|/2), compdeg=[1,2] —
verified independently by Moebius over all 15 output masks and by brute
force (bijective ✓, S(0)=3≠0 ✓, DU=8 exact, max |LAT entry|=16 at
(a,b)=(5,2)). Six starts landed DU=8, six DU=16. **DU=4 is unreachable in
the pure-quadratic bijective family per this 12-start evidence** (the
anneal IS the optimizer over the family — this is the family's empirical
floor, not a theorem; consistent with the fact that LP-optimal 4-bit
classes all carry cubic components).

- **Q4 LUT = [3,4,15,5,0,6,1,10,14,13,2,12,9,11,8,7]**
  (energy=9.0, seed 0xB492; fail-loud asserts in `t6_b49_screen.py`:
  bijective ✓, no-zero-corner ✓ — the b42 hard gate and the b47
  discriminator, co-designed per the queued lead).

## Axis
Two arms (pre-whiten `x ^= k`; final `S = cascade ^ rotl(k,13)` — the
b33c/b45/b46/b47 frame; REPLACEMENT stage wiring; the ONLY delta from
chiS4 (b45) is the S-box):

- **q4bS4** (prize): 4 stages of `stage(x,a,b) = L_{a,b}(Q4(x))` where
  `L_{a,b}(y) = y ^ rotl(y,a) ^ rotl(y,b)` — b45's 2-rotation tree
  VERBATIM (cheapest nonsingular linear layer per the b48 proof, O45
  class; comparability frame preserved). Q4 applied on 16 contiguous
  4-bit lanes (bits 0..63, full coverage, no passthrough bits).
- **q4bS3** (wall probe): 3 stages of the identical stage form.
  (Rationale: chiS4 needs 4 stages (b45: 10/40) while 3st dense died
  all flavors (b47); if 4st quality survives, 3st is dead by mechanism —
  but a 3st q4bS3 KEEP at ~3.6u/stage would be a direct frontier
  challenger, so the probe is cheap information.)

Draw constraints (fail-loud asserts): a,b ∈ 1..63, a≠b (b45 verbatim —
no mod-4 cut: the ONLY delta from chiS4 is the S-box; rank-64 layer
premise inherited from b45, assert at import); duplicate (tag,a,b)
stage-tuples re-drawn within a try (b41); draw-loop cap 10000 (b45).

## Cost thesis (measured at S0, not estimated — bar strictly <19.3u)
4st × per-stage budget <4.83u/stage ⟹ frontier viability (19.3u bar,
hyb28_mu5_324). Per-bit stage cost: Q4 is quadratic (compdeg {1,2}) —
unrolled: ~2 AND levels + XOR tree per output bit, on 16 4-bit lanes
(synth-friendly: shallow AND-XOR, no INV chains like chi's) + the 2-XOR
rotation tree (b48 cost floor). 3st × <6.43u/stage is the secondary bar
only if q4bS4 dies and q4bS3 lives. The S-box cost is decided by
`run_synth.py` measurement on a cost-eligible keep (S0), never by
estimation.

## Mechanism question (crisp)
chiS4's quality finding rests on (i) no-zero-corner and (ii) the S-box's
in-lane avalanche (chi_3 DU=2/8=1/4) feeding (iii) the 2-rot tree's
3-position spread. Q4 keeps (i) (S(0)=3) and (iii) verbatim, but its
in-lane profile is DU=8 (4x weaker per S-box than chi_3) and one
perfectly-correlated linear approximation (LAT entry 16/16 at (5,2)).
**Does the exact-DIFF quality survive 4 stages of a DU=8 quadratic S-box
when the linear layer is unchanged?** Two sub-mechanisms compete: (a) the
quadratic S-box's cheaper AND structure + co-designed bijectivity may
preserve enough mixing for the exact-DIFF triage to pass; (b) DU=8 with a
correlation-1 linear relation may let low-weight differentials ride the
4-stage cascade (the b43/b44/b46/b47 kill signature). The triage decides.

**Falsifier:** 0/6 keeps on both arms with min z in the b48-class (≥1e4)
or b47-class (≥1e3) with killkey-0x0 dominance → Q4's per-S-box weakness
kills it; axis closed scoped to (4st/3st repeated Q4 replacement cascade,
2-rot tree, pre-whiten, rotl(k,13)). Any KEEP → mechanism alive → pilot.

**The two hard lessons (applied):**
(a) Triage z doesn't rank S0 within a form → S0 on a STRATIFIED keep
    sample spanning the z range (min/median/max-z), never best-z-only.
(b) Exact-DIFF triage is blind to the S1 marginal/inner-DIFF kill → S1
    FAIL-FAST on the FIRST cost-eligible keep (no S0 batching). The S1
    LIN test is the designated catcher for Q4's correlation-1 linear
    relation ((a,b)=(5,2) at lane level) — measured directly in the
    fail-fast S1, not assumed.

## De-dup (grep-verified 2026-10-11, incarnation XIX)
- Bijective-quadratic 4-bit S-box repeated-stage screen: NEVER screened.
  All chi-stage screens (b45/b46/b47/b48) use chi_3 (DU=2) or chi_5;
  chi_4 cut on b42 bijectivity proof (16→12, non-bijective —
  compounding violates the b42 hard gate). Q4 is bijective — different
  primitive, different mechanism question.
- **fz24_g / fz24_h** (`fused/gen_fused24.py`): 5-stage nibble-chi
  (`nch` = chi_4 per-nibble Keccak-chi) fused forms — the non-bijective
  primitive; explicitly NOT the bijective Q4.
- Midori/Sb0/Sb1 nibble S-boxes (VERDICT_SCOPE O63): keyed-SPN + P-box
  chassis — no repeated-stage quadratic-bijective cascade.
- All "nibble" hits elsewhere (O34/O37/O39): S-box+P-box SPN chassis —
  no shared mechanism with the replacement-stage cascade.

## Cuts recorded (defensible reason at each cut site)
1. **Triangular quadratic S-box construction: CUT ON MEASUREMENT + PROOF.**
   1024 cores all DU=16; proof: x0 enters linearly → the construction
   cannot reach DU<16. Re-test trigger: none (proof-backed).
2. **Random quadratic-ANF screening: CUT ON MEASUREMENT.**
   0/200000 bijective — far below any affordable screen density; mining
   (anneal) is the right search, not sampling. Re-test trigger: none
   (density argument, not a design claim).
3. **LP-optimal-class S-boxes as repeated stages: CUT ON FAMILY SCOPE.**
   DU=4/LATbias=4 optimal but component degrees {2,3}/{3} (not pure
   quadratic — `verify_lp.py`); screening them would abandon the
   cost thesis (cubic = more AND levels) — the quadratic axis tests the
   cheap end first. Re-test trigger: Q4 axis dies AND a cost-viable
   cubic S-box is mined (different axis, different lead).
4. **5st/6st q4: CUT on measured-cost projection** (5×~4.5 ≈ 22.5u >
   19.3u; b45's 6st-cut precedent). Re-test trigger: 4st keeps AND
   measured per-stage < 3.86u.
5. **Per-stage round key: CUT on measured cost** (b8 het5a 5.0u/stage
   rk-bearing cost dominance; b45/b46/b47 precedent).
6. **Fused forms (x entering the nonlinear op): CUT on evidence** (b8
   fchi6a S1-killed z 47k–160k; t6_fmaj6a difference-contraction kill).
7. **mod-4 rotation cut (chi arms): NOT applied.** Deliberate
   non-minimal comparability: the ONLY delta from chiS4 is the S-box;
   a≠b is the only draw constraint (b45 verbatim).
8. **LIN proxy triage: N/A** (b39–b47 precedent: DIFF-only triage for
   rotation cascades; S1 LIN gates escalation — and here it is
   load-bearing, since the correlation-1 relation must be measured).
9. **Pre-pilot 3-draw short-cuts per arm: CUT.** ~6 draws/arm is the
   pre-registered minimum for a verdict with any discriminating power;
   fewer draws cannot separate "dead" from "unlucky" at the expected
   keep-rate ceiling.

## Pipeline (b33 playbook + lessons)
1. Calibration: and1/b33c must reproduce z=3.3 (fail-loud;
   `t6_b49_screen.py calibrate`). The b33c schedule is copied verbatim
   from `batch47/t6_b47_screen.py` so the z=3.3 reproduction is exact.
2. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Pre-pilot: ~6 draws/arm
   (seeds 0xB491 block: q4bS4 0xB491, q4bS3 0xB492). Keeps → JSONL
   per-try appended immediately (b39). Fail-loud draw-loop cap 10000
   (b45). Duplicate stage-tuples re-drawn (b41). Q4 asserts (bijective,
   S(0)≠0) fail-loud at import.
3. Pre-registered pre-pilot verdict rules (see next section).
4. Escalation on any KEEP: bundle gen bit-exact 2000/2000 → S0 via
   `run_synth.py` (bar strictly <19.3u MEASURED, XCHECK clean — ref
   mul64 103.5u) on a STRATIFIED keep sample (lesson a) → S1 FAIL-FAST
   on the FIRST cost-eligible keep (lesson b) → survivors staged
   battery S1→S2→S3→S4→Q1 (round13/q1_sacbic.py; sac_z5=0 mandatory for
   any Frontier-S claim).

## Pre-registered pre-pilot verdict rules
- 0 keeps both arms with min z ≥1e3 (b47-class) or ≥1e4 (b48-class) with
  killkey-0x0 dominance → **KILL LOUDLY**: Q4's DU=8 weakness kills the
  cascade; axis closed scoped to the tested construction; no pilot; no
  S0. Next lead per the widen directive (never stop silently).
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
- Scripts: `batch49/t6_b49_screen.py` (LUT-filled, asserts pass),
  runner pattern `batch47/run_b47.sh` (backoff-poll ≤12h, setsid launch,
  tag track6/b49-pilot).
- 2×40 draws: q4bS4 seed 0xB493, q4bS3 seed 0xB494.
- Escalation: any pilot KEEP → bundle gen bit-exact 2000/2000 → S0
  stratified (bar <19.3u) → S1 fail-fast → staged battery.
- All arms dead → axis closed (VALID scoped kill); next axis per the
  widen directive.

## Backoff / launch log
- 2026-10-11 17:02 CEST: backoff gate = BACKOFF (load 12.47 ≥ 12).
  LUT fill + DESIGN.md written under the gate; calibration + pre-pilot
  launch queued until `load-shed.sh backoff` exits 0.
- <launch line appended at launch>
- 2026-10-11 17:07 CEST: pre-pilot LAUNCHED via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b49-prepilot`
  (wrapper `run_b49_prepilot.sh`: backoff-poll ≤12h → calibration
  fail-loud → q4bS4 6 draws seed 0xB491 → q4bS3 6 draws seed 0xB492 →
  keeps to `prepilot_keeps.jsonl`; logs `prepilot.log`,
  `prepilot_calibrate.log`). At launch load=12.47 → wrapper correctly
  waiting on backoff (starts the 12 draws when clear).
