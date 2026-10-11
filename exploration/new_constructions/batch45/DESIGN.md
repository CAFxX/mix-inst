# Batch-45 design note — true chi S-box as the repeated STAGE (track 6, 2026-10-11)

**Status: PILOT LAUNCHED** (track-6 supervisor incarnation XV).
Trigger: batch-44 COMPLETED 2026-10-11T10:15:06Z — andorM5 0/40
(dual-tap does NOT breach the 5-stage wall), andorM6 2/40 quality-ok but
S0 cost-killed 22.0/22.9u. Sparse secondary-gate space FULLY MAPPED per
the XIV adjudication. The next lever must be elsewhere.

## The two hard findings this axis must respect
1. **The 5-stage wall is SEQUENTIAL NONLINEAR DEPTH, not tap count**
   (b44: andorM5's dual nonlinear taps died with the b43 signature,
   min 195.8 — the discriminating experiment against the tap-count
   hypothesis).
2. **6-stage quality-ok forms are cost-closed**: the OR-mask measured
   3.67u/stage, not the projected ~3.3u — it does not fuse into the XOR
   tree. A 6-stage challenger needs <3.22u/stage (19.3/6); none of the 6
   measured sparse forms gets there.

## Axis
True Keccak chi S-box (degree-2, DU-optimal 2^-2, bijective at odd
width, EVERY output bit nonlinearly active) as the REPEATED STAGE
FUNCTION of a masked cascade — not fused, not final:

```
stage(x, a, b) = chi3(x) ^ rotl(chi3(x), a) ^ rotl(chi3(x), b)
```

chi3 = chi_3 on 21 contiguous 3-bit lanes (bits 0..62), bit 63 identity
— the exact b42 lane geometry (`_chi_scalar(v,3)` LUT, bijectivity
asserted fail-loud). Pre-whiten `x ^= k`; final `x ^= rotl(k,13)`
(same frame as b33c/b41/b43/b44 for comparability).

Two arms:
- **chiS-4**: 4 stages (prize arm — cost thesis live, see below)
- **chiS-5**: 5 stages (mechanism probe — direct 5-stage-wall challenger
  for dense degree-2; cost-doomed vs 19.3u at ~5×4.5u, but a strong
  triage keep reframes the wall and triggers cost-engineering follow-ups)

## Co-design rationale
The wall is nonlinear DEPTH. Sparse AND stages contribute depth only
through the AND corner — on sparse inputs the nonlinear term vanishes
(killkey 0x0 dominates every killed arm) and the stage is effectively
linear. A chi stage has NO sparse corner: every output bit is
nonlinearly active on every input (dense degree-2). Per stage of
sequential nonlinear depth, the chi stage carries strictly more
effective nonlinearity than a sparse AND stage — this is the lever the
tap-count experiment (b44) could not pull, because it stayed inside the
sparse-gate family.

Cost thesis (gate-count, measured S0 decides): per bit, the chi stage
is 1×AND2 + 3×XOR2 + 1×INV vs the frontier stage's 1×AND2 + 2×XOR2
(measured 3.3u/stage). The delta is one XOR2 + one INV per bit —
projected ~4.3–4.8u/stage. 4 stages ≈ 17–19u: plausibly under the
<19.3u bar; 5 stages ≈ 21.5–24u: over bar (mechanism probe only).
The 6-stage cost wall is dodged by using FEWER stages, not cheaper ones.

**Falsifier:** 0/40 on chiS-5 with mins in the hundreds (the b43/b44
signature) → dense degree-2 does NOT breach the 5-stage wall either;
the wall needs degree>2 per stage or 6 stages; close scoped. If chiS-4
keeps but chiS-5 dies → the wall moved 6→5 for dense S-boxes on the
quality axis (advance even before cost). If chiS-4 keeps AND measures
<19.3u → frontier challenger, b33 playbook.

## De-dup (grep-verified 2026-10-11)
- b42 chi3lanes/chi5lanes: TRUE chi S-box but as a SINGLE FINAL layer
  on a 5-stage AND cascade (quality-killed 0/40, min 40–61) — position
  is final, not repeated stage. Different construction.
- b8 t6_fchi6a (`x ^ (ra & ~rb)`, fused, per-stage rk): SPARSE masked
  form, not the 3-input S-box; S1-killed (z 47k–160k) regardless.
- b8 t6_het5a: 5-stage hetero incl. sparse "chi" op
  `r0 ^ (r1 & ~r2)` + per-stage round key; S0 25.2u (5.0u/stage)
  cost-dominated. Different op AND different key schedule.
- b4 t6_chi3col8/10: chi_3 as the ROUND function of an 8–10 round full
  cipher with key schedule — different construction + cost class
  (S0 43.3u cost-killed).
- b3 ascon5: 5-bit S-box full cipher — different.
- directed_design batch 9 "keccak" flavor:
  `x ^ (rotl(x,a) & ~rotl(x,b)) ^ rotl(x,c)` — SPARSE masked form (AND
  with one inverted input), not the 3-input S-box. Different function.
