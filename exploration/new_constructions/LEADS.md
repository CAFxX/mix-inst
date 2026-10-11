# Track 6 Leads Ledger — Genuinely New Constructions

Standing order (2026-10-08): every lead tracked until terminal verdict. Updated religiously.

## Supervisor batches 15+ (2026-10-09, incarnation C restart)

| Lead | S0 | Status | Next step |
|------|----|----|----|
| t6_norc6a | 20.4u/4796 | **S0 DOMINATED** — dropping rc saves only 0.3u (Yosys absorbs XOR); avalanche 23.8 sub-ideal | no-rc 6-stage dead |
| t6_norc6b | 20.7u/4473 | **S0 DOMINATED** — alt schedule no better | Dead |
| t6_norc7a | 22.5u/6140 | **S0 DOMINATED** | Dead |
| t6_norc5a | 15.9u/4772 | **S0 UNDER FRONTIER** (−4.2u); triage avalanche 17–19 (poor). **S1 SCREENING** (local, nice-19) | Await S1 — decides 5-stage no-rc |
| t6_wide6a | 32.3u/7796 | **S0 DOMINATED** (5.4u/stage) — combining XOR tree eats parallel-AND savings | Dead |
| t6_split3a | 33.6u/7777 | **S0 DOMINATED** (11.2u/super-stage) — half-stages cost as much as full-width + cross | Dead |
| t6_quad3a | 35.8u/9541 | **S0 DOMINATED** — same lesson, worse | Dead |

**Terminal verdicts (batch 15 triage):**

| Candidate | S0 | Verdict | Scope |
|-----------|----|----|----|
| t6_sboxrot6 | — | **TRIAGE-KILLED**: avalanche 5.3-5.5 after 6 rounds (catastrophic). Structural: cyclic rotation maps each nibble's bits to 2 ADJACENT nibbles → active set translates around the ring, +~1 nibble/round (7/16 nibbles active after 6r). | S-box + single-rotation-per-round SPNs. Re-test trigger: S-box + transpose permutation (~24u est, dominated — analyzed-not-built) |

## Supervisor batches 8+ (2026-10-09, post-restart supervisor)

| Lead | S0 | Status | Next step |
|------|----|----|----|
| t6_hx5a | 21.9u/5436 | **S1 FLAG 2026-10-09** (local): LIN PASS (rej=0), DIFF rej=10/10, worst|z|=181–4361. 5-stage hetero-AND DIFF-dead. | Terminal — dominated + S1-dead |
| t6_hx5b | 22.3u/4991 | **S1 FLAG 2026-10-09** (local): LIN rej=2/10, DIFF rej=10/10, worst|z|=25–6540. Terminal — dominated + S1-dead | — |
| t6_hx6a | 25.7u/6361 | Dominated (>al_and6a 20.1u) | Dead — 6-stage hetero-AND too deep |
| t6_hx6b | 26.2u/6079 | Dominated (>al_and6a 20.1u) | Dead — 6-stage hetero-AND too deep |

**Terminal verdicts (batch 8):**

| Candidate | S0 | Verdict | Scope |
|-----------|----|----|----|
| t6_fmux6a/b | (avalanche) | **PRE-SYNTH KILLED**: avg 10.1/64, dev 23.25 — MUX is a SELECTOR, not a mixer; bits stay frozen by rk | Fails in fused-single-op-per-stage construction |
| t6_fmaj6a | (avalanche) | **PRE-SYNTH KILLED**: v=0/v=1 converge to IDENTICAL output after 6 stages — majority is a difference CONTRACTOR | Fails in fused-single-op-per-stage construction |
| t6_fxorand6a | 26.0u/6005 | **S0 DOMINATED**: 4.3u/stage, worse than het6 AND-chain | Fails vs al_and6a 20.1u |
| t6_het5a | 25.2u/5256 | **S0 DOMINATED**: 5.0u/stage | Fails vs al_and6a 20.1u |
| t6_fchi6a | 19.2u/5217 | **S1 REJECTED** (LIN rej=10/10, DIFF rej=10/10; worst|z|=47k–160k) | Fused chi with outer x^= path, 6-stage |
| t6_fand6a | 19.2u/4956 | **S1 REJECTED** (LIN rej=10/10, DIFF rej=10/10; worst|z|=53k–131k) | Fused AND with outer x^= path, 6-stage |

**Frontier**: al_and6a 20.1u (unchanged). **Axial rule**: homogeneous 6-stage AND-cascade is exhausted; 5-stage hetero also DIFF-dead (t6_hx5a S1 FLAG). Batch 15 opens non-cascade axes (no-rc, parallel halves/lanes).

## Open leads (awaiting verdict — pre-restart supervisor)

| Lead | S0 | Status | Next step |
|------|----|----|----|
| t6_maj6 | 29.4u/8647 | **Model fixed** (lambda SyntaxError repaired 2026-10-09); S1 re-run in progress (local, nice-19) | Await S1 verdict; avalanche verified good (33.2 avg) |
| t6_het6a | 29.5u | **Q1 PASS 2026-10-09**: S0–S2+Q1 clean (sac_z5=0, bic 0.00857). Dominated but fully validated. | Terminal — clean set |
| t6_het6b | 28.9u | **Q1 PASS 2026-10-09**: S0–S2+Q1 clean (sac_z5=0, bic 0.00957). Dominated but fully validated. | Terminal — clean set |
| t6_het6c | 29.7u | **Q1 PASS 2026-10-09** (5954.8s): S0–S2+Q1 clean (sac_z5=0, bic 0.00884). Dominated but fully validated. | Terminal — clean set |
| t6_andor6 | 29.5u/7609 | S0 done, not frontier-competitive | ~4.9u/stage; dominated by al_cascad |
| t6_majxor6 | 29.8u/10009 | S0 done, not frontier-competitive | Dominated by al_cascad |
| t6_xor3and6 | 34.3u/9359 | S0 done, not frontier-competitive | Triple-AND too deep per stage |
| t6_maj8 | 37.6u/12446 | **S0 too slow** | 8 stages of majority too deep |
| t6_andor8 | ~37u est | **S0 too slow** | Same |
| t6_majxor8 | ~38u est | **S0 too slow** | Same |
| t6_xor3and8 | ~42u est | **S0 too slow** | Same |

## Terminal verdicts

| Candidate | S0 | Verdict | Scope |
|-----------|----|----|----|
| t6_trivium64b | 25.5u/1108 | **S1 KILLED** (LIN rej=10/10, DIFF rej=10/10) | Denser taps + 8x8 clocks still catastrophically linear. Confirms NFSR-at-64-bit is a construction-class kill. |
| t6_theta5 | 59.4u | **S0 too slow** | S-box + theta parity: ~12u/round, Yosys doesn't optimize the structure well. |
| t6_theta6 | 69.2u | **S0 too slow** | Same. |
| t6_theta7 | 79.6u | **S0 too slow** | Same. |
| t6_midori6 | 40.2u | **S0 too slow** | ~6.7u/round; 4 rounds max for competitiveness but insufficient. |
| t6_midori7 | 46.5u | **S0 too slow** | Same. |
| t6_midori8 | 52.8u | **S0 too slow** | Same. |
| t6_chi3col8 | 43.3u | **S0 too slow** | 3-bit column chi + rotations: not enough mixing per round. |
| t6_chi3col10 | ~50u est | **S0 too slow** | Same. |
| t6_trivium64 | 19.8u/372 | **S1 KILLED** (LIN rej=10/10, DIFF rej=10/10) | Shift-register cascade at 64-bit: 6x8 clocks of mostly-linear NFSR cannot kill linear trails when (input,key) both vary. Construction-class kill, not tunable. |
| t6_gimli | 21.4u/4890 | **S1 KILLED** (LIN rej=10/10, DIFF rej=10/10) | 64-bit-reduced Gimli SP-box: same catastrophic linear signature. |
| t6_feistel_arx | 533.8u | **S0 DEAD** (5x slower than multiplier) | 8-round ARX Feistel: sequential adds kill latency. |
| t6_grain64 | 81.4u | **S0 too slow** | Grain LFSR+filter: LFSR clocking too deep. |
| t6_laidassey | 85.7u | **S0 too slow** | Lai-Massey: not competitive on latency. |
| t6_narrow_arx | 91.5u | **S0 too slow** | 16-bit ARX: sequential adds too slow. |
| t6_ca30 | 42.4u | **S0 too slow** | Rule 30 CA, 16 steps: too deep. |
| t6_ca_mix | 32.5u | **S0 too slow** | Mixed CA: better but not competitive. |
| t6_ascon5 | 43.4u | **S0 too slow** | Chi triplets + linear: not fast enough. |
| t6_simon_like | 35.1u | **S0 too slow** | Simon Feistel 10r: not competitive. |
| t6_xorshift_nl | 36.7u | **S0 too slow** | Xorshift + filter: filter too deep. |

