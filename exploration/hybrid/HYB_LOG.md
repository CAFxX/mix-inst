# Hybridization Log

## Batch 1 (2026-10-07)

### hyb_rasc20_p22c_lin513_nw
- Components: rasC2_0 S-box + r22c P-box (5i+27) + lin(5,13)
- S0: 26.2u / 5,542 cells — NEW SPEED POINT (faster than 26.4u frontier)
- S1: FLAG (LIN PASS, DIFF PASS, marginal PB rej=0 RD rej=0, but verdict FLAG not CAL_PASS)
- S2: Formal PASS (repeats ≤ 10) but max|z|=812.9 — SEVERE differential spikes
- Verdict: FRONTIER-DEAD. The r22c P-box does not co-diffuse with (5,13) linear.
- Lesson: P-box and linear layer must be co-designed; naive component swap fails.

### hyb_rasc20_p22c_lin311_nw
- Components: rasC2_0 S-box + r22c P-box + lin(3,11)
- S0: 26.6u / 5,355 — slower than frontier, dominated. Not pursued.

### hyb_s1_pba19_lin513_nw
- Components: S1 S-box + pba19 P-box + lin(5,13)
- S0: 27.9u — dominated. Not pursued.

### hyb_rasc20_pba19_lin815_nw
- Components: rasC2_0 S-box + pba19 P-box + lin(8,15)
- S0: 26.6u / 5,155 cells — 0.2u slower than (5,13) but 230 cells smaller
- S1: CAL_PASS (clean)
- S2: pending

### hyb_rasc20_pba19_lin815_nw (update)
- S2: **KILL** — 6 deltas with repeats > 10 (threshold 10). Max|z|=336.1.
- Verdict: DEAD. (8,15) linear does not co-diffuse with pba19 P-box despite analytical tie with (5,13).
- Lesson: Analytical branch/spread metrics do NOT predict empirical S2. The (5,13)+pba19 combination is special.

## Batch 1 Conclusions (2026-10-07)
1. Naive component swapping FAILS. P-box + linear must be co-designed/tested together.
2. The (5,13) + pba19 + rasC2_0 combination is a delicate optimum — changing any component breaks diffusion.
3. Next: Keep the proven (5,13)+pba19 core, hybridize the S-BOX (the untested axis).

## Batch 2 (2026-10-07): S-box swaps in proven (5,13)+pba19 core

### hyb_midori0_pba19_lin513_nw
- S0: 27.7u / 4,944 cells. Slower than 26.4u frontier (+1.3u), but 441 cells smaller.
- Not a speed point. Size tradeoff vs r22c (28.3u/4,656) is marginal.
- Not pursued beyond S0.

### hyb_midori1_pba19_lin513_nw
- S0: 28.2u. Dominated. Not pursued.

### hyb_present_pba19_lin513_nw
- S0: 33.4u. Dominated. Not pursued.

### hyb_skinny_pba19_lin513_nw
- S0: 31.2u. Dominated. Not pursued.

