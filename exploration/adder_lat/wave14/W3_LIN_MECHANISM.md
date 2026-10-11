# W3 S1-LIN kill — structural mechanism (Sequential Affinity Collapse)

Found 2026-10-11 ~22:45 CEST by track-3 supervisor. All four W3 bundles
(al_w3a/b/c/d) S1-LIN-killed (rej 9-10/10, D=4096/4096, logp=-inf on all keys).

## The mechanism

The W3 AND layer is g(x) = x ^ (rotl(x,a) & rotl(x,b)).

**Lemma (Sequential Affinity).** On any block of 64 consecutive inputs, g is
AFFINE iff (b−a) mod 64 ∉ {0,1,2,3,4,5,59,60,61,62,63}.

*Proof.* On a 64-block exactly 6 input bits vary (bits 0–5, up to affine
shift). Output bit i of the AND term is x_{i−a}·x_{i−b} — quadratic iff both
(i−a),(i−b) are varying, i.e. iff intervals [a,a+5],[b,b+5] (mod 64)
intersect, i.e. iff (b−a) mod 64 ∈ {−5..5}. With no quadratic terms the AND
is affine, hence g is affine. ∎

*Empirical:* 24/24 random (a,b) pairs confirm — d∈{6..58} → rank stays 7
(affine); d∈{0..5,59..63} → rank 8–12 (genuinely quadratic). Script:
/tmp/w3lin/sweep_ab.py (ephemeral; logic reproduced below).

Since the GF(2^64) layer and key XORs are LINEAR, a sequentially-affine AND
contributes ZERO nonlinearity against S1-LIN's sequential gate.

## Per-bundle rank evolution (64 sequential outputs, key fixed)

- al_w3a: 7 →7 [AND(52,26) d=38 affine] →7 →22 [AND(19,44) d=25]
          →22 →57 [AND(9,54) d=45] →57. 1 leading affine AND.
- al_w3b: 7 →7 [d=52] →7 [d=56] →7 →22 [d=54] →57 [d=59] →57. 2 affine.
- al_w3c: 7 →7 [d=48] →7 [d=14] →7 →22 [d=21] →57 [d=62] →57. 2 affine.
- al_w3d: 7 →12 [d=1, 5 quadratic terms] →12 →44 [d=4, 2 terms] →44. 0 affine.

S1-LIN needs rank ≥ 62 (D counts rank ≤ 61). All four stall at 44–57.

## The deeper fact (decisive experiment)

Varying stage count with the SAME W3 form:
- all ANDs non-affine (d∈{1..4}): 2st → rank 44 (FAIL); 3st → 63 (PASS); 4st → 63.
- first AND affine (d=38), rest non-affine: 2st → 22; 3st → 57 (FAIL); 4st → 63.

So the form is NOT LIN-doomed — it is a nonlinearity-BUDGET issue:
3 effective (non-affine) stages suffice; 2 do not. A leading affine AND
costs one full stage of budget.

## Co-designed W3' (validated, not yet screened at scale)

1. **Anti-affinity constraint:** every (a,b) has d=(b−a) mod 64 ∈
   {1,2,3,4,5,59,60,61,62,63} — every AND genuinely quadratic on sequential
   inputs; the mechanism cannot recur BY CONSTRUCTION.
2. **3 stages** (2 ANDs/stage is fine): measured rank 63 > 61 on sequential
   64-blocks.
3. **DIFF smoke:** 3 d-constrained 3-stage schedules → seq z = 2.7/3.0/3.0
   (< 10 KEEP bar). Small-d ANDs do not hurt DIFF — GF(2^64) carries diffusion.
4. **Cost thesis:** 3st × ~18u ≈ 53–54u < 123.4u adder-like bar. ✓

Next experiment (triage spec, NOT launched): re-screen W3 with the
d-constraint enforced at schedule generation (reject d∉{1..5,59..63}),
3 stages, 2 ANDs/stage, exact-DIFF triage (bar z<10 seq) + the new
sequential-affinity pre-check (assert no AND affine) + rank probe
(assert 64-block rank ≥ 62) BEFORE S0. Survivors → S0 (<123.4u) → staged
battery S1→S4+Q1 (b33 playbook).

## Evidence paths

- S1 kills: fast_battery/results/al_w3{a,b,c,d}/s1_result.json (lin_detail)
- Bundle models: fast_battery/candidates/al_w3*/model.py
- Schedules: wave14/gen_wave14.py CANDS
- Rank evolution + (a,b) sweep + deeper-stage experiment: /tmp/w3lin/*.py
  (ephemeral; key numbers recorded here)
