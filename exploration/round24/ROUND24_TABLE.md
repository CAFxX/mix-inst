# Round 24 — (19,1) speed-point neighborhood sweep (2026-10-04)

**Directive:** round-23 follow-up (parent brief): push the two clearest levers
r23 exposed — (P1) affine-P-box refinement around (19,1), (P2) key-schedule
delay lever — plus (P3) VERDICT_SCOPE O45 HIGH re-test (odd-term rotation
mixing layers), (P4) hetero-S-box × (19,1) size plays.

**Baseline (not rebuilt):** r23_spn_mix4r_pba19b01_nw = 4r keyed SPN
x_{i+1} = L(P(S16(x_i ^ rk_i))), S1, P(i)=(19i+1)%64, L=lin(3,11),
rk_i = rotl64(key,13(i+1)) ^ ((i+1)*GOLDEN64). 27.8u/5732/15374, full battery
PASS, bic 0.01092. (No input/final whitening: x_0 = val, out = x_4; the
`_nw` suffix is literal. The parent brief's "whitening" phrase does not match
the implemented construction — verified in gen_r23.py/r22.py.)

**Method:** staged kill-chain xcheck (C vs Python 10k) → rtlcheck (RTL vs
Python 300) → S0 (run_synth.py; analyze.py AND analyze2.py must agree) →
S1 (s1_screen.py; verdict honors EVERY kill field per its contract) →
S2 (N=2^22, 115 deltas, kill repeats>10) → S3 (PractRand 16M→1G ×2 configs)
→ S4 (SmallCrush) → Q1 (sac_z5=0 mandatory). Polite ≤2-heavy-pipeline
concurrency, counted by heavy binaries. Generator: `gen_r24.py`; model:
`models/r24.py`; specs frozen in `specs24.json`. Round constants live in
`r24.RK_VARIANTS` — the single source of truth for model, C table, and
Verilog literals (self-test asserts all three agree per spec).
(S3 note, verified 2026-10-04: PractRand's first interim report is at 32MB,
so the 16MB stage legitimately yields zero test results and RNG_test prints
"error reading from file" on stdin EOF — benign; the 64MB stage covers the
32MB point. The s3_practrand.sh FAIL-grep verdict is unaffected.)

**Per-layer bijectivity (SPN hard gate):** every spec's S-box lane tables
verified 4-bit permutations, P-box a 64-permutation, L GF(2) rank 64
pre-synthesis; 5k×2-key empirical collision-free per spec at generation.
Key schedule is a per-round fixed XOR for fixed key — bijective for every
ks variant.

## Spec table

Chassis for all 31: 4r keyed SPN x_{i+1} = L(P(S16(x_i ^ rk_i))), order LPS,
S1, no whitening, rk_i = rotl64(key,13(i+1)) ^ RC(ks,i).

| # | Candidate | Axis | Spec |
|---|---|---|---|
| 1 | r24_spn_mix4r_pba19b03_nw | P1a: P-box b | a=19, b=03 |
| 2 | r24_spn_mix4r_pba19b05_nw | P1a: P-box b | a=19, b=05 |
| 3 | r24_spn_mix4r_pba19b07_nw | P1a: P-box b | a=19, b=07 |
| 4 | r24_spn_mix4r_pba19b09_nw | P1a: P-box b | a=19, b=09 |
| 5 | r24_spn_mix4r_pba19b11_nw | P1a: P-box b | a=19, b=11 |
| 6 | r24_spn_mix4r_pba19b13_nw | P1a: P-box b | a=19, b=13 |
| 7 | r24_spn_mix4r_pba19b15_nw | P1a: P-box b | a=19, b=15 |
| 8 | r24_spn_mix4r_pba19b17_nw | P1a: P-box b | a=19, b=17 |
| 9 | r24_spn_mix4r_pba19b19_nw | P1a: P-box b | a=19, b=19 |
| 10 | r24_spn_mix4r_pba19b21_nw | P1a: P-box b | a=19, b=21 |
| 11 | r24_spn_mix4r_pba19b23_nw | P1a: P-box b | a=19, b=23 |
| 12 | r24_spn_mix4r_pba19b25_nw | P1a: P-box b | a=19, b=25 |
| 13 | r24_spn_mix4r_pba19b27_nw | P1a: P-box b | a=19, b=27 |
| 14 | r24_spn_mix4r_pba19b29_nw | P1a: P-box b | a=19, b=29 |
| 15 | r24_spn_mix4r_pba29b01_nw | P1b: P-box a | a=29, b=01 (1×64-cycle) |
| 16 | r24_spn_mix4r_pba31b01_nw | P1b: P-box a | a=31, b=01 (16×4-cycle) |
| 17 | r24_spn_mix4r_pba35b01_nw | P1b: P-box a | a=35, b=01 (2×32-cycle) |
| 18 | r24_spn_mix4r_ks_smallodd_nw | P2: key schedule | RC'[i]=2i+1 |
| 19 | r24_spn_mix4r_ks_gold16_nw | P2: key schedule | RC'[i]=(i+1)*0x9E37 |
| 20 | r24_spn_mix4r_ks_rotgolden_nw | P2: key schedule | RC'[i]=rotl64(GOLDEN,8(i+1)) |
| 21 | r24_spn_mix4r_ks_nibrep_nw | P2: key schedule | RC'[i]=(i+1)*0x1111…1111 |
| 22 | r24_spn_mix4r_ks_gold32_nw | P2: key schedule | RC'[i]=(i+1)*0x9E3779B9 |
| 23 | r24_spn_mix4r_ks_altbit_nw | P2: key schedule | RC'[i]=0xAAAA…/0x5555… alt |
| 24 | r24_spn_mix4r_l0317_pb19_nw | P3: linear | L=x^R3^R17 |
| 25 | r24_spn_mix4r_l0513_pb19_nw | P3: linear | L=x^R5^R13 |
| 26 | r24_spn_mix4r_l0517_pb19_nw | P3: linear | L=x^R5^R17 |
| 27 | r24_spn_mix4r_l0711_pb19_nw | P3: linear | L=x^R7^R11 |
| 28 | r24_spn_mix4r_l0717_pb19_nw | P3: linear | L=x^R7^R17 |
| 29 | r24_spn_mix4r_l1113_pb19_nw | P3: linear | L=x^R11^R13 |
| 30 | r24_spn_mix4r_hsaff_pb19_nw | P4: hetero S-box | per-lane affine S1 variants (r23 hs_aff tables) |
| 31 | r24_spn_mix4r_hsalt_pb19_nw | P4: hetero S-box | lanes alternate S1/SB1 (r23 hs_alt tables) |