- fused fz24_c/f (`(~ra & rb)` "Keccak-chi term") and fz24_o family:
  sparse terms — different function.
- fused fz24_g/h (gen_fused24.py): per-NIBBLE (4-bit) chi
  `y[4n+i] = x[4n+i] ^ (~x[4n+(i+1)%4] & x[4n+(i+2)%4])`, 5-stage with
  fixed lin rots — the closest relative (true chi S-box as a repeated
  layer). NEVER SCREENED (zero hits in supervisor.log / wave24*.log;
  the generator comment "Nobody has tested this primitive" stands).
  Different in three co-designed respects: (1) lane width 4 vs 3 —
  chi_4 is PROVABLY non-bijective (16→12, b42 proof; the batch-31
  catastrophe mechanism), chi_3 is bijective; (2) stage wiring: my
  linear layer is a randomized 2-rotation XOR per stage, theirs fixed
  lin rots; (3) triage: exact-DIFF randomized-schedule screen vs
  never-run. fz24_g/h stay OPEN as a follow-up (with the bijectivity
  caveat recorded), not a duplicate.
- No batch (19–44) screened a true chi S-box as the repeated stage of
  a masked cascade (pre-whiten + final whiten, no per-stage rk).

## Cuts recorded (defensible reason at each cut site)
1. **chi_5 lanes as stage: CUT from pilot, not killed.** Reason:
   lane width is a follow-up variable, not the pilot question — the
   pilot answers dense-S-box/stage-count with chi_3 (b42's lane
   comparison chi_5 > chi_3 was as FINAL; as stage it is untested).
   Re-test trigger: any chiS KEEP → chi_5-lane stage arm next.
2. **6 stages: CUT on measured cost.** 6 × ~4.5u ≈ 27u > 19.3u. The
   quality question at 6st is settled (sparse forms keep); the open
   questions are quality-at-≤5 and cost.
3. **3 stages: CUT.** Structurally below the wall — 4st sparse is dead
   three ways (fz16_a catastrophic S1 FLAG; xc4a / dual4a S1-killed) +
   b34 d2a3@4st 0/200; 3st is weaker still. No mechanism proposed.
4. **Per-stage round key (b8 style): CUT on measured cost.** b8's
   rk-bearing hetero measured 5.0u/stage (cost-dominated); the no-rk
   masked cascade is the cheaper wiring and keeps the b33c/b44
   comparability frame.
5. **Fused form `x = chi(x,ra,rb)` (x entering nonlinearly): CUT on
   evidence.** b8's fused chi was S1-killed at z 47k–160k; the
   masked-cascade wiring (`x ^=`) is the quality-proven one (b33c, 324).
6. **Hetero chi+AND interleave: CUT from pilot, queued as follow-up.**
   Reason: it muddies the mechanism — the pilot must isolate whether
   DENSE stages alone breach the wall. Re-test trigger: chiS-5 keeps
   (quality proven, cost-doomed) → hetero interleave as the cost
   engineering follow-up (≈2×4.5+2×3.3 ≈ 15.6u/4st projected).
7. **LIN proxy triage: N/A.** b39/b40/b41/b44 precedent: DIFF-only
   triage for rotation cascades; the S1 LIN family gates escalation.

## Cost bar
Strictly **<19.3u MEASURED** via run_synth.py, XCHECK clean — the live
frontier is hyb28_mu5_324 19.3u.

## Pipeline (b33 playbook + the two hard lessons)
1. Triage: exact S1 DIFF (`lin_diff.diff_cell_logps`), 10 keys,
   sequential inputs N=2^18, KEEP bar max|z|<10. Positive control:
   and1/b33c → z=3.3 (fail-loud; run `calibrate` first). Keeps appended
   to JSONL per-try (b39 lesson).
2. S0: STRATIFIED sample of keeps (span the z range), bar strictly
   <19.3u MEASURED, XCHECK clean (lesson a: triage z does not rank S0).
3. S1 FAIL-FAST on the first cost-eligible keep (lesson b: exact-DIFF
   triage is blind to the marginal/inner-DIFF kills — do not batch all
   S0s first).
4. Survivors → staged battery S1→S2→S3→S4→Q1 (round13/q1_sacbic.py).

## Pre-registered kill rule
0/40 keeps on an arm with min orders of magnitude above bar → arm
closed, mechanism refuted for that stage count (scoped to the tested
construction: 4/5-stage chi_3-lane masked cascade + rotl(k,13)).
Both arms dead → the dense-S-box-stage hypothesis is FALSIFIED; next
axis per the widen directive (never stop silently).

## Draw constraints (fail-loud asserts)
`a == b` degenerates the linear layer to identity (excluded); rotations
drawn 1..63 (b43/b44 convention). Duplicate stage-tuples re-drawn
(b41 precedent).