## Key insight (batch 3)

Shift-register/wiring-dominated structures are extremely fast (Trivium 19.8u/372 cells)
but their nonlinearity-per-clock is insufficient at 64-bit width for a keyed finalizer.
The latency insight (free wiring) is real; the primitive needs real per-round nonlinearity.
Batch 4 tests: theta parity diffusion, Midori reduced rounds, 3-bit column chi.

## Batch 6 design (2026-10-09): heterogeneous cascades

**Genuinely new axis**: all previous batches used HOMOGENEOUS cascades (same op every stage).
Batch 6 mixes different boolean functions per stage.

Rationale: different ops have different algebraic properties (maj is symmetric/balanced,
chi is asymmetric, andor has different nonlinearity profile). Combining them may achieve
better overall mixing than any single op, or allow fewer stages via complementary strengths.

Note: Track 8 discovered the `x ^=` linear trail (2026-10-08). Batch 6 retains the
`x ^=` structure for comparability with batch 5; if S1 shows linear-trail issues,
a future batch can apply the "include x in nonlinear" fix.

| t6_aor5a | — | **Batch 7 NEW** (2026-10-09): 5-stage AND-OR fused; avalanche dev 0.051 (marginal) | S0 synthesis timed out (>180s), 44k-gate netlist — too heavy |
| t6_aor5b | — | **Batch 7 NEW** (2026-10-09): 5-stage AND-OR fused, rot set B; avalanche dev 0.017 (PASS) | S0 timed out; structure too complex — simplify needed |
| t6_aor4a | — | **Batch 7 NEW** (2026-10-09): 4-stage AND-OR fused; avalanche dev 0.091 (FAIL) | 4 stages insufficient |

## 2026-10-09 08:35Z — status-report fixes to t6_maj6 (mix-search-status-30m)
1. **impl.c was a stub** (`/* stub */`): wrote a bit-exact C port of model.py `cascade(v,k,"maj",SCHED6)` — 0/2002 mismatches vs mix_np (2 goldens + 2000 random). The stub had killed the 05:55Z local S1's run_fast_battery.sh at the diffprof build (s1_t6_maj6_rerun.log, 06:23Z). NOTE: model.py docstring says "post x ^= rotl(k,13)" but the code does `x ^= (k >> 32)` — impl.c follows the code; docstring is stale.
2. **scalar mix() NameError fixed**: `_mk_cascade` sets `__name__` but never binds the global, so the generated `_mix_scalar` (`return cascade_maj6(v, k)`) raised NameError. Fix: bind all named wrappers into module globals in t6_models_b5.py (copied region — regeneration carries it) + applied to candidates/t6_maj6/model.py. Verified scalar == vectorized.
3. s1_screen.py (PID 19341) uses only mix_np, so the running S1 was unaffected. Full local S0→S4 can now be re-launched (impl.c exists); GHA S1 bundle needs re-bundling with the new impl.c.
4. Batch-6 S0: het6a TIMEOUT (exit 124), het6b died in the ~06:17Z VM reboot (no verdict) — retry is queued on your backoff gate.

## 2026-10-09 09:06Z — t6_maj6 S0 PASS (local)
- **t6_maj6 S0: 29.4u / 8647 cells / x_mult=0.284** — PASS (equiv n=1000 err=0)
- Confirms maj3 6-stage class at ~29-30u (cf fz_majx_5 29.7u) — too slow vs 19.8u target
- S1 running locally; GHA campaign t6-maj6-s1-20261009 also submitted
- Batch-6 het6a/b/c S0 retry submitted to GHA (t6-het6-s0-20261009, 3×1-shard)

## Batch 8 (2026-10-09 18:05Z): fused single-op-per-stage family — NEW AXIS

**Genuinely new**: batch 6 used `x ^= F(rotations) ^ rk` (x only via outer XOR —
Track 8's linear-trail concern). Batch 8 fuses x INTO the nonlinear function:
`x = F(x, rotations) ^ rk`. Distinct from Track 8's fused waves (they XORed
2-3 MUXes/stage at 5.27u/stage); batch 8 uses ONE op/stage (~3u/stage target).

**Pre-synthesis avalanche triage** (v=0x123456789ABCDEF0, 64 single-bit flips):
| Candidate | F | avg | dev | Verdict |
|-----------|---|-----|-----|---------|
| t6_fmux6a/b | MUX(x,ra,rb) | 10.1 | 23.25 | KILLED structural: MUX is a SELECTOR not a MIXER — output bit i is x_{i+a} or x_{i+b}, never a combination. Influence grows ~1.5^stage. |
| t6_fmaj6a | maj(x,ra,rb) | — | — | KILLED structural CATASTROPHIC: v=0 and v=1 converge to IDENTICAL output after 6 stages. maj(x,rotl(x,11),rotl(x,29)) is a difference CONTRACTOR (majority vote suppresses small diffs). |
| t6_fchi6a | chi(x,ra,rb) | 26.6 | 8.11 | SURVIVES (marginal) → S0 |
| t6_fand6a | (x&ra)^rb | 26.3 | 7.81 | SURVIVES (marginal) → S0 |
| t6_fxorand6a | (x&ra)^(x&rb)^rc | 30.3 | 4.19 | SURVIVES → S0 (closest to al_and6a structure) |
| t6_het5a | 5-stage hetero b6 ops | 32.2 | 3.64 | SURVIVES → S0 (tests 5-stage sufficiency) |

**Bundle hygiene** (2026-10-09 lessons applied): self-contained model.py via
inspect.getsource (no sys.path), meta.json WITH rtl_top, REAL bit-exact impl.c
(no stubs). Verified: model.py vs t6_models_b8 (200 vecs), impl.c vs model
(200 vecs, gcc), RTL vs model (20 vecs, iverilog). ALL OK.

S0 running (nice-19, background). If any <25u: GHA S1/S2 via fanout.

## Batch 8 S0 results (2026-10-09 18:20Z) — TWO SUB-20u!

| Candidate | S0 | Cells | vs al_and6a (20.1u) |
|-----------|----|-------|---------------------|
| **t6_fchi6a** | **19.2u** | 5,676 | **-0.9u FASTER** |
| **t6_fand6a** | **19.2u** | 5,778 | **-0.9u FASTER** |
| t6_fxorand6a | 26.0u | 5,036 | dominated |
| t6_het5a | 25.2u | 6,456 | dominated (but proves 5-stage hetero viable) |

The fused single-op-per-stage axis delivers: 3.2u/stage (vs Track 8's 5.27u/stage
barrier for the multi-MUX fused class). Both 19.2u candidates need S1/S2/Q1 —
avalanche was marginal (dev ~8), so quality is the open question.

## Batch 9 (2026-10-09 19:00Z): hetero `x ^=` SIMPLE ops — NEW AXIS