**P1a design note (cycle-structure lemma, verified numerically):** all 15
O34-valid (19,b odd) share the identical cycle structure [32,32]; all 15
even-b fail O34 (fixed points: 18x≡−b mod 64 solvable iff b even). Reason:
x→ax+b and x→ax+b′ are translation-conjugate iff b≡b′ (mod gcd(a−1,64));
for a=19, gcd(18,64)=2, so all odd b are conjugate. **Matched-a 2-vs-4-cycle
comparison is impossible for affine P-boxes** — the directive's premise was
wrong, verified before sweeping. The b-sweep therefore tests the OFFSET
(wiring), not cycle structure. Cross-a cycle data comes from P1b: (29,1) is
1×64, (31,1) is 16×4, (35,1) is 2×32.

**P1b design note:** (21,1) and (33,1) FAIL the O34 spread criterion (single
64-cycle, but a nibble's 4 bits don't land in 4 distinct nibbles) — recorded
as a spec-build finding, not swept. Valid untested odd-a near 19/27: 29, 31,
35.

**P2 design note:** r23 F7 measured −0.4u for removing GOLDEN constants
(27.9u vs 28.3u baseline) but S1-marginal kill (PB rej=1). P2 keeps constants
NONZERO but synthesis-cheap (few set bits / structured) to keep the delay
win without the marginality. All 6 variants have round-asymmetric nonzero
RC′ (asserted in r24.RK_VARIANTS).

**P3 design note:** O45 re-test — x^rotl(x,R)^rotl(x,S) odd-term variants as
the SPN bit-mixing layer, rank-checked (all rank 64, p(1)=1). r23 P2 mapped
(3,7),(3,13),(5,11),(7,13),(11,17),(1,7) on the (5,27) chassis; P3 tests 6
fresh pairs on the (19,1) chassis (no-retest guard vs r23 asserted in
specs24.py).

## Stage results

*(a) failing signal / (b) mechanistic hypothesis / (c) follow-up per kill —
to be filled as the queue completes)*

