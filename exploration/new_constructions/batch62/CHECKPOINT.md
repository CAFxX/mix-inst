# Batch-62 CHECKPOINT — resume instructions

**Axis:** weakness-gated local — m~U{1,2,3} perturbation around
t6_b59_47 (18.6u frontier, the single proven-clean basin center),
triaged by the failing instruments themselves: fisher + inner
DIFF-SEQ/LIN gate (screen_lindiff, the t6_b61_56 killer) + RD-SEQ
reduction gate (the t6_b61_24 cell class) + Low1/64 PractRand
prescreen at 256MB (the t6_b61_38 killer). Strict S0 bar <18.6u.
DESIGN.md (sibling) was written BEFORE any run; it carries the
failure-signature characterization and pre-registered rules.

## Pipeline state

- [ ] Pre-pilot (12 draws, seed 0xB621): calibration (CALIB-1..4c)
      + selftest + draws. Log: `prepilot.log`, keeps: `prepilot_keeps.jsonl`.
- [ ] Pilot (80 draws, seed 0xB622): log `pilot.log`, keeps `pilot_keeps.jsonl`.
- [ ] Bundles: `gen_b62_bundle.py` (b61-adapted); bit-exact 2000/2000
      C-vs-Python + 500/500 screener-vs-bundle per keep.
- [ ] S0: `run_b62_s0.sh` (run_synth.py, strict <18.6u, ref mul64
      103.5u, XCHECK). Log `s0_all.log`.
- [ ] Battery: cost-eligible keeps in z-order, `run_b62_battery.sh`
      (start_stage=1) → S1→S2→S3→S4 → Q1 (sac_z5=0 mandatory).
- [ ] Verdicts: O127+ in VERDICT_SCOPE.md; ledger prepended;
      PARETO/RETAINED/RTL only on a full-pass (S0-S4+Q1 sac_z5=0)
      challenger, adjudicated from raw files.

## Resume

Pre-pilot and pilot are resumable via JSONL checkpoints: re-running
with the same seed reproduces the draw sequence; skip
already-recorded tries by counting lines in the keeps file (all tries
print to stdout — check the log for the last completed try number).
The PractRand prescreen compiles a per-try gen binary into
`build_prescreen/` (idempotent; safe to re-run).

## Runners

- `run_b62_prepilot.sh` / `run_b62_pilot.sh`: cleared-flag backoff
  pattern (see batch61 runners). Launch via
  `setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 --tag track6/b62-<stage> -- ...`
- Heartbeat: touch `heartbeat.txt` every ~20 min while live.
- Never two workers on one candidate: check `pgrep -f track6/b62`
  and heartbeat.txt mtime before relaunching.

## Battery escalation (supervisor, 2026-10-12 13:09 CEST)

- S0 sweep COMPLETE 37/37 ranks (11:05:19Z), per-rank XCHECK clean,
  launcher exited (no fail-loud needed). Results in `s0_all.log`.
- Eligibility adjudicated RAW from s0_all.log vs Frontier S (PARETO.md)
  -- CORRECTS the 13:05 report's list: t6_b62_8 EXCLUDED (dominated by
  t6_b59_47 18.6/6656/21830); t6_b62_26 ADDED (dominates t6_b59_0
  19.1/6358/20580); t6_b62_36 ADDED (dominates t6_b33c 19.8/6133/19817);
  t6_b62_6, t6_b62_21 dominate t6_b33c; t6_b62_10 excluded as
  near-duplicate of the speed point (18.6u tie, -3 cells/+7 area).
- Queue (10, z-order, `queue_b62_size.txt`): t6_b62_22, t6_b62_25,
  t6_b62_33, t6_b62_17, t6_b62_26, t6_b62_9, t6_b62_3, t6_b62_6,
  t6_b62_21, t6_b62_36. All promoted to fast_battery/candidates/.
- Marginal nondominated keeps (5, 11, 12, 13, 14, 19, 24, 28, 30, 35)
  DEFERRED not killed -- escalate if the strong ten all fail.
  Dominated keeps (0, 1, 2, 4, 7, 15, 16, 18, 20, 23, 27, 29, 31, 32, 34)
  get no battery; covered by the batch S0 verdict (O142 reserved).
