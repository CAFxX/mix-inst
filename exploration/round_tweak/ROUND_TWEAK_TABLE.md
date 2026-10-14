# Round TWEAK — exhaustive local-neighborhood hill-climbing (2026-10-03)

S0-gated single-parameter perturbations around frontier points, with
analytical failure analysis steering the sweep order (diagnosis → next probe).
Complements round 21 (directed), hybridization, GA, and analytical tracks.

Parents: chioff13all 37.0u/4357/12511 (Frontier S speed), chioff31
37.5u/3863/11199 (Frontier S size), fm07 38.8u/5053/14320 (Frontier Q speed).

## Neighborhoods

| ID | Perturbation | # probes | Parent | Promote rule |
|---|---|---:|---|---|
| N1 | lin rotation pairs (a,b), 1≤a<b≤15, all-5-linears, minus 7 tested in range | 99 | chioff13all | delay<37.0 → battery; ≤37.3 → S1+S2 (top 5) |
| N2 | chi offsets (2,3),(3,2) on r2,4 / r6-tr; mixed (3,1)+(1,3); on 31-base | 8 | chioff13all/chioff31 | delay<parent → battery |
| N3 | final mixing y^rotl(y,m), m=1..31, on chioff13all + chioff31 | 61 | fm07 38.8u | delay<38.8 → Q1 → battery iff bic≤0.02 |
| N4 | RK rotation multiplier c ∈ odd 1..31 | 15 | chioff13all | delay<37.0 → battery |
| N5 | single-round F swaps (s1↔chi13, →chi31; r6 →s1/chi31) | 12 | chioff13all | delay<37.0 → battery |
| Z1 | round constants (single-bit×9, byte×4, counter×2), Keccak-iota style | 15 | chioff13all | delay<37.0 → battery; ≤37.1 → S1+S2 |
| Z2 | free P-box (rev/byteswap/nibperm) + single-rot lin(3/7/11) | 9 | chioff13all | **ANALYSIS-KILLED**: single-rot linear provably singular (see below) |
| Z2b | free P-box (in/out/inout) + bijective lin(3,11) kept | 9 | chioff13all | delay<37.0 or area win → battery (S2 |z| arbiter) |
| Z3 | constant pre/post whitening (GOLDEN64) | 5 | chioff13all/chioff31 | delay<37.0 → battery; ≤37.1 → S1+S2 |
| Z4 | masked micro-step x^((x>>>r)&M) on chi rounds, r×M grid | 32 | chioff13all | delay<37.0 → battery; ≤37.3 → S1 (top 6) |
| N6 | truncation toggle on Frontier-Q points | 0 (covered) | — | covered by r19: ps_notr 39.5u, r9_notr 39.9u, both dominated; not re-swept |
| N7 | odd-term 3-rotation linears on notr (round 21 FA1 axis): N7a x^R^a^R^b (465 pairs, id kept), N7b R^a^R^b^R^c (455 triples vals≤15, id dropped); GF(2) rank pre-gate (all 920 rank 32, 0 singular — see A3) | 920 | notr | S1/S2 if ≤38u OR ≤3800 cells; battery on Pareto win |
| N8 | fm cures on the rtw_lin_ab0408 chassis (32: m=1..31 + '311'): ab0408 is the sweep's fastest probe (35.7u) with S1–S4 PASS, Q1-killed only (sac_z5=12, bic=0.255, unmixed-final-chi class); O22's fm cure transfers — the prize is beating r21b_3rot_ns_fm311 (38.3u) as fastest Frontier-Q-eligible Feistel point. **Cost calibration (2026-10-11, from N3 on the same base family): fm costs +2.1–3.8u on chioff13all (39.1–40.8u) and +1.1–3.3u on chioff31 (38.6–40.8u) — NOT the +0.9–1.9u seen on notr (O22). Expected ab0408+fm range ~37.8–39.5u; only the cheapest-m variants (cf. fm14's +1.1u on chioff31) can beat the 38.3u bar. First probe rtw_ab48_fm01: 38.7u (+3.0u, outside the 37.7u stats window → terminal, no stats burned).** | 32 | rtw_lin_ab0408 35.7u | delay<38.3 → Q1 → battery iff bic≤0.02 (fq_speed rule) |
| N9 | winner-pbox × near-miss pairs: rev-inout pbox (Z2b winner) × lin pairs (4,8)/(6,12)/(3,8) on chioff13all — tests additivity of two independent wins on the same parent | 3 | chioff13all | delay<37.0 or area win → battery (S2 |z| arbiter) |
| N10 | Z1 round constants (bit15/ctr/ctrg — the three Z1 variants that moved the parent) re-targeted on the ab0408 chassis | 3 | rtw_lin_ab0408 35.7u | delay<35.7 → battery |

Total: 1220 probes (1182 + 38 N8/N9/N10, 2026-10-11).

## Cuts recorded with reasons (2026-10-11 batch design)

- **N7-on-truncated-chassis: CUT.** N7's 10 stats-window probes on notr: 6 S1 CAL_PASS but S2 differential spikes zmax 59–1024 (rtw_n7b_010407: 58 deltas |z|>15, worst 683) — the 3-rotation linear family is differentially weak independent of chassis; the notr chassis was already structurally +3.0u (rtw_n7a_0311 baseline). No evidence the truncated chassis repairs the family's differential weakness → not opened. Re-test trigger: a 3-rot variant that is S2-clean on notr.
- **nibperm-ordering variations on Z2b: CUT.** No mechanistic differentiator: nibperm space is 8! with no proxy to rank orderings; rev already won. Recorded, not probed.
- **fm cure on rtw_lin_ab0612 (bic 0.035): CUT.** fm adds +0.9–1.9u (O22) → ~37.6u, slower than its 36.7u parent with no delay prize — a bic cure that costs the delay win. Recorded, not probed.
- **ab0306 family: CUT.** S1 FLAG (diff rej=5), dead by the promote rule.
- **Z3 whitening on new chassis: CUT.** Z3 showed no win on the parent (all 5 probes); no mechanism for a different outcome on ab0408.

## Winners (2026-10-11 correction)

**The sweep's "winners=[]" terminal line was wrong.** The in-memory `winners`
list was wiped on every restart (the sweep restarted ~15 times over its run),
so 4 `*** WINNER` declarations in the log never reached the summary or
`winners.txt` (which was empty). Fixed 2026-10-11: winners persist into the
record (`rec["winner"]`) and `work/winners.txt` at declaration time, with
backfill on startup. Re-audit of `work/sweep_results.json` (battery rc=0,
S3 PASS, S4 PASS, Q1 sac_z5=0) gives **6 true winners**:

| Candidate | NB | Delay | Cells | Area | bic | Frontier relevance |
|---|---|---:|---:|---:|---:|---|
| rtw_lin_ab0612 | N1 | 36.7u | 4,068 | 11,698 | 0.035 | **Frontier-S candidate: ties r21 chioff31final (36.7u) on delay, −130 cells, −307 area** — parent's call after raw-log verification |
| rtw_pb2_rev_inout | Z2b | 36.9u | 4,284 | 12,210 | 0.143 | qualified but dominated (chioff31final 36.7u/4,198/12,005) |
| rtw_rk07 | N4 | 36.9u | 4,300 | 12,396 | 0.144 | dominated |
| rtw_rk23 | N4 | 36.9u | 4,446 | 12,686 | 0.142 | dominated |
| rtw_rc_bit15 | Z1 | 36.9u | 4,418 | 12,702 | 0.142 | dominated |
| rtw_fm14_31 | N3 | 38.6u | 4,770 | — | 0.0089 | bic-clean but dominated by r21b_3rot_ns_fm311 (38.3u) |

Near-miss with the highest remaining value: **rtw_lin_ab0408** (N1, 35.7u/3,970/11,453) —
full battery PASS (S3/S4 rc=0), killed ONLY at Q1 (sac_z5=12, bic=0.255).
The N8 neighborhood (above) is the co-designed follow-up.

## S0 sweep results

| Candidate | NB | Delay | Cells | Area | vs parent | Disposition |
|---|---|---:|---:|---:|---|---|
| rtw_pb_rev_a03 | Z2 | 33.1u | 3,207 | 9,310 | −3.9u / −1,150 cells | **S1-KILLED** (LIN rej=10, DIFF rej=10; singular linear — see A1) |
| rtw_pb2_rev_in | Z2b | 37.5u | 4,411 | 12,443 | +0.5u / +54 cells | no win |
| rtw_pb2_rev_inout | Z2b | 36.9u | 4,284 | 12,210 | −0.1u / −73 cells / −301 area | **🏆 WINNER** — full battery PASS (S0/S1/S2/S3/S3b/S4 rc=0), Q1 sac_z5=0 (bic=0.143); S1 CAL_PASS ×4, S2 0 repeats |z|=12.4 ×3, S0 36.9u ×4 |
| rtw_pb2_rev_out | Z2b | 38.0u | 4,119 | 11,819 | +1.0u / −238 cells | no win (slower; smaller but delay dominates) |
| rtw_lin_ab0102 | N1 | 37.0u | 3,643 | 10,532 | =delay, −714 cells | no win (delay not < 37.0) |
| rtw_ms_r03_byte | Z4 | 37.7u | 4,505 | 12,893 | +0.7u | dominated |
| rtw_fswap_r2_s1 | N5 | 37.7u | 4,253 | 11,958 | +0.7u | no win (s1 costlier than chi here) |
| rtw_n7a_0311 | N7a | 40.0u | 4,407 | 12,743 | +3.0u vs r20 notr (37.0u) | **baseline probe**: all-6-rounds lin(3,11) vs r20's 5-round version — the round-6 linear costs +3.0u on this chassis; confirms the N7a chassis is structurally slower (best of 237 so far: 38.2u) |

*(table fills as the sweep runs; see [work/sweep_results.json](work/sweep_results.json))*

**Resume checkpoint 2026-10-04 ~01:00 CEST:** previous coordinator died 2026-10-03
22:56 UTC on a runtime restart (not a task failure). State: [`rtweak.py`](models/rtweak.py)
self-test green; `rtw_n7a_0311` was never emitted (stale build-FAIL entry) —
emitted via `gen_tweak.emit_one` and its results entry cleared so the sweep
re-queues it (S0 40.0u/4407/12743, see row above). Sweep relaunched detached
(`setsid nohup python3 [sweep.py](sweep.py)`, log [`work/sweep_resume.log`](work/sweep_resume.log)), resumed from
the [`sweep_results.json`](work/sweep_results.json) checkpoint (1182 specs, 259 already probed, no redo).
Registered as `mix-tweak-sweep` in the work registry. rtw_pb2_rev_inout needs
nothing further (parent-verified, [RETAINED.md](../RETAINED.md) #24, dominated off-frontier).

## Failure analyses

Analytical failure analysis per probe (signal → mechanistic hypothesis →
steered next probes). Raw records: [work/diagnoses.jsonl.](work/diagnoses.jsonl)

### A1 — rtw_pb_rev_a03 (Z2): single-rotation linear is provably singular [KILL]
- **Signal**: S0 33.1u/3,207/9,310 ("fast number, broken design"); S1 LIN
  FLAG rej=10, DIFF FLAG rej=10, worst|z|=233775.6 (logp=-inf).
- **Mechanism (proven)**: L(x) = x^rotl(x,a) is non-bijective for EVERY a:
  1+t^a is always divisible by (1+t), and t^32+1 = (t+1)^32 in
  characteristic 2, so L(0xFFFFFFFF) = 0 — a 2-to-1 collision in the linear
  layer (verified numerically for a=3,7,11; (3,11) confirmed injective).
  A singular F-layer collapses diffusion no matter what P-box surrounds it;
  the "P-box compensates for dropped rotation" hypothesis was untestable in
  this chassis. The 33.1u was synthesis exploiting the degenerate layer.
- **Steered next probes**: Z2b (9 probes: free P-box at in/out/inout +
  bijective lin(3,11) kept) prioritized to the head of the queue — the
  corrected experiment. The other 8 single-rot Z2 probes are ANALYSIS-KILLED
  by the proof (no synthesis burned).
- **Cross-track note**: single-rotation linear layers are dead as a gene for
  the GA track too (any x^rotl(x,a) is singular on 32 bits).

### A2 — [sweep.py](sweep.py) battery_done() false-positive [INFRA BUG, fixed]
- **Signal**: After a VM reboot killed the rtw_pb2_rev_inout battery mid-S3b,
  the resumed sweep logged "PROMOTE-SKIP: battery already done" and marked a
  WINNER without S3b/S4/Q1 ever running.
- **Mechanism**: `battery_done()` matched bare `"FAIL" in log_text` — the
  killed battery.log contained "no FAIL" (from passing S3 stages), a
  substring false-positive. The function also never checked for the actual
  completion marker.
- **Fix**: `battery_done()` now requires `"BATTERY-PASS" in t or
  "BATTERY-FAIL" in t` (the script's explicit terminal markers). Sweep
  restarted; rev_inout re-ran the full battery to a genuine PASS.
- **Process lesson**: terminal-state predicates must match explicit
  completion markers, never substrings that also appear in progress logs.
  (Same class as the AGENTS.md "silent wrong numbers" lessons.)

### A3 — N7 GF(2) rank pre-gate results (round 21 FA1 axis)
- **Pre-gate**: For each odd-term linear, compute GF(2) rank of the 32×32
  layer matrix; skip rank<32 before synthesis (FA1 lesson: singularity is
  checkable in milliseconds).
- **Result**: All 920 pass — 465/465 Type A (x^R^a^R^b) rank 32, 455/455
  Type B (R^a^R^b^R^c, vals≤15) rank 32, **0 singular**.
- **Why (theory)**: t^32+1 = (t+1)^32 in char 2, so L is singular iff
  p(1)=0 where p(t) is the layer polynomial. Odd-term (3 XOR terms) ⇒
  p(1)=1 ⇒ gcd(p,(t+1)^32)=1 ⇒ always bijective. The pre-gate is a
  no-op for odd-term but stays in code to catch future even-term slips.
- **Steered**: N7 queued at priority 1 (highest-value rotation work per
  parent directive; even-term space closed by O29).

## Winners

*(candidates passing the full battery + Q1 with Pareto improvement; [PARETO.md](../PARETO.md)
is updated by the parent only after raw-log verification)*

### 🏆 rtw_pb2_rev_inout (Z2b neighborhood, 2026-10-03)
- **What**: r20 chioff13all + free bit-reversal P-box at F input AND F output (bijective lin(3,11) kept).
- **S0**: 36.9u / 4,284 cells / 12,210 area — beats parent (37.0u/4,357/12,511) on all three axes (−0.1u, −73 cells, −301 area). Measured 4×, deterministic.
- **Gates**: S1 CAL_PASS ×4 | S2 PASS ×3 (0 repeats, max|z|=12.4) | S3 PASS ×2 (PractRand 16MB→1GB, no FAIL) | S3b PASS (strided) | S4 PASS (TestU01 SmallCrush) | Q1 sac_z5=0 (bic=0.143, reported not gated).
- **Evidence**: `fast_battery/results/rtw_pb2_rev_inout/battery.log`, `round_tweak/work/sweep.log`, `round_tweak/work/sweep_results.json`.
- **Note**: Frontier has moved since this probe was designed (r21 chioff31final 36.7u now leads); parent to verify Pareto status vs current frontier. The 36.9u is a strict improvement over its design parent (r20 chioff13all 37.0u).

## Process notes

- Correctness before S0: every probe gets 1k-vector C↔model xcheck and
  300-vector RTL↔model check BEFORE synthesis (cheap insurance against
  "fast number, wrong design").
- Dedupe by model equivalence before synthesis: against all existing
  fast_battery candidates AND within the sweep (48-vector signatures).
- S0 via run_synth.synth_one (authorized flow: pinned Yosys 0.69,
  memory_map before techmap, dual-analyzer agreement); reference
  re-measurement skipped for probes, full [run_synth.py](../run_synth.py) for winners.
- Polite concurrency: backoff when ≥2 heavy pipelines system-wide.
- N1 control rtw_lin_ab0311_ctrl re-probes (3,11) to check flow determinism.
- **Standing retention rule (Carlo 2026-10-03)**: NEVER delete
  `fast_battery/candidates/<name>/` or any round logs — for any candidate,
  retired or not. "Retired" = off the Pareto frontier only. Every
  full-battery survivor is retained indefinitely (extended PractRand
  breaking-point batteries will run over all of them; registry at
  [`exploration/RETAINED.md`](../RETAINED.md)). This sweep never deletes.