| Candidate | xcheck | rtlcheck | S0 | S1 | S2 | S3 | S4 | Q1 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| r24_spn_mix4r_pba19b03_nw | PASS | PASS | 27.9u PASS (5306/14225) | CAL_PASS | KILL (delta 0x0000000000000400, 14 repeats, maxz=6.9) |  |  |  | KILLED |
| r24_spn_mix4r_pba19b05_nw | PASS | PASS | 27.9u PASS (5371/14391) | FLAG (rd_rej=1) |  |  |  |  | KILLED |
| r24_spn_mix4r_pba19b07_nw | PASS | PASS | 27.8u PASS (5376/14375) | CAL_PASS | KILL (delta 0x0000000070000000, 94 repeats, maxz=11.9) |  |  |  | KILLED |
| r24_spn_mix4r_pba19b09_nw | PASS | PASS | 28.4u PASS (4978/13611) | CAL_PASS | PASS | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00943 | SURVIVED |
| r24_spn_mix4r_pba19b11_nw | PASS | PASS | 28.1u PASS (5000/13582) | CAL_PASS | KILL (delta 0x0000000070000000, 116 repeats, maxz=11.8) |  |  |  | KILLED |
| r24_spn_mix4r_pba19b13_nw | PASS | PASS | 27.9u PASS (5259/14251) | CAL_PASS | PASS (max_repeats=0, max|z|=16.7) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00851 | SURVIVED |
| r24_spn_mix4r_pba19b15_nw | PASS | PASS | 27.7u PASS (5438/14446) | CAL_PASS | KILL (delta 0x0000000070000000, 92 repeats, maxz=11.9) |  |  |  | KILLED |
| r24_spn_mix4r_pba19b17_nw | PASS | PASS | 28.3u PASS (5153/14000) | CAL_PASS | PASS (max_repeats=1, max|z|=13.0) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=1, bic=0.00893 | SURVIVED (frontier-ineligible: sac_z5=1) |
| r24_spn_mix4r_pba19b19_nw | PASS | PASS | 27.8u PASS (5135/13873) | CAL_PASS | KILL (delta 0x0000000070000000, 98 repeats, maxz=12.4) |  |  |  | KILLED |
| r24_spn_mix4r_pba19b21_nw | PASS | PASS | 27.8u PASS (5507/14784) | CAL_PASS | PASS (max_repeats=0, max|z|=14.9) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00884 | SURVIVED |
| r24_spn_mix4r_pba19b23_nw | PASS | PASS | 28.0u PASS (5136/13864) | CAL_PASS | KILL (delta 0x0000000070000000, 76 repeats, maxz=11.8) |  |  |  | KILLED |
| r24_spn_mix4r_pba19b25_nw | PASS | PASS | 28.1u PASS (5378/14485) | CAL_PASS | PASS (max_repeats=1, max|z|=8.6) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00902 | SURVIVED |
| r24_spn_mix4r_pba19b27_nw | PASS | PASS | 28.0u PASS (5378/14531) | CAL_PASS | KILL (delta 0x0000000070000000, 115 repeats, maxz=12.3) |  |  |  | KILLED |
| r24_spn_mix4r_pba19b29_nw | PASS | PASS | 28.1u PASS (5264/14289) | CAL_PASS | PASS (max_repeats=0, max|z|=9.6) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00876 | SURVIVED |
| r24_spn_mix4r_pba29b01_nw | PASS | PASS | 27.7u PASS (5474/14628) | CAL_PASS | KILL (delta 0x0000000070000000, 12 repeats, maxz=57.7) |  |  |  | KILLED |
| r24_spn_mix4r_pba31b01_nw | PASS | PASS | 28.2u PASS (4971/13615) | CAL_PASS | PASS (max_repeats=5, max|z|=38.4) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00927 | SURVIVED |
| r24_spn_mix4r_pba35b01_nw | PASS | PASS | 28.4u PASS (4827/13231) | FLAG (diff_rej=1) |  |  |  |  | KILLED |
| r24_spn_mix4r_ks_smallodd_nw | PASS | PASS | 27.9u PASS (5416/14607) | CAL_PASS | PASS (max_repeats=0, max|z|=9.3) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00812 | SURVIVED |
| r24_spn_mix4r_ks_gold16_nw | PASS | PASS | 28.0u PASS (5366/14371) | CAL_PASS | PASS (max_repeats=1, max|z|=7.8) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.01003 | SURVIVED |
| r24_spn_mix4r_ks_rotgolden_nw | PASS | PASS | 28.0u PASS (5308/14370) | CAL_PASS | PASS (max_repeats=0, max|z|=16.6) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00920 | SURVIVED |
| r24_spn_mix4r_ks_nibrep_nw | PASS | PASS | 28.4u PASS (5173/14040) | CAL_PASS | PASS (max_repeats=1, max|z|=13.6) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00845 | SURVIVED |
| r24_spn_mix4r_ks_gold32_nw | PASS | PASS | 28.5u PASS (4683/12860) | CAL_PASS | PASS (max_repeats=1, max|z|=8.7) | PASS (PractRand 1G×2keys) | KILL (sstring_HammingIndep p=8.3e-4) |  | KILLED |
| r24_spn_mix4r_ks_altbit_nw | PASS | PASS | 28.0u PASS (5242/14187) | FLAG (pb_rej=1) |  |  |  |  | KILLED |
| r24_spn_mix4r_l0317_pb19_nw | PASS | PASS | 27.9u PASS (5586/14930) | FLAG (diff_rej=1) |  |  |  |  | KILLED |
| r24_spn_mix4r_l0513_pb19_nw | PASS | PASS | 28.0u PASS (5374/14258) | CAL_PASS | PASS (max_repeats=0, max|z|=4.3) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00959 | SURVIVED |
| r24_spn_mix4r_l0517_pb19_nw | PASS | PASS | 28.3u PASS (5168/14073) | CAL_PASS | PASS (max_repeats=6, max|z|=22.0) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00837 | SURVIVED |
| r24_spn_mix4r_l0711_pb19_nw | PASS | PASS | 27.5u PASS (5380/14515) | FLAG (rd_rej=1) |  |  |  |  | KILLED |
| r24_spn_mix4r_l0717_pb19_nw | PASS | PASS | 26.9u PASS (5789/15521) | FLAG (diff_rej=1) |  |  |  |  | KILLED |
| r24_spn_mix4r_l1113_pb19_nw | PASS | PASS | 28.5u PASS (4944/13733) | CAL_PASS | KILL (delta 0x1000000000000000, 51 repeats, maxz=21.5) |  |  |  | KILLED |
| r24_spn_mix4r_hsaff_pb19_nw | PASS | PASS | 28.2u PASS (5206/14142) | CAL_PASS | PASS (max_repeats=1, max|z|=11.4) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00855 | SURVIVED |
| r24_spn_mix4r_hsalt_pb19_nw | PASS | PASS | 29.0u PASS (5174/14185) | CAL_PASS | PASS (max_repeats=0, max|z|=7.4) | PASS (PractRand 1G×2keys) | PASS (SmallCrush) | sac_z5=0, bic=0.00853 | SURVIVED |

## Failure analyses

