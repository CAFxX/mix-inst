# Marginal-PB Triage-Upgrade Lead (O125) — Evidence & Validation
Date: 2026-10-12 13:06+ CEST. Owner: triage-upgrade lane (dispatched 13:05 CEST).

## Domain enumeration (AGENTS.md audit rule: 188 S1 runs, all classified)

Source: fast_battery/results/*/s1_result.json (188 files).

### Marginal-rejection cases (pb>=1 OR rd>=1): 43/43 FLAG (100%)
| class | examples | pb | rd | outcome |
|---|---|---|---|---|
| batch-60 | t6_b59_14 | 3 | 0 | S1 FLAG |
| batch-60 | t6_b59_17 | 2 | 0 | S1 FLAG |
| batch-60 | t6_b59_9 | 0 | 1 | S1 FLAG |
| batch-61 | t6_b61_24 | 0 | 1 | S1 FLAG |
| w4t | w4t_0, w4t_108, w4t_112 | 1 | 0 | S1 FLAG |
| w4t | w4t_131, w4t_150 | 2 | 0 | S1 FLAG |
| batch-29 | hyb29_mu5_005 | 2 | 0 | S1 FLAG |
| batch-29 | hyb29_mu5_006 | 0 | 1 | S1 FLAG |
| batch-29 | hyb29_mu5_009 | 0 | 1 | S1 FLAG |
| batch-29 | hyb29_mu5_011 | 3 | 0 | S1 FLAG |
| batch-29 | hyb29_mu5_015 | 2 | 1 | S1 FLAG |
| batch-29 | hyb29_mu5_017 | 1 | 0 | S1 FLAG |
| batch-29 | hyb29_mu5_018 | 2 | 0 | S1 FLAG |
| batch-29 | hyb29_mu5_021 | 3 | 0 | S1 FLAG |
| hyb28 | hyb28_mu5_234 | 3 | 0 | S1 FLAG |
| hyb28 | hyb28_mu5_266b | 0 | 1 | S1 FLAG |
| hyb28 | hyb28_mu5_328 | 1 | 0 | S1 FLAG |
| xorh5 | t6_xorh5_0/1/5/7/10/12/14/18 | 1-2 | 0-1 | S1 FLAG |
| b59 | t6_b59_1/7/15/54/61 | 1-3 | 0-1 | S1 FLAG |
| b57 | t6_b57_2 | 2 | 0 | S1 FLAG |
| b33 | t6_b33a | 2 | 1 | S1 FLAG |
| feist | r10_feist5_rot311, r9_feist6_nork, etc. | 1-2 | 0-1 | S1 FLAG |
| as6 | as6_200_15 | 1 | 0 | S1 FLAG |
| rtw | rtw_ab48_fm09 | 0 | 1 | S1 FLAG |

### Clean cases (pb=rd=lin=diff=0): 96 total → 82 CAL_PASS, 14 FLAG
The 14 clean-FLAGs are inner LIN/DIFF kills inside screen_calibrated
(MAJOR-3 s1_kill signal): hyb29_mu5_003/013/014/026, t6_b61_56,
hyb28_mu5_304a/304b/323/326/351/443/471, t6_b55_f0, as6_200_68.
These are NOT marginal kills; the gate does not affect them.

### Six battery-passers (non-vacuity): ALL pb=0, rd=0
t6_b59_47, t6_b59_41, t6_b59_0, hyb28_mu5_324, t6_xorh5_15, hyb29_mu5_008 —
verified from raw s1_result.json (this lane, 2026-10-12 13:10 CEST).

## Gate formulation
**"At triage, run the S1 marginal PB/RD screen (screen_calibrated S1b) on the
Python model; REJECT if Holm-rejected PB cells >= 1 OR RD cells >= 1."**

Threshold justification (each cut defensible):
- rej>=1 (not >=2): the S1 rule itself is Holm@0.01; all 43 historical
  marginal kills had >=1; the six passers had 0. A >=2 threshold would have
  let w4t_0/108/112, hyb29_mu5_006/009/017, t6_b61_24, t6_b59_9 etc. through
  (all S1-doomed). Evidence scope matches: the cut is exactly the S1 rule.
- PB and RD both: kills occur in PB-only (30 cases), RD-only (11 cases), and
  both (2 cases). Excluding either family misses real kills.

## Soundness argument (why triage marginal = S1 marginal)
1. screen_calibrated S1b is DETERMINISTIC (fixed scenario vectors, no RNG).
2. S0a XCHECK (10000/10000 C==Python) guarantees the C bundle matches the
   Python model triage runs on.
3. Therefore triage-marginal verdict == S1-marginal verdict for every
   candidate that reaches S1. No additional false-positive risk vs status quo:
   a candidate rejected at triage would be rejected at S1 anyway.
4. Savings: S0a XCHECK + S0 synth (yosys minutes) + S1 LIN/DIFF (~70s) per
   marginal-doomed keep. Cost: marginal itself (~60-620s) runs once at triage
   instead of once at S1 — net wash on the marginal, pure savings downstream.

## False-positive risk estimate
- Statistical: Holm-Bonferroni FWER <= 0.01 per family per candidate. A good
  candidate has <=1% chance of false marginal rejection — SAME at triage or S1
  (no new risk from moving the test earlier).
- Empirical: 0/6 battery-passers rejected; 0/82 S1 CAL_PASS had rej>=1
  (tautological — CAL_PASS requires rej=0, but confirms the rule is the S1 rule).
- The 14 clean-FLAGs (inner LIN/DIFF) are unaffected by this gate.

## Implementation plan
1. screen_cal.py: extract S1b into `screen_marginal(fn, name, verbose)` (shared).
   Refactor screen_calibrated to call it (no behavior change; selftest still green).
2. t6_b62_screen.py: add G5 marginal gate on keeps (batch-62 active).
3. hyb_b29_screen.py: add marginal gate on keeps (batch-29 active).
4. screen_w4t.py: track-3 TERMINAL — no change (note only).
5. Re-run selftest + calib for each touched screen.
