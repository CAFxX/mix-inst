# Round 21 — chioff31 compound, fm cures on r20, 3-rot in notr, key-in-chi × (3,1)

**Date:** 2026-10-03. **Frontier after round:**
Frontier S = {r21 chioff31final 36.7u/4,198/12,005,
r21 3rot_ns 37.4u/3,667/10,742} (r20 chioff13all, r19 chioff13, r20 chioff31
all retired — dominated).
Frontier Q = {r19 fm07 38.8u, r21 chioff13all_fm311 39.1u, r19 fm311 39.5u,
r15 parsplit 40.7u, r9 41.0u, r8 42.9u} (r19 fm11 retired — dominated).
Entering: Frontier S {r20 chioff13all 37.0u/4,357/12,511, r19 chioff13
37.4u/4,149/11,820, r20 chioff31 37.5u/3,863/11,199}.
Frontier Q entering: {r19 fm07 38.8u, fm11 39.3u, fm311 39.5u, r15 parsplit
40.7u, r9 41.0u, r8 42.9u} — all battery-confirmed in round 20.

**Multiplier reference:** 103.5u (pinned Yosys-0.69 flow; S0 bar ≤ 93.15u).

## Families (all 6r Feistel, no whitening, affine r7/r8/r9 key schedule)

Baseline (r20 notr): odd rounds F_S1 = lin(3,11)(S1(R))^rk, even rounds
2,4 F_chi = lin(3,11)(chi32(R))^rk, round 6 F = chi32(R)^rk (truncated).

- **chioff31all**: chi variant (3,1) [b_i = a_i ^ (~a_{i+3} & a_{i+1})] on
  rounds 2,4 AND truncated round 6 — does the r20 size play compound with
  the truncated-final speed?
- **chioff31final**: (1,3) chi on 2,4; (3,1) chi on truncated round 6 only —
  does (3,1) buy speed on round 6, or only size?
- **chioff13all_fm07 / chioff31_fm07 / chioff13all_fm311**: fm cures on the
  r20 notr variants — can Frontier Q's speed point move below 38.8u?
- **3rot / 3rot_chioff13**: 3-rotation linear lin = x^R³x^R⁷x^R¹¹x on all
  five linear rounds, chi-F (plain / chi(1,3)) — O2 re-test: r16 showed
  3-rot is statistically fine with chi-F, but tested only (3,11)-odd-round
  hybrids; here all rounds use the 3-rot layer in pure notr.
- **keyin31 / keyinw**: key-inside-chi on round 6 — (3,1)-variant chi
  (keyin31) and wide-input variant (keyinw); O25 was (1,3)-only.
- **chioff21**: chi variant (2,1) [b_i = a_i ^ (~a_{i+2} & a_{i+1})] on
  rounds 2,4, plain chi final — a second offset in the family.
- **3rot_ns** (added mid-round, diagnosis probe): nonsingular 3-rotation
  layer lin3ns = R³x^R⁷x^R¹¹x (identity term dropped) — tests whether the
  3rot S1-LIN kill was singularity rather than rotation count. Not a
  frontier attempt; see Failure analyses.