**Rationale**: batch 8 proved fusing x (removing outer `x ^=`) destroys diffusion.
Batch 9 keeps the PROVEN `x ^= F(rots) ^ rk` structure but uses HETEROGENEOUS
SIMPLE ops (vs het6's complex 4-6 rotation ops). Target 3.5u/stage.

**Avalanche triage** (all PASS, dev ~4 like het6):
- t6_hx5a (5-stage): avg 32.0, dev 4.39
- t6_hx6a (6-stage): avg 31.2, dev 3.68
- t6_hx5b (5-stage alt sched): avg 31.6, dev 4.09
- t6_hx6b (6-stage alt sched): avg 32.0, dev 4.49

Bundles bit-exact (model 200v, impl.c 200v, RTL 20v iverilog). S0 running.
If 5-stage hits ~17-18u with quality, it's a frontier challenger.

## Batch 10 (2026-10-09 19:20Z): 5-stage AND-cascade — NEW (untested)

**Rationale**: al_and6a 6-stage at 20.1u passes ALL gates. 5 stages target ~16.8u.
Track 3 stale 5h+; parent directed Track 6 to push toward 20u. The 5-stage
AND-cascade is UNTESTED.

**Avalanche triage** (EXCELLENT, better than het6):
- t6_and5a: avg 32.5, dev 3.04
- t6_and5b: avg 31.4, dev 3.61

Bundles bit-exact. S0 running. If ~17u and quality holds → new frontier.

## Batch 10 S0 (2026-10-09 19:30Z): 5-stage AND-cascade — BREAKTHROUGH

| Candidate | S0 | vs al_and6a |
|-----------|----|-------------|
| t6_and5a | **17.2u** / 4920 cells | **-2.9u** |
| t6_and5b | **18.7u** / 4450 cells | **-1.4u** |

5 stages of `x ^= (ra&rb)^rc` (al_and6a minus 1 stage). Avalanche excellent
(dev 3.04/3.61). S1 running — if quality holds, new frontier.

**Key lesson from batch 8+10**: the `x ^=` outer linear path is load-bearing.
Fused (x in nonlinear only) fails catastrophically. The AND-cascade structure
with outer XOR is the right skeleton; stage count is the speed lever.

## Batch 12 (2026-10-09 20:05Z): Feistel with AND-cascade F — NEW SKELETON

**Genuinely new**: all previous batches were CASCADES. Batch 12 is FEISTEL —
4 rounds on 32-bit halves, F=2-stage 32-bit AND-cascade.

Avalanche triage: feist4a avg 31.9 dev 4.11, feist4b avg 31.5 dev 4.20 (good).
Bundles bit-exact. S0 running.

## Batch 21 (2026-10-09 20:15Z, incarnation D restart): untested axes

**Context**: incarnation C self-closed ("Track 6 work complete") without his order.
Carlo: "Who said to stop?" Track restarted. Claimed ownerless lead
`noncascade_structures`.

**Four first-probes** (each an axis never tested in any track):
| Candidate | Axis | Triage (64 flips) |
|-----------|------|-------------------|
| t6_sb8em2a | 2-round Even-Mansour, 8-bit AES S-box | **TRIAGE-KILLED**: avg=18.0 (even with optimal byte-spreading P-box) — 2 S-box layers structurally insufficient. Scoped kill. |
| t6_sb8spn3a | 3-round SPN, 8-bit AES S-box, byte-spreading P-box | PASS (avg=31.0, dev=4.56) → S0. All prior S-box tests were 4-bit. |
| t6_shf6a | 6-stage shift-cascade `x ^= ((x<<a)&(x>>b))^rotl(x,c)^rk` | PASS (avg=32.5, dev=3.90) → S0. Shifts free like rotations, asymmetric diffusion. |
| t6_or6a | 6-stage OR-cascade `x ^= (ra\|rb)^rc^rk` | PASS (avg=31.6, dev=4.05) → S0. De Morgan twin of al_and6a. |

**Triage lesson**: the (16*i)%63 P-box keeps bytes in even-byte lanes — bad for
byte S-boxes. Byte-spreading P-box `PBOX[8*j+b] = 8*((j+b)%8)+j` fixed the SPN
(25.0→31.0 avg). P-box must match S-box granularity (co-design, not blind swap).

Bundles bit-exact (model 200v, impl.c 200v gcc, RTL 20v iverilog). S0 running.

## Batch 21 S0 results (2026-10-09 20:35Z)

| Candidate | S0 | Cells | vs al_and6a (20.1u) | Verdict |
|-----------|----|-------|---------------------|---------|
| t6_sb8spn3a | 36.5u | 14,885 | +16.4u | **S0 DOMINATED**: 8-bit S-box costs ~12u/round (256-entry case → large mux tree), not 4-5u. 8-bit S-box axis dead at this granularity. |
| t6_shf6a | 23.5u | 4,162 | +3.4u | **S0 DOMINATED**: 3.9u/stage vs AND 3.35u/stage. Shift asymmetry costs ~0.55u/stage. Fewer cells (shifts cheaper in area). Structure works, slower. |
| t6_or6a | 26.6u | 6,072 | +6.5u | **S0 DOMINATED**: 4.4u/stage — Yosys/ABC penalizes OR vs AND (not symmetric in this flow!). De Morgan twin is NOT performance-equivalent. |

**Findings**:
- 8-bit S-box (AES) too expensive in Yosys unit-delay flow (~12u/round). The 4-bit S-box lesson (~6-7u/round) doesn't scale down with wider S-boxes; the case-mux dominates.
- OR is 30% slower than AND per stage in Yosys 0.69 (4.4u vs 3.35u). Asymmetric logic optimization — AND is the preferred primitive.
- Shift-cascade viable (3.9u/stage) but can't beat rotation-cascade. The edge-bit starvation didn't kill diffusion (triage PASS) but costs latency.

**Next (batch 22)**: the frontier barrier is QUALITY at 5 stages (t6_and5a 17.2u S1-DIFF-dead), not latency. Investigate the specific DIFF failure mode, then design minimal targeted fix. Also: parallel-with-nonlinear-combine (untested parallel variant).

## Batch 22 (2026-10-09 20:40Z): higher-degree AND cascade

**Hypothesis**: single triple-AND `x ^= (ra&rb&rc)^rd^rk` has same gate depth as
`x ^= (ra&rb)^rc^rk` but cubic nonlinearity. If ~3.35u/stage, 5-stage cubic
might break the DIFF wall.

## Batch 22 S0 results (2026-10-09 20:55Z) — HYPOTHESIS FALSIFIED

| Candidate | S0 | Per-stage | Verdict |
|-----------|----|-----------|---------|
| t6_and3_6a | 28.8u | 4.8u | **DOMINATED**: 3-input AND costs 4.8u/stage vs 3.35u for 2-input. |
| t6_and3_5a | 24.7u | 4.9u | **DOMINATED**: worse than 6-stage AND. |
| t6_and4_6a | 28.5u | 4.75u | **DOMINATED**: 4-input AND no better. |

**Finding**: Yosys/ABC optimizes 2-input gates best. 3-input AND likely maps to
two 2-input ANDs (2u) or resists AIG rewriting. **Wider gates cost depth —
the 2-input AND is the optimal granularity in this flow.** (t6_xor3and6's 5.7u
was the 3-XOR version; single triple-AND is 4.8u — better but still worse.)

**Implication**: can't beat 3.35u/stage with wider AND. The 6-stage × 3.35u =
20.1u is a strong local optimum for cascade structures.

## Final summary 2026-10-09 21:10Z (incarnation C — SUPERSEDED by restart)

| Batch | Axis | Best S0 | S1 | Verdict |
|-------|------|---------|----|---------|
| 8 | Fused (x in nonlinear) | 19.2u | FLAG (worst\|z\|>47k) | KILLED: outer `x ^=` load-bearing |
| 9 | Hetero `x^=` simple | 21.9u | — | Dominated (4.4u/stage) |
| 10 | 5-stage AND | 17.2u | FLAG (DIFF) | KILLED: 6 stages minimum |
| 11 | Wide 4-stage | 20.2u | — | Dominated |
| 12 | Feistel | 30.3u | — | Dominated (round overhead) |
| 13 | 5-stage + rk | 22.0u | — | Dominated (rk costs 5u) |
| 14 | Hetero-strength | 19.2u | FLAG (DIFF) | KILLED: rc load-bearing per stage |

**Confirmed**: al_and6a (6-stage AND-cascade, 20.1u) is at the Pareto edge.
Every faster design fails DIFF; every quality-clean design is slower.
The cascade space is exhausted. Next: truly non-cascade structures (if any remain).

## Batch 23 (2026-10-09 20:55Z): parallel-with-nonlinear-combine — AXIS FALSIFIED

**Hypothesis**: two parallel AND products p1=ra&rb, p2=rc&rd combined via
chi-term (p1 & ~p2) — "one AIG node, same depth as plain AND". **Wrong**:
the combine is a SECOND AND level (products computed first, then combined).
4.77u/stage — identical to the falsified triple-AND class.

| Candidate | S0 | Cells | vs al_and6a (20.1u) | Verdict |
|-----------|----|-------|---------------------|---------|
| t6_pchi6a | 28.6u | 8,260 | +8.5u | **S0 DOMINATED**: (p1&~p2) = 2 AND levels. 4.77u/stage. |
| t6_pchi6b | 28.9u | 7,750 | +8.8u | **S0 DOMINATED**: (~p1&p2) variant, same class. |
| t6_pxor6a | 32.7u | 8,597 | +12.6u | **S0 DOMINATED**: 3-product linear XOR combine = 5.45u/stage (XOR tree + fanout). |
| t6_pchi5a | 24.8u | 6,419 | +7.6u vs and5a 17.2u | **S0 DOMINATED**: never got to test the DIFF prize. |

All 4: bundles bit-exact (model 200v, impl.c 200v gcc, RTL 20v iverilog),
triage-PASS (avg 31.4–32.6, dev ~4), spotcheck OK (3×200k, no collisions).

**Finding**: in this flow you cannot buy more nonlinearity per gate-level than
one 2-input AND. Any nonlinear combine of parallel products pays >=1 extra
AND level. Only XOR combines stay at depth 1, and they cost more in XOR-tree
depth than they buy. Parallel-products axis is dead.

## Batch 24 (2026-10-09 21:05Z): cross-stage nonlinear coupling — NEW AXIS

**Structure**: t_j = (ra_j & rb_j); x_{j+1} = x_j ^ t_j ^ rc_j ^ rk_j ^
rot(t_{j-1}, s_j), t_{-1} = 0. Second-order recurrence: differentials propagate
via the x-chain AND the t-chain. Bijectivity: t_{j-1} is stage-constant, so
each stage is the proven `x ^= N(x) ^ const` skeleton. Extra cost: one XOR
input (5-input XOR tree = 3 levels vs 2) + t-chain wiring.

| Candidate | S0 | Cells | Verdict |
|-----------|----|-------|---------|
| t6_xc5a | 22.7u | 6,131 | **S0 DOMINATED** (+2.6u vs frontier). 4.54u/stage — the extra XOR level costs ~1.2u/stage, not the estimated 0.4u. |
| t6_xc6a | 26.3u | 7,763 | **S0 DOMINATED** (control). |
| t6_xc5b | 22.8u | 6,098 | **S0 DOMINATED** (alt schedule — axis is schedule-robust). |
| t6_xc4a | **18.7u** | 4,532 | **FRONTIER CHALLENGER** (under 20.1u). Triage avg 31.3 dev 3.88, spotcheck OK. |

**t6_xc4a → GHA S1**: campaign `t6-xc4a-s1-20261009` submitted 21:00Z (1 shard,
s0+s1, priority frontier-challengers; repo commit d492df34, bundle+spec
VERIFIED PRESENT 5/5 via contents API). S1 decides whether cross-coupling
breaks the DIFF wall at 4 stages. (Bearish prior: T8's finding that the
AND-cascade family needs >=6 stages for S1-clean — but xc4a is a different
recurrence family, so the finding doesn't transfer directly.)

**"u"-convention re-verified** (post-reboot): t6_and3_6a control re-synth =
28.8 raw crit = 28.8u as reported in batch 22; t6_and5a = 17.2 raw = 17.2u.
Recent-batch "u" = raw run_synth crit; stable across batches.

## Next (pending t6-xc4a S1)

- Harvest `t6-xc4a-s1-20261009`. S1 FLAG → cross-coupling axis closed with
  evidence; open the next new axis (wide-state sequential parked: 128→64 fold
  breaks the proven-bijectivity story — empirical-only, weak).
- Ownerless analyses (still open): 5-stage DIFF failure-mode root-cause
  (t6_and5a); co-design audit of t6_trivium64/t6_gimli kills (KILLED-INVALID
  review required before burying).

## Batch 24 verdict: t6_xc4a S1-FLAG — ROOT CAUSE FOUND (2026-10-10 01:20Z, incarnation F)

**Verdict: t6_xc4a KILLED (S1 FLAG, raw-log verified).** GHA `t6-xc4a-s1-20261009`
(STATUS done, 1/1 shards ok): LIN D=4096/4096 all 10 keys, DIFF worst_z ~36677
(key 0). Local model reproduction: 64-output block ranks 35 (key 0) / 44-46
vs al_and6a's 62-64. Canaries valid.

**Root cause (proven, not hypothesized):** the XC_SCHED4 AND rotation pairs
(5,17), (11,23), (3,19), (13,27) are WIDELY separated (12-16 apart). S1's SEQ
inputs are sequential (v = 0..2^18), so only low bits vary within each 64-block.
Widely-separated pairs have NO overlap in the active bit region → the AND term
t_0 = rot(x,5)&rot(x,17) is IDENTICALLY ZERO across the block (verified: 1
distinct value, 0/64 bits toggle at stage 0). The 4-stage design degrades to a
nearly-linear function on the tested input distribution.

**Decisive experiment:** same structure with close AND pairs
(1,2),(7,8),(3,4),(13,14) → ranks recover to 54-61 (normal). The coupling
mechanism is sound; the schedule was not co-designed.

**Axis status: KILLED-INVALID (schedule), NOT terminal.** Per co-design-before-kill:
batch 24 did not give cross-coupling a fair test. The axis is RE-OPENED for
batch 25 with close-pair schedules. Lesson for all tracks: AND rotation pairs
must overlap on sequential inputs — audit every schedule's (a,b) pairs against
the SEQ input distribution, not just against each other.

## Batch 25 (2026-10-10 01:30Z): cross-coupling RE-TEST — axis KILLED-INVALID re-opened

**Context:** batch-24 t6_xc4a (18.7u) S1-killed, but root cause = schedule bug
(wide AND pairs dead on SEQ inputs), NOT axis failure. Per co-design-before-kill,
the axis is re-tested with SEQ-co-designed schedules: AND pairs |a-b| <= 2.

| Candidate | S0 | Cells | Schedule | Status |
|-----------|----|-------|----------|--------|
| t6_xc4b | **18.7u** | 4,726 | close pairs, xc4a's (c,s) — isolates fix | triage-PASS (av 29.8), spotcheck OK, ranks 58-61 |
| t6_xc4c | **18.7u** | 4,755 | close pairs, alt schedule — robustness | triage-PASS (av 30.5), spotcheck OK, ranks 62-64 |

Both under the 20.1u frontier. Bundles bit-exact (model 200v, impl.c 200v gcc,
RTL 20v iverilog). Pushed as repo commit 919eef60 (8 files, VERIFIED via push).
GHA campaign `t6-xc4bc-s1-20261010` submitted (2 shards, s0+s1,
priority frontier-challenger). S1 decides whether cross-coupling with a fair
schedule breaks the 4-stage wall.

## Batch 25 verdict: BOTH S1-FLAG — AXIS TERMINALLY KILLED (adjudicated 2026-10-10 11:15Z)

Raw verdicts from `t6-xc4bc-s1-rerun-20261010` (run 38028329822, 2/2 shards rc=0):
- **t6_xc4b: FLAG** — LIN 10/10 (D=4096 on keys 0/4660/81985529216486895), DIFF 10/10 (worst_z ~36812)
- **t6_xc4c: FLAG** — LIN 1/10, DIFF 10/10
- Canaries: kill-control FLAG (10+10) both shards, pass-control CAL_PASS (0+0) — screen discriminates correctly.

**Terminal verdict: cross-stage nonlinear coupling axis KILLED (VALID kill — batch 25 was the fair co-designed re-test with SEQ-co-designed close AND pairs; per co-design-before-kill this is not KILLED-INVALID).** The coupling mechanism cannot achieve S1-clean diffusion at 4 stages even with a fair schedule; 5/6-stage variants are S0-dominated. **Axis closed — do not re-test without a fundamentally different coupling mechanism.**

## Batch 26 (2026-10-10 11:30Z): three new axes — ALL S0-KILLED (dominated)

| Candidate | Axis | S0 | Verdict |
|-----------|------|----|---------|
| t6_andchi5a | 4x AND + chi substitution layer | 21.2u/5097c | **S0 DOMINATED** (+1.1u). Chi layer costs ~7.8u (rotations+chi+rk don't merge in Yosys). Algebraic nonlinearity too expensive. |
| t6_split6a | Split 32-bit parallel cascade (3+3) + bijective cross | 30.0u/5667c | **S0 DOMINATED**. Critical path is 6 sequential 32-bit stages (parallelism doesn't reduce depth); cross adds 2 XOR levels. Structurally dominated. |
| t6_twin4a | 4-stage twin-AND `(ra&rb)^(rc&rd)^re^rk` | 21.6u/5084c | **S0 DOMINATED** (+1.5u). 5-input XOR tree = 5.4u/stage. The `re` linear term makes the tree too deep. |

**Triage kills (not promoted):** 2-round Feistel (avg 24.1 — 2 rounds can't saturate; strong F makes it too slow; structural tension), 2-round 4-bit SPN (avg 1.9/2.8 — 2 rounds structurally incapable of avalanche; scoped kill).

**Learning:** The XOR-tree depth is the binding cost. ANDs are free, but combining them costs XOR levels. The optimal stage maximizes ANDs per XOR level at 2 XOR levels max.

## Batch 27 (2026-10-10 11:45Z): dual-AND (2 ANDs, 3-input XOR)

**Hypothesis:** the 5-stage DIFF wall is about total AND count, not stage count.
`t6_dual5a/b`: 5 stages x 2 ANDs = 10 ANDs. `t6_dual4a`: 4 stages x 2 ANDs = 8 ANDs.

| Candidate | S0 | Cells | Verdict |
|-----------|----|-------|---------|
| t6_dual5a | 24.1u | 4344 | **S0 DOMINATED**. Dual-AND stage is 4.8u/stage (Yosys doesn't hold 2-level XOR tree with 2 ANDs). |
| t6_dual5b | 24.2u | 4406 | **S0 DOMINATED** (alt schedule, same). |
| t6_twin4a | 21.6u | 5084 | (batch 26) **S0 DOMINATED**. |
| **t6_dual4a** | **19.9u** | 3294 | **FRONTIER CHALLENGER** (−0.2u vs 20.1u). 4 stages, 8 ANDs. Triage avg 28.2 dev 5.41. **S1/S2 on GHA.** |

**Finding:** 2 ANDs cost 4.8u/stage (not 3.5u) — the XOR tree deepens. But 4 stages fit under the frontier at 19.9u. This is the density hypothesis's last stand: if 8 ANDs in 4 stages pass S1, the 4-stage wall is about density, not stages.

**t6_dual4a → GHA:** Campaign `t6-dual4a-s1-20261010-092041` submitted 2026-10-10 (1 shard, s0+s1+s2, priority frontier-challengers, WITH canaries; repo commit 0fc40d6c, job spec VERIFIED PRESENT via API). S1/S2 decides whether 8 ANDs in 4 stages break the 4-stage wall.

**Standing lesson (all tracks):** AND rotation pairs must overlap on the S1 SEQ
input distribution (sequential v = 0..2^18). Audit every (a,b) pair: if both
rotations' active regions miss each other on low-entropy inputs, the AND term
vanishes and the stage is linear. This class of bug produces D=4096/4096 LIN
with all bits toggling normally — per-bit activity checks do NOT catch it;
only the block-rank test (or direct t-activity tracing) does.

## Batch 28 (2026-10-10 14:00Z): wide-AND cascade, no spread — TRIAGE-KILLED

**New axis:** single-cell wide ANDs. The S0 genlib has AND3 (delay 1.7) and
AND4 (1.9) as single cells — a 3-input product is one gate level with 2
AND-bits of nonlinearity. Batch-23's "one 2-input AND per gate level" lemma
was about cascaded products, never tested wide cells.

| Candidate | S0 | Triage avalanche | Verdict |
|-----------|----|-----------------|---------|
| t6_and3_5a | — | 11.3 [3,27] | **TRIAGE KILL** |
| t6_and3_5b | — | 11.5 [2,22] | **TRIAGE KILL** |
| t6_and3_4a | — | 8.0 [2,19] | **TRIAGE KILL** |
| t6_and4_5a | — | 5.2 [1,22] | **TRIAGE KILL** |

**Root cause (structural):** close AND operands (needed for SEQ-safety) LOCALIZE
differences — a 1-bit flip perturbs only ~3 adjacent term bits per stage, and
the sparse term (1/8, 1/16 density) rarely converts them into state changes.
Scope of kill: narrow-triplet AND3/AND4 WITHOUT a spreading term. The
frontier's answer (al_and6a's (a,b,c) triplets) is the co-design: close
nonlinear pair + wide LINEAR rotation spreader (a permutation — SEQ-immune).

**Test bug found & fixed:** the avalanche triage used V==K, making x0=0, so all
AND terms were identically zero and distances came out constant ([24,24]).
Fixed to V!=K. Batch-28 kill re-confirmed on the fixed test (11.3 max), so
the verdict stands. All future triage uses distinct V,K.

## Batch 29 (2026-10-10 14:15Z): wide-AND + spread rotation (per-stage rk) — S0-DOMINATED

Stage: `x ^= (ra&rb&rc) ^ rot(x,d) ^ rk` — 4-operand XOR tree (2 levels).

| Candidate | S0 | Cells | Triage av | Verdict |
|-----------|----|-------|-----------|---------|
| t6_wand3_5a | 23.7u | 5355 | 32.1 | **S0 DOMINATED** (+3.6u) |
| t6_wand3_5b | 24.5u | 5800 | 31.0 | **S0 DOMINATED** |
| t6_wand4_5a | 23.3u | 5440 | 31.6 | **S0 DOMINATED** |

Diffusion FIXED by the spread rotation (av 31-32). But S0 is +3.2..+4.4u over
the frontier.
**Root cause (measured):** NOT the AND3 — the t6 per-stage-rk convention.
`x^t^r^rk` is a 4-operand XOR that ABC chains as 3 XOR2 levels (+2u/stage
vs al_and6a's 3-operand `x^t^r` at 2 levels). The AND3 itself costs only
+0.2u (1.7 vs 1.5). Mapped netlists confirm ABC maps AND3/AND4 cells (7/4).
**Lesson:** the frontier's key schedule (pre-whiten + final only) is the
correct co-design for wide-AND; per-stage rk costs ~1.4u/stage in XOR depth.

## Batch 30 (2026-10-10 14:30Z): wide-AND + spread, frontier key schedule

Same stages as batch 29 on al_and6a's key schedule: pre-whiten `x0=v^k`,
stages `x ^= (AND) ^ rot(x,d)`, final `out = xN ^ rot(k,13)`.
Projection: 23.7 − 5×1.4 ≈ 16.7u for 5-stage AND3.

| Candidate | Triage av (fixed test) | S0 | Status |
|-----------|----------------------|----|--------|
| t6_wand3_5c | 29.9 [18,38] PASS | running | await S0 |
| t6_wand3_5d | 31.5 [23,42] PASS | running | await S0 |
| t6_wand3_4b | 25.6 [17,38] borderline | running | await S0 (4-stage wall probe) |
| t6_wand4_5b | 30.9 [22,39] PASS | running | await S0 |

If S0 lands ~17u: S1 locally (nice-19) on passers. The 4-stage wall test
(order-3, 8 AND-bits) rides on 4b.

## Batch 30 verdict (2026-10-10 15:00Z): S1-KILLED — wide-AND axis TERMINALLY CLOSED

S1 (local, s1_screen.py) on the three S0 survivors:

| Candidate | S0 | S1 LIN | S1 DIFF | Verdict |
|-----------|----|--------|---------|---------|
| t6_wand3_5c | 20.0u (−0.1u) | FLAG (rej 2/10, D~24-25) | FLAG (rej 10/10, worst\|z\|~3482) | **S1-KILLED** |
| t6_wand3_5d | 20.1u (+0.0u) | FLAG (rej 3/10) | FLAG (rej 10/10, worst\|z\|~21921) | **S1-KILLED** |
| t6_wand3_4b | 16.6u (−3.5u) | FLAG (rej 10/10) | FLAG (rej 10/10, worst\|z\|~104613) | **S1-KILLED** |
| t6_wand4_5b | 20.5u | — (not run) | — | S0-dominated; axis killed by 5c/5d |

**Terminal verdict: wide-AND (AND3/AND4 single-cell) + spread rotation axis
KILLED — VALID kill.** Both schedules S1-killed on the real gate (not a test
artifact; numbers are genuine statistical signals across 10 keys). Higher
nonlinear order per stage (3, 4) does NOT break the 5-stage DIFF wall.
Failure-mode signature: LIN near-clean (2-3/10 rej) but DIFF catastrophic
(10/10, |z| in the thousands) — the same differential-bias family as the
and6a-heterostage kills (xc4c, dual4a-pattern). The 4-stage wall holds against
order-3 as well (4b: LIN 10/10 + DIFF 10/10, |z|~10^5).
**Scope:** 4-5 stage AND3/AND4 with spread rotation + frontier key schedule.
6-stage untested (would be ~24u, latency-dominated — no point).
**Lesson:** the DIFF wall is not about nonlinear order per stage. The
differential bias persists even when linearity is nearly clean; the wall is
about differential mass redistribution, which needs the 6th stage (or a
structurally different final, cf. track-8's chi-final fz30_m).

**Key-schedule finding (stands as a positive result):** the batch-29→30
comparison proves the t6 per-stage-rk convention costs ~0.74u/stage in XOR
depth (23.7→20.0u on identical stages). All future t6 batches use the
frontier key schedule (pre-whiten + final) unless per-stage keying is
specifically being tested.

**Open (new lead):** 5-stage DIFF failure-mode analysis now has a clean
data point (LIN-clean/DIFF-dead at order 3). A chi-final or permutation-final
stage that specifically redistributes differential mass is the co-designed
next probe — overlaps track 5 (hybridization); noted, not started here.

## Batch 31 (2026-10-10 15:10Z, incarnation H): the "final-form" probe — NEW AXIS

**Hypothesis:** b30 proved the 5-stage DIFF wall is NOT about per-stage
nonlinear order. New hypothesis: it's about the FINAL stage's functional
form. A final nonlinear layer with NO outer `x ^=` linear path forces every
differential through a full nonlinear map, redistributing differential mass.
Two sub-axes, both untested in any track:
- (A) **chi-final**: 5-stage (and 4-stage) AND cascade (frontier skeleton,
  SEQ-safe close pairs) + final `x = chi64(x) ^ rot(k,13)`,
  chi64(x)_i = x_i ^ (~x_{i+1} & x_{i+2}). NOTE: chi is a permutation only
  for odd n; at n=64 it is NOT bijective — no bijectivity claim, S1/S2 gate.
- (B) **non-rotational P-box diffusion**: 5-stage AND cascade with the linear
  diffusion term a fixed non-rotation bit permutation (bit-reversal;
  byte-transpose from batch 21) — still 0-delay wiring; every prior cascade
  in every track used rotations only.

**Avalanche triage** (fixed V!=K test):

| Candidate | av [min,max] | Triage |
|-----------|--------------|--------|
| t6_chif5a (5-stage + chi, sched A) | 31.4 [21,39] | PASS → S0 |
| t6_chif5b (5-stage + chi, sched B) | 32.8 [23,40] | PASS → S0 |
| t6_chif4a (4-stage + chi, wall probe) | 29.6 [16,38] | PASS → S0 |
| t6_pbox5a (bit-reversal diffusion) | 19.8 [0,36] | **TRIAGE-KILLED** (structural: reversal misaligns AND pairs vs diffusion) |
| t6_pbox5b (byte-transpose diffusion) | 28.6 [0,39] | PASS → S0 (marginal; min=0 noted) |

Bundles bit-exact (model 200v, impl.c 200v gcc, RTL 20v iverilog — the gen
script's `rotl` helper initially dropped a `]`; fixed, b30's copy was fine).
S0 queued behind the load-backoff gate (load 12.35 at 15:20Z); background
retry loop armed, results land in s0_b31/.

**Overlap note:** chi-final is adjacent to track-5 hybridization and track-8's
fz30_m ([..chi] fused final, 19.8u S1/S2-clean) — but track-6's skeleton
(uniform AND cascade + nonlinear final) is a different construction; if
chif5a lands ~19u with quality, cross-check with track-5/8 rather than
claiming independently.

## Batch 31 verdict (2026-10-10 ~16:30Z, harvested by mix-search-status-30m from raw s1_result.json)

S0 (local, verified from s0_b31/retry.log): chif4a 15.9u/4550c, chif5a 18.5u/5743c, chif5b 19.1u/5626c, pbox5b 18.2u/4464c — all under the 20.1u frontier. All four went to local S1 (s1_screen.py).

| Candidate | S0 | S1 LIN | S1 DIFF | Verdict |
|-----------|----|--------|---------|---------|
| t6_chif4a | 15.9u (−4.2u) | FLAG (rej 2/10) | FLAG (rej 10/10) | **S1-KILLED** |
| t6_chif5a | 18.5u (−1.6u) | FLAG (rej 1/10) | FLAG (rej 10/10) | **S1-KILLED** |
| t6_chif5b | 19.1u (−1.0u) | FLAG (rej 0/10) | FLAG (rej 9/10) | **S1-KILLED** |
| t6_pbox5b | 18.2u (−1.9u) | FLAG (rej 8/10) | FLAG (rej 10/10) | **S1-KILLED** |

**Terminal verdict: BOTH sub-axes TERMINALLY CLOSED (VALID kills — the batches
were properly co-designed: SEQ-safe close AND pairs, spread diffusion,
frontier key schedule).**
- (A) chi-final: a final `x = chi64(x) ^ rot(k,13)` does NOT redistribute the
  differential mass that the 5-stage DIFF wall blocks. The failure signature
  (LIN near-clean, DIFF 10/10) is identical to the and5a/wand3_5c family — the
  final-form hypothesis is falsified: chi at the final stage is itself
  differentially biased in this composition (chi is a permutation only for
  odd n; at n=64 its differential profile leaks through). Do NOT design
  chi-final variants.
- (B) non-rotational P-box diffusion (byte-transpose): DIFF 10/10 with LIN
  8/10 — the transpose destroys the AND-pair/diffusion co-design (pairs
  misalign under transpose on SEQ inputs). Do NOT design non-rotational
  diffusion variants of the cascade skeleton.

**Standing rule from b31:** the 4/5-stage DIFF wall now holds against
AND-order (b30), final-form nonlinearity (b31A), and diffusion-permutation
shape (b31B). The wall is a property of the 5-stage AND-cascade skeleton
itself, not of its per-stage order, final form, or diffusion shape. The
remaining untried levers are: (1) state-structure changes (lanes with proven
bijectivity, staged cross-feeds), (2) stage-function changes with different
XOR-tree depth economics (sandwich, skip-coupled), (3) anything that is NOT
a uniform cascade. — incarnation I, 2026-10-10 17:43Z.

## Batch 32 (2026-10-10 17:45Z, incarnation I): post-cascade structural axes — NEW AXIS

**Design rationale:** batch-31 falsified the last cascade-skeleton levers
(per-stage order, final form, diffusion shape). Batch 32 abandons the uniform
cascade skeleton entirely — three structural axes, all untested in any track.

(A) **Cross-fed dual-lane cascade**: two 64-bit lanes evolve in parallel.
    Lane A: N-stage AND cascade on x0=v^k (proven skeleton). Lane B:
    N-stage AND cascade on b0=rot(k,29), each stage one-way fed
    `b ^= F(b) ^ rot(a_j, s_j)`. Output `a_N ^ b_N ^ rot(k,13)`.
    Bijectivity PROVEN: a-chain bijective; each b-stage is
    b -> b ^ F(b) ^ const(a_j) (bijective); composition bijective; output
    fold is 2:1 (fine for a finalizer). Crit-path target ~12u at N=3.
    Differentials propagate through two coupled recurrences, not a cascade.
(B) **AND-sandwich stage**: genuinely new stage function
    `x ^= rot(x,a) ^ (rot(x,b) & rot(x,c)) ^ rot(x,d)` — two direct linear
    rotations with the AND product BETWEEN them (al_and6a: one linear + AND).
    4 XOR operands + 1 AND at ~2-level XOR tree. Frontier key schedule.
    (b,c) close (|b-c|<=2), SEQ-safe.
(C) **Skip-coupled cascade**: `x_j = x_{j-1} ^ t_{j-1} ^ rot(x_{j-1},d_j) ^
    rot(x_{j-2}, s_j)`, x_{-1}=0 — residual coupling on the x-STATE
    (batch 24 coupled the t-terms; this is a different axis). Each stage
    x -> x ^ const, bijective. The skip gives differentials a linear bypass
    around the stage's AND.

**Avalanche triage** (fixed V!=K test):

| Candidate | av [min,max] | Triage |
|-----------|--------------|--------|
| t6_lane3a (3+3, sched A) | 24.3 [14,33] | **TRIAGE-KILLED** (below the 28 bar; cf. killed 2r-Feistel 24.1) |
| t6_lane3b (3+3, sched B) | 28.6 [22,36] | PASS (marginal) -> S0 |
| t6_lane4a (4+4, sched A) | 32.6 [24,40] | PASS (strong) -> S0 |
| t6_sand5a (5-stage sandwich, A) | 31.9 [24,41] | PASS -> S0 |
| t6_sand5b (5-stage sandwich, B) | 31.9 [24,41] | PASS -> S0 |
| t6_sand4a (4-stage sandwich, C) | 31.4 [18,44] | PASS (wall probe) -> S0 |
| t6_skip4a (4-stage skip) | 28.6 [20,41] | PASS (marginal) -> S0 |
| t6_skip5a (5-stage skip) | 31.7 [20,40] | PASS -> S0 |

Note: lane3a's kill is schedule-scoped, not axis-scoped (lane3b passes on the
same axis with a different schedule) — per co-design-before-kill, only the
lane3a schedule is dead, not the dual-lane axis.

Bundles bit-exact (model 200v, impl.c 200v gcc, RTL 20v iverilog — ALL OK,
gen_t6_b32.py). S0 queued behind the load-backoff gate (load 13.55 >= 12 at
17:47Z): s0_b32_retry.sh polls every 120s, runs 7x run_synth (nice-19,
sequential) when clear, results -> s0_b32/, marker s0_b32/DONE.

## Ownerless analysis resolved (2026-10-10 17:52Z, incarnation I): trivium64/gimli KILLED-INVALID audit

Open since batch 24: "co-design audit of t6_trivium64/t6_gimli kills
(KILLED-INVALID review required before burying)."
AUDIT RESULT: **both kills are VALID, not KILLED-INVALID — terminal.**
- t6_trivium64 (19.8u): S1 LIN 10/10, DIFF 10/10. The batch already tested
  the co-designed variant t6_trivium64b (denser taps + 8x8 clocks) — still
  catastrophically linear. The only remaining co-design knob is MORE clocks,
  which is latency-dominated by construction (6x8 clocks = 19.8u; doubling
  to fix quality pushes ~40u, S0-dead). No fair re-test exists at
  frontier-competitive latency. Construction-class kill stands.
- t6_gimli (21.4u): 64-bit-reduced Gimli SP-box, same catastrophic linear
  signature. Same argument: full rounds cost ~40u+ (dominated); the reduced
  form is the only latency-viable point and it is quality-dead.
Scope recorded: NFSR/shift-register cascades at 64-bit with <= ~20u latency
budget cannot kill linear trails when (input,key) both vary. CLOSED.

Remaining ownerless analysis: 5-stage DIFF failure-mode root-cause
(t6_and5a family) — partially informed by b30 (order-3) and b31A (chi-final)
data points; formal analysis still open. The standing rule from b31 (the
wall is a skeleton property, not per-stage/final/diffusion) is the current
working characterization.

## Batch-32 TERMINALLY CLOSED (2026-10-10 21:20 CEST, track-6 incarnation II)

All 4 sub-frontier S1-KILLED, raw-verified from fast_battery/results/b32_chain.log
(chain ran 18:36-18:39Z by the 20:42 status report; this session verified numbers,
no duplicate run):
- t6_lane3b (15.0u, FASTEST S0 EVER): S1 FLAG LIN=10/DIFF=10, worst|z|=458502
- t6_skip4a (17.8u): S1 FLAG LIN=10/DIFF=10, worst|z|=18852.9
- t6_lane4a (18.2u): S1 FLAG LIN=10/DIFF=10, worst|z|=1553.8
- t6_sand4a (18.8u): S1 FLAG LIN=1/DIFF=10, worst|z|=52224.4
xcheck PASS 10000/10000 on all four. The cross-fed dual-lane / AND-sandwich /
skip-coupled axis is TERMINALLY KILLED (VALID) — same DIFF-wall signature as
batch-31 chi-final. Ledger rows updated (LEADS_LEDGER.md 21:20 CEST entry).

## DIFF-wall structural analysis (ownerless lead, OWNED 2026-10-10 21:20 CEST)

MECHANISM HYPOTHESIS (t6_diffwall_analysis.py): for stage
`x ^= (rot(x,a)&rot(x,b))^rot(x,c)`, a weight-1 input delta 2^k produces a
DETERMINISTIC output-differential skeleton
  D[x1]_i = d_i ^ d_{i-c}   for all i not in {k+a, k+b}   (exact, any x)
because D[a&b]_i = (da_i&b_i)^(db_i&a_i)^(da_i&db_i) is value-independent
wherever the input differential carries no delta. Each stage only randomizes
bits the AND probes; the S1 DIFF wall = deterministic skeleton bits SURVIVING
to the output (a single deterministic outbit makes the low-8-bit chi2
catastrophic — matches observed worst|z| 10^3..10^5). Design rule: the skeleton
must fully randomize before the last stage; rotation schedules are the
co-design knob. Verification: t6_diffwall_verify.py (nice-19, bg) counts
deterministic differential bits per stage on RANDOM inputs, dead-vs-al_and6a.
Predictions: P1 dead designs have >=1 deterministic output bit; P2 al_and6a has
zero; P3 al_and6a's per-stage count -> 0 before the last stage.

**RESULT 21:35Z (t6_diffwall_verify.py + verify2.py, random inputs, 2^18 pairs):
MECHANISM CONFIRMED with a refinement.**

| candidate | worst det_bits | worst max|z| | det decay/stage | S1 |
|---|---|---|---|---|
| t6_lane3b | 17 | huge | [126,113,63] fold | FLAG 458502 |
| t6_skip4a | 2 | 512.0 | [62,54,29,2] | FLAG 18852.9 |
| t6_sand4a | 0 | 258.8 | [62,54,24,0] | FLAG 52224 |
| t6_lane4a | 0 | 194.7 | [126,114,69,4] fold | FLAG 1553.8 |
| al_and6a | 0 | 3.5 | [62,54,29,1,0,0] | CLEAN |

Findings:
1. Every `x ^= (ra&rb)^rc` stage imprints a deterministic differential
   skeleton (~62 det bits after stage 1; 126 for dual-lane fold). The skeleton
   decays as the AND probes randomize it — but 4-stage designs never reach
   det=0 with margin (skip4a: 2 left; lane4a: 4 left; sand4a: 0 only at the
   LAST stage).
2. det=0 is NECESSARY but NOT SUFFICIENT: sand4a reaches det=0 yet max|z|=
   258.8 (catastrophic bias without determinism). The discriminator that
   rank-predicts S1 DIFF is **max|z|** (dead: 194-512+, clean: 3.5).
3. al_and6a: det->0 at stage 5 of 6, then one full margin stage -> max|z|=3.5.
   Rule: skeleton must extinguish with >=1 stage of margin for bias decay.
4. Depth, not rotation quality, separates sand4a [62,54,24,0] from and6a
   [62,54,29,1,0,0] through stage 3 — consistent with track-3's 5-stage wall
   theorem and track-8's "more stages = fewer fails". Minimal clean depth for
   AND2-xor cascade ~6 (4 and 5 die, 6 lives).
5. The det-decay/max|z| proxy runs in ~2 min/candidate (vs S1 minutes +
   synthesis) and rank-predicts S1 DIFF — usable as a CHEAP rotation-schedule
   triage. Validation vs as6_200_106 (dead 6-stage) running (t6_proxy_validate.py):
   if it distinguishes dead-vs-clean 6-stage rotations, batch-33 = proxy-guided
   rotation screen for 6-stage AND cascades.

**RESOLUTION 21:45Z:**
- The GHA "diff_rejected deltas 0 and 4660" = **KEYS 0x0 and 0x1234**
  (4660 = 0x1234 decimal): rejected (DIFF, key) cells. Local s1_screen.py on
  as6_200_106 reproduces the kill bit-for-bit (DIFF FLAG rej=2, worst|z|=71.4
  on keys 0x0/0x1234, LIN PASS; log s1_as6_200_106.log). The 6-stage rotation
  wall manifests on STRUCTURED keys, not random ones — the 3-key proxy missed it.
- Refined triage = EXACT S1 DIFF (lin_diff.diff_cell_logps, all 10 keys,
  sequential, ~40s/candidate, no synthesis): reproduces S1 DIFF verdicts exactly.
- **Batch-33 pilot LAUNCHED** (t6_b33_screen.py, nice-19, bg, log b33_pilot.log):
  20 random 6-stage AND rotation schedules through the exact-DIFF triage,
  KEEP bar max-worst|z| < 10 (al_and6a ~= 3.0, as6_200_106 = 71.4). Survivors
  escalate to S0 + full S1. Genuinely new METHOD axis (proxy-guided rotation
  search; track-3's 120-sched screen used the weak proxy and all died).

## NEW AXIS: ARX (2026-10-10 21:20 CEST, track-6)

al_arx1 (single-addition) / al_arx2 (2-addition) bundles existed in
fast_battery/candidates/ with goldens but were NEVER screened and never
ledgered — buried lead surfaced this session, added to LEADS_LEDGER.md.
Addition's differential has NO deterministic skeleton (carry chain is
value-dependent at every bit) — the natural DIFF-wall escape; latency target
is adder-like (the ultimate goal). Full battery S0->S4 chain launched
21:15Z (nice-19, agentwork-launch, tag mix/track6/arx-chain, log
fast_battery/results/arx_chain.log). **INFRA REPAIRS by this session (both
bundles were incomplete):** al_arx1/impl.c was a STUB (returned 0) -> real impl
written from model.py, bit-exact (goldens + 2000/2000 vs Python); al_arx1/rtl.v
was a stub -> real RTL written (ports val/key/out, P-box as wiring);
al_arx2/rtl.v ports renamed v,k,o -> val,key,out (pipeline binds by name);
both meta.json gained "rtl_top". First chain: al_arx1 xcheck-FAIL (stub, since
fixed), al_arx2 S0-infra-FAIL (missing rtl_top, since fixed). **Relaunched
21:20Z** (tag mix/track6/arx-chain2, log fast_battery/results/arx_chain2.log).

**VERDICTS 21:25Z — shallow-ARX TERMINALLY KILLED (VALID):**
- al_arx1: S0 PASS 81.2u (0.785x mult, bar 0.9; equiv 1000/1000) then S1-FLAG
  (LIN 10/10, DIFF 10/10, worst|z|~1.48M — worse than the boolean cascades).
  Mechanism: a single addition's differential is concentrated on ~64-k
  carry-run values for weight-1 input delta 2^k; the linear post-layers
  (xor-rots, P-box) only permute that structured set. Structural for
  one-addition designs.
- al_arx2: S0-FAIL 150.3u (1.452x mult > 0.9 bar) — two 64-bit adds delay-dead.
Axis closed: 1 add quality-dead (structural), 2+ adds delay-dead. Re-test
trigger: addition-driven diffusion within delay budget (parallel narrow adds).
Ledgered 21:30 CEST.

## Batch-33 OPENED (2026-10-10 21:50 CEST, track-6)

Proxy-guided 6-stage AND rotation screen. Pilot (t6_b33_screen.py, exact S1-DIFF
triage = lin_diff.diff_cell_logps on all 10 keys): **7/20 KEEP** (z 2.6-8.3;
bar <10; 13 killed z 20-4086, mostly on key 0x0):
- t6_b33a z=2.6 [(37,43,51),(12,11,63),(28,33,27),(63,2,57),(4,14,1),(18,17,40)]
- t6_b33b z=3.0 [(58,53,21),(52,17,18),(25,23,40),(54,55,13),(42,33,61),(53,57,29)]
- t6_b33c z=3.3 [(25,45,42),(44,14,26),(51,54,34),(41,53,51),(54,40,6),(12,15,11)]
- t6_b33d z=3.4 [(38,34,15),(47,35,33),(47,2,23),(16,11,60),(19,5,44),(18,42,41)]
- t6_b33e z=5.7 [(57,43,8),(41,50,24),(52,3,22),(36,32,21),(41,56,10),(54,56,22)]
- t6_b33f z=6.9 [(25,44,8),(27,40,37),(63,5,39),(11,22,6),(29,7,21),(12,3,44)]
- t6_b33g z=8.3 [(21,46,53),(29,16,38),(57,4,18),(5,59,5),(12,41,31),(23,11,51)]
Bundles: gen_t6_b33.py (model.py/impl.c/rtl.v/meta.json+goldens+rtl_top),
bit-exact 300/300 C-vs-Python (b33_verify.py). Full battery S0->S4 chain
launched 19:48Z post-reboot (nice-19, tag mix/track6/b33-chain, log
fast_battery/results/b33_chain.log). NOTE: VM rebooted ~19:48Z; chain is the
first post-reboot track-6 work.

## Batch-33 first verdict (2026-10-10 21:55 CEST)

t6_b33a (S0 20.4u, triage z=2.6): **S1-FLAG — LIN PASS, DIFF PASS** (exact-DIFF
triage validated: it correctly predicted DIFF survival), **marginal kill:
PB rej=2** (SINGLE-BIT on keys 0x0 and 0xFFFFFFFFFFFFFFFF — same anomaly class
as as6_200_15). Lesson: triage is DIFF-only; marginal PB/RD is a separate gate.
Structured keys (0x0, 0x1234, 0xFF..F) are where 6-stage AND cascades show
defects — key-structure interaction is the next analysis target. Chain
continues with b33b-g (log fast_battery/results/b33_chain.log).

## Batch-33 second verdict (2026-10-10 22:00 CEST) — FIRST S1 SURVIVOR

t6_b33b (S0 20.1u, triage z=3.0): **S1 CAL_PASS — verdict CAL_PASS, ALL reject
lists EMPTY** (pb_red/rejected=[], lin_rejected=[], diff_rejected=[]; LIN/DIFF
26s PASS rej=0; marginal 187s PB rej=0 RD rej=0; wall 193s). Raw:
fast_battery/results/t6_b33b/{s1_result.json,battery.log}.
**AUTO-ESCALATED to S2** by the chain 19:55:19Z (run_fast_battery.sh runs
S0->S4 stopping at first kill). Delay 20.1u TIES the frontier speed point
al_and6a 20.1u — if S2/S3/S4 pass, b33b joins the frontier (independent
6-stage AND rotation schedule, 5992 cells vs al_and6a 6116 — possible
dominance on cells at equal delay). Chain continues c-g.
