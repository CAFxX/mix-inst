# Batch-47 design note — "fewer, fatter stages": 3-stage dense-quadratic cascades (track 6, 2026-10-11)

**Status: PILOT COMPLETE — AXIS CLOSED (VALID)** (track-6 supervisor
incarnation XVI). 2026-10-11T12:29:20Z: chi3S-3 0/40 (min z=2163.0),
chi5S-3 0/40 (min 790.0), maj3S-3 0/40 (min 21319.7). Raw:
`batch47/pilot_{chi3S3,chi5S3,maj3S3}.log` (40 try-lines each),
`run_b47.log`. Adjudication in LEADS_LEDGER.md (2026-10-11 14:3x CEST entry).

**Trigger:** batch-46 CLOSED 2026-10-11T11:25:40Z — hetero 2xchi+2xAND
interleave 0/80 (VALID scoped empirical kill). The cost-engineering
follow-up to batch-45 is dead; the next lever must be elsewhere. Batch-45's
headline finding reframes the whole wall: **the 5-stage wall is specific to
SPARSE-gate cascades** — dense chi_3 stages breach it decisively (chiS5 40/40
KEEP median z=2.8; chiS4 10/40 KEEP) but cost 5.77u/stage (cost-closed at
22.9–23.2u). The dense wall's location is UNKNOWN: chiS4 already keeps at
25%. **This batch probes the dense wall at 3 stages, where the cost thesis
is live.**

## Axis
Three 3-stage masked-cascade arms (pre-whiten `x ^= k`; final
`x ^= rotl(k,13)` — the b33c/b41/b43/b44/b45/b46 frame):

- **chi3S-3** (prize arm): `stage(x,a,b) = chi3(x) ^ rotl(chi3(x),a) ^ rotl(chi3(x),b)`,
  chi_3 on 21 contiguous 3-bit lanes, bit 63 identity (b42/b45 geometry, verbatim).
- **chi5S-3** (geometry control): same stage with chi_5 on 12 contiguous 5-bit
  lanes (bits 0..59), bits 60..63 identity (b42 geometry, verbatim).
- **maj3S-3** (mechanism control): `x ^= maj(ra,rb,rc) ^ rd`,
  `maj(a,b,c) = (a&b)|(a&c)|(b&c)` (b5 t6_maj6 form, verbatim; S1-CAL_PASS at 6st).

## Co-design rationale
The b45 mechanism finding is bounded: chi stages carry quality because they
have **no sparse zero-corner** (every output bit nonlinearly active on every
input; on a single-bit input the AND term still fires 1 bit/lane). Majority
is the discriminating probe: it is "wide" (3 ANDs + 2 ORs per bit, every
output bit a function of 3 input bits) but **retains the zero corner**
(on a single-bit input, maj fires 0 bits — the stage degrades to `x ^= rd`,
pure linear, exactly the b37 pathology). The three arms jointly answer the
standing question: **is the dense-wall breach a chi-specific property, a
general dense-firing property, or specifically the no-zero-corner property?**

- chi3S-3 keeps, maj3S-3 dies with killkey-0x0 dominance → the no-zero-corner
  property is the discriminator (CONFIRMS the b45 mechanism); dense wall for
  chi_3 sits in {3,4}.
- maj3S-3 keeps → majority is a SECOND quality primitive at ~14.7u-class cost
  → new lead (cheaper than chi per stage).
- chi3S-3 dies (0/40, mins in hundreds) → dense wall sits at 4 stages for
  chi_3; close scoped. chi5S-3 outcome tests lane-width sensitivity.

**Cost thesis (measured components, S0 decides):**
- chi3S-3: 3 × 5.77u ≈ **17.3u < 19.3u** (2.0u margin; the b41
  spread-settlement window is ~1.1u — a borderline S0 needs a 2nd schedule).
- chi5S-3: same per-bit gate count as chi_3 → ~17.3u class.
- maj3S-3: 3 × 4.9u ≈ **14.7u < 19.3u** (4.6u margin; t6_maj6 measured
  29.4u/6 = 4.9u/stage).

## De-dup (grep-verified 2026-10-11)
- 3-stage chi as repeated stage of a masked cascade: NEVER screened. b45 did
  4st/5st only; b42's chi_3/chi_5 were SINGLE FINAL layers; fused forms
  (gen_fused1/14/15/24, adder_lat/gen_wave1) use sparse chi-terms
  `(~ra&rb)` or fixed-lin nibble forms — different function and wiring.
- Majority below 6 stages: NEVER. b5 tested maj6 (29.4u, S1-CAL_PASS) and
  maj8 (37.6u); t6_fmaj6a was the FUSED form `maj(x,ra,rb)` — killed by
  difference-contraction, a different construction (x enters nonlinearly).
- chi_5 as repeated stage: NEVER (b45 cut it as a follow-up variable; the
  re-test trigger died with b46).
- No batch 19–46 screened a 3-stage dense-quadratic masked cascade.