- Battery launched 13:09 CEST: setsid agentwork-launch.sh --nice 19
  --tag track6/b62-battery -- run_b62_battery.sh <10 keeps>
  (S1->S2->S3->S4 + Q1 on survivors; logs battery_<cand>.log,
  summary run_b62_battery.log). run_b62_battery.sh header comment fixed
  (was stale "S0 STRICTLY <18.6u" wording).
- Next O-number: O142 (claimed at verdict write time).
- workreg track6-batch62 heartbeat'd 11:09:20Z; heartbeat.txt live.

## Battery escalation resumed (supervisor, 2026-10-12 13:39 CEST)

- PREVIOUS SUPERVISOR DIED ~11:39 UTC (runtime vanished, VM/daemon
  instability). Its launcher + checkpoint survived; resumed from disk,
  no work redone. workreg re-heartbeat'd 11:39:57Z; heartbeat.txt live.
- Launcher LIVE, untouched: PIDs 187658/187660, tag
  track6/b62-battery, nice-19, setsid. battery_launch.out adjudicated RAW:
  - t6_b62_22: KILLED S1 (battery.log 11:17:54Z rc=2: verdict FLAG --
    PB rejected SINGLE-BIT key=0x0000000000000000; raw worst perbit
    z=4.55, red z=3.18; LIN/DIFF pass but marginal FLAG).
  - t6_b62_25: S0a PASS (XCHECK 10000/10000); S1 CAL_PASS
    (pb/red/lin/diff rej=0; raw worst perbit z=4.11, red z=3.04);
    S2 PASS (11:35, rc=0, max|z|=257.4 all 115 deltas);
    S3 PractRand 1GB in flight 11:35:56Z (64/128/256MB: no anomalies
    at 11:39Z).
- Queue standing by: 33, 17, 26, 9, 3, 6, 21, 36 (z-order). Deferred:
  5, 11, 12, 13, 14, 19, 24, 28, 30, 35 (escalate only if strong ten
  all fail). Dominated (no battery): 0,1,2,4,7,15,16,18,20,23,27,29,
  31,32,34.

## Battery verdicts (raw-adjudicated 13:4x CEST)

- t6_b62_22: KILLED S1 (11:17:54Z rc=2, FLAG: PB rej SINGLE-BIT
  key=0x0; raw worst perbit z=4.55).
- t6_b62_25: **KILLED S3 PractRand** — adjudicated RAW from
  `fast_battery/results/t6_b62_25/s3_practrand_1GB.log` (1GB block
  COMPLETE): no FAIL, but **six p<1e-3 low-bit results** —
  [Low4/64]FPF/16:all R=+7.5 p=1.5e-6 SUSPICIOUS,
  [Low4/64]FPF/16:(0,14-0) R=+7.7 p=9.6e-7 mildly suspicious,
  [Low1/64]FPF/16:all p=2.5e-4, [Low1/64]BCFN(2+1) p=6.3e-4,
  [Low1/64]BCFN(2+2) p=5.6e-4, full BCFN(2+0) p=2.0e-5 mildly
  suspicious; family-clustered FPF/16+BCFN low-bit signature
  growing with depth (512MB: single unusual p=2.8e-4). Basis:
  DESIGN.md gate-4 pre-registered rule (REJECT [Low1/64] on
  "suspicious" p<1e-3 — THREE [Low1/64] lines <1e-3 at 1GB) +
  O62 precedent (S4 kill at SmallCrush p=8.3e-4<0.001) + O140
  (G4 reject at p=8.1e-4). The mechanical FAIL-grep does not
  catch this; the verdict history is unambiguous. Supervisor
  terminated the S3b-strided run (PID 189915, + orphans) to save
  compute; wrapper logged rc=143 and moved on.
- Launcher now on t6_b62_33 (11:44:03Z). In flight: 33.
- t6_b62_33: S1 **CAL_PASS** (11:49:43Z, rc=0, wall=328s; raw-verified
  s1_result.json: pb/red/lin/diff rej all empty; raw worst perbit
  z=4.75). S2 differential in flight (started 11:49:43Z).

## VM reboot recovery (12:00Z)

