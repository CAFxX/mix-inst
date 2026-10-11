# Round 25 — key-schedule delta (A2/A4), S-box least-depth (Track B), r9 F restructures (Track C) (2026-10-05)

**Context — round24 collision (verified 2026-10-05):** the dispatched "Round 24"
brief assumed `round24/` did not exist. It does: a prior round-24 (31 candidates,
2026-10-04) already ran a key-schedule sweep (P2: rc_smallodd/gold16/rotgolden/
nibrep/gold32/altbit) with FULL batteries, concluding "no delay win"
(smallodd 27.9u ≥ golden 27.8u; gold32 S4-killed; altbit S1-killed pb_rej=1).
The brief's Track A variants A1/A3/A5 are retests of that closed work and are
NOT repeated here (VERDICT_SCOPE rule: no retest without new construction).
This round runs only the genuinely-new delta. It also found an unapplied
winner: **r24_spn_mix4r_pba19b21_nw (27.8u/5,507/14,784, sac_z5=0, bic 0.00884)**
strictly dominates r23 pba19b01 (27.8u/5,732/15,374) — flagged for the parent,
PARETO.md NOT edited by this round.

**Restoration (2026-10-05):** the initial setup overwrote the untracked
`round24/models/r24.py` and `round24/gen_r24.py`. Both were reconstructed from
the generated candidates (exact RC tables from impl.c, literal+comment Verilog
form from rtl.v) and verified: generator reproduces all 4 candidate classes
bit-exactly; model matches all golden vectors. No evidence lost.

**Track A' scope:** A2 (walking hot bit) and A4 (hot nibble-lane bit) on the
pba19b01 chassis — the two P2-untested sparse variants. Expectation from P2's
trend (sparser ⇒ slower-or-equal): ≥27.9u; a sub-27.9u result reopens the lever.

**Track B scope (refined per parent directives 2026-10-05):** least-depth ranking
in the GJN17 sense, adapted to our flow. Standalone synthesis via run_synth.py
(pinned Yosys); rank by mapped unit-delay (= logic levels). Literature: Banik et
al. 2015 (depth as S-box delay metric, MIDORI Sb0/Sb1); GJN17 (least-depth logical
expression tool); Sto16 (SAT with depth criterion). S1 is cryptographically
optimal (DU=4, NL=4); 4 AND + 4 XOR is the proven gate-count floor (Ullrich et
al.) — headroom is depth/shape only.
**Broad pool (parent correction 2026-10-05 — NOT Rasoolzadeh-only):** (1) ~12
Rasoolzadeh low-latency S-boxes (S4D3C1/S4D3C2 spread), (2) 4-6 affine-equivs of
S1 (aff1/aff2 + aff_eq3-6), (3) MOLS-derived: PROBED and CLOSED — MOLS(8) GF(8)
pairs via natural 4x4-corner-mod4 restriction yield only affine maps (DU=16,
4/6 bijective, all affine=True), extending round23 P7's complete-enumeration
proof; no MOLS candidates in pool, (4) 5 random DU=4/NL=4 (rnd_opt1-5),
(5) published anchors: PRESENT, SKINNY-64, RECTANGLE (tables verified vs primary
papers; my recalled RECTANGLE table was WRONG — primary paper gives
9,4,f,a,e,1,0,6,c,7,3,8,2,b,5,d), (6) **MIDORI Sb0/Sb1 PRIORITY** (parent directive;
tables from round24/sbox_pool/literature_lowlatency.txt, DU=4/NL=4 verified,
delay-designed by Banik et al. via the depth metric). Rank ALL by standalone
mapped depth; top 3-4 → S0 in pba19b01 → S1 → S2.
CAVEAT: literature depth counts logical-operation levels over {NAND,NOR,INV};
ours counts mapped Sky130 cell levels — strongly correlated (AND-level dominated)
but not identical, which is why the pool is NOT restricted to the paper's depth-3
set. Standalone depth is only the pre-filter; final ranking from S0 in context.