*(S1 verdicts verified 2026-10-04 ~20:00Z: 31/31 s1_result.json match progress.log
S1_DONE lines exactly — verdict + all four reject counts. Per s1_screen.py
contract, LIN+DIFF runs FIRST on SEQ outputs (10 keys, N=2^18); a LIN/DIFF kill
skips the marginal PB/RD screen. KEYS = 8 fixed + 2 seeded-random
(0xf0b52a9e7d8ba2b5, 0x92988f142674743). DIFF family: 18 weight-1 deltas
2^0..2^17, 2^17 pairs each, low-8-bit chi2, Fisher-combined; worst_z = worst
two-sided z across the probe.)*

**1. r24_spn_mix4r_pba19b05_nw (P1a, P(i)=(19i+5)%64) — S1 FLAG, rd_rej=1.**
(a) Failing signal: RD-family marginal reject on `('SEQ', key 0x092988f142674743)`
(the seeded-random key); raw worst red z=3.34. Marginal screen ran (not skipped);
LIN/DIFF families clean (rej=0). Raw log: `s1/r24_spn_mix4r_pba19b05_nw/s1_result.json`.
(b) Mechanistic hypothesis: all odd-b P-boxes are translation-conjugate
([32,32] cycle structure — verified numerically), so the b-sweep tests wiring,
not cycle structure. b=5 routes round 1's varying low nibble-bits (sequential
inputs 0..2^18−1 leave the high ~46 bits constant) into lane positions whose
S-box × lin(3,11) chain leaks slightly more through one of the 9 reduction
tests (Lemire X / mask / mod) under this key. A wiring resonance, not a cipher
break — DIFF is clean.
(c) Targeted follow-up: run the `('SEQ', 0x092988f142674743)` probe across all
15 b-values to test whether b=5 is an isolated wiring resonance or part of a
pattern; S2 differential (N=2^22, 115 deltas) for a real differential correlate.
Scoped kill: *"P-box offset b=5 fails in the 4r keyed SPN
x_{i+1}=L(P(S16(x_i^rk_i))) (LPS order, S1, P(i)=(19i+5)%64, L=lin(3,11),
rk_i=rotl64(key,13(i+1))^(i+1)*GOLDEN64, no whitening)"*.

**2. r24_spn_mix4r_pba35b01_nw (P1b, P(i)=(35i+1)%64) — S1 FLAG, diff_rej=1.**
(a) Failing signal: DIFF-family reject on `('DIFF', key 0x92988f142674743)`
(seeded-random key); worst_z=6.55, fisher_logp=−9.17, bonf_logp=−20.69.
LIN/DIFF kill → marginal skipped. Raw log:
`s1/r24_spn_mix4r_pba35b01_nw/s1_result.json`.
(b) Mechanistic hypothesis: (35,1) shares the 2×32-cycle structure with (19,1),
so the difference is the multiplier a itself (orbit mixing), not cycle counts.
The truncated-differential probe detected structure at N=2^18 under this key —
the a=35 wiring admits a differential path that a=19's does not at this sample
size.
(c) Targeted follow-up: S2 differential at N=2^22 × 115 deltas for the exact
delta profile; key-sweep over the 10 calibrated keys to test key-specificity
vs structure.
Scoped kill: *"P-box a=35 fails in the 4r keyed SPN (same chassis as #1,
P(i)=(35i+1)%64)"*.

**3. r24_spn_mix4r_ks_altbit_nw (P2, RC'=0xAAAA…/0x5555… alternating) — S1 FLAG, pb_rej=1.**
(a) Failing signal: PB-family marginal reject on `('SINGLE-BIT', key
0xAAAAAAAAAAAAAAAA)` — the 64 single-bit inputs with the structured key
0xAAAA; raw worst per-bit z=4.0. Marginal ran; LIN/DIFF clean. Raw log:
`s1/r24_spn_mix4r_ks_altbit_nw/s1_result.json`.
(b) Mechanistic hypothesis: key-structure resonance. Odd rotations of an
alternating 64-bit word stay alternating, so rotl64(0xAAAA…,13(i+1)) is still
an alternating pattern; rk_i = alt-key ^ alt-RC' then degenerates (rounds pair
complementary/constant XORs), thinning effective round-key entropy and leaking
a per-bit bias on the single-bit inputs at N=2^18. The failure may be an artifact
of the calibrated key set containing exactly the structured keys that resonate
(0xAAAA, 0x5555 are both in KEYS).
(c) Targeted follow-up: RC'[i]=rotl64(0xAAAAAAAAAAAAAAAA,13i) — keeps structured,
synthesis-cheap constants but breaks the per-round alignment; separately a key
sweep to test whether only the structured keys flag.
Scoped kill: *"alternating-bit round constants fail in the 4r keyed SPN (same
chassis as #1, RC'[i]=0xAAAA…/0x5555… alternating)"*.

**4. r24_spn_mix4r_l0317_pb19_nw (P3, L=x^R3^R17) — S1 FLAG, diff_rej=1.**
(a) Failing signal: DIFF-family reject on `('DIFF', key 0x0123456789ABCDEF)`;
worst_z=10.54, fisher_logp=−55.41, bonf_logp=−55.23 — the strongest kill of the
round. LIN/DIFF kill → marginal skipped. Raw log:
`s1/r24_spn_mix4r_l0317_pb19_nw/s1_result.json`.
(b) Mechanistic hypothesis: the (3,17) odd-term rotation pair as the SPN's
bit-mixing layer admits a truncated differential detectable at N=2^18 (18
weight-1 deltas, 2^17 pairs each, low-8-bit chi2). The rotation offsets couple
S-box input bits into output-bit groups with correlated differences. This is the
O45 HIGH re-test family (nonsingular odd-term x^rotl(x,R)^rotl(x,S) layers);
(3,17) is the weak member of the six pairs tested here.
(c) Targeted follow-up: S2 differential (N=2^22, 115 deltas) to map the
weak-delta profile; compare against passing siblings (5,13)/(5,17)/(11,13) to
delimit the weak-offset set; no further (3,17) variants without a new diffusion
argument.
Scoped kill: *"odd-term linear L=x^R3^R17 fails in the 4r keyed SPN (same
chassis as #1, L=x^R3^R17)"*.