- VM REBOOTED ~11:59Z (uptime "up 1 min" at 12:00:18Z) — killed the
  launcher (PID 187660) + 33's diffprof mid-S2 (s2.out ends 11:59,
  no PASS verdict line). Load 6.49 post-reboot, backoff CLEAR, no
  frozen procs. dmesg unreadable (no perms) but timing = reboot.
- Recovery per resume pattern: skipped adjudicated 22/25; relaunched
  remaining queue 12:00:35Z — setsid agentwork-launch.sh --nice 19
  --tag track6/b62-battery -- bash run_b62_battery.sh
  t6_b62_33 t6_b62_17 t6_b62_26 t6_b62_9 t6_b62_3 t6_b62_6 t6_b62_21
  t6_b62_36 (PID 3606; script's internal cleared-flag backoff ran
  CLEAR). 33 re-runs S0a+S1 deterministically (~6 min), then S2.
- workreg re-heartbeat'd post-reboot; heartbeat.txt touched.

## Resume-agent check 12:27Z (no action taken)

- A fresh resume subagent was dispatched (registry said "launcher died
  ~12:02Z, PIDs 11531/11532/11653 all dead"). Disk+ps truth: the
  12:09:43Z relaunch is LIVE — PID 11531 (setsid agentwork-launch,
  tag track6/b62-battery) and PID 11532 (run_b62_battery.sh) both
  running; t6_b62_33 S1 started 12:10:48Z with a live python3 worker.
  NO relaunch was performed. Backoff currently gates dispatch anyway
  (load 16.2 >= 12).
- Takeaway for future recovery runs: verify with `pgrep -f run_b62_battery`
  / ps before trusting a registry note's "dead" claim.

## Battery verdicts 14:13–15:14Z + reboot 15:23Z + relaunches (resume worker 16:35Z)

- 14:13:42Z: t6_b62_33 battery rc=0 (resumed from S2): S0a XCHECK
  10000/10000, S1 CAL_PASS (PB/RD rej=0), S2 max|z|=120.6, S3 1GB
  no FAIL, S3b strided 1GB no FAIL, S4 SmallCrush PASS.
- 14:13:49Z: launcher chained to t6_b62_17. 14:39:16Z: **t6_b62_17
  S1-KILLED (FLAG)** — marginal PB rej=2, RD rej=0, rc=2
  (battery_t6_b62_17.log; O143 marginal gate behaving as designed).
- 14:39:16Z: launcher chained to t6_b62_26. 15:02Z: 26 S1 CAL_PASS
  (PB/RD rej=0) → S2 in flight (started 15:02:03Z).
- ~14:43Z: Q1 launched detached on 33 (tag track6/b62-q1-33).
  15:07Z: **Q1 COMPLETE — t6_b62_33 Q1-KILLED: sac_z5=14** (≠0,
  mandatory gate FAIL; bic_maxcorr=0.00912 clean but moot;
  avalanche_mean=32.01 sane; N=262144, wall 1417.9s).
  Adjudicated 15:14Z in LEADS_LEDGER.md: NO frontier change,
  PARETO/RETAINED/RTL/VERDICT_SCOPE untouched, **no O-number claimed**
  (precedent for Q1 kills: ledger entry only). Evidence archived in
  `verdict_evidence/q1_t6_b62_33_2026-10-12T1507Z.{log,json}`
  (wrapper re-runs will overwrite the live q1 files).
- Killed to date: 22 (S1), 25 (S3 PractRand gate-4), 17 (S1),
  33 (Q1). All ledger-adjudicated, no O-numbers (O142 stays reserved
  for the batch-S0 verdict pending battery outcomes).
- 15:23:32Z: **VM REBOOT** (who -b; boot_id a59af2ed-…; parent
  orchestrator already updated boot-id.last). Killed launcher PID
  38381 + 26's S2 mid-flight.
- 15:58:07Z: predecessor (died 16:28Z, runtime infra vanishing, NOT
  a reboot) relaunched battery PID 48480 with
  33/26/9/3/6/21/36 — 33 REDUNDANT (already Q1-killed 15:07Z,
  adjudicated 15:14Z; predecessor likely missed the ledger entry).
  33 re-ran S0a+S1+S2+S3 all PASS (confirming pre-reboot), S3b
  strided in flight 16:28:07Z.
- 16:28Z: predecessor's background exec vanished; setsid launcher
  survived.
- 16:33:37Z: **launcher replaced by unknown actor** (NOT this resume
  worker): old PID 48480 + its 33 S3b tree killed; NEW launcher
  PID 116521 (parent 116519, setsid agentwork-launch.sh --nice 19,
  tag track6/b62-battery, blessed detach pattern) with CORRECTED
  queue **t6_b62_26 t6_b62_9 t6_b62_3 t6_b62_6 t6_b62_21 t6_b62_36**
  (33 removed). Verified: single launcher, no duplicates, old 33
  procs dead. Currently in cleared-flag backoff-poll (load ~12-14
  gating at 16:35Z); starts 26 when clear.
- 16:35Z: resume worker verified live state, heartbeat'd workreg
  track6-batch62 + heartbeat.txt, archived Q1 evidence. NO new
  launches (backoff GATING — load 14.3 >= 12).
- Remaining queue after 26: 9, 3, 6, 21, 36. Deferred marginal keeps
  (5, 11, 12, 13, 14, 19, 24, 28, 30, 35) escalate only if the
  remaining six all fail (DESIGN.md).

## Battery verdicts 16:32–18:13Z + reboot ~18:14Z + Q1 relaunch (resume worker 18:30Z)

- t6_b62_26: **BATTERY-PASS** (16:42–17:09Z): S0a XCHECK 10000/10000,
  S1 CAL_PASS (PB/RD rej=0), S2 max|z|=127.7 (115 deltas),
  S3 1GB PASS, S3b strided 1GB PASS, S4 SmallCrush PASS. 19.1u
  dominates t6_b59_0 (19.1/6272/20327 vs 19.1/6358/20580) — pending Q1.
- t6_b62_9: **BATTERY-PASS** (17:09–17:29Z): S0a, S1 CAL_PASS,
  S2 max|z|=95.7, S3/S3b PASS, S4 PASS. 19.2u dominates
  hyb29_mu5_008 — pending Q1.
- t6_b62_3: **BATTERY-PASS** (17:30–18:03Z): S0a, S1 CAL_PASS
  (PB/RD rej=0), S2 max|z|=108.4, S3/S3b PASS, S4 PASS. 19.6u
  dominates t6_xorh5_15 — pending Q1.
- t6_b62_6: **S1-KILLED (FLAG)** 18:06:29Z — raw: PB rej=2
  (SINGLE-BIT 0xaa/0x55), RD rej=1 (PTR-j8 0xffff...); O143 marginal
  gate as designed.
- t6_b62_21: **S1-KILLED (FLAG)** 18:09:30Z — raw: PB rej=2
  (SINGLE-BIT 0xaa/0x55), RD rej=0; marginal gate.
- t6_b62_36: **S1-KILLED (FLAG)** 18:13:09Z — raw: PB rej=0,
  RD rej=1 (PTR-j8 0xf0b52a9e7d8ba2b5); marginal gate.
- Launcher printed "S4 survivors: t6_b62_26 t6_b62_9 t6_b62_3"
  18:13:09Z, then **VM REBOOT ~18:14Z** (uptime "up 11 min" at
  18:25Z) killed it before its Q1 loop started — no Q1 ran.
- All 10 battery candidates now terminal EXCEPT Q1 on 26/9/3.
  Deferred marginal keeps (5,11,12,13,14,19,24,28,30,35) stay
  deferred (three strong challengers pending, not "all fail").
- 18:30Z: resume worker launched Q1-only runner
  `run_b62_q1_resume.sh` (cleared-flag backoff, nice -n 19, skips
  candidates with q1 JSON on disk): setsid agentwork-launch.sh
  --nice 19 --tag track6/b62-q1 -- bash run_b62_q1_resume.sh
  t6_b62_26 t6_b62_9 t6_b62_3 (PIDs 33316/33317; q1_sacbic worker
  on 26 live 18:32Z; ~24 min each, sequential). Heartbeats
  workreg track6-batch62 on completion.
- Next O-number: O142 reserved for batch-S0 verdict; kills above
  ledger-adjudicated, no O-numbers (precedent: 22/25/17/33).