**Track C scope (construction correction, verified 2026-10-05):**
r9_feist6_rot311_nw's F is S1 S-boxes + lin(3,11) — there is NO chi in the
construction (verified in impl.c; critical path is 33/35 pure S-box DNF
levels). The brief's "chi re-placement" premise (from CRITPATH.md's loose
"chi placement" language) does not match. Honest adaptation: restructure the
actual F to minimize mapped nonlinear depth (r9's 5.5 NL/round vs 4.3–4.5 norm).

**Method:** staged xcheck (C vs Python 10k) → S0 (run_synth.py) → S1 →
S2 (N=2^22, 115 deltas, kill repeats>10). Stop at first kill. Polite
≤2-foreign-heavy gate (tweaking + GA active).

## Spec table

| # | Candidate | Axis | Spec |
|---|---|---|---|
| 1 | r25_spn_pba19_ks_a2_nw | A': key schedule | rc_i=0x8000..>>(i-1), pba19b01 chassis |
| 2 | r25_spn_pba19_ks_a4_nw | A': key schedule | rc_i=1<<(16*(i-1)), pba19b01 chassis |
| 3 | r25_spn_pba19_sb_aff1_nw | B: S-box | aff1, DU=4, standalone depth 3 |
| 4 | r25_spn_pba19_sb_inv13_nw | B: S-box | inv13 (GF(2^4) x^-1, poly 0x13), DU=4, depth 3 |
| 5 | r25_spn_pba19_sb_rnd4_nw | B: S-box | rnd4, DU=6, standalone depth 3 |
| 6 | r25_feist6_linfirst_nw | C: r9 F | F=S1(lin(R,3,11))^rk |
| 7 | r25_feist6_keyin_nw | C: r9 F | F=lin(S1(R^rk),3,11) |
| 8 | r25_feist6_rot13_nw | C: r9 F | F=S1+lin(1,3) |

## Track B standalone screening (mapped depth)

### Old pool (superseded — kept as secondary data)
| Candidate | Kind | DU | Mapped depth (levels) | Nonlin levels | Cells | Verdict |
|---|---|---|---|---|---|---|
| S1_baseline | — | 4 | 3 | 3 | 260 | baseline |
| aff1 | affine-equiv S1 | 4 | 3 | 2 | 296 | KEEP (in S2) |
| inv13 | GF(2^4) inverse | 4 | 3 | 2 | 321 | KEEP (in S2) |
| rnd4 | random | 6 | 3 | 2 | 242 | KEEP (in S2, DU caveat) |

### Broad pool (2026-10-05; unit-delay via run_synth.py; affine MOLS excluded)
| Candidate | Source | DU/NL | Delay | Verdict |
|---|---|---|---|---|
| lit_midori_sb0 | MIDORI Sb0 (Banik et al.) **PRIORITY** | 4/4 | **3.0u** | **TOP-4 → S0** |
| s1_baseline | our S1 (reference) | 4/4 | 3.7u | reference |
| lit_midori_sb1 | MIDORI Sb1 (Banik et al.) | 4/4 | 4.0u | — |
| aff_eq3 | affine-equiv S1 | 4/4 | 4.2u | — |
| lit_rectangle | RECTANGLE paper | 4/4 | 4.5u | — |
| aff_eq5 | affine-equiv S1 | 4/4 | 4.5u | — |
| aff_eq6 | affine-equiv S1 | 4/4 | 4.5u | — |
| rnd_opt4 | random DU=4/NL=4 | 4/4 | 4.5u | — |
| aff_eq4 | affine-equiv S1 | 4/4 | 4.7u | — |
| lit_skinny | SKINNY-64 spec | 4/4 | 5.2u | — |
| user_sbox1 | **USER_SBOX1** (user-supplied) | 4/4 | 5.0u | — (7th, below top-4 cutoff) |
| rnd_opt1 | random DU=4/NL=4 | 4/4 | 5.5u | — |
| rnd_opt3 | random DU=4/NL=4 | 4/4 | 5.5u | — |
| lit_present | PRESENT paper | 4/4 | 6.0u | — |
| rnd_opt2 | random DU=4/NL=4 | 4/4 | 6.0u | — |
| mols8_c12/c23/c35/c25 | MOLS(8) GF(8) | 16/0 | — | EXCLUDED (affine) |

### Rasoolzadeh pool (2026-10-05; tracer levels via critpath.py)
| Candidate | File:line | DU | Levels | Cells | Verdict |
|---|---|---|---|---|---|
| rasC2_5 | S4D3C2:128 | 4 | 3 | 223 | **TOP-4 → S0** |
| rasC2_0 | S4D3C2:0 | 4 | 3 | 238 | **TOP-4 → S0** |
| rasC1_2 | S4D3C1:60 | 4 | 3 | 239 | **TOP-4 → S0** |
| rasC2_1 | S4D3C2:26 | 4 | 3 | 242 | — |
| rasC2_2 | S4D3C2:51 | 4 | 3 | 254 | — |
| rasC2_4 | S4D3C2:102 | 4 | 3 | 255 | — |
| rasC2_3 | S4D3C2:77 | 4 | 3 | 257 | — |
| rasC1_1 | S4D3C1:30 | 4 | 3 | 257 | — |
| rasC1_0 | S4D3C1:0 | 4 | 3 | 273 | — |
| rasC1_3/4/5 | S4D3C1 | 4 | 4 | 258-268 | — (depth 4) |

**Top 4 for S0:** lit_midori_sb0 (3.0u, priority) + rasC2_5 + rasC2_0 + rasC1_2
(3 smallest-cell depth-3 Rasoolzadeh). All DU=4/NL=4 optimal.
Worker dispatched 2026-10-05 for xcheck→S0→S1→S2 (log: track_b_broad.log).
xcheck PASS for all 4; S0 gate-blocked (worker completed xcheck phase).

### Literature add2 pool (2026-10-05; 28 S-boxes from literature_lowlatency_add2.txt)
27 new (LU21_SKINNY duplicates lit_skinny, already measured at 5.2u, skipped).
All verified bijective, DU=4/NL=4, zero collisions with existing pool.
Standalone screening COMPLETE (unit-delay via run_synth.py):

| Candidate | Delay | Note |
|---|---|---|
| ULBC_s1 | **3.4u** | 2nd best overall (after MIDORI Sb0 3.0u) |
| THF_BLINK_S0 | **3.4u** | 2nd best overall (involution) |
| LU21_LBLOCK_S0 | 4.0u | tied |
| PRINCE_S0 | 4.0u | tied |
| ORTHROS_S0 | 4.0u | **did NOT beat MIDORI Sb0** despite 90nm claim |
| SAAR11_G10 | 4.0u | tied |
| BOYAR19_GF4INV | 4.2u | tied 5-way |
| SAAR11_G0/G4/G5/G9 | 4.2u | tied 5-way |
| SAAR11_G7/G12 | 4.4u | tied |
| SAAR11_G8/G13/G14 | 4.5u | tied 6-way |
| JIA25_12GE_R1/R2/R3 | 4.5u | tied 6-way |
| SAAR11_G2/G11 | 4.7u | tied |
| LU21_RECTANGLE | 5.0u | inverse of paper RECTANGLE; tied 5-way |
| SAAR11_G1/G3/G6/G15 | 5.0u | tied 5-way |
| LU21_PICCOLO | 5.2u | |

### Literature add3 pool (2026-10-05; 5 S-boxes, expert-suggested)
All verified bijective, DU=4/NL=4. Standalone screening COMPLETE:

| Candidate | Delay | Degrees | Note |
|---|---|---|---|
| QARMA_S1 | 4.2u | [3,3,3,3] | best add3 (tied) |
| JIA25_11GE | 4.2u | [3,3,2,2] | best add3 (tied); 11-GE headline |
| QARMA_S2 | 4.5u | [3,3,3,3] | |
| JIA25_12GE_EX | 4.5u | [3,3,2,2] | confirmed NOT dup of R1..R3 |
| QARMA_S0 | 5.0u | [3,3,2,3] | one degree-2 coord as noted |

None beat MIDORI Sb0 (3.0u). Best add3 (4.2u) is 1.2u behind.

### USER_SBOX1 degree verification (expert flag)
USER_SBOX1 coordinate degrees: **[3,3,3,3]** (all degree 3, verified via ANF Mobius).
Expert's concern: "degree-3 in every coordinate with a 2-level NAND implementation
would be unusual." **Resolution:** USER_SBOX1 does NOT achieve 2-level; its
standalone mapped depth is 5.0u (7th in broad pool). The 5.0u depth is consistent
with all-degree-3 coordinates requiring deeper logic. No contradiction — the
S-box is not a 2-level implementation. It remains below the top-4 S0 cutoff.

### Variant sweep (2026-10-05; in progress)
Worker dispatched for 4096-variant sweep (16 input perms × 16 output perms ×
16 output XORs) on top-3: MIDORI Sb0, ULBC_s1, THF_BLINK_S0. Ranking by
standalone mapped delay. Log: variant_sweep.log. Results pending.
| inv19 | GF(2^4) inverse | 4 | 4 | 4 | 335 | drop |
| rnd1 | random | 6 | 4 | 4 | 397 | drop |
| rnd2 | random | 4 | 4 | 4 | 385 | drop |
| rnd3 | random | 6 | 4 | 3 | 287 | drop |
| aff2 | affine-equiv S1 | 4 | 5 | 5 | 405 | drop |

No candidate beats S1's standalone depth of 3 (best tie). Notably aff2, an
affine-equivalent of S1, maps to 5 levels — affine equivalence preserves
crypto (DU=4) but NOT mapped depth. The three kept candidates tie S1; S0 in
the pba19b01 construction decides the final ranking.

## Stage results

| Candidate | xcheck | S0 | S1 | S2 | Verdict |
|---|---|---|---|---|---|
| r25_spn_pba19_ks_a2_nw | PASS 10k/10k | 28.0u/5341/14318 | CAL_PASS | PASS (rep 0) | **SURVIVES** (+0.2u, neutral) |
| r25_spn_pba19_ks_a4_nw | PASS 10k/10k | 27.9u/5569/14960 | CAL_PASS | PASS (rep 1) | **SURVIVES** (+0.1u, neutral) |
| r25_spn_pba19_sb_aff1_nw | PASS 10k/10k | 29.8u/6932/18675 | CAL_PASS | PASS (rep 0) | **S0-SLOWER** (+2.0u) |
| r25_spn_pba19_sb_inv13_nw | PASS 10k/10k | 31.0u/7165/20188 | CAL_PASS | PASS (rep 0) | **S0-SLOWER** (+3.2u) |
| r25_spn_pba19_sb_rnd4_nw | PASS 10k/10k | 28.2u/6519/18299 | CAL_PASS | PASS (rep 0) | **S0-SLOWER** (+0.4u, DU=6) |
| r25_spn_pba19_sb_midori_sb0_nw | — | — | — | — | in pipeline |
| r25_spn_pba19_sb_rasC2_5_nw | PASS 10k/10k | PASS 28.1u/5778/15764, ratio 0.272, equiv 1000/1000 | **CAL_PASS**: pb=0 rd=0 lin=0 diff=0 | PASS max_repeats=1, max\|z\|=12.1 (115 deltas) | **FULL-PASS REFERENCE** (S0–S4 + Q1 sac_z5=0 bic 0.01009, parent-verified 2026-10-05); dominated by r25 rasC2_0 — retained #28, off frontier |
| r25_spn_pba19_sb_rasC2_0_nw | PASS 10k/10k | PASS 26.5u/5125/14019, ratio 0.256, equiv 1000/1000 | **CAL_PASS**: pb=0 rd=0 lin=0 diff=0 | PASS max_repeats=1, max\|z\|=11.3 (115 deltas) | **FRONTIER S+Q SPEED POINT** (S0–S4 + Q1 sac_z5=0 bic 0.01012, parent-verified 2026-10-05; strictly dominates r23 pba19b01 and wf2d aff_a17_b17 on all axes) |
| r25_spn_pba19_sb_rasC1_2_nw | PASS 10k/10k | PASS 28.5u/4980/13247, ratio 0.275, equiv 1000/1000 | **CAL_PASS**: pb=0 rd=0 lin=0 diff=0 | PASS max_repeats=0, max\|z\|=7.1 (115 deltas) | **FULL-PASS REFERENCE** (S0–S4 + Q1 sac_z5=0 bic 0.00847, parent-verified 2026-10-05); strictly dominated by r22c — retained #30, off frontier |
| r25_feist6_linfirst_nw | PASS 10k/10k | 46.3u/4808/14267 | — | — | **S0-KILLED (delay)** |
| r25_feist6_keyin_nw | PASS 10k/10k | 45.2u/4532/12115 | — | — | **S0-KILLED (delay)** |
| r25_feist6_rot13_nw | PASS 10k/10k | 40.9u/3844/10641 | **FLAG** | — | **S1-KILLED** |

## Failure analyses

### FA1. r25_feist6_linfirst_nw — S0 delay kill (46.3u vs r9 41.0u)
- **Failing signal:** S0 RESULT `crit=46.3` (+5.3u vs r9), cells 4,808 (+13%).
- **Mechanistic hypothesis:** linear layer before the S-box puts a 3-XOR level
  on the S-box input side where the mapper cannot absorb it; r9's post-S-box
  linear XORs merge into downstream logic.
- **Follow-up:** none — direction is wrong (deeper, bigger). Closed.

### FA2. r25_feist6_keyin_nw — S0 delay kill (45.2u vs r9 41.0u)
- **Failing signal:** S0 RESULT `crit=45.2` (+4.2u vs r9).
- **Mechanistic hypothesis:** SPN-style key-into-S-box moves the round-key XOR
  onto the critical path ahead of the S-box; r9's key-XOR-after-F sits off the
  critical path / merges better.
- **Follow-up:** none — the Feistel key-after-F placement is load-bearing for
  delay. Closed.

### FA3. r25_feist6_rot13_nw — S1 kill (LIN D=4096/4096, DIFF |z|≈7.4e5)
- **Failing signal:** S1 FLAG: `LIN D=4096/4096 logp=-inf` on all 10 keys;
  `DIFF worst|z|=739994.3` on all 10 keys. (S0 was 40.9u, nominally under r9,
  but cryptographically dead.)
- **Mechanistic hypothesis (verified computationally):** taps (1,3) give a
  4-bit interaction window vs 12-bit for (3,11), crippling cross-nibble
  diffusion. 4096 sequential inputs → outputs span only a 59-dim subspace
  (r9 spans 64). Reduced-round rank growth over 600 sequential inputs:
  (1,3) = 19/26/33/40/47/54 vs (3,11) = 19/39/62/64/64/64 — six rounds
  insufficient for (1,3) diffusion.
- **Follow-up:** none — (1,3) taps are cryptographically unsound at 6r.
  Scoped to this construction; the (3,11) tap choice is load-bearing. Closed.

### FA0. Generator bug (found and fixed during Track C)
`gen_r25c.py` emitted inconsistent key schedules: C `RK32` used r9-canonical
`rotl64(k,13*(i+1))^((i+1)*GOLDEN64)` but Python `_rk32` and Verilog `rk64`
used `13*i`/`i` — caught by xcheck failing 10000/10000 on all three.
Fixed by canonicalizing to r9's schedule in `models/r25c.py`, all three
`rtl.v`, and both templates in `gen_r25c.py`; xcheck re-run 3× PASS.
Class hunt: Track B's chain already consistent — only Track C affected.

## Follow-up batteries (top-4 Track B, 2026-10-05)

**Method:** sequential S0→S1→S2 per candidate, stop at first kill; candidates
sequentially, no parallelism. Outdirs: `round25/s0_r25_top4_<short>/`.
S2: key=`0x123456789abcdef0` (meta.json practrand_keys[0]), N=2^22,
kill_repeats=10 (ref/s2_kill_repeats.txt). xcheck (C vs Python 10k) PASS for
all 4 per track_b_broad.log (not re-run). S0 bar: delay_ratio ≤ 0.9×
multiplier (103.5u). S1 bar: CAL_PASS = zero Holm-Bonferroni rejections
across PB/RD/LIN/DIFF (all verdict/kill fields checked, incl.
`marginal_skipped`). Polite ≤2-foreign-yosys gate observed (two 60s waits).
Yosys 0.69 pinned.

**Escalation note:** rasC2_5 passed S0 AND S1 AND S2, triggering the
escalation rule: Verdict written as **FRONTIER-CHALLENGER**, table written,
all further battery work stopped. rasC2_0 and rasC1_2 were NOT run.
Honest caveat for the parent: rasC2_5 is +0.3u/+271 cells/+980 area vs the
27.8u reference (r24_spn_mix4r_pba19b21_nw) — it passes all gates but does
NOT Pareto-dominate. PARETO.md untouched; raw logs pending parent
verification.

| Candidate | xcheck | S0 | S1 | S2 | Verdict |
|---|---|---|---|---|---|
| r25_spn_pba19_sb_midori_sb0_nw | PASS 10k/10k | PASS 27.4u/5169/14170, ratio 0.265 (bar 0.9), equiv 1000/1000 | **FLAG**: pb=0 rd=0 lin=0 diff=**1** — DIFF key=0x0 worst\|z\|=8.24, bonf_logp=-33.36 (marginal skipped after DIFF kill) | — | **S1-KILLED** |
| r25_spn_pba19_sb_rasC2_5_nw | PASS 10k/10k | PASS 28.1u/5778/15764, ratio 0.272, equiv 1000/1000 | **CAL_PASS**: pb=0 rd=0 lin=0 diff=0 (marginal ran, 379s) | PASS max_repeats=1, max\|z\|=12.1 (115 deltas, key 0x123456789abcdef0) | **FRONTIER-CHALLENGER** (+0.3u vs 27.8u; does not Pareto-dominate; parent to verify raw logs) |
| r25_spn_pba19_sb_rasC2_0_nw | PASS 10k/10k | — | — | — | not run (batteries stopped per escalation rule after rasC2_5) |
| r25_spn_pba19_sb_rasC1_2_nw | PASS 10k/10k | — | — | — | not run (batteries stopped per escalation rule after rasC2_5) |

**rasC2_5 Q-gates (follow-up, 2026-10-05):** Q1 PASS — sac_z5=0 (mandatory),
bic_maxcorr=0.010094 ≤ 0.02 (Q-frontier bar). Raw: `round25/q1/q1_r25_spn_pba19_sb_rasC2_5_nw.json`,
log `round25/s0_r25_top4_rasC2_5/q1.log`. S3 PractRand 1GB standard
(KEY1=0x123456789abcdef0): **PASS** (16MB→1GB, all 4 stages, no FAIL; log
`s0_r25_top4_rasC2_5/s3.log`). S3 strided 1GB (KEY2=0x0, stride
0x9E3779B97F4A7C15): **PASS** (log `s0_r25_top4_rasC2_5/s3b.log`). S4
SmallCrush: **PASS** — `All tests were passed`, 15 statistics, 31.78s CPU,
no "gave p-values outside" lines (log `s0_r25_top4_rasC2_5/s4.log`; binary
exit 0). Driver exit 0: ALL FOUR Q-GATES PASS (a)(b)(c)(d).
**rasC2_5 is a Q-Frontier candidate pending parent's raw-log verification**
— 28.1u/5778/15764 (+0.3u vs 27.8u reference; does NOT Pareto-dominate).
PARETO.md NOT touched.

**rasC2_0 / rasC1_2 batteries (follow-up, 2026-10-05):** escalation-stopped,
not killed — running S0→S1→S2 now.
- rasC2_0 S0: **PASS 26.5u/5125**, ratio 0.256 (bar 0.9), equiv 1000/1000 ok.
  Fastest S0 in round 25 so far (vs 27.8u ref, 27.4u midori_sb0, 28.1u rasC2_5).
  Raw: `round25/s0_r25_top4_rasC2_0/{s0.log,s0_result.json}`. S1 re-running
  (first attempt hit the known s1_screen.py relative-outdir bug AFTER
  LIN/DIFF both passed; re-run with absolute outdir).
- rasC2_0 S1: **CAL_PASS** (pb=0 rd=0 lin=0 diff=0 on all 10 keys; marginal
  ran clean). Raw: `round25/s1_r25_spn_pba19_sb_rasC2_0_nw/{s1.log,
  s1_result.json}`.
- rasC2_0 S2: **PASS** — max_repeats=1, max|z|=11.3, all 115 deltas (N=2^22,
  key 0x123456789abcdef0, kill_repeats=10, no KILLs). Raw:
  `round25/s2_r25_spn_pba19_sb_rasC2_0_nw/s2.log`.
- rasC2_0 Q1 (sac_z5 + BIC): **PASS** — sac_z5=0 (mandatory),
  bic_maxcorr=0.01012 ≤ 0.02 (Q-frontier bar), sac_maxdev=0.0032,
  avalanche_mean=31.998. Log `round25/s0_r25_top4_rasC2_0/q1.log`, raw
  `round25/q1/q1_r25_spn_pba19_sb_rasC2_0_nw.json`. Escalation complete at
  the Q1 level (per task: sac_z5 + BIC, then report).
- rasC1_2 S0→S1→S2:
  - S0: **PASS 28.5u/4980**, ratio 0.275 (bar 0.9), equiv 1000/1000 ok. Raw:
    `round25/s0_r25_top4_rasC1_2/{s0.log,s0_result.json}`. (28.5u > 27.8u
    reference — no Pareto pressure, standard screen.)
  - S1: **CAL_PASS** (LIN rej=0, DIFF rej=0 on all 10 keys; marginal PB
    rej=0, RD rej=0, 479s). Raw:
    `round25/s1_r25_spn_pba19_sb_rasC1_2_nw/{s1.log,s1_result.json}`.
    (Second launch — the first instance died in the runtime restart.)
  - S2: **PASS** — max_repeats=0, max|z|=7.1, all 115 deltas (N=2^22,
    key 0x123456789abcdef0, kill_repeats=10, no KILLs). Raw:
    `round25/s2_r25_spn_pba19_sb_rasC1_2_nw/s2.log`. Cleanest S2 in the
    round so far.
  - Q1 (sac_z5 + BIC): **PASS** — sac_z5=0 (mandatory), bic_maxcorr=0.00847
    ≤ 0.02 (Q-frontier bar; best BIC of the three), sac_maxdev=0.0033,
    avalanche_mean=31.998. Log `round25/s0_r25_top4_rasC1_2/q1.log`, raw
    `round25/q1/q1_r25_spn_pba19_sb_rasC1_2_nw.json`. Escalation complete at
    the Q1 level (per task: sac_z5 + BIC, then report).
**rasC1_2 escalation verdict:** S0 28.5u/4980 PASS, S1 CAL_PASS, S2 PASS
(max_repeats=0, max|z|=7.1 — cleanest S2 in the round), Q1 PASS
(sac_z5=0, bic_maxcorr=0.00847). Full-battery profile matches rasC2_5's
(28.1u) modulo delay. NOT claimed as frontier — PARETO.md untouched;
parent verifies raw logs.
**rasC2_0 escalation verdict:** S0 26.5u/5125 PASS (fastest S0 in round 25),
S1 CAL_PASS, S2 PASS (max_repeats=1, max|z|=11.3), Q1 PASS (sac_z5=0,
bic_maxcorr=0.01012). Same — pending parent's raw-log verification.
- rasC2_5 S3/S4 (Item 1c/d): S3 PractRand 1GB standard (KEY1=0x123456789abcdef0)
  STARTED 08:37 UTC 2026-10-05 (RNG_test running); strided + S4 to follow in
  the same driver. Note: the first driver instance (started 07:42) died in a
  runtime service restart while in the polite wait — S3 had never started;
  relaunched cleanly. Driver log
  `round25/s0_r25_top4_rasC2_5/s3s4_driver.log`, per-stage logs s3.log,
  s3b.log, s4.log.

**Raw logs:** S0/S1 `round25/s0_r25_top4_midori/{s0.log,s0_result.json,s1.log,
s1_result.json}`; rasC2_5 same dir names under `s0_r25_top4_rasC2_5/` plus
`s2.log`. Checkpoint: `round25/top4_batteries_checkpoint.json`.

### FA4. r25_spn_pba19_sb_midori_sb0_nw — S1 kill (DIFF anomaly on key=0x0)
- **Failing signal:** S1 verdict FLAG; `diff_rejected=[('DIFF', 0)]`; DIFF
  key=0x0: worst|z|=8.24, fisher_logp=-33.06, bonf_logp=-33.36. Other 9 keys
  clean (worst|z| ≤ 4.0, bonf_logp ≥ -6.8); LIN rej=0 on all 10 keys; PB/RD
  lists empty but `marginal_skipped=True` — the marginal screen never ran
  (short-circuit after the DIFF kill), so PB/RD pass is NOT established.
- **Mechanistic hypothesis:** MIDORI Sb0 is an involution-class, all-degree-3
  S-box with optimal DU=4/NL=4. Under key=0x0 the round-key XORs vanish, so
  the differential structure reduces to the pure S-box + pba19b01 linear-layer
  composition; a specific delta then shows an ~8σ repeat-count anomaly. The
  other 9 keys are clean, pointing to a key-dependent clustering effect —
  plausibly a high DDT entry in Sb0's table being preserved/echoed by the
  linear layer when no key breaks the alignment — rather than a
  construction-wide diffusion failure. Standalone S-box optimality (DU=4)
  bounds only single-S-box differentials, not the composed multi-round
  structure, so no contradiction.
- **Follow-up (scoped to the pba19b01 construction):** (1) re-run the DIFF
  screen over more keys incl. structured near-zero keys to map the anomaly;
  (2) identify the offending delta(s) and check against Sb0's DDT; (3)
  compare MIDORI Sb1 (4.0u standalone) — if Sb1 is clean, the effect is
  Sb0-specific, not involution-class. Closed for this round (S1-killed);
  note Sb0's S0 (27.4u) is the fastest in round 25 so far, so this is worth
  the follow-up before discarding the S-box entirely.


## FA4 mechanism follow-up (2026-10-05)

**Method:** cheap S1-DIFF screens only (LIN+DIFF ~38s per run; no marginal).
Drivers: `round25/fa4_followup_a.py` (near-zero keys + per-delta dump),
`fa4_followup_b.py` (DDT + empirical histograms), `fa4_followup_b2.py`
(round-by-round trace), `fa4_followup_b3.py` (key-dependent DDT selection).
Results: `round25/fa4a_result.json`.

### (a) Near-zero keys — kill is NOT key=0-specific (REFINED, not confirmed)

| key | weight | DIFF worst\|z\| | fisher_logp | bonf_logp | worst delta |
|---|---|---|---|---|---|
| 0x0 | 0 | 8.24 | -33.1 | -33.4 | 2^8 |
| 0x1 | 1 | 8.02 | -39.4 | -31.6 | 2^8 |
| 0x2 | 1 | 6.83 | -15.9 | -22.6 | 2^8 |
| 0x4 | 1 | 5.69 | -13.8 | -15.3 | 2^10 |
| 0x8000000000000000 | 1 | 9.10 | -38.4 | -41.0 | 2^8 |
| 0x3 | 2 | 6.61 | -15.2 | -21.1 | 2^8 |
| 0x7 | 3 | 6.83 | -12.9 | -22.6 | 2^8 |
| 0xF | 4 | 5.37 | -11.7 | -13.5 | 2^8 |
| 0x1F | 5 | 2.08 | -0.7 | -0.4 | — |
| 0x12345 | 7 | 2.27 | -1.1 | -0.9 | — |

**Verdict:** the kill persists across all tested low-weight keys (0–4 bits),
including a high single-bit key (bit 63). It is a **low-weight weak-key
phenomenon** (boundary between weight 4 and 5 in the tested set), NOT a
key=0x0-specific effect. The original FA4 "zero-key" framing was too narrow.

### (b) Offending delta vs Sb0 DDT — PARTIALLY CONFIRMED, hypothesis corrected

- **Offending delta:** 2^8 (bit 8 = nibble 2, bit 0) in 4/5 flagging keys;
  2^10 (nibble 2, bit 2) at key=0x4.
- **Sb0 DDT check:** row for nibble delta 1 = {1:2, 2:4, 4:2, 5:2, 6:2, 8:2,
  14:2} — contains a count-4 entry (1→2). Row for nibble delta 4 =
  {1:2, 2:4, 3:2, 4:2, 5:2, 8:2, 11:2} — also count-4 (4→2). Both offending
  deltas sit on count-4 DDT entries. ✓ (consistent with the hypothesis)
- **Round-by-round trace** (delta 2^8, low-8-bit chi2 z per round):
  key=0x0: r1=737092 → r2=80189 → r3=3349 → r4=27.8;
  key=0xffffffffffffffff: r1=737092 → r2=75123 → r3=255 → r4=12.2.
  The round-1 differential is **key-independent** (z=737092 both keys) — the
  linear layer + S-box genuinely produce an enormous 1-round truncated
  differential from delta 2^8. The key modulates the **decay rate** from
  round 2 onward (round-3 z: 3349 vs 255, ~13×).
- **Key-dependent DDT-selection test (b3): NEGATIVE.** For sequential inputs
  x∈[0,2^17), the round-1 S-box output-nibble distribution at nibble 2 is
  identical across keys (P(dout=2)=0.25 for key 0x0, 0xff..f, 0x55..5) —
  x's range covers all nibble values regardless of rk0's XOR shift. The
  key-dependence therefore enters at **round 2+ via absolute state values**
  through the nonlinear S-box, not via round-1 DDT-entry selection.
- **Correction to FA4's hypothesis:** "under key=0x0 the round-key XORs
  vanish" is **factually wrong** — rk64(k,i) = rotl64(k,13(i+1)) ^ RC[i] with
  RC[i]=(i+1)·GOLDEN64 ≠ 0, so at key=0 the round keys are the golden
  constants. Nothing vanishes.
- **Mechanism verdict:** a high-DDT differential (count-4 entry 1→2 at the
  input nibble) IS echoed by the pba19b01 linear layer with slow decay
  (737k→80k→3.3k→28 over 4 rounds), but the echo is **not zero-key-specific**:
  it is a low-key-weight effect (≤4 bits), the round-1 component is
  key-independent, and key-dependence enters through later-round absolute
  state values. Scoped to the pba19b01-SPN + Sb0 construction.

### (c) MIDORI Sb1 control — KILL DOES NOT REPRODUCE (Sb0-specific)

Variant `r25_spn_pba19_sb_midori_sb1_nw` generated via the round-25 pipeline
(spec appended to specs25.json; impl.c/rtl.v/model.py/meta.json emitted;
goldens computed; xcheck PASS 10000/10000 C==Python). S1 LIN+DIFF: **PASS** —
DIFF key=0x0 worst|z|=2.4 (vs Sb0's 8.24), all 10 keys clean, LIN rej=0.
Sb1's DDT row din=1 also has the count-4 hot entry (1→2), so the kill is
**not** driven by that entry alone — it is specific to Sb0's full DDT/ANF
structure in this construction, not an involution-class or pba19-wide
effect. Full S1 (marginal PB/RD) re-running with absolute outdir after the
known s1_screen.py relative-outdir bug cut the first attempt short.
Full-S1 result (2026-10-05): **CAL_PASS** — LIN rej=0, DIFF rej=0 on all 10
keys; marginal PB rej=0, RD rej=0. Sb1 is clean end-to-end in this
construction; the FA4(c) control is fully closed.

## Variant sweep results (2026-10-05 follow-up)

4096-variant affine sweep per base box (16 input bit-perms x 16 output bit-perms x 16 output XOR constants), standalone mapped delay via run_synth.py (pinned Yosys). Top-10 per base box by (crit, cells):

### midori_sb0 — converged: 1024 done, top-10 within 0.1u (best 3.0u/176c)

| # | vi | pin | pout | c | table | crit | cells | area | fanout |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3824 | e | f | 0 | 31b870f259cad4e6 | 3.0 | 176 | 464 | 5 |
| 2 | 3552 | d | e | 0 | 51d839ac70f4b2e6 | 3.0 | 176 | 464 | 5 |
| 3 | 3280 | c | d | 0 | 546cd8a970e2f1b3 | 3.0 | 176 | 464 | 5 |
| 4 | 3008 | b | c | 0 | 6740ef825dc19ba3 | 3.0 | 176 | 464 | 5 |
| 5 | 2736 | a | b | 0 | 3b7f10429dce586a | 3.0 | 176 | 464 | 5 |
| 6 | 1920 | 7 | 8 | 0 | ae84bf0295c6d713 | 3.0 | 176 | 464 | 5 |
| 7 | 1648 | 6 | 7 | 0 | 57df12049abe368c | 3.0 | 176 | 464 | 5 |
| 8 | 832 | 3 | 4 | 0 | c98adb01e326f745 | 3.0 | 176 | 464 | 5 |
| 9 | 560 | 2 | 3 | 0 | 6aeb230879fd154c | 3.0 | 176 | 464 | 5 |
| 10 | 288 | 1 | 2 | 0 | a6e7b5fd2304198c | 3.0 | 176 | 464 | 5 |

### ulbc_s1 — converged: 1024 done, top-10 within 0.1u (best 3.0u/192c)

| # | vi | pin | pout | c | table | crit | cells | area | fanout |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1113 | 4 | 5 | 9 | 1b9a08ecdf524763 | 3.0 | 192 | 528 | 6 |
| 2 | 2482 | 9 | b | 2 | 31602c48a9efbd57 | 3.0 | 192 | 528 | 6 |
| 3 | 3044 | b | e | 4 | 5163c0ef4a7b829d | 3.0 | 192 | 528 | 6 |
| 4 | 2498 | 9 | c | 2 | 64a0298135bf7dce | 3.0 | 192 | 528 | 6 |
| 5 | 42 | 0 | 2 | a | 8ab30726ecf145d9 | 3.0 | 192 | 528 | 6 |
| 6 | 2502 | 9 | c | 6 | 20e46dc571fb398a | 3.0 | 192 | 528 | 6 |
| 7 | 1961 | 7 | a | 9 | 8dbf012e95a4736c | 3.0 | 192 | 528 | 6 |
| 8 | 2517 | 9 | d | 5 | 10d45ec672fb3a89 | 3.0 | 192 | 528 | 6 |
| 9 | 1154 | 4 | 8 | 2 | a624805137bc9fde | 3.0 | 192 | 528 | 6 |
| 10 | 276 | 1 | 1 | 4 | c4e3576208ab1f9d | 3.0 | 208 | 544 | 6 |

### thf_blink_s0 — converged: 1024 done, top-10 within 0.1u (best 3.4u/240c)

| # | vi | pin | pout | c | table | crit | cells | area | fanout |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2192 | 8 | 9 | 0 | 4805cb671a2f93ed | 3.4 | 240 | 576 | 5 |
| 2 | 3572 | d | f | 4 | c6d740895132ebaf | 3.4 | 240 | 624 | 6 |
| 3 | 2208 | 8 | a | 0 | 410c5b6e832f9a7d | 3.4 | 240 | 576 | 5 |
| 4 | 2210 | 8 | a | 2 | 632e794ca10db85f | 3.4 | 240 | 624 | 6 |
| 5 | 1392 | 5 | 7 | 0 | 231d0a6e459c8bf7 | 3.4 | 240 | 576 | 5 |
| 6 | 36 | 0 | 2 | 4 | 54716da9c0e32b8f | 3.4 | 240 | 624 | 6 |
| 7 | 320 | 1 | 4 | 0 | 2086a3d7419fcb5e | 3.4 | 240 | 580 | 6 |
| 8 | 1920 | 7 | 8 | 0 | 4c2a8b93051d67fe | 3.4 | 241 | 578 | 5 |
| 9 | 292 | 1 | 2 | 4 | 546d71a9c02be38f | 3.4 | 241 | 624 | 6 |
| 10 | 3316 | c | f | 4 | c640d78951eb32af | 3.4 | 241 | 624 | 6 |