**5. r24_spn_mix4r_l0711_pb19_nw (P3, L=x^R7^R11) — S1 FLAG, rd_rej=1.**
(a) Failing signal: RD-family marginal reject on `('SEQ', key 0x0000000000001234)`;
raw worst red z=4.99 — the round's strongest raw red z. Marginal ran;
LIN/DIFF clean. Raw log: `s1/r24_spn_mix4r_l0711_pb19_nw/s1_result.json`.
(b) Mechanistic hypothesis: on sequential inputs (high ~46 bits constant) with
key 0x1234, the (7,11) layer's rotation geometry interacts with the round-1
nibble structure so one of the 9 reduction tests flags. Plausibly a
low-entropy-input artifact of the SEQ scenario rather than a cipher break —
LIN and DIFF families are both clean, and the flag is single-key.
(c) Targeted follow-up: rerun `('SEQ')` across all 10 calibrated keys to test
key-specificity; S2 differential for a real differential correlate; no verdict
change without S2-level evidence.
Scoped kill: *"odd-term linear L=x^R7^R11 fails in the 4r keyed SPN (same
chassis as #1, L=x^R7^R11)"*.

**6. r24_spn_mix4r_l0717_pb19_nw (P3, L=x^R7^R17) — S1 FLAG, diff_rej=1.**
(a) Failing signal: DIFF-family reject on `('DIFF', key 0x0)` — the null key;
worst_z=6.62, fisher_logp=−18.47, bonf_logp=−21.18. LIN/DIFF kill → marginal
skipped. Raw log: `s1/r24_spn_mix4r_l0717_pb19_nw/s1_result.json`.
(b) Mechanistic hypothesis: truncated-differential structure under the null key
at N=2^18 — the (7,17) odd-term pair couples bit differences into a low-8-bit
chi2-detectable pattern. (Round keys are still nonzero RCs under key 0, so this
is not a null-key degeneracy of the schedule itself.)
(c) Targeted follow-up: key-sweep over the 10 calibrated keys to test whether
the weakness is null-key-specific or structural; S2 differential profile on any
flagging key.
TENSION (reported honestly, not rescued): 26.9u was the round's fastest S0 —
0.9u better than the 27.8u r23 baseline — but the statistical gate fails.
Speed buys no rescue; the candidate is dead in this construction.
Scoped kill: *"odd-term linear L=x^R7^R17 fails in the 4r keyed SPN (same
chassis as #1, L=x^R7^R17), despite the round's best S0 delay"*.

**7. r24_spn_mix4r_pba19b03_nw (P1a, P(i)=(19i+3)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL delta=0x0000000000000400
repeats=14 > kill_repeats=10`, max|z|=6.9, low8_chi2=290.9. Raw log:
`s2_r24_spn_mix4r_pba19b03_nw.log`. Null E[repeats/delta] = 2^−42.
(b) Mechanistic hypothesis: bit-10 delta shows 14 exact output repeats at N=2^22 —
a low-input-bit differential freezing pattern (same bit-10 signature family as
the r22 O31/O32/O34/O35/O37 S2 kills): for sequential inputs the high bits are
constant, the b=3 wiring keeps the bit-10 difference confined to a weak
round-1→2 path that the 4r chassis cannot avalanche.
(c) Targeted follow-up: S2 delta profile across all 15 b-values to map whether
the weak offset set is b-specific (wiring) or chassis-wide; the P1b a-variants
(29/31) are the control.
Scoped kill: *"P-box offset b=3 fails in the 4r keyed SPN (same chassis as #1,
P(i)=(19i+3)%64) — S2 differential kill on bit-10 delta"*.

**8. r24_spn_mix4r_pba19b07_nw (P1a, P(i)=(19i+7)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x0000000070000000 repeats=94 > kill_repeats=10`, max|z|=11.9,
low8_chi2=463.6. Raw log: `s2_r24_spn_mix4r_pba19b07_nw.log`.
(b) Mechanistic hypothesis: bits 28–30 delta freezes — 94 exact output repeats
at N=2^22. The b=7 wiring routes these mid-word bits through a round-1→2
differential path the 4r chassis cannot avalanche for sequential inputs.
S1-passed (CAL_PASS) — S1's N=2^18 DIFF probe was blind to it; the S2
differential at 4× the samples caught the frozen path.
(c) Targeted follow-up: complete the b-sweep S2 profile (b=13..29 pending) to
map the weak-offset set; b=9's PASS is the within-family control.
Scoped kill: *"P-box offset b=7 fails in the 4r keyed SPN (same chassis as #1,
P(i)=(19i+7)%64) — S2 differential kill on bits 28–30 delta"*.

