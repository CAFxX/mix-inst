# Batch-48 design note — "cheap-chi-stage": 4-stage chi with reduced single-rotation linear layer (track 6, 2026-10-11)

**Status: AXIS CLOSED (VALID: proof + loud empirical kills) — PILOT NOT
LAUNCHED (foregone; verdict reached pre-pilot — see "Verdict" below).**
(track-6 supervisor incarnation XVII, 2026-10-11 14:44 CEST.) The
mechanism experiment (`batch48/mechanism_experiment.py`) + single-variable
control (`batch48/harness_check.py`) closed the axis before the pilot:
the reduced layer is provably singular (rotation-independent), 3/3 draws
die at triage with z~1e5–1.5e6, and the 2-rot control on the identical
rotation skeleton is 28,000x cleaner. Burning a 40-draw pilot to confirm a
proof-backed foregone 0/40 would be theater, not measurement (standing
order: every cut needs a defensible reason — here the reason is proof +
loud empirical kills, the strongest cut category; cf. b47 cut #1, O45).

**Trigger:** batch-47 CLOSED 2026-10-11T12:29:20Z — all three 3-stage dense
arms 0/40 ("fewer, fatter stages" falsified; dense wall pinned at 4 stages;
no-zero-corner discriminator CONFIRMED by the maj3S-3 mechanism control).
The dense-quadratic repeated-stage line is now fully mapped: 3st dead all
flavors (b47), 4st quality-ok/cost-dead (b45: 22.9–23.2u at 5.77u/stage),
5st quality-ok/cost-dead (b45), hetero cost-engineering dead (b46). The only
cost-engineering direction on the quality-proven dense form that b46 didn't
take: **reduce the per-stage cost via the linear layer.**

## Axis
Two 4-stage arms (pre-whiten `x ^= k`; final `x ^= rotl(k,13)` — the
b33c/b41/b43/b44/b45/b46/b47 frame; REPLACEMENT stage wiring verbatim from
b45, i.e. `x := stage(x)`):

- **chi3R4** (prize): 4 stages of `stage(x,a) = chi3(x) ^ rotl(chi3(x),a)`,
  chi_3 on 21 contiguous 3-bit lanes, bit 63 identity (b42/b45 geometry,
  verbatim). Rotation `a` drawn from ODD 1..63.
- **chi5R4** (lane-width control): 4 stages of
  `stage(x,a) = chi5(x) ^ rotl(chi5(x),a)`, chi_5 on 12 contiguous 5-bit
  lanes (bits 0..59), bits 60..63 identity (b42 geometry, verbatim).

## The linear layer, precisely (co-design)
b45's stage: `y ^ rotl(y,a) ^ rotl(y,b)` — 3-term XOR tree (2 XORs),
nonsingular for a≠b. The reduction drops exactly one rotation term:
`L_a(y) = y ^ rotl(y,a)` — 1 XOR. This is the **minimal edit** of the
quality-proven form (comparability frame preserved: the ONLY delta from
chiS4 is the dropped rotation).

**The surviving rotation is load-bearing:** it carries 100% of the
inter-lane diffusion (each S-box output bit spreads to 2 positions, not 3).
Without it (`a=0`) the stage degenerates to `x := chi3(x)` — 21 independent
3-bit lanes, zero inter-lane diffusion (fail-loud assert `a ∈ 1..63`).

**Singularity (PROOF, O45 class):** `L_a(y) = y ^ rotl(y,a)` fixes the
all-ones vector (any permutation preserves it: `L_a(u) = u^u = 0`) and 0,
so `ker(L_a) ∋ {0, u}` — **every 1-XOR linear layer is GF(2)-singular**;
there is NO nonsingular 1-XOR option (even XOR-term count ⟺ p(1)=0 ⟺
singular; O29/O38). Measured (`mechanism_experiment.py`, fail-loud
asserts): `rank(L_a) = 63` for ALL odd a; `rank(L_a) ≤ 62` for ALL even a
(e.g. a=2 → period-2 kernel, dim 2). Consequences in the replacement frame:
- each stage is exactly 2-to-1 (odd a); the 4-stage cascade is 16-to-1;
- every stage output has EVEN parity deterministically, so the final
  `S = x4 ^ rotl(k,13)` is confined to a 63-dim affine subspace
  (`parity(S) = parity(k)`, input-independent).

**Mechanism question (crisp):** b45's quality finding rests on (i) the
no-zero-corner property (CONFIRMED by b47's maj3S-3 control: maj died three
orders of magnitude above bar with killkey-0x0 dominance) and (ii)
inter-lane diffusion from the linear layer. The 1-rot layer keeps (i) fully
(the chi S-box is untouched) but weakens (ii) (2-position spread) AND adds
the singular kernel. chiS4 kept 10/40 with min z=2.8 — headroom exists.
**Does the exact-DIFF quality survive the reduced diffusion at 4 stages?**

**Falsifier:** chi3R4 0/40 with mins in the hundreds+ (the b43/b44/b46/b47
kill signature) → the reduced diffusion does NOT survive; prime suspect the
singular kernel (bounded); arm closed scoped. chi3R4 ≥1 KEEP → quality
SURVIVES → the cost thesis decides at S0.

**Discriminating follow-up (queued, NOT screened):** if 1-rot dies, the
4-term EVEN layer `y^ra^rb^rc` (singular per O29/O38, rank ≤63) diffuses
MORE than 1-rot — 4-term-singular vs 3-term-nonsingular (b45) discriminates
"singularity" from "diffusion amount". Recorded as re-test trigger.

## Mechanism experiment readout (pre-pilot, 2026-10-11 — DECISIVE)
`batch48/mechanism_experiment.py` on the EXACT prize form (odd-a draws),
raw `batch48/mechanism_experiment.log`:
- (a) rank asserts: odd-a all rank 63, even-a rank 32–62 — PASS (premise
  confirmed; even-a strictly worse, cut #1 validated).
- (b) exact-DIFF triage on 3 draws: **ALL KILLED, 4–6 orders of magnitude
  above bar** — draw 0 (stages [45,33,27,43]) z=156,695.8 killkey=0x5555…;
  draw 1 (stages [23,19,21,43]) z=1,480,000.0 killkey=0x0; draw 2 (stages
  [31,27,61,59]) z=113,166.0 killkey=0x0. The prize question ("does chi
  quality survive?") is answered NO at the triage itself — no S0/S1 needed.
- (c) S1 LIN rank test on 1 draw: **D=4096/4096, logp=-inf** (null
  E[D]≈21.6); output-parity-constant premise CONFIRMED across 2^18
  outputs. Independent second gate, total linear collapse.
- Control (`batch48/harness_check.py`, raw `batch48/harness_check.log`):
  the b45 2-rot form on the IDENTICAL rotation skeleton ([23,19,21,43] →
  pairs (23,30),(19,26),(21,28),(43,50)) through the IDENTICAL code path
  gives z=53.3 (kill, but **28,000x smaller** than the 1-rot draw's
  1,480,000). Single variable changed = the dropped rotation. The
  linear-layer reduction is ISOLATED as the killer; the harness is trusted
  (no 1e6-artifact).

## Verdict (2026-10-11 14:44 CEST, incarnation XVII)
**Cheap-chi-stage axis CLOSED — VALID kill (proof + loud empirical).**
- The reduced single-rotation linear layer is GF(2)-singular for EVERY
  rotation (proof, rotation-independent): any 1-XOR layer has even term
  count ⟹ p(1)=0 ⟹ singular (O29/O38/O45 class). In the b45 replacement
  frame each stage is exactly 2-to-1, the cascade 16-to-1, outputs confined
  to a 63-dim affine subspace.
- 3/3 triage draws killed at z~1e5–1.5e6 (bar: z<10); S1 LIN D=4096/4096;
  28,000x control contrast vs the 2-rot form. A keep would require the
  proven rotation-independent mechanism to vanish — foregone.
- **Scope (VERDICT_SCOPE.md):** kills the TESTED construction — 4-stage
  chi_3/chi_5-lane replacement cascade, 1-rot linear `y^rotl(y,a)`,
  pre-whiten, `rotl(k,13)` — AND the class claim "1-XOR linear-layer cost
  reduction on chi stages" (proof covers the class: no nonsingular 1-XOR
  layer exists). NOT a claim about other dense primitives or S-boxes.
- **Cost-engineering corollary (proof):** the linear layer is at its cost
  floor — 2 XORs (b45's tree) is the cheapest nonsingular option. The
  S-box is the only remaining per-stage lever, and chi_3's INV is
  load-bearing for bijectivity (`a^(b&c)` ablation collides: 000→000 and
  111→000 — CUT ON PROOF, exhibited collision) and for the no-zero-corner
  property. The dense chi-stage line is FULLY CLOSED on cost.
- **Correction to the queued follow-up:** the 4-term even layer
  `y^ra^rb^rc` discriminator is ALSO dead on proof (even term count ⟹
  singular, same class) — NOT queued; closed without screening.
- **Considered and cut:** pure-permutation (0-XOR) linear layer —
  1-position spread is strictly weaker than the killed 2-position 1-rot
  form; CUT ON MECHANISM (weaker than a killed form, no rescue mechanism).
- Pilot NOT launched (foregone 0/40; ~1h CPU during backoff for zero
  information gain). No escalation (no keeps; S0 moot).

## Next lead (queued for next incarnation / coordinator)
**4-bit quadratic bijective S-box stage.** chi_4 is non-bijective (b42
proof) but that is chi-specific; the 4-bit S-box classification contains
bijective quadratics (untested as repeated stages). Constraints for
co-design: (i) bijective lanes (b42 hard gate — assert fail-loud);
(ii) no-zero-corner or better than AND-mask's 1/3-fire (b47 discriminator);
(iii) linear-layer floor 2 XORs (this batch) ⟹ S-box+tree <4.83u/stage
(4st) or <3.86u/stage (5st) for frontier viability. First step is S-box
mining + DDT/duality check, NOT a blind screen. Alternative if the
coordinator prefers: the dense line as mapped is cost-closed — pivot to a
different line entirely.

## Cost thesis (measured components; S0 decides)
b45 measured 5.77u/stage for the 3-term form (1×INV + 1×AND + 3×XOR per bit
+ the 2-rotation XOR tree). Removing one XOR level from the tree →
est. ~4.5–5.0u/stage → 4st ≈ 18–20u, live vs the 19.3u frontier bar
(hyb28_mu5_324). Bar: strictly **<19.3u MEASURED** via run_synth.py,
XCHECK clean (ref mul64 103.5u).

## De-dup (grep-verified 2026-10-11, incarnation XVII)
- Single-rotation chi linear layer: NEVER screened. All chi-stage screens
  (b45/b46/b47) use the 2-rotation tree `y ^ rotl(y,a) ^ rotl(y,b)`; grep
  for single-term `y ^ rotl(y,` forms across `batch*/` → zero hits.
- "1rot" / "single-rotation" / "reduced linear" → zero hits across
  batches 19–47 (code + DESIGN.md).
- b45 cut chi_5 lanes with re-test trigger "any chiS KEEP" — FIRED (chiS4
  10/40). chi5R4 is the owed follow-up, now on the reduced layer.

## Cuts recorded (defensible reason at each cut site)
1. **Even-a rotations: CUT ON PROOF.** `rank(L_a) ≤ 62` for even a
   (mechanism_experiment.py asserts; a=2 → period-2 kernel, dim 2) —
   strictly larger kernel than odd-a; no mechanism by which a larger kernel
   aids diffusion. Re-test trigger: none (proof).
2. **Alternative reduced form `x ^= chi3(x) ^ rotl(x,a)` (rotate the
   pre-image, masked wiring): CUT ON MECHANISM.** Abandons the "linear layer
   diffuses S-box output" principle the b45 quality finding rests on —
   nonlinear output bits stay in-lane (strictly weaker diffusion for the
   nonlinear terms). Also breaks the comparability frame (wiring change on
   top of the layer change = two deltas, not one).
3. **Alternative reduced form `rotl(y,a) ^ rotl(y,b)` (drop the unrotated
   term): CUT as non-minimal-delta.** Same 1-XOR cost class, same
   singularity class as the chosen form; `y ^ rotl(y,a)` is the minimal edit
   of the quality-proven b45 stage (one dropped term).
4. **chi_4 / nibble-chi repeated stage: CUT ON PROOF** (b42 exhaustion:
   chi_4 non-bijective 16→12; compounding violates the bijectivity hard
   gate; O45 precedent). No re-test trigger.
5. **5st/6st 1-rot: CUT on measured-cost projection**
   (5×~4.75 ≈ 23.75u > 19.3u; b45's 6st-cut precedent). Re-test trigger: 4st
   keeps AND measured per-stage < 3.86u.
6. **3st 1-rot: CUT on mechanism.** b47: 3st dense dead all flavors
   (chi3S-3 min z=2163); weaker diffusion at 3st is weaker still — no
   mechanism proposed for why less diffusion succeeds where more failed.
7. **Per-stage round key: CUT on measured cost** (b8 het5a 5.0u/stage
   rk-bearing forms cost-dominated; b45/b46/b47 precedent).
8. **Fused forms (x entering the nonlinear op): CUT on evidence** (b8 fchi6a
   S1-killed z 47k–160k; t6_fmaj6a difference-contraction kill).
9. **b45-2rot reproducibility control arm: CUT.** Calibration z=3.3
   fail-loud already gates harness health per run; b45's 10/40 stands as the
   comparator; compute better spent on the prize question (the control would
   answer "harness drift", which calibration already answers).
10. **4-term singular layer as mechanism discriminator: CUT from pilot** —
    conditional follow-up (informative only if 1-rot dies); queued as
    re-test trigger.
11. **LIN proxy triage: N/A** (b39–b47 precedent: DIFF-only triage for
    rotation cascades; S1 LIN gates escalation).

## The two hard lessons (applied)
(a) **Triage z doesn't rank S0 within a form** → S0 on a STRATIFIED keep
    sample spanning the z range (min/median/max-z), never best-z-only.
(b) **Exact-DIFF triage is blind to the S1 marginal/inner-DIFF kill** → S1
    FAIL-FAST on the FIRST cost-eligible keep (no S0 batching). Batch-48
    subtlety: the triage IS the exact S1 DIFF computation (O86: reproduces
    S1 DIFF bit-for-bit), so triage↔S1-DIFF correlation holds by
    construction; the known blind spots are the marginal/inner-DIFF and LIN
    families — fail-fast S1 covers them immediately. Additional batch-48
    blind-spot note: the singular layer's parity confinement (output in a
    63-dim affine subspace) is invisible to per-bit/low-8-bit DIFF machinery
    by construction (the 2-to-1 twin map `T(x)=chi^{-1}(chi(x)^u)` preserves
    per-bit marginals); the S1 LIN rank test is the designated catcher —
    its sensitivity is measured directly by mechanism_experiment.py (c).

## Pipeline (b33 playbook + lessons)
1. Calibration: and1/b33c must reproduce z=3.3 (fail-loud).
2. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys, sequential
   inputs N=2^18, KEEP bar max|z|<10. Keeps → JSONL per-try (b39).
   Fail-loud draw-loop cap 10000 (b45). Duplicate stage-tuples re-drawn
   (b41). Draw asserts: a ∈ odd 1..63 (cut #1); rank-63 layer assert at
   import (mechanism premise, fail-loud).
3. S0: STRATIFIED keep sample, bar strictly <19.3u MEASURED, XCHECK clean
   (lesson a).
4. S1 FAIL-FAST on the first cost-eligible keep (lesson b) — full S1
   (LIN+DIFF+marginals; the parity-confinement blind spot is LIN's to
   catch).
5. Survivors → staged battery S1→S2→S3→S4→Q1 (round13/q1_sacbic.py;
   sac_z5=0 mandatory for any Frontier-S claim).

## Pre-registered verdict rules
- chi3R4 0/40 with min in the hundreds+ → reduced diffusion FALSIFIED for
  chi_3 at 4st; prime suspect = singular kernel (bounded claim); arm closed
  scoped to (4-stage chi_3-lane replacement cascade, 1-rot odd-a linear,
  pre-whiten, rotl(k,13)). Queue the 4-term-singular discriminator as next
  lead.
- chi3R4 ≥1 KEEP → quality SURVIVES → bundle gen bit-exact 2000/2000 → S0
  stratified → S1 fail-fast → b33 playbook. A keep at measured <19.3u is a
  FRONTIER CHALLENGER.
- chi5R4 outcome decides lane-width sensitivity of the survival (b47
  parallel); verdict scoped to chi_5 lanes.
- All arms dead → cheap-chi-stage axis closed (VALID scoped kill); next axis
  per the widen directive (never stop silently).

## Draw constraints (fail-loud asserts)
- a drawn from odd integers 1..63 (cut #1: even-a cut on proof).
- Duplicate (type, a) stage-tuples re-drawn within a try.
- Seeds: chi3R4 0xB481, chi5R4 0xB482 (batch-48 block). 40 draws/arm.

## Pilot wiring — NOT LAUNCHED (verdict reached pre-pilot)
The 40-draw pilot (`t6_b48_screen.py` / `run_b48.sh`) was designed but NOT
launched and the scripts were NOT created: the mechanism experiment +
control closed the axis first (foregone 0/40; ~1h CPU during backoff for
zero information gain). The evidence lives in
`batch48/mechanism_experiment.py` (+`.log`), `batch48/harness_check.py`
(+`.log`), and this DESIGN.md — not in pilot logs. If the coordinator
wants the 40-draw confirmation anyway, the screen is a 10-minute adaptation
of `batch47/t6_b47_screen.py` (forms chi3R4/chi5R4, stage tuples
`("C3"/"C5", a)`, a odd 1..63, seeds 0xB481/0xB482, rank-63 assert at
import); the runner follows the `batch47/run_b47.sh` pattern (tag
track6/b48-pilot, backoff-poll ≤12h, calibration fail-loud, setsid launch).