## Batch 2 Conclusions
1. S-box standalone depth (Midori Sb0: 3.0u) does NOT predict full-construction speed (27.7u vs rasC2_0's 26.4u).
2. The rasC2_0 S-box is well-matched to the (5,13)+pba19 construction.
3. Next: Try systematic P-box variations with (5,13), or different structures entirely.

## Batch 3 (2026-10-07): CO-DESIGN — P-boxes optimized FOR lin(5,13)

User directive: "don't just blindly swap components, but swap and coadjust the design."

Method: Fixed lin(5,13) + rasC2_0, swept affine P-boxes P(i)=(a*i+b)%64 for S0 speed, then S1/S2 on the fast ones. Co-design = choose the P-box FOR the linear layer, not independent of it.

### Pilot S0 (8 affine P-boxes, lin(5,13) fixed)

| P-box (a,b) | S0 delay | Cells | Note |
|---|---|---|---|
| (5,27) p22c | 26.2u | 5,542 | prior blind swap; S2 BROKEN (\|z\|=813) |
| (27,1) | 26.2u | 5,609 | NEW |
| (21,7) | 26.3u | 5,447 | NEW |
| (13,5) | 26.3u | 5,266 | NEW |
| (19,1) pba19 | 26.4u | 5,588 | frontier baseline |
| (23,1) | 26.4u | 5,649 | — |
| (11,3) | 26.4u | 5,560 | — |
| (17,17) | 26.5u | 5,214 | — |

### S1/S2 on the three fast unknowns

- **cd1_p_a27b1_l513_nw** (27,1): S0 26.2u, S1 CAL_PASS, **S2 PASS** (max_repeats=0, max|z|=20.0, all 115 deltas)
- **cd1_p_a21b7_l513_nw** (21,7): S0 26.3u, S1 CAL_PASS, **S2 PASS** (max_repeats=0, max|z|=12.6, all 115 deltas)
- **cd1_p_a13b5_l513_nw** (13,5): S0 26.3u, S1 CAL_PASS, **S2 PASS** (max_repeats=0, max|z|=246.9) — formal pass but weak; not pursued

### Batch 3 Conclusions
1. **Co-design WORKS.** Blind p22c swap: 26.2u but |z|=813 (dead). Co-designed (27,1): 26.2u with |z|=20.0 (alive). Same speed, opposite diffusion — the P-box must be chosen FOR the linear layer.
2. **Two new challengers**: a27b1 (26.2u, |z|=20.0) and a21b7 (26.3u, |z|=12.6) both beat the 26.4u frontier on S0 and pass S1/S2. a21b7 has the cleanest differential profile of any (5,13) variant measured (|z|=12.6 vs frontier's 25.1).
3. a13b5 is a formal S2 pass but |z|=246.9 signals weak co-diffusion — excluded from follow-up.
4. Next: S3/S4/Q1 for a27b1 and a21b7 (needs parent prioritization vs other tracks).

## Batch 4 (2026-10-07): CO-DESIGN round 2 — systematic (a,b) sweep, two fronts

Method: fixed rasC2_0 S-box; affine P-boxes P(i)=(a*i+b)%64 co-designed FOR the
linear layer via a new analytical prior: **lin-trail metric** =
min-over-single-bit-output-masks of the 4-round backward active-S-box count
(mu -> L^T(mu) = mu^R^{-ra}mu^R^{-rb}mu, cost = active nibbles of L^T(mu) per
round, mu := P^{-1}(L^T(mu))). Validation on batch 3 (lin(5,13)): p22c
S2-killer (|z|=813): 29 < a13b5 weak-pass (|z|=246.9): 31 < a27b1 pass
(|z|=20.0): 33 < pba19 frontier (|z|=25.1): 34 < a21b7 cleanest (|z|=12.6):
38 — monotone vs measured S2 |z|. Prior only; S1/S2 decide. Screener:
hybrid/codesign/lin_trail.py; rankings: codesign/lintrail_{513,311}.txt.

S1 cutoff for batch 4: S0 <= 26.3u (batch-3 "fast unknown" practice; the 26.4u
frontier point stands — dominated candidates are not worth the ~13min S1).

### FRONT 1: lin(5,13), top lin-trail tier (a=43:39, 53:39, 21:38-39, 29:37-38, 35:37, 3:35-37, 61:35-36), b in each a's top-min group

| P-box (a,b) | S0 delay | Cells | lin-trail min | S1 | S2 |
|---|---|---|---|---|---|
| (43,1) | 26.6u | 5,384 | 39 | — (dominated, skip) | — |
| (43,7) | 26.3u | 5,471 | 39 | **CAL_PASS** (LIN/DIFF PASS, PB=0 RD=0) | QUEUED |
| (53,1) | 26.3u | 5,557 | 39 | QUEUED* | — |
| (53,7) | 26.4u | 5,423 | 39 | — (tie, ≤26.3u cutoff) | — |
| (21,1) | 26.4u | 5,264 | 38–39 | — (tie, ≤26.3u cutoff) | — |
| (21,5) | 26.9u | 4,770 | 38–39 | — (dominated, skip) | — |
| (29,1) | 26.5u | 5,342 | 37–38 | — (dominated, skip) | — |
| (35,7) | 26.4u | 5,229 | 37 | — (tie, ≤26.3u cutoff) | — |
| (3,7) | **26.2u** | 5,513 | 35–37 | S1 NEEDED (speed-point challenger, ties a27b1) | — |
| (61,1) | 26.3u | 5,611 | 35–36 | QUEUED (S1 rest-batch) | — |

\* (43,7)'s wrapper S1 printed rc=0 but wrote no s1_result.json and no summary lines (rc was tail's, not s1_screen's) — re-running in the rest-batch. S1 for (53,1) = **FLAG** (LIN PASS, DIFF rej=1, worst|z|=4.1) — per batch-1 precedent, goes to S2 to measure the true differential profile before a co-design verdict.

### FRONT 2: lin(3,11) — all 20 S0 done (S0 driver finished; wrapper printed BATCH4_RESUME_ALLDONE)

| P-box (a,b) | S0 delay | Cells | lin-trail min | S1 | S2 |
|---|---|---|---|---|---|
| (11,7) | 26.2u | 5,451 | 36–38 | QUEUED (S1 rest-batch) | — |
| (11,3) | 26.3u | 5,538 | 36–38 | QUEUED | — |
| (3,1) | **26.1u** | 5,388 | 35–37 | QUEUED — **new fastest of batch 4** | — |
| (3,5) | 26.6u | 4,998 | 35–37 | — (dominated, skip) | — |
| (53,1) | 26.3u | 5,340 | 36–37 | QUEUED | — |
| (53,2) | 26.3u | 5,354 | 36–37 | QUEUED | — |
| (61,1) | 26.3u | 5,110 | 34–37 | QUEUED | — |
| (9,1) | 26.3u | 5,342 | 34–35 | QUEUED | — |
| (29,2) | 26.5u | 5,505 | 34–36 | — (dominated, skip) | — |
| (21,1) | 26.4u | 5,289 | 33–34 | — (tie, ≤26.3u cutoff) | — |

### FRONT 2: lin(3,11) (never co-designed), top lin-trail tier (a=11:36-38, 3:35-37, 53:36-37, 61:34-37, 9:34-35, 29:34-36, 21/35/43:33-34)

(pending S0 completion)

## Batch 5 (2026-10-08): CO-DESIGN — P-box augmented chi/AND cascades

User directive: co-design al_ family with SPN elements; P-box chosen FOR the cascade.

Method: chi_pbox_diffuse.py — bit-dependency spread through cascaded chi/AND
stages with inter-stage P-box. Metric: min_dep(3) - max_gap(3), bigger=better.
Key finding: **pba19 (a=19) scores 18, WORSE than no-P-box baseline (29)** for
AND-cascade. The frontier SPN P-box is actively harmful here — quantitative
proof that P-boxes must be co-designed FOR the construction, not reused.
Top tier: a=43 (42), a=27 (41), a=11 (41). b-parameter irrelevant (rotation).

Metric limitation (honest): cannot distinguish chi6 vs chi8 schedules at equal
stage counts (dependency saturates at 5 stages; S2 quality needs stage COUNT).
Weak prior only; S1/S2 decide.

Candidates (all bit-exact C/Python/Verilog verified):
| Candidate | Base | P-box | Stages | Note |
|---|---|---|---|---|
| hyb5_chi8_p43 | al_chi8 | (43,1) | 8 | metric top |
| hyb5_chi8_p27 | al_chi8 | (27,1) | 8 | metric top |
| hyb5_chi8_p19 | al_chi8 | (19,1) | 8 | NEGATIVE CONTROL |
| hyb5_casc8_p43 | al_cascad | (43,1) | 8 | metric top |
| hyb5_chi6_p43 | al_chi8[:6] | (43,1) | 6 | reduced, P-box compensates? |
| hyb5_casc6_p43 | al_cascad[:6] | (43,1) | 6 | reduced, P-box compensates? |

S0 running (nice-19 sequential, VM load high).

## Batch 6 (2026-10-09): CO-DESIGN — P-box FOR al_and6a's rotation schedule

Supervisor restart (previous died ~5h ago; nobody said to stop).

**Co-design mismatch found in batch 5**: the 6-stage variants (hyb5_chi6_p43,
hyb5_casc6_p43) used al_cascad triplets [(1,8,2),(3,11,5),...], NOT al_and6a's
[(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)]. The P-box was
selected for the wrong schedule. (hyb5_chi6_p43 used CHI8[:6] which includes
(13,5,17) at stage 4; al_and6a skips that stage.)

**Re-ran chi_pbox_diffuse.py FOR al_and6a's exact 6-stage schedule**:
- No P-box baseline: score=29
- P=(37,x): score=43 (NEW top pick)
- P=(43,x): score=42 (old pick, still good)
- P=(27,x): score=41
- P=(45,x): score=16 (worse than baseline — avoid)
- b-parameter irrelevant (all b give same score per a)

**Candidates** (all bit-exact C/Python/Verilog verified):
| Candidate | Stages | P-box | Metric | Note |
|---|---|---|---|---|
| hyb6_and6a_p37 | 6 (al_and6a exact) | (37,1) | 43 | metric top pick |
| hyb6_and6a_p43 | 6 (al_and6a exact) | (43,1) | 42 | control |
| hyb6_and5_p37 | 5 (first 5) | (37,1) | — | speed challenger |

Generator: hybrid/codesign/gen_batch6.py (includes rtl_top in meta.json).
S0 running.

### Batch 6 S0 results (2026-10-09)
| Candidate | Delay | Cells | vs frontier |
|---|---|---|---|
| hyb6_and6a_p37 | 20.1u | 6,017 | TIES al_and6a (20.1u) |
| hyb6_and6a_p43 | 20.1u | 6,148 | TIES al_and6a (20.1u) |
| hyb6_and5_p37 | **17.2u** | 5,004 | **2.9u FASTER** |

All XCHECK pass (analyze.py == analyze2.py). P-box added zero delay (pure wiring).
S1 running on all three.

### Batch 6 S1 results (2026-10-09) — ALL FLAGGED
| Candidate | S0 | S1 | Detail |
|---|---|---|---|
| hyb6_and6a_p37 | 20.1u | **FLAG** | DIFF rej=6, worst|z|=18.5 |
| hyb6_and6a_p43 | 20.1u | **FLAG** | DIFF rej=2, worst|z|=7.9 |
| hyb6_and5_p37 | 17.2u | **FLAG** | LIN rej=2, DIFF rej=10, worst|z|=1443.4 (catastrophic) |

**KEY FINDING**: Inter-stage P-boxes HURT the al_and6a construction. The
rotation triplets are a delicate sequence co-design — inserting a permutation
between stages disrupts the diffusion pattern and CREATES linear/differential
weaknesses (the P-box is linear; it re-aligns bits to form multi-stage trails).

The chi_pbox_diffuse.py metric is MISLEADING here: it predicted P(37,1) would
help (score 43 vs 29 baseline) because it measures dependency SPREAD, not
statistical quality. Spread ≠ security.

**Scoped verdict**: P-box BETWEEN al_and6a stages is a dead end. The triplets
must be treated as an inseparable sequence.

**Next**: Try P-box AFTER all stages (final diffusion layer, doesn't disrupt
inter-stage co-design). Or co-design triplets+P-box jointly from scratch.

## Batch 7 (2026-10-09): 3-input AND cascade

**Rationale**: Batch-6 proved inter-stage P-box hurts al_and6a triplets. New
direction: stronger per-stage nonlinearity (algebraic degree 3 vs 2) so fewer
stages suffice. 3-input AND: `x ^= (ra & rb & rc) ^ rd`.

**Candidates**:
| Candidate | Stages | Structure |
|---|---|---|
| hyb7_and3_5 | 5 | 3-input AND, quads from al_and6a triplets + spread 4th rot |
| hyb7_and3_6 | 6 | 3-input AND (control) |

Generator: hybrid/codesign/gen_batch7.py. Bit-exact verified (100 vecs).
S0 running.

### Batch 7 S0 results (2026-10-09)
| Candidate | Delay | Cells | vs frontier |
|---|---|---|---|
| hyb7_and3_5 | **19.8u** | 3,781 | **0.3u FASTER than al_and6a** |
| hyb7_and3_6 | 23.2u | 4,255 | slower (overkill) |

S1 running on hyb7_and3_5.

### Batch 7 S1 results (2026-10-09)
| Candidate | S0 | S1 |
|---|---|---|
| hyb7_and3_5 | 19.8u | **FLAG** (LIN rej=2, DIFF rej=10) |
| hyb7_and3_6 | 23.2u | — (slower than frontier, skip S1) |

**Finding**: 3-input AND still needs 6 stages. 5 stages insufficient regardless
of per-stage strength. The 6-stage depth is necessary for this family.

**Next (batch-8)**: Single P-box at cascade MIDPOINT (between stage 3 and 4),
not between every stage. Preserves intra-block triplet co-design.

### Batch 8 S1 results (2026-10-09)
| Candidate | S0 | S1 |
|---|---|---|
| hyb8_midp37 | 20.1u | **FLAG** (DIFF rej=3) |

**CONFIRMED**: Even a SINGLE P-box at the midpoint hurts al_and6a triplets.
The sequence co-design is fragile — any inter-stage permutation disrupts it.

**P-box direction: EXHAUSTED** (4 candidates, all FLAG).
- Between every stage: FLAG (batch-6, 3 cands)
- At midpoint only: FLAG (batch-8, 1 cand)
- No P-box: PASS (al_and6a)

**Pivot (batch-9)**: Different nonlinear op. Try MAJ3: `x ^= maj(ra,rb,rc)`
where maj(a,b,c)=(a&b)|(b&c)|(a&c). Same degree as AND but different function.

### Batch 9 S0 (2026-10-09)
| Candidate | S0 |
|---|---|
| hyb9_maj3_6 | 25.8u (too slow, skip S1) |

MAJ3 (3 ANDs + 2 ORs) is more expensive than single AND. Direction dead.

**New idea (batch-10)**: Restructure stage for parallelism.
Current: `x ^= (ra & rb) ^ rc` = AND(1u) -> XOR(1u) -> XOR(1u) = 3u/stage
New: `x ^= ra ^ (rb & rc)` = [XOR(ra) || AND(rb,rc)](1u) -> XOR(1u) = 2u/stage
6 stages x 2u = 12u + overhead. Target ~15u.

### Batch 10 S0 (2026-10-09)
| Candidate | S0 | Structure |
|---|---|---|
| hyb10_xorand_6 | **19.8u** | `x ^= ra ^ (rb & rc)` (parallel) |

**0.3u faster than al_and6a!** The restructured stage (XOR and AND in parallel,
then final XOR) saves 1 gate level per stage. S1 running.

### Batch 10 S1 (2026-10-09)
| Candidate | S0 | S1 |
|---|---|---|
| hyb10_xorand_6 | 19.8u | **FLAG** (LIN rej=2, DIFF rej=2) |

**FINDING**: The restructured `x ^= ra ^ (rb & rc)` is faster (2u/stage) but
creates a linear trail via the `ra` term (D=252/4096 on key=0). The 3u/stage
`x ^= (ra & rb) ^ rc` structure is NECESSARY — the AND must cover the linear
terms. Parallelism and security are in tension here.

**Track 5 summary (2026-10-09 supervisor restart)**:
- Batch-6 (P-box for al_and6a): 3 cands, ALL S1 FLAG. P-box hurts.
- Batch-7 (3-input AND): 5-stage FLAG, 6-stage too slow (23.2u).
- Batch-8 (mid-P-box): S1 FLAG. P-box direction exhausted.
- Batch-9 (MAJ3): 25.8u, too slow.
- Batch-10 (XOR-AND restructure): 19.8u but S1 FLAG (linear trail).

**Conclusion**: al_and6a (20.1u, 6-stage `x ^= (ra&rb)^rc`) is at a strong local
optimum. The 3u/stage structure is load-bearing for security. Beating 20.1u
requires a fundamentally different construction, not tweaks to this family.

## Batch 11 (2026-10-09): final diffusion layer + 5B/5C reconstruction (respawn)

Supervisor respawn after ~20:35Z VM reboot. Findings summary written to
`hybrid/FINDINGS_SUMMARY.md`. Two directions launched:

**DIR 1 — final diffusion layer** (the one placement batch-6 never tried):
P-box AFTER all stages, not between them. Does not disrupt inter-stage
triplet co-design.

| Candidate | S0 | Structure |
|---|---|---|
| hyb11_and5_finalPL | **19.9u** / 5,544 cells | 5-stage al_and6a triplets + final P(37,1) + L(5,13). **Beats 20.1u frontier by 0.2u** |
| hyb11_and6_finalPL | 23.0u / 6,740 cells | 6-stage + final P(37,1) + L(5,13) (control: does final layer break quality?) |

All XCHECK pass (analyze.py == analyze2.py). Bit-exact: model vs C 5/5 vecs,
RTL vs model 16/16, meta goldens match, rtl_top present.

**DIR 2 — 5B/5C reconstruction** (lost in a restart; redesigned):
4-round SPN skeleton from proven batch-3 core (rk[i]=rotl(k,13*(i+1))^RC[i]),
nonlinear layer = 64-bit cascade stage (NOT a 4-bit S-box — the prototyped
y_i=x_i^(literal&literal) AND-S-box hits ddt=16 structurally across the full
1.68M literal-AND space; documented in FINDINGS_SUMMARY.md).

| Candidate | S0 | Structure |
|---|---|---|
| hyb11b_andSPN_p27 | 28.8u | AND-stage NL (1,2,13), P(27,1), L(5,13) — 5B |
| hyb11c_chiSPN_p27 | 28.7u | chi-stage NL (1,2,13), P(27,1), L(5,13) — 5C, SPN pick |
| hyb11c_chiSPN_p43 | 29.4u | chi-stage NL (1,2,13), P(43,1), L(5,13) — 5C, chi-metric pick |

Dominated on speed (SPN-class ~29u) but NEW axes (first AND/chi NL in the SPN
skeleton) — quality science, submitted for S1/S2 alongside.

**GHA**: campaign `hyb11-s1s2-20261009` (5 shards, stages s1,s2,
priority=frontier-challengers), bundles pushed as repo commit `148a5e3a`,
VERIFIED PRESENT 21/21 via API tree read. Generator:
`hybrid/codesign/gen_batch11.py`.

## Batch 12 (2026-10-10): heterogeneous AND/S-box cascade (respawn after 00:57Z reboot)

Supervisor respawn ~01:05Z (VM rebooted 00:57Z, nobody said stop). Batch-11 verdicts
confirmed from ledger (and5_finalPL 19.9u S1-FLAG dead; other 4 S1 CAL_PASS+S2 PASS,
dominated). Pivot per brief: fundamentally different hybrid family — S-box+AND
co-design, not P-boxes in al_and6a.

**Thesis**: the 5-stage AND cascade dies on DIFF (batch-7, batch-11/and5_finalPL).
A 4-bit S-box layer (rasC2_0 — proven S2-clean in cd2 batch-4, algebraic degree 3,
max DDT 4) adds a full layer of degree-3 nonlinearity in ~3.5u, where batch-11's
P-box final layer added zero differential strength and failed. Co-design: the AND
stages' rotations are free wiring — placing the S-box AFTER/AMONG AND stages lets
the surrounding triplets diffuse the S-box nibbles (rotation schedule does double
duty).

| Candidate | S0 | Structure |
|---|---|---|
| hyb12_asb4a | **19.4u** / 4,732 cells | 4xAND (triplets 1-4) + S-box + L(5,13). **Beats 20.1u frontier by 0.7u — CHALLENGER** |
| hyb12_asb5a | 22.3u / 5,823 cells | 5xAND + S-box + L(5,13). Quality probe: does S-box fix 5-stage DIFF death? |
| hyb12_sand2a | 20.2u / 5,002 cells | 2xAND + S-box + 2xAND (triplets 3-4) + L(5,13). Interleaved. Dominated by 0.1u. |

All XCHECK pass (analyze.py == analyze2.py). Bit-exact: model vs C 200/200 vecs,
RTL vs model 20/20 (iverilog). Measured S-box+L cost ~5.5u (S-box ~3.5u, L ~2u).

**GHA**: campaign `hyb12-s1s2-20261010` (3 shards, S1+S2, priority frontier-challengers),
bundles pushed as repo commit `705b9d90`, VERIFIED PRESENT 13/13 via API tree read.
Dispatch run 38012623657 in_progress. Generator: `hybrid/codesign/gen_batch12.py`.

## Batch 12 resubmit (2026-10-10 ~02:15Z, respawn after 01:47Z reboot)

Track 5 respawned. Regenerated all 3 hyb12 bundles with the fixed
`gen_batch12.py` (vectorized `_sbox64`, bit-exact scalar+vector verified).
impl.c/rtl.v byte-identical (only model.py changed); goldens unchanged.
Bit-exact: model vs C 200/200 (asb5a; asb4a/sand2a verified scalar+vector).

**GHA**: campaign `campaign-rerun-20261010-021319` (3 shards, S1+S2,
priority frontier-challengers), fixed bundles pushed as repo commit
`7381be15`, VERIFIED: job spec `jobs/mix-sbox-search/campaign-rerun-20261010-021319.json`
present in repo tree + repo blob for hyb12_asb4a/model.py contains the
vectorized fix. Ledger rows 168-170 updated.

## Batch 13 (2026-10-10): co-design for speed (respawn, predecessor silent 02:14Z)

**Diagnosis of batch-12**: Local diffprof (N=2^22) on hyb12 trio:
- asb4a (19.4u): 50/72 deltas |z|>9, max|z|=448.9 @ bit44. CATASTROPHIC.
- asb5a (22.3u): profile running (GHA: max|z|=6.4, S2 PASS).
- sand2a: profile running.
Conclusion: 4 AND stages provide insufficient differential diffusion; the
nibble-local S-box cannot compensate for structured input differences.
The S-box provides ~1-1.5 AND-stages of strength for 5.5u (worse trade than
AND's 3.35u). Placement tweaks alone unlikely to fix catastrophic failure.

**Batch-13 structural variants** (all bit-exact model vs C 200/200):
| Candidate | Structure | Est. S0 |
|---|---|---|
| hyb13_sbfirst_a | SBOX -> 4xAND (1-4) -> L(5,13) | ~18.9u |
| hyb13_minispn_a | 3xAND (1-3) -> SBOX -> ROT(2) -> SBOX -> L | ~19.05u |
| hyb13_rotalign_a | 4xAND (1-4) -> ROT(2) -> SBOX -> L | ~18.9u |
| hyb13_sbfirst5_a | SBOX -> 5xAND (1-5) -> L | ~22.25u |

Generator: `hybrid/codesign/gen_batch13.py`.
S0 + local diffprof running. If any <20.1u with clean DIFF, submit to GHA.

**Batch-13 S0** (run_synth.py, Yosys 0.69 pinned, XCHECK pass):
| Candidate | S0 | Verdict |
|---|---|---|
| hyb13_sbfirst_a | 21.4u / 4,586 cells | OVER 20.1u. S-box-first synthesizes poorly (+2.5u vs est). |
| hyb13_minispn_a | **19.5u** / 3,938 cells | **UNDER frontier!** Mini-SPN works on speed. |
| hyb13_rotalign_a | **19.7u** / 4,826 cells | **UNDER frontier!** ROT(2) alignment is free. |
| hyb13_sbfirst5_a | pending | Expected ~22u (dominated control). |

Note: iverilog missing on VM, so s0_delay.py equiv_check fails. Used run_synth.py
directly (authorized path). Bit-exact model vs C 200/200 already verified;
RTL generated from same logic (Python sim check pending).

diffprof (N=2^22) running on minispn_a, rotalign_a, sbfirst_a. If DIFF clean,
submit to GHA for S1/S2.

**Batch-13 verdict: COMPLETE STRIKEOUT** (local diffprof N=2^22)
| Candidate | S0 | DIFF |
|---|---|---|
| hyb13_sbfirst_a | 21.4u | over budget (S-box-first synthesizes +2.5u) |
| hyb13_minispn_a | 19.5u | S2-KILL: 24 deltas \|z\|>9, max 1025, repeats=13>10 |
| hyb13_rotalign_a | 19.7u | 70/72 deltas \|z\|>9, max 448 (WORSE than asb4a baseline) |
| hyb13_sbfirst5_a | pending | dominated control |

**Terminal conclusion**: 4-bit S-box hybrids cannot achieve sub-20.1u with S1-clean
DIFF. The S-box provides ~1-1.5 AND-stages of strength for 5.5u (worse than AND's
3.35u). Nibble alignment is not the issue (ROT(2) made it worse). Double S-box
cannot compensate for <4 AND stages. S-box-first synthesizes poorly.

**Pivot**: 3-input AND stages. If 3-AND provides ~1.5x the differential strength
of 2-AND per stage, then 4x3AND (+ S-box?) could reach 6-equivalent strength
under 20.1u. Testing the 3-AND strength/cost ratio directly in batch-14.

## Batch 14 (2026-10-10): 3-input AND hybrids (pivot from S-box)

**Rationale**: Batch-13 proved 4-bit S-box cannot reach sub-20.1u (strength/cost).
Hypothesis: 3-input AND x^=(ra&rb&rc)^rd provides ~1.5x differential strength
per stage (degree 3 vs 2). 4x3AND (+S-box) could hit 6-equivalent strength <20.1u.

| Candidate | Structure | Est. S0 |
|---|---|---|
| hyb14_3and4_a | 4x3AND (no S-box) | ~14.4u |
| hyb14_3and4s_a | 4x3AND + SBOX + L(5,13) | ~19.9u |
| hyb14_3and5_a | 5x3AND (no S-box, calibration) | ~18u |

Generator: `hybrid/codesign/gen_batch14.py`. All bit-exact 200/200.
S0 via run_synth.py running; diffprof binaries built.

## Session summary (2026-10-10 respawn, ~09:00-11:30Z)

**Batch-12 local DIFF diagnosis** (diffprof N=2^22, key 0x123456789abcdef0):
- asb4a (19.4u): 50/72 deltas |z|>9, max 448.9 → CATASTROPHIC. 4 AND stages
  insufficient; nibble-local S-box cannot fix structured differences.
- asb5a (22.3u): 0/72 deltas |z|>9, max 6.4 → CLEAN. Confirms GHA S2 PASS.
  The 5th AND stage is load-bearing.

**Batch-13**: 4 structural variants, all bit-exact 200/200.
- sbfirst_a (SBOX->4xAND->L): 21.4u. S-box-first synthesizes +2.5u (poor).
- minispn_a (3xAND->SBOX->ROT2->SBOX->L): 19.5u, S2-KILL (24 deltas, max 1025,
  repeats 13>10). Double S-box cannot compensate for 3 AND stages.
- rotalign_a (4xAND->ROT2->SBOX->L): 19.7u, 70/72 deltas fail, max 448.
  ROT(2) made it WORSE than baseline. Alignment hypothesis FALSIFIED.
- sbfirst5_a: dominated control, S0 not completed.

**TERMINAL**: 4-bit S-box hybrids cannot reach sub-20.1u with S1-clean DIFF.
Strength-per-cost unfavorable (S-box+L: 5.5u for ~1.5 AND-equiv; AND: 3.35u).

**Batch-14**: 3-input AND pivot (x^=(ra&rb&rc)^rd).
- 3and4_a: 16.6u (4.15u/stage) BUT DIFF catastrophic — schedule flaw:
  rotations (1,2,3) are too close, linearizing the AND term (2031 repeats
  on first delta). Needs spread-rotation schedule co-design.
- 3and4s_a: 22.4u (over budget).
- 3and5_a: S0 not completed.

**Track 5 status**: S-box path EXHAUSTED for sub-20.1u. 3-AND needs schedule
work. Awaiting parent direction on next pivot.

**Batch-12 sand2a local DIFF** (completed): 4/72 deltas |z|>9, max 35.1, repeats=14
on delta 0x1 → S2-KILL (rc=2). Less catastrophic than asb4a (50/72) but still
dead. The 2+2 interleaved arrangement fails.

## Batch 15 (2026-10-10): 4x3AND with co-designed schedules - ALL KILLED

**Rationale**: Batch-14 3-AND failed due to schedule flaws (local triples, danger zones).
Batch-15 tests whether proper co-design fixes it.

**Schedules**: A/B/C all danger-zone-free, min pairwise diff >= 7, validated.

**Results** (diffprof N=2^22, key 0x123456789abcdef0):
- hyb15_3and4_A: KILL on delta 0x400, repeats=48126 (catastrophic)
- hyb15_3and4_B: KILL on delta 0x400, repeats=76418 (catastrophic)  
- hyb15_3and4_C: KILL on delta 0x400, repeats=29053 (catastrophic)

**Root cause**: Single 3-AND term has 1/8 density (vs 1/4 for 2-AND). Probe shows
only 8 unique output diffs per 100k samples - stage effectively linear. The
"degree 3 > degree 2" hypothesis was WRONG; density matters more than degree.

## Batch 16 (2026-10-10): 5x3AND with co-designed schedules - BOTH KILLED

**Rationale**: 4 stages insufficient; test if 5 stages with good schedules work.
hyb14_3and5_a (flawed schedule) passed repeats (max 3) but |z|=1539.

**Results**:
- hyb16_3and5_A (20.0u): KILL repeats=15 on delta 0x4; |z| up to 1180
- hyb16_3and5_B (20.0u): PASS repeats (max 0) but |z| 443-917 across 94/115 deltas

**TERMINAL VERDICT**: 3-AND fundamentally broken. Sparsity (1/8) makes it
differentially weaker than 2-AND, not stronger. This is a VALID kill
(fair co-design across batches 14-16), not KILLED-INVALID.

## Batch 17 (2026-10-10): 4x AND-OR hybrid - BOTH KILLED

**Rationale**: Track-3 wave-9 found OR viable. Combine AND+OR for two nonlinear
terms with different DDTs. Stage: x ^= (ra&rb) ^ (rc|rd) ^ re.

**Results**:
- hyb17_andor4_A (20.2u): KILL repeats=43 on delta 0x0200000000000000
- hyb17_andor4_B (20.0u): PASS repeats (max 0) but |z| 94/115 deltas >9 (max 927.8)

**Failure mode**: OR term introduces systematic per-bit bias (OR outputs 1 with
prob 3/4). Different signature than 3-AND (bias not repeats), but equally fatal.

## Track 5 Summary (2026-10-10 12:30Z)

**Exhausted/terminal**:
1. 4-bit S-box hybrids: strength-per-cost unfavorable (terminal)
2. 3-input AND: sparsity kills differentials (TERMINAL, valid kill)
3. AND-OR hybrids: systematic |z| bias (failed)

**Live lead**: hyb12_asb5a (22.3u) S1+S2 clean - proves 5-stage wall breakable
with S-box, but too slow. S3 blocked on canary-pipe infra.

**Open question**: What primitive enables sub-20.1u 5-stage? 2-AND needs 6 stages
(20.1u floor). S-box too slow. 3-AND broken. AND-OR biased.

## Track 5 — batch-25 P7 arm terminal verdict (2026-10-11 ~01:50Z, supervisor inc. IV)

**hyb25_p7t0_probe (7-stage PNL cascade, gen batch21/gen_b25.py):**
- S0 = **29.5u** (6146 cells, 17641 area; ref mul64 103.5u; run_synth.py, XCHECK
  analyze.py==analyze2.py; results/hyb25_p7t0_probe/s0_run.log). ABC outage resolved (transient).
- S1 CAL_PASS (all rejection lists empty; LIN/DIFF 120s, marginal 489s) — re-verified from raw.
- S2 PASS verified from raw s2_run.log: 115 rows, full_repeats=0 everywhere,
  max|z|=16.2 on delta 0x20000000 (within r25 25.1 PASS precedent). Script quirk: deltas
  0x400 and 0x4000000 each appear twice (coincide with bit-10/bit-26 single-bit deltas)
  -> 113 unique deltas probed. XCHECK C==Python 10000/10000.
- **Verdict: KILLED-VALID (cost).** 29.5u >> 19.8u frontier; strictly dominated by
  r22c (28.3/4656/12949) on all three axes. No S3/S4/Q1 escalation (b33 playbook:
  not cost-eligible). Retained as quality evidence only.
- PNL form quality-validated (~4.2u/stage vs b33c 3.3u/stage): the extra rotl(x,d)
  XOR term per stage buys DIFF-cleanliness at +0.9u/stage — too deep for the frontier.

**Screen (search_b25.py, RUN2): nominal, alive.** P7 150/150 KEEP; P8 53/80 all KEEP
(8-stage PNL — structurally >= P7 cost, no escalation regardless); X5/X6 (xfc form,
5/6 stages, ~AND+2XOR/stage like b33c — COST-PLAUSIBLE, pending); C5 = negative
control (frontier-5st, expect 0 KEEP per batch-22 control z=179.5). Positive control
b33c KEEP-OK at screen start; fail-loud asserts: 410 draws, nkill>0.