**9. r24_spn_mix4r_pba19b11_nw (P1a, P(i)=(19i+11)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x0000000070000000 repeats=116 > kill_repeats=10`, max|z|=11.8,
low8_chi2=367.5. Raw log: `s2_r24_spn_mix4r_pba19b11_nw.log`.
(b) Mechanistic hypothesis: same bits 28–30 freezing as b=7 (116 repeats —
the strongest S2 kill of the round so far). The b=7/b=11 pair shares the
freezing delta while b=3 froze bit 10 and b=9 passes: differential freezing is
wiring-offset-dependent. Note the tension with the P1a design note — odd-b
P-boxes are translation-conjugate (identical cycle structure), but conjugacy
does not survive composition with the fixed S-box/L layers, so differential
behavior legitimately varies with b.
(c) Targeted follow-up: same b-sweep profile; if the weak set clusters,
characterize the b↔delta mapping as a predictive rule for future P-box picks.
Scoped kill: *"P-box offset b=11 fails in the 4r keyed SPN (same chassis as
#1, P(i)=(19i+11)%64) — S2 differential kill on bits 28–30 delta"*.

**10. r24_spn_mix4r_pba19b15_nw (P1a, P(i)=(19i+15)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x0000000070000000 repeats=92 > kill_repeats=10`, max|z|=11.9,
low8_chi2=451.7. Raw log: `s2_r24_spn_mix4r_pba19b15_nw.log`. (Recovered
post-cancellation: log verified complete — delta row + col-0 KILL final line;
deterministic fixed-key run, ingested rather than re-run.)
(b) Mechanistic hypothesis: third member of the bits 28–30 freezing family
(after b=7 at 94, b=11 at 116 repeats). The weak b-set is now {3,7,11,15,19}
= b≡3 (mod 4); the S2-clean set so far is {9,13,17} plus the r23 baseline b=1
= b≡1 (mod 4). Conjugacy was mod 2 (all odd b), but the S-box/lin layers
partition bits into 4-bit nibbles, and b mod 4 controls the intra-nibble
alignment of the P-box output: (19i+b) mod 4 = (3i+b) mod 4, so b→b+2 shifts
every bit's lane position by 2 — a genuine mod-4 sub-class structure that the
translation conjugacy does not protect. b≡3 mod 4 admits the freezing path;
b≡1 mod 4 does not.
(c) Targeted follow-up: b=21/25/29 (b≡1 mod 4) predicted S2-PASS; b=23/27
(b≡3 mod 4) predicted S2-KILL — all five are pending in this round's queue.
Confirming the prediction converts the hypothesis into a verified b-mod-4
selection rule for future affine-P-box picks.
Scoped kill: *"P-box offset b=15 fails in the 4r keyed SPN (same chassis as
#1, P(i)=(19i+15)%64) — S2 differential kill on bits 28–30 delta"*.

**11. r24_spn_mix4r_pba19b19_nw (P1a, P(i)=(19i+19)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x0000000070000000 repeats=98 > kill_repeats=10`, max|z|=12.4,
low8_chi2=364.5. Raw log: `s2_r24_spn_mix4r_pba19b19_nw.log`. (Recovered
post-cancellation, same as #10.)
(b) Mechanistic hypothesis: fourth member of the bits 28–30 freezing family
(b=7/11/15/19: repeats 94/116/92/98 — remarkably consistent). Weak set
{3,7,11,15,19} = b≡3 (mod 4) grows to five; clean set stays b≡1 (mod 4).
The b=3 case froze bit 10 instead of bits 28–30 — one weak sub-class, two
freezing deltas; the remaining ≡3-mod-4 candidates (b=23, 27, pending) will
test whether the delta choice is predictable too.
(c) Targeted follow-up: same as #10 — the five pending b-values are the
confirmatory experiment. If b=23/27 kill and b=21/25/29 pass, the mod-4 rule
is confirmed and the (19,1) chassis's S2-clean b-set is exactly {1,9,13,17,21,25,29}.
Scoped kill: *"P-box offset b=19 fails in the 4r keyed SPN (same chassis as
#1, P(i)=(19i+19)%64) — S2 differential kill on bits 28–30 delta"*.

**12. r24_spn_mix4r_pba19b23_nw (P1a, P(i)=(19i+23)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x0000000070000000 repeats=76 > kill_repeats=10`, max|z|=11.8,
low8_chi2=432.8. Raw log: `s2_r24_spn_mix4r_pba19b23_nw.log`.
(b) Mechanistic hypothesis: fifth member of the bits 28–30 freezing family
(b=7/11/15/19/23: 94/116/92/98/76 repeats). The mod-4 prediction from #10–11
holds: b≡3 (mod 4) → KILL, b≡1 (mod 4) → PASS (b=21 passed this same batch).
(c) Targeted follow-up: b=27 (last untested ≡3-mod-4 value) predicted KILL;
b=25/29 (≡1) predicted PASS — all three in this batch.
Scoped kill: *"P-box offset b=23 fails in the 4r keyed SPN (same chassis as
#1, P(i)=(19i+23)%64) — S2 differential kill on bits 28–30 delta"*.

**13. r24_spn_mix4r_pba19b27_nw (P1a, P(i)=(19i+27)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x0000000070000000 repeats=115 > kill_repeats=10`, max|z|=12.3,
low8_chi2=375.7. Raw log: `s2_r24_spn_mix4r_pba19b27_nw.log`.
(b) Mechanistic hypothesis: sixth and final member of the bits 28–30
freezing family (repeats 94/116/92/98/76/115 across b=7/11/15/19/23/27).
**The mod-4 rule is now confirmed 7/7:** weak = {3,7,11,15,19,23,27} =
b≡3 (mod 4) — all killed; clean = {1,9,13,17,21,25,29} = b≡1 (mod 4) — all
S2-passed (b=1 is the r23 baseline, full battery PASS). Mechanism: b mod 4
controls the intra-nibble alignment of the P-box output —
(19i+b)≡(3i+b) (mod 4) — and b→b+2 shifts every bit's lane position by 2
inside the 4-bit S-box/lin nibble structure. The translation conjugacy was
only mod 2; the fixed nibble-partitioned layers see two genuine sub-classes.
b≡3 (mod 4) admits the freezing differential path; b≡1 (mod 4) does not.
(c) Targeted follow-up: none needed for the rule itself — the prediction was
made before the batch and confirmed 7/7. Design consequence: future
affine-P-box picks on this chassis must use **b≡1 (mod 4)**; the (19,1)
chassis's S2-clean offset set is exactly {1,9,13,17,21,25,29}.
Scoped kill: *"P-box offset b=27 fails in the 4r keyed SPN (same chassis as
#1, P(i)=(19i+27)%64) — S2 differential kill on bits 28–30 delta"*.

**14. r24_spn_mix4r_pba29b01_nw (P1b, P(i)=(29i+1)%64) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x0000000070000000 repeats=12 > kill_repeats=10`, max|z|=57.7,
low8_chi2=1355.5 (null ≈235). Raw log: `s2_r24_spn_mix4r_pba29b01_nw.log`.
(b) Mechanistic hypothesis: the same bits 28–30 delta that froze the
(19,b≡3) family also freezes the (29,1) 1×64-cycle P-box — but much more
weakly (12 full repeats vs 76–116). The marginal full-repeat count (2 over
threshold) is NOT a threshold fluke: the low-8-bit chi2 of 1355.5 vs a
~235 null is extreme, an independent confirmation of real differential
structure. The 1×64-cycle's finer orbit mixing partially avalanches the
weak path — enough to collapse exact full-64 repeats, not enough to restore
the low-8-bit distribution. (a=29 shares the 1×64-cycle with the O34-failing
(21,1)/(33,1) but passed the O34 spread check — cycle structure is not the
decisive axis here.)
(c) Targeted follow-up: re-run S2 with a second key to test robustness of the
marginal full-repeat kill (the chi2 signal predicts it reproduces);
compare against the surviving (31,1) 16×4-cycle sibling to test whether
finer cycle granularity correlates with weaker freezing.
Scoped kill: *"P-box a=29 fails in the 4r keyed SPN (same chassis as #1,
P(i)=(29i+1)%64) — S2 differential kill on bits 28–30 delta (12 full repeats,
chi2 1355.5 vs 235 null)"*.

**15. r24_spn_mix4r_l1113_pb19_nw (P3, L=x^R11^R13) — S2 KILL.**
(a) Failing signal: S2 differential, N=2^22, 115 deltas: `KILL
delta=0x1000000000000000 repeats=51 > kill_repeats=10`, max|z|=21.5,
low8_chi2=789.6. Raw log: `s2_r24_spn_mix4r_l1113_pb19_nw.log`.
(b) Mechanistic hypothesis: the (11,13) odd-term pair admits a bit-52
differential freeze the 4r chassis cannot avalanche. The P3 scorecard is now
complete: (3,17) killed at S1, (7,11) and (7,17) flagged at S1, (11,13)
killed at S2 — and the only survivors are the two pairs with smaller offset
5: (5,13), (5,17). Pattern: pairs with min(R,S)≥7 fail; min(R,S)=5 survives.
Larger rotation offsets couple difference bits into coherent groups the
S-box layer cannot decorrelate (bit-52 resonance for (11,13)); the (5,x)
geometry diffuses before the groups cohere.
(c) Targeted follow-up: test the min(R,S)≥7 rule with one more pair, e.g.
(5,11) (predicted PASS) vs (9,11) (predicted KILL); the O45 HIGH re-test
trigger on odd-term layers stays open for the (5,13)/(5,17) survivors.
Scoped kill: *"odd-term linear L=x^R11^R13 fails in the 4r keyed SPN (same
chassis as #1, L=x^R11^R13) — S2 differential kill on bit-52 delta"*.

**16. r24_spn_mix4r_ks_gold32_nw (P2, RC'[i]=(i+1)*0x9E3779B9) — S4 KILL.**
(a) Failing signal: S4 SmallCrush (single key 0x123456789ABCDEF0):
`sstring_HammingIndep p=8.3e-4 < 0.001` — the only failing statistic of 15;
all other tests passed. S3 PractRand 1G×2keys was clean, S2 PASS
(max_repeats=1). Raw log: `survivors/r24_spn_mix4r_ks_gold32_nw/s4.log`.
(b) Mechanistic hypothesis: the 32-bit golden-ratio round constants leave a
Hamming-weight correlation signature across consecutive output blocks that the
16-bit gold16 (0x9E37), smallodd (2i+1), rotgolden and nibrep variants do not —
HammingIndep tests independence of consecutive-block Hamming weights, and it is
the ONLY failing test, so this is a weight-transition weakness, not a
bitstream-uniformity one (S3 clean). The 32-bit structured constant's bit
pattern interacts with the per-round key XORs to bias weight transitions.
(c) Targeted follow-up: re-run S4 on the second PractRand key to test
key-specificity vs structural; compare HammingIndep p-values across the full
P2 family to isolate the constant-width effect.
Parse note (honest): run_survivors.sh's first S4 grep looks for the singular
"gave a p-value outside" but TestU01 1.2.3 prints the plural "gave p-values
outside" — the kill was still registered via the "All tests were passed"
fallback check (a failing run prints "All other tests were passed"), so the
verdict is correct; only the logged reason string ("no pass confirmation") is
misleading. Verdict-parse patterns must be tested against actual tool output.
Scoped kill: *"32-bit golden-ratio round constants RC'[i]=(i+1)*0x9E3779B9
fail in the 4r keyed SPN (same chassis as #1) — S4 SmallCrush kill
(sstring_HammingIndep p=8.3e-4)"*.

## Winners

*(full battery + Q1 sac_z5=0 with Pareto improvement; PARETO.md updated by parent only)*

**r24_spn_mix4r_pba19b21_nw — speed-point size play: 27.8u / 5,507 / 14,784.**
Ties the r23 pba19b01 speed point's delay at S0's 1-decimal reporting
precision (crit=27.8, delay_ratio 0.269 — identical; XCHECK analyze.py ==
analyze2.py) at −225 cells (−3.9%) / −590 area (−3.8%) → strict Pareto
improvement on the speed point on two axes at equal reported delay. Full
battery: S1 CAL_PASS (rej=0); S2 PASS (max_repeats=0, max|z|=14.9, all 115
deltas); S3 PractRand 1G clean on both key configs (key1 + strided key2);
S4 SmallCrush all 15 statistics passed; bijectivity 2M×2 keys collision-free;
Q1 sac_z5=0, bic_maxcorr=0.00884 (≤0.02 → Frontier-Q eligible in the same
slot; also beats r23's bic 0.01092). Mechanism: the b=21 offset is a member
of the S2-clean ≡1-mod-4 class (confirmed 7/7 this round, analyses #10–13);
the wiring change vs b=1 buys the size win at no delay cost. Raw logs:
`survivors/r24_spn_mix4r_pba19b21_nw/{s3.log,s3b.log,s4.log,bij1.log,bij2.log,q1.log}`,
`q1/q1_r24_spn_mix4r_pba19b21_nw.json`,
`s2_r24_spn_mix4r_pba19b21_nw.log`, `s0/r24_spn_mix4r_pba19b21_nw.log`.
Parent action for PARETO.md: b21 takes the 27.8u speed-point slot on
Frontier S (retiring r23 pba19b01, strictly dominated on cells+area at the
reported delay) and the same slot on Frontier Q (bic-clean).

**Battery-passers without Pareto improvement (threshold-exclusion / dominated):**
- b13 (27.9u/5,259/14,251, bic 0.00851): vs wf2d_aff_a17_b17 (27.9u/5,299/14,223)
  — delay tie, −40 cells, +28 area; a wash, no improvement → threshold-excluded.
- b31 (28.2u/4,971/13,615, bic 0.00927): vs r22c (28.3u/4,656/12,949) — 0.1u
  edge at +6.8% cells / +5.1% area; the r23-pba27b01 precedent (0.1u at +9%
  cells → excluded) applies directly → threshold-excluded.
- smallodd (27.9u/5,416/14,607, bic 0.00812), gold16 (28.0u/5,366/14,371,
  bic 0.01003), rotgolden (28.0u/5,308/14,370, bic 0.00920), l0513
  (28.0u/5,374/14,258, bic 0.00959): all dominated by wf2d/b13 on
  delay+cells+area.
- b09 (28.4u/4,978/13,611, bic 0.00943), b25 (28.1u/5,378/14,485, bic 0.00902),
  b29 (28.1u/5,264/14,289, bic 0.00876), nibrep (28.4u/5,173/14,040,
  bic 0.00845), l0517 (28.3u/5,168/14,073, bic 0.00837), hsaff
  (28.2u/5,206/14,142, bic 0.00855), hsalt (29.0u/5,174/14,185, bic 0.00853):
  dominated within the round (by b13/b21/b31) or by r22c.
- b17 (28.3u/5,153/14,000, bic 0.00893): full battery PASS but **sac_z5=1**
  (q1 JSON verified) → frontier-ineligible (sac_z5=0 mandatory for all
  frontier claims); pipeline-complete, not a winner.
- gold32: S4 KILL (analysis #16), not a winner.

**Round tally:** 31 candidates → 6 S1 FLAGs (analyses #1–6) + 9 S2 KILLs
(analyses #7–15) → 16 S3 entrants → 15 battery-passers (14 frontier-eligible:
all sac_z5=0, bic 0.00812–0.01003, all ≤0.02) + 1 S4 kill (gold32, analysis
#16) → **1 Pareto winner (b21)**. P1a's mod-4 rule (b≡1 clean / b≡3 weak,
7/7 confirmed) is the round's durable design output; P2's key-schedule sweep
yielded no delay win (gold16/rotgolden/smallodd all ≥27.9u, gold32 S4-killed);
P3's odd-term re-test closed with min(R,S)=5 as the surviving geometry
((5,13)/(5,17) both full-battery clean); P4's hetero S-boxes both survived
but are dominated (hsaff 28.2u, hsalt 29.0u).
