# Batch-57 CHECKPOINT (resumable state)

**Incarnation:** XXXII. **Updated:** 2026-10-12T01:05Z.

## State
- Pre-pilot: COMPLETE 2026-10-12T00:27:30Z — calibration PASS both gates,
  muxD5f 3/12 KEEP in `prepilot_keeps.jsonl`.
- Pilot: COMPLETE 2026-10-12T00:29:18Z — muxD5f **13/80 KEEP**, min z=2.36
  (seed 0xB572), exit=0. 13 entries in `pilot_keeps.jsonl`, z-order (all
  n_reject=0): 2.359, 2.413, 2.554, 2.829, 2.881, 3.222, 3.668, 3.708, (+5 more).
- Escalation rule (DESIGN.md) FIRED. Bit-exact re-verified by XXXII from raw
  (re-ran `gen_b57_bundle.py` for ranks 0-2): C-vs-Python 2000/2000 OK,
  screener-vs-bundle 500/500 OK on t6_b57_0/1/2.
- **t6_b57_0** (rank 0, z=2.36): S0 19.2u cost-eligible (O102) -> staged battery
  -> **KILLED at S3 PractRand KILL@16MB ([Low1/64]Gap-16:A R=+15.5 p=3.3e-12)**;
  S1 PASS, S2 PASS (wall=244s). O103 recorded. Log:
  `battery_t6_b57_0.log` (partially overwritten by XXXII's 00:35Z duplicate-launch
  incident; stage verdicts re-verified raw).
- **t6_b57_1** (rank 1, z=2.41): S0 **19.5u >= 19.3u COST-DOOMED**, XCHECK clean.
  O104 recorded. Log: `s0_t6_b57_1.log`.
- **t6_b57_2** (rank 2, z=2.55): S0 **18.9u STRICTLY <19.3u COST-ELIGIBLE**
  (6198 cells, area 20478), XCHECK clean. O105 recorded.
  Staged battery LIVE since ~01:02Z (`run_b57_battery2.sh`, setsid nice-19
  tag track6/b57-battery2, backoff CLEAR; log `battery_t6_b57_2.log`,
  wrapper log `run_b57_battery2.log`).
- INCIDENT 00:35Z (XXXII): misread transient empty pgrep as battery-dead,
  launched duplicate battery; self-killed duplicate (own PIDs 107032/107072
  only). Lesson: confirm with `ps aux` before declaring a process dead.

## Pending
1. Staged battery S1->S2->S3->S4 on t6_b57_2, then Q1 (sac_z5=0 mandatory).
2. Adjudicate per pre-registered rules:
   - t6_b57_2 Q1-clears at 18.9u -> FRONTIER CHALLENGER: report + PARETO.md
     update + ledger prepend + VERDICT_SCOPE O-entry.
   - dies at any gate -> escalate rank 3 (z=2.83) as `t6_b57_3`:
     `python3 gen_b57_bundle.py pilot_keeps.jsonl 3 t6_b57_3`; S0 via
     `run_b57_s0_3.sh` (sed from run_b57_s0_2.sh); if eligible -> battery3;
     then rank 4 (z=2.88), rank 5 (z=3.22) in z-order. Form verdict only
     after all 13 keeps terminal.
   - all 13 keeps terminal without a Q1-clearing challenger -> form verdict
     on muxD5f + VERDICT_SCOPE O-entry + ledger prepend.
3. Heartbeat: touch `batch57/heartbeat.txt` every ~30 min while live.

## Resume instructions (if this incarnation dies)
1. Check for live battery: `ps aux | grep run_fast_battery` — if a
   `t6_b57_<k>` battery PID is alive and its `battery_t6_b57_<k>.log` is
   growing, DO NOT relaunch; heartbeat and monitor.
2. If battery gone: check its log tail for BATTERY-PASS/BATTERY-FAIL and
   adjudicate per rules above; relaunch only if the stage verdicts are
   inconclusive (log truncated mid-stage).
3. Ledger: prepend entry on each terminal verdict; VERDICT_SCOPE.md O-entry
   scoped to tested configs.

## Frontier
hyb28_mu5_324 at 19.3u (unchanged; t6_b57_2 at 18.9u pending quality gates).