Generator: `round21/gen_r21.py`; reference: `round21/models/r21.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 — results in `round21/xcheck/`,
`round21/rtlcheck/`. Round-key indexing: (i+2) convention (round-11 lesson);
all 11 first try. The tail-skip for key-baking tags was generalized
(`tag.startswith("chi_fm") or tag.endswith("_keyin_notr")`) — round-20
escape-protocol lesson applied proactively (class hunt at design time).

## S0 (run_synth.py, authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r21_feist6_alt_notr_chioff31all_nw | 37.2u | 0.359× | 4,420 | 12,627 | dominated by chioff31final |
| r21_feist6_alt_notr_chioff31final_nw | **36.7u** | 0.354× | 4,198 | 12,005 | **faster than chioff13all (37.0u)** — full battery |
| r21_feist6_alt_notr_chioff13all_fm07_nw | 39.4u | 0.381× | 4,870 | 13,729 | fm: Frontier-Q candidate |
| r21_feist6_alt_notr_chioff31_fm07_nw | 39.2u | 0.379× | 4,661 | 13,159 | fm: Frontier-Q candidate |
| r21_feist6_alt_notr_3rot_nw | 41.2u | 0.398× | 5,279 | 14,964 | S1-KILLED (LIN) |
| r21_feist6_alt_notr_3rot_chioff13_nw | 41.6u | 0.402× | 5,292 | 15,022 | S1-KILLED (LIN) |
| r21_feist6_alt_notr_keyin31_nw | 36.9u | 0.356× | 4,191 | 11,986 | near-dup of chioff31final — verify, then threshold-exclude |
| r21_feist6_alt_notr_keyinw_nw | 36.8u | 0.356× | 4,481 | 12,823 | strictly dominated by chioff31final |
| r21_feist6_alt_notr_chioff21_nw | 38.3u | 0.370× | 4,042 | 11,556 | dominated by r20 chioff31 |
| r21_feist6_alt_notr_chioff13all_fm311_nw | 39.1u | 0.378× | 4,485 | 12,763 | fm: Frontier-Q candidate |
| r21_feist6_alt_notr_3rot_ns_nw | **37.4u** | 0.361× | **3,667** | **10,742** | **dominates r20 chioff31 on all axes** — full battery |

All pass the S0 bar. Multiplier ref: 103.5u.

**Frontier-S triage (all confirmed):** chioff31final (36.7u/4,198/12,005)
strictly dominates chioff13all on all three axes → battery clean,
chioff13all retired. 3rot_ns (37.4u/3,667/10,742) strictly dominates r20
chioff31 AND r19 chioff13 → battery clean, both retired. keyinw and
chioff31all strictly dominated by chioff31final → no battery. chioff21
dominated by r20 chioff31 → no battery. keyin31 (+0.2u, −7 cells, −19 area
vs chioff31final) → battery clean, then threshold-excluded per Carlo's
standing rule (0.1%-class area edge below flow threshold).

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| chioff31all | **CAL_PASS** | rej=0 all four families |
| chioff31final | **CAL_PASS** | rej=0 all four families |
| chioff13all_fm07 | **CAL_PASS** | rej=0 all four families |
| chioff31_fm07 | **CAL_PASS** | rej=0 all four families |
| 3rot | **KILLED** | LIN rej=9 (D=132–160/4096, logp −133…−187); DIFF clean |
| 3rot_chioff13 | **KILLED** | LIN rej=9; DIFF clean |
| keyin31 | **CAL_PASS** | rej=0 all four families |
| keyinw | **CAL_PASS** | rej=0 all four families |
| chioff21 | **CAL_PASS** | rej=0 all four families |
| chioff13all_fm311 | **CAL_PASS** | rej=0 all four families |
| 3rot_ns | **CAL_PASS** | rej=0 all four families — singularity diagnosis CONFIRMED |

9/11 CAL_PASS (8/10 of the designed set). The 3-rot kills are
construction-specific: r16's chi-F 3-rot evidence (O2) used the 3-rot layer
only on even rounds with nonsingular lin(3,11) on odd rounds; here the
layer is on all five linear rounds. See Failure analyses for the mechanism
and the 3rot_ns follow-up.

## S2 (N=2^22, 115 deltas, kill threshold 10)

Run for the 8 S1-passing, non-strictly-dominated candidates.

| Candidate | S2 verdict | max\|z\| | repeats |
|---|---|---:|---:|
| chioff31all | **PASS** | 12.5 | 0 |
| chioff31final | **PASS** | 11.2 | 0 |
| chioff13all_fm07 | **PASS** | 11.2 | 0 |
| chioff31_fm07 | **PASS** | 12.5 | 0 |
| keyin31 | **PASS** | 12.5 | 0 |
| keyinw | **PASS** | 12.5 | 0 |
| chioff21 | **PASS** | 12.3 | 0 |
| chioff13all_fm311 | **PASS** | 11.2 | 0 |

8/8 S2-clean, 0 repeats everywhere — the |z| column is load-bearing here
and all values sit at the family norm (10.7–12.5). No truncation-class
breakage (cf. r19 notr5 |z|=477, r20 drop4 |z|=743).

| 3rot_ns (probe) | **PASS** | 4.7 | 0 |

The probe's |z|=4.7 is the round's best — the nonsingular 3-rot diffusion
is differentially the cleanest of the tested linears.

## Q1 (SAC/BIC, N=2^18, fixed key, same script/procedure as r13/r18/r19)

| Candidate | sac_z5 | sac_maxdev | bic_maxcorr | avalanche_mean |
|---|---|---:|---:|---:|
| chioff31all | 0 ✓ | 0.00378 | 0.14076 (blemish) | — |
| chioff31final | 0 ✓ | 0.00359 | 0.14029 (blemish) | — |
| chioff13all_fm07 | 0 ✓ | 0.00362 | **0.00892** ✓ | — |
| chioff31_fm07 | 0 ✓ | 0.00390 | **0.00851** ✓ | — |
| keyin31 | 0 ✓ | 0.00378 | 0.14092 (blemish) | — |
| keyinw | 0 ✓ | 0.00378 | 0.14375 (blemish) | — |
| chioff21 | 0 ✓ | 0.00417 | 0.17366 (blemish, worst of family) | — |
| chioff13all_fm311 | 0 ✓ | 0.00364 | **0.00860** ✓ | — |

sac_z5=0 (mandatory) holds for all. BIC blemish class persists on every
non-fm variant (unmixed final chi, structural); the three fm cures are all
≤ 0.02, Frontier-Q eligible. Note chioff21's 0.17366 — the (2,1) offset's
wider-spread AND-term leaves slightly stronger bit correlations.

| 3rot_ns (probe) | 0 ✓ | 0.00366 | 0.25384 (blemish, worst of family) | — |

The probe's BIC blemish (0.254) is markedly stronger than the family norm
(0.14–0.17) — structural, not noise (the family value is stable across 10+
candidates). Hypothesis: lin3ns drops the identity term, so every linear
output bit is a pure combination of three OTHER bits; through five rounds
this entangles the (R_5, L_5) bits feeding the unmixed final chi more
tightly, amplifying the final-chi correlated-flip structure that r19
identified as the blemish carrier. Consequence: 3rot_ns is a Frontier-S
candidate only (BIC reported, not gated); any Frontier-Q claim would need
the fm cure on top.

## S3 / S4

| Candidate | S3 (2 PractRand configs, 1GB) | S4 SmallCrush | Battery |
|---|---|---|---|
| keyin31 | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| chioff31final | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| chioff31_fm07 | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| chioff13all_fm07 | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| chioff13all_fm311 | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| 3rot_ns | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |

Battery queue: detached, 2 concurrent, `run_battery_queue.sh`, progress in
`round21/battery_progress.log`. A mid-queue VM reboot killed chioff31final's
S4 after S3/S3b had passed; iverilog was reinstalled from the apt cache
(per AGENTS.md reboot lesson) and the S4 was resumed via
`run_fast_battery.sh <cand> 4`; the queue was relaunched for the remaining
4 with keyin31's BATTERY_DONE checkpoint honored.

## Failure analyses

### FA1 — 3rot / 3rot_chioff13: S1 LIN kill (singularity, not rotation count)

**(a) Precise failing signal.** S1 LIN screen (4096 64×64 matrices over
GF(2), rows = 64 consecutive sequential-input outputs; D = #{rank ≤ 61},
null E[D] = 21.6): 3rot D=132–160/4096, logp −133 to −187, 9/10 keys
reject (Holm). DIFF family fully clean (worst|z| ≤ 2.9). The DIFF-clean /
LIN-flagged split points at a global linear invariant, not a local
approximation.

**(b) Mechanistic hypothesis.** The 3-rotation layer
lin(x) = x ⊕ R³x ⊕ R⁷x ⊕ R¹¹x has an EVEN number of XOR terms, hence is
GF(2)-singular: verified rank 31 (kernel ∋ 0xFFFFFFFF; lin(0xFFFFFFFF)=0).
Every F output therefore satisfies parity(F_i) = parity(rk32_i) — a
constant for fixed key. Tracing parity through the Feistel
(R_{i+1} = L_i ⊕ F_i, L_{i+1} = R_i): parity(out_lo) = parity(R_5) =
parity(rk32_1 ⊕ rk32_3 ⊕ rk32_5) ⊕ parity(L_0), which is INPUT-INDEPENDENT
for sequential inputs (L_0 = 0). Verified on the model: parity(out_lo) is
constant (all-0 or all-1, key-dependent) across 5000 sequential inputs for
3rot, while the (3,11) control varies freely — and the constant equals the
predicted parity(rk32_1⊕rk32_3⊕rk32_5) exactly (checked 1=1 for key
0x123456789ABCDEF0), closing the mechanism end-to-end. Every LIN matrix's 64 rows
are thus confined to a 63-dimensional affine subspace, making rank ≤ 61
~6× more likely — exactly the observed D inflation. r16's F2 escaped this
because its odd rounds used the nonsingular lin(3,11): parity(F_1/F_3/F_5)
is then unconstrained and the parity chain breaks at the first odd round.
Refined verdict: the killer is the SINGULARITY (even XOR-term count), not
"3 rotations". Any x⊕R⊕R⊕R layer is singular; any odd-term layer is
generically a permutation. O2's scope note updated: 3-rot lin fails LIN in
the all-rounds construction; r16's hybrid construction is unaffected.

**(c) Follow-up candidate.** `r21_feist6_alt_notr_3rot_ns_nw`: nonsingular
3-rotation layer lin3ns(x) = R³x ⊕ R⁷x ⊕ R¹¹x (identity term dropped; GF(2)
rank verified 32). If the diagnosis is correct, this passes S1 while
keeping the 3-rotation diffusion shape — isolating singularity as the sole
cause. **Diagnosis CONFIRMED and probe promoted:** 3rot_ns is S1 CAL_PASS
(rej=0 all families) — the singularity was the sole cause of the LIN kill;
the 3-rotation diffusion shape is statistically sound. Unexpected upside:
S0 = 37.4u / 3,667 cells / 10,742 area — dropping the identity term removes
one XOR level per bit per linear round (−3.8u vs the singular 3rot), and
the design now strictly dominates r20 chioff31 (37.5u/3,863/11,199) on all
three axes. S2 PASS with the round's best |z| (4.7, 0 repeats). Q1:
sac_z5=0 ✓, bic=0.25384 (strongest blemish in the family — see Q1 note;
Frontier-S only). Full S3/S4 battery clean — 3rot_ns took the
Frontier-S size point, retiring r20 chioff31 and r19 chioff13.

### FA2 — winners' mechanisms (positive direction)

- **chioff31final (36.7u, new speed point).** The (3,1) chi variant
  b_i = a_i ⊕ (~a_{i+3} ∧ a_{i+1}) was r20's size play on rounds 2,4; here
  it ALSO buys speed on the truncated final round (−0.3u vs (1,3),
  −0.5u vs r18 notr's plain chi). Structural reason: the final round's chi
  output goes straight to the ciphertext XOR with no downstream linear, so
  the variant whose AND-term input cone (a_{i+3} complemented, further
  from the output bit) admits better gate sharing with the final XOR tree
  wins on both axes — strictly dominating chioff13all on delay, cells,
  and area. The lesson compounds: (3,1) is the better chi variant in this
  chassis in BOTH the mid-round (size) and final-round (speed) positions.
- **fm cures on r20 bases (Frontier Q).** The y^rotl(y,m) final mixing
  breaks the unmixed-final-chi output-bit correlation (bic 0.14→0.0085)
  with cost set by the underlying chi cone: +1.7u on the (3,1)-final base
  (chioff31_fm07: 39.2u), +2.4u on the (1,3)-final base
  (chioff13all_fm07: 39.4u) — the wider (1,3) cone makes the fm XOR-tree
  more expensive. chioff13all_fm311 (39.1u) is the cheapest cure tested,
  0.4u under r19 fm311's 39.5u at +18 cells — a genuine Frontier-Q
  tradeoff, full battery clean, now on Frontier Q.
- **keyin31 (36.9u).** Key-inside-chi on the (3,1) final: near-neutral vs
  chioff31final (+0.2u, −7 cells, −19 area) — same neutrality r20 found
  for (1,3). Statistically indistinguishable so far; the 0.1%-class area
  edge sits below flow threshold → threshold-exclusion (standing rule).

## Findings

1. **chioff31final (36.7u) — new Frontier-S speed point, dominates r20
   chioff13all on all axes.** The (3,1) chi variant on the truncated final
   round is −0.3u vs (1,3) and −0.5u vs plain chi — the variant r20 found
   to be the size play on rounds 2,4 is ALSO the speed play on round 6.
   Full battery clean (S1 CAL_PASS, S2 |z|=11.2, Q1 sac_z5=0, PractRand
   1GB ×2, SmallCrush passed).
2. **3rot_ns (37.4u/3,667/10,742) — new Frontier-S size point, dominates
   r20 chioff31 AND r19 chioff13.** The FA1 diagnosis probe became the
   round's second frontier point: dropping the identity term from the
   3-rotation layer fixed the singularity AND removed one XOR level per
   bit per round (−3.8u vs the singular 3rot). S2 |z|=4.7 is the round's
   best differential number; the nonsingular 3-rot diffusion is the
   cleanest linear tested. Caveat: bic=0.254, the strongest blemish in the
   family (Frontier-S only; an fm cure would be needed for any Q claim).
3. **Frontier Q: chioff13all_fm311 (39.1u) enters; fm11 retires.** The
   fm311 cure on the chioff13all base is 0.4u faster than r19 fm311 at
   +18 cells / −6 area — a genuine tradeoff, both stay. fm11 is strictly
   dominated by chioff31_fm07 (39.2/4,661/13,159), which is itself
   strictly dominated by chioff13all_fm311 — both out. The fm cure's cost
   scales with the underlying chi cone: +1.7u on the (3,1)-final base,
   +2.4u on the (1,3)-final base.
4. **The 3-rot S1-LIN kill is singularity, not rotation count (FA1).**
   x⊕R³x⊕R⁷x⊕R¹¹x is GF(2)-singular (rank 31); every F output's parity is
   key-constant, forcing parity(out_lo) input-independent and confining
   all LIN rows to a 63-dim affine subspace. The constant was predicted
   (parity(rk32_1⊕rk32_3⊕rk32_5)) and matched empirically. r16's hybrid
   passed because its nonsingular odd rounds broke the parity chain.
   O2 refined: any even-XOR-term layer is suspect in the all-rounds
   construction. The 3rot_ns probe (rank 32) is S1-clean, closing the
   mechanism.
5. **keyin31 (36.9u) — verified, threshold-excluded.** Key-inside-(3,1)-chi
   is near-neutral vs chioff31final (+0.2u, −7 cells, −19 area), same
   neutrality r20 found for (1,3). Full battery clean; the 0.1%-class area
   edge sits below flow threshold → excluded per standing rule.
6. **chioff21 (2,1) loses to (3,1) on delay AND size** (38.3u/4,042 vs
   37.5u/3,863) and carries the family's worst BIC blemish (0.17366).
   (3,1) remains the offset play in notr.
7. **BIC blemish is invariant across all non-fm notr variants**
   (0.140–0.254) — the unmixed final chi is the sole carrier; the fm cure
   remains the only known fix, and its cost is now mapped per base
   (+1.7–2.4u).
8. **Process:** a mid-queue VM reboot killed chioff31final's S4 after
   S3/S3b passed; iverilog was reinstalled from the apt cache and the S4
   resumed via `run_fast_battery.sh <cand> 4` (BATTERY-PASS). The
   per-candidate checkpointing in battery_progress.log made the resume
   exact. The round-20 tail-skip escape was applied at design time
   (generalized condition before any RTL was emitted).

## Evidence locations

- Candidates: `exploration/fast_battery/candidates/r21_*/` (impl.c, rtl.v, model.py, meta.json)
- Generator: `round21/gen_r21.py`; models: `round21/models/r21.py`
- xcheck: `round21/xcheck/`; rtlcheck: `round21/rtlcheck/`; S0: `round21/s0/`; S1: `round21/s1/`
- S2 logs: `round21/s2_r21_*.log`; progress: `round21/progress.log`
- Q1: `round21/q1/q1_*.json`
- S3/S4: `fast_battery/results/<cand>/{s3.out,s4.out,battery.log}`

## Process notes

- The round-20 keyin tail bug's escape protocol was applied at design
  time: the tail-skip condition was generalized to
  `tag.startswith("chi_fm") or tag.endswith("_keyin_notr")` before any
  RTL was emitted (class hunt during design, not after a bug).
- Mid-round methodology upgrade (Carlo 2026-10-03): analytical failure
  analysis is now mandatory per kill. The 3rot LIN kill was diagnosed to
  GF(2)-singularity of the even-term linear layer (verified: rank 31;
  parity(out_lo) input-independent on 5000 sequential inputs), generating
  the 3rot_ns follow-up probe. R16's O2 note is refined accordingly:
  singularity, not rotation count, is the killer.
- 3rot_ns added as candidate #11 mid-round via generator patch; all
  self-tests (DNF, chi×4, bijection 11×2000, dedupe) re-run green.

## r21b follow-up (2026-10-03): `r21b_3rot_ns_fm311_nw` — full pipeline

(a) **Design rationale.** r21's 3rot_ns (37.4u/3,667/10,742, Frontier-S size
point) carries bic_maxcorr=0.25384 — the strongest BIC blemish in the notr
family, from the unmixed truncated final chi. r19's fm-cure experiments
proved the mechanism: adding two-rotation final mixing
(F_6 = rotl(chi,3)^rotl(chi,11)^rk, no identity term) restores bic to
0.008–0.009 on every chi-based notr structure. r21b applies the identical
fm311 form to the 3rot_ns base, changing ONLY round 6 (plain chi32 final;
rounds 1–5 byte-identical to 3rot_ns). Target: Frontier-Q size point vs
r19 fm311 (39.5u/4,467/12,769).

(b) **Results — full pipeline, all green.**
- Generation: r21.py extended with `_F_chi_fm311` (plain-chi fm311,
  matches the already-emitted C `F_chi_fm311` and the Verilog `chi_fm311`
  branch, both added during round 21 for the plain-chi case); gen_r21.py
  gained the `chi_fm311` C_F_EXPR entry + spec. All self-tests re-run:
  DNF OK, chi×4 OK, bijection 12×2000 distinct OK, dedupe 12 specs
  pairwise-distinct OK. The 11 round-21 candidates regenerate
  bit-identical (md5 verified).
- xcheck: 10000/10000 C==Python PASS. RTL check: 300/300 PASS
  (all logic inside the single always block; fm round tail-skip via the
  generalized `tag.startswith("chi_fm")` condition).
- S0: **38.3u** / 4,299 cells / 12,356 area (run_synth.py, pinned Yosys
  0.69, analyze.py == analyze2.py). Cure cost vs base: +0.9u, +632 cells,
  +1,614 area — consistent with the fm cure scaling with chi cone.
- S1: CAL_PASS. S2: PASS, 0 repeats, max|z|=4.7 (all 115 deltas).
- Q1: **sac_z5=0**, **bic_maxcorr=0.00883**, bic_meancorr=0.00156,
  sac_maxdev=0.00371, avalanche_mean=31.999 — the blemish is cured
  (0.25384 → 0.00883), Frontier-Q bic gate met with 2.3× headroom.
- S3: PractRand 1GB ×2 configs PASS (base: 16MB/64MB/256MB/1GB no FAIL;
  strided key=0x0: 1GB no FAIL). S4: SmallCrush "All tests were passed".
  BATTERY-PASS — `round21/battery_r21b_3rot_ns_fm311_nw.log`.
- r21b is a **full-battery survivor** (S0–S4 + Q1 sac_z5=0): retained
  indefinitely per the standing retention rule; joins the RETAINED.md
  registry. Nothing deleted; candidate dir and all round logs intact.

(c) **Frontier-Q assessment** (post-O44 landscape: r22c 28.3u/4,656/12,949
is the Q speed point; fm07 retired; Q = r22c, chioff13all_fm311 39.1u,
fm311 39.5u, parsplit 40.7u, r9 41.0u, r8 42.9u):
r21b (38.3u/4,299/12,356) **strictly dominates chioff13all_fm311
(39.1u/4,485/12,763) and fm311 (39.5u/4,467/12,769) on all three axes**
→ retires both. vs parsplit (40.7u/4,318/12,356): −2.4u, −19 cells,
area TIE — weakly dominates (coordinator's call on the tie).
vs r22c: +10u slower but −357 cells/−593 area (genuine tradeoff).
r21b does NOT take the speed point (r22c) nor the size point (r8 4,133);
it becomes the mid-frontier point, strictly removing two members.
NOT yet edited into PARETO.md — pending coordinator raw-log
verification (S0/S1/S2/Q1/S3/S4). RTL package sync pending.