## Why b45's "3 stages: CUT" does not block this batch
b45 cut #3 ("3 stages: CUT. Structurally below the wall") rested ENTIRELY on
sparse-cascade evidence (fz16_a catastrophic S1 FLAG; xc4a/dual4a S1-killed;
b34 d2a3@4st 0/200) — "3st is weaker still. No mechanism proposed." At cut
time the wall was assumed stage-count-driven. b45's own headline finding then
changed the framework: the wall is sparse-specific; dense chi breaches at 4st.
Per the re-test discipline (AGENTS.md: re-test past decisions when
requirements change), the 3-stage cut stands for SPARSE forms and is re-opened
for DENSE forms, which were never tested at 3st. The cut's scope is respected,
not violated.

## Cuts recorded (defensible reason at each cut site)
1. **chi_4 / nibble-chi repeated stage: CUT ON PROOF.** chi_4 provably
   non-bijective (16 inputs → 12 outputs, b42 exhaustion proof); compounding
   across stages violates the bijectivity hard gate (O45 precedent: 2-to-1
   maps killed analytically). Re-test trigger: none — proof, not samples.
2. **maj@4st: CUT on measured-cost projection.** 4 × 4.9u = 19.6u > 19.3u
   (t6_maj6 measured). Re-test trigger: maj@3st keeps AND measured maj
   per-stage < 4.8u.
3. **maj@5st: CUT on measured cost.** 5 × 4.9u = 24.5u > 19.3u. Same trigger
   family.
4. **3-stage SPARSE forms: CUT on mechanism.** b37 structural kill (no-mask
   shift-AND min z=287,285 — the zero-corner pathology proven); andnM@5st
   0/40 (b39); 3st sparse weaker still. (b45 cut #3, retained for sparse.)
5. **Per-stage round key (b8 style): CUT on measured cost.** b8's rk-bearing
   forms measured 5.0u/stage (cost-dominated); the no-rk masked cascade keeps
   the b33c/b45 comparability frame.
6. **Fused forms (x entering the nonlinear op): CUT on evidence.** b8's fused
   chi S1-killed (z 47k–160k); fused maj t6_fmaj6a killed by
   difference-contraction (LEADS.md:37). Masked-cascade wiring (`x ^=`) is the
   quality-proven one (b33c, 324, b45).
7. **Midori-Sb0 3-stage: CUT on evidence.** wave-35 terminal: S-layer costs
   4.2u/stage AND needs ≥4 AND stages before it (nibble-collapse); 3r SPN
   killed at S1 (O39). Not a dense-quadratic stage.
8. **LIN proxy triage: N/A.** b39–b46 precedent: DIFF-only triage for rotation
   cascades; the S1 LIN family gates escalation, not the screen.

## Cost bar
Strictly **<19.3u MEASURED** via run_synth.py, XCHECK clean — the live
frontier is hyb28_mu5_324 19.3u (ref mul64 103.5u).

## Pipeline (b33 playbook + the two hard lessons)
1. Calibration: and1/b33c must reproduce z=3.3 (fail-loud; run `calibrate`
   first — harness untrusted otherwise).
2. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys, sequential
   inputs N=2^18, KEEP bar max|z|<10. Keeps appended to JSONL per-try (b39
   lesson). Fail-loud draw-loop cap 10000 (b45 lesson). Duplicate stage-tuples
   re-drawn (b41 precedent). Draw asserts: chi stages a!=b (else linear layer
   = identity); maj stages a,b,c pairwise distinct (else maj degenerates —
   `maj(ra,ra,rb) = ra`, linear).
3. S0: STRATIFIED sample of keeps (span the z range), bar strictly <19.3u
   MEASURED, XCHECK clean (**lesson a**: triage z does not rank S0 cost
   within a form — do NOT S0 only the best-z).
4. S1 FAIL-FAST on the first cost-eligible keep (**lesson b**: exact-DIFF
   triage is blind to the S1 marginal/inner-DIFF kill — do not batch all S0s
   first).
5. Survivors → staged battery S1→S2→S3→S4→Q1 (round13/q1_sacbic.py).

## Pre-registered verdict rules
- chi3S-3 0/40 with min in the hundreds (the b43/b44/b46 signature) →
  **dense wall sits at 4 stages for chi_3**; arm closed, scoped to the tested
  construction (3-stage chi_3-lane masked cascade + pre-whiten + rotl(k,13)).
- chi5S-3 0/40 while chi3S-3 keeps → dense-wall location is lane-width
  sensitive; close chi_5-lane stage form scoped.
- maj3S-3 0/40 with killkey-0x0 dominance → zero-corner discriminator
  CONFIRMED (mechanism data for the b45 finding); arm closed scoped.
- Any arm with ≥1 KEEP → bundle gen bit-exact 2000/2000 → S0 stratified →
  b33 playbook. A chi3S-3 keep at measured <19.3u is a FRONTIER CHALLENGER.
- All arms dead → the "fewer, fatter stages" hypothesis is FALSIFIED for the
  tested dense primitives; next axis per the widen directive (never stop
  silently).

## Draw constraints (fail-loud asserts)
- chi stage rotations (a,b) drawn 1..63, a!=b.
- maj stage rotations (a,b,c,d) drawn 1..63, a,b,c pairwise distinct
  (maj-degeneracy guard); d free.
- Duplicate (type, rotations) stage-tuples re-drawn within a try.
- Seeds: chi3S-3 0xB471, chi5S-3 0xB472, maj3S-3 0xB473 (batch-47 block).
