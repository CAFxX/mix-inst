# fz24_o independent verification report (2026-10-10 ~14:40 CEST)

**Claim under test** (track-8 supervisor, waves 24-26, handoff 13:01 CEST):
fz24_o = 5-stage [t3(1,7,13,29), t3(3,11,19,37), AND(5,15,21), AND(9,23,43),
CHI(31,19,35,53)], "20.3u, S1/S2-clean" — 0.2u over the 20.1u frontier
(al_and6a). UNVERIFIED at handoff: no raw S0/S1/S2 artifacts in tree,
no report file, 20.3u provenance unknown.

**Scope**: S0 via pinned run_synth.py + S1 + S2. No S3/S4 (per brief). No frontier
claim — raw numbers only.

## Construction checked
- Candidate tree `fast_battery/candidates/fz24_o/`: rtl.v / model.py / impl.c /
  meta.json all present and mutually consistent with the claimed spec
  (verified by reading; stage semantics t3/and/chi as in gen_fused24.py).
- Bit-exactness chain (independent): pure-Python spec model
  (`ref_fz24_o.py`, written directly from the stage-semantics spec, NOT from
  the generator) == model.py on **10,000 random + 144 edge vectors**; impl.c ==
  model.py on **10,000/10,000** (battery xcheck). RTL equiv (below) closes
  the loop.

## 1. S0 — pinned flow (run_synth.py, the only authorized delay path)
Raw: `s0_result.txt` (RESULT record), mapped netlist in `s0/_dut/`.
- REF mul64: cells=12645 area=35323 crit=103.5
- DUT fz24_o: cells=5870 area=18260 crit=20.3
- delay_ratio=0.196, area_ratio=0.517
- XCHECK: analyze.py == analyze2.py (cells/area/crit identical)
- **Verdict: supervisor's 20.3u REPRODUCED exactly on the pinned flow.**
- Equiv check (own replication of s0_delay.py::equiv_check, oracle = independent
  spec model): `EQUIV n=1000 err=0 -> PASS` (`s0/equiv.out`) — the mapped
  netlist that produced the 20.3u number exactly implements the spec'd
  construction. No dretime-miscompile class of issue.

## 2. S1 — calibration + differential screen (fast_battery, exact code)
Raw: `s1/s1.out`, `s1/s1_result.json`.
- LIN family (10 keys, N=2^18): rej=0; D=16-25/4096 per key (null ~20.5).
- DIFF family: rej=0; worst|z| per key 1.5-2.5 (fisher/bonf logp all >= -1.68).
- Marginal PB+RD (468 cells, 10 keys, 246s): pb_rejected=[], red_rejected=[];
  raw worst per-bit z=4.40, raw worst red z=3.01.
- **Verdict: CAL_PASS (exit 0). Supervisor's "S1-clean" claim CONFIRMED,
  down to the same per-key worst|z| 1.5-2.5 band the row quotes.**

## 3. S2 — full diffprof (all 115 deltas)
Raw: `s2/s2.out`. Command: `diffprof_fz24_o 0x123456789abcdef0 22 10`
(key=practrand_keys[0], N=2^22, kill_repeats from ref/s2_kill_repeats.txt).
- `PASS max_repeats=0 max|z|=48.7 (all 115 deltas)`
- Worst per-bit flip bias 48.7 on weight-1 delta 0x0020000000000000 (bit 53);
  next 48.2 (bit 21), 46.1 (bit 63), 44.7 (bit 61). full_repeats=0 everywhere.
- **Verdict: S2 PASS (repeats-based gate).**

## Discrepancies / notes
1. The ledger's supervisor-authored row claimed S2 max|z|=26.2. The canonical
   diffprof run (deterministic) gives 48.7. No supervisor S2 artifact exists in
   the tree, so the 26.2 has no provenance; it is superseded by the
   artifact-backed 48.7. Verdict (PASS, repeats=0) agreed.
2. The row's "Bit-exact 200/200" understates the check: 10k-vector chain done.
3. README prose claims S2 kill threshold 1000, but the battery actually reads
   ref/s2_kill_repeats.txt (= 10, principled per MAJOR-7: null E[repeats]=2^-42,
   any repeat is ~2^42 above null). The run applied the file's bar (10).
4. The max|z|=48.7 per-bit flip-bias (bit-53 weight-1 delta) is a real weak
   structural signal — materially higher than dd14_ax1's 11.0. Below the
   repeats kill gate, and S1's DIFF family (10 keys, truncated chi2) is clean,
   so no gate fires. Worth keeping in mind if S3/S4 or later rounds show
   anything on high-bit weight-1 deltas.

## Bottom line
All three gates VERIFIED with artifact-backed numbers: S0 20.3u reproduced on
the pinned flow, S1 CAL_PASS, S2 PASS (max_repeats=0). fz24_o is a genuine
S1+S2-clean frontier challenger at 20.3u — 0.2u over al_and6a (20.1u) — pending
S3/S4. First 5-stage non-AND-final construction to survive the DIFF wall
family in this program's history.

All raw artifacts: this directory (s0_result.txt, s0/_dut/, s1/, s2/, xcheck/,
ref_fz24_o.py, equiv_check.py).
