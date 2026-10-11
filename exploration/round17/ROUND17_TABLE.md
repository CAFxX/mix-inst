# Round 17 — 5-round probes, O3/O4 re-tests, parsplit variants

**Date:** 2026-10-03. **Frontier after round:** UNCHANGED
{r13_feist6_alt_s1chi_nw: 40.1u, r15_feist6_parsplit_nw: 40.7u,
r9_feist6_rot311_nw: 41.0u, r8_feist6_s1_1sbox_nw: 42.9u}.

**Multiplier reference:** 103.5u (pinned Yosys-0.69 flow; S0 bar ≤ 93.15u).
All 10 candidates pass S0.

## Families

- **F1** — 5r parsplit-F: F = lin(3,11)(S1(R[15:0]) || chi16(R[31:16])) ^ rk,
  5 rounds, no whitening (highest-value probe: 5r phase transition was
  established for the single-S1 F; parsplit-F is stronger).
- **F2** — 5r alt: rounds 1,3,5 S1-F / rounds 2,4 chi-F (`alt_s1chi`);
  and chi-first order probe (`alt_chifirst`: rounds 1,3,5 chi-F).
- **F3** — [re-test O4] `parmix`: 6r, F = lin(3,11)(S1(R^rk)) ^
  lin(3,11)(chi32(R)) (r14's version died at 4r; tested here at 6r).
- **F4** — [re-test O3] `alt_pshalf`: 6r alt, odd (S1) rounds apply S1 to the
  low 16 bits of R only (high 16 pass through the linear layer unmodified),
  even chi rounds unchanged.
- **F5** — `dbs1split`: 6r parsplit geometry, S1 on R[15:0] and S1rev on
  R[31:16] (S1rev = S1 composed with nibble bit-reversal; affine-equivalent
  S-box, different active bit positions). Probes whether more S-box coverage
  cleans parsplit's S2 |z|=18.6.
- **F6** — `parsplit_chioff01`: 6r parsplit with chi16 offsets (0,1)
  (r16 tested (2,3); (1,2) is the incumbent).
- **F7** — `premix`: 6r, F = lin(3,11)(S1(R ^ rotl32(R,16))) ^ rk.
- **F8** — 4r parsplit-F (S1-gated probe only).
- **F9** — 5r parsplit-F with lin(7,13) (rotation data point at 5r).

All: 32-bit halves, {R,L} output, NO whitening, affine r7/r8/r9 key schedule.
Generator: `round17/gen_r17.py`; reference: `round17/models/r17.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 for all 10 — first try on all
novel conventions (S1rev bit-reversed DNF nibbles, chi16(0,1), parmix
key-inside-S1, pshalf, premix). One generator bug caught by hand-review
before emission: the parmix Verilog XORed rk after the S-box (mid-key
semantics) instead of into R before it — fixed, then xcheck/rtlcheck passed.
Self-tests: S1 DNF 4×16, S1REV vs brute-force bit-reversal (16 values),
chi16(0,1) vs bit loop (200 vectors). Dedupe: all 10 specs
pairwise-distinct by numpy model output before generation.

## S0 (run_synth.py, authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r17_feist5_parsplit_nw | 35.0u | 0.338× | 3,590 | 10,217 | faster+smaller than speed point — Pareto-eligible iff battery-clean |
| r17_feist5_alt_s1chi_nw | 34.3u | 0.331× | 3,508 | 10,078 | faster+smaller than speed point — Pareto-eligible iff battery-clean |
| r17_feist5_parsplit_713_nw | 35.4u | 0.342× | 3,664 | 10,251 | S1-killed |
| r17_feist5_alt_chifirst_nw | 34.9u | 0.337× | 3,774 | 10,637 | S1-killed |
| r17_feist6_parsplit_chioff01_nw | 39.1u | 0.378× | 3,573 | 10,067 | would dominate r13 alt AND r15 parsplit — S1-killed |
| r17_feist6_alt_pshalf_nw | 37.7u | 0.364× | 4,015 | 11,535 | S1-killed |
| r17_feist6_premix_nw | 21.0u | 0.203× | 1,723 | 5,324 | S1-killed (structural: x^rotl32(x,16) is 2^16-to-1) |
| r17_feist6_dbs1split_nw | 41.7u | 0.403× | 4,642 | 12,843 | dominated by r9 (41.0u/4,265/11,996) — no S2 per precedent |
| r17_feist6_parmix_nw | 54.6u | 0.528× | 10,368 | 28,955 | S1-killed |
| r17_feist4_parsplit_nw | 28.3u | 0.273× | 2,760 | 7,951 | S1-killed (S1-gated probe: stop) |

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r17_feist5_parsplit_nw | **CAL_PASS** | full screen clean |
| r17_feist5_alt_s1chi_nw | **CAL_PASS** | full screen clean |
| r17_feist6_dbs1split_nw | **CAL_PASS** | full screen clean (dominated — no S2) |
| r17_feist6_parmix_nw | **FLAG** | DIFF rej=7, worst\|z\|=857.6 |
| r17_feist6_alt_pshalf_nw | **FLAG** | DIFF rej=1 (marginal), worst\|z\|=2.3 |
| r17_feist5_alt_chifirst_nw | **FLAG** | LIN/DIFF pass; PB rej=7 |
| r17_feist6_parsplit_chioff01_nw | **FLAG** | DIFF rej=3, worst\|z\|=246.5 |
| r17_feist6_premix_nw | **FLAG** | LIN rej=10 + DIFF rej=10, worst\|z\|=272775.1 |
| r17_feist4_parsplit_nw | **FLAG** | LIN rej=10 + DIFF rej=10, worst\|z\|=940.9 |
| r17_feist5_parsplit_713_nw | **FLAG** | DIFF rej=5, worst\|z\|=2.1 |

Notable: the 5r phase transition does NOT reproduce at the S1 level for the
stronger Fs — both 5r parsplit-F and 5r alt (S1-first) CAL_PASS. S1-first
order matters at 5r (chi-first dies on PB rej=7). Rotation pair controls the
5r boundary: parsplit-F passes S1 with (3,11) but fails DIFF rej=5 with
(7,13).

## S2 (N=2^22, 115 deltas, kill threshold 10 — verified at call site)

| Candidate | S2 verdict | Detail |
|---|---|---|
| r17_feist5_parsplit_nw | **KILL** | delta 0x0000000100000000: repeats=33 > 10, max\|z\|=217.2 |
| r17_feist5_alt_s1chi_nw | **KILL** | delta 0x0000000100000000: repeats=45 > 10, max\|z\|=1215.8 |

Both 5r S1-passers die on the SAME single-bit delta (input bit 32, the low
bit of L) with large repeat counts. The 6r versions of both structures are
S2-clean (parsplit 6r: 0 repeats, |z|=18.6; alt 6r: 0 repeats, |z|=10.7).
The 5r phase transition therefore holds at the S2 differential level for ALL
tested F strengths (single-S1, parsplit-F, alt S1/chi) — S1's marginal screen
is blind to it for the stronger Fs, S2 is the gate that holds. No Q1/S3/S4
(no frontier claim survives).

## Findings (scoped per VERDICT_SCOPE.md)

1. **5r is dead at S2 for every tested F.** 5r parsplit-F and 5r alt (S1-first)
   pass the full S1 screen at ~34-35u but both show a strong differential on
   input bit 32 (33/45 repeats, |z| 217/1216). The phase transition is
   F-strength-dependent at S1 (stronger Fs pass) but round-count-absolute at
   S2. Frontier stays at 6 rounds.
2. **[O4 closed]** Parallel S1+chi in one F fails DIFF at 6r (rej=7,
   |z|=857.6) as well as 4r (r14: LIN rej=9 + DIFF rej=10). The construction
   is unsound at both round counts; verdict no longer round-scoped.
3. **[O3 closed]** Partial-S-box F fails in the heterogeneous alt context too:
   half-S1 odd rounds die on DIFF rej=1 (marginal). Combined with r12
   (homogeneous: 8r to pass S1, then S2-killed on un-S-boxed bits), the
   verdict is now multi-context.
4. **Order matters at 5r:** 5r alt S1-first CAL_PASS vs chi-first PB rej=7 —
   same lesson as r14's 6r (S1-first 40.1u/|z|=10.7 vs chi-first 41.4u/
   |z|=15.0), now at the statistical-kill level.
5. **chi16 offsets (0,1) are bad in parsplit-F:** DIFF rej=3, |z|=246.5.
   The tempting 39.1u would-be dominator dies here. (1,2) offsets stand;
   (2,3) dominated (r16).
6. **premix is structurally degenerate:** x ^ rotl32(x,16) has kernel
   {x : low16 == high16} (2^16-to-1), so F sees 16 effective input bits.
   S0's 21.0u/1,723 cells were true for the degenerate design — same lesson
   class as r13's naive Lai-Massey (fast number, broken design). Killed at
   S1 LIN+DIFF rej=10.
7. **4r barrier holds for parsplit-F** (LIN+DIFF rej=10) — stronger F does
   not buy down the round count below 5r statistically, and 5r fails at S2.
8. **dbs1split is statistically clean** (CAL_PASS) at 41.7u but dominated by
   r9 — heterogeneous S-boxes (S1/S1rev) don't beat the homogeneous S1-F on
   delay. Whether they clean parsplit's |z|=18.6 is untested (no S2 per
   precedent); recorded as open, low value.
