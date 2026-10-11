# Batch-49 checkpoint — incarnation XVIII

## 2026-10-11 14:55 CEST
- Spawned; XVII adjudication + b48/DESIGN.md + VERDICT_SCOPE.md read.
- De-dup complete (batches 19–48): no bijective-quadratic 4-bit S-box
  repeated-stage screen anywhere. LP-optimal 16 classes verified in code
  (`verify_lp.py`): all have DU=4/LATbias=4 but NO class is purely quadratic
  (component degrees {2,3} or {3}) — the "optimal" classes are not the
  quadratic classes. Triangular quadratic construction CUT ON MEASUREMENT
  (1024 cores, all DU=16; proof: x0 enters linearly).
- `mine_q4.py` (random quadratic ANF): 0/200000 bijective — too rare, cut.
- `anneal_q4.py` (simulated annealing, 8 starts × 60000 steps) RUNNING in
  background (session proc_e08891a299b4) for best bijective quadratic
  (DU, LATbias) profile.
- `t6_b49_screen.py` written (Q4 LUT placeholder + fail-loud asserts).
- Backoff at 14:48: load 14.32 ≥ 12 → heavy work (pre-pilot) queued until
  backoff clears. Light work (mining, scripts) proceeds under nice-10.
- Next: annealing verdict → fill Q4 LUT → DESIGN.md → calibration +
  pre-pilot (~6 draws × q4bS4/q4bS3) on exact triage path → adjudicate.

## 2026-10-11 15:02 CEST — TIMEOUT RESOLVE
- Parent cron hit execution timeout; stopping per resolve-phase guidance.
- Mining (anneal_q4_fast.py, 12 starts x 25000 steps, nice-19, tag
  track6/b49-mine) LEFT RUNNING detached; log mine_q4_fast.log. Start 0
  done: coll=0 DU=16 LATbias=8 compdeg=[1,2] S0=9 -- POOR (DU=16 basin);
  successor: if all 12 starts land DU>=8, rethink construction family.
- Pre-pilot NOT launched (blocked on Q4 LUT from mining). Screen script
  ready at t6_b49_screen.py (LUT placeholder + fail-loud asserts).
- No ledger/VERDICT_SCOPE edits made; no GHA/pushes; no external effects.
- Resume: collect mining -> fill LUT -> DESIGN.md -> calibrate + pre-pilot
  -> adjudicate -> ledger prepend -> next lead. Heartbeat due ~15:30.

## 2026-10-11 15:15 CEST — MINING DIED, RELAUNCHED (status run)
- The b49 mining (anneal_q4_fast.py, 12 starts) DIED SILENTLY ~13:04 UTC
  after 3 starts (log mtime 13:04, no process, no traceback) — 2 min after
  XVIII stopped per the cron-timeout resolve. Root cause: session teardown
  (same class as the batch-43 pilot incident — the mining was "LEFT RUNNING
  detached" but NOT under setsid, so the timeout cleanup SIGTERM'd it).
- FIXED by this run: partial log preserved -> mine_q4_fast.log.dead1;
  relaunched DETERMINISTICALLY (same script, same 12 starts, seeds
  0xB492+k — start 0/1/2 lines will be byte-identical) via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b49-mine-resume`,
  immune to session teardown. Expected ~35 min for 12 starts.
- Track-6 has NO live supervisor incarnation (XVIII stopped). The next
  30-min report run collects the mining BEST_LUT and spawns incarnation
  XIX for: fill Q4 LUT -> DESIGN.md -> calibrate + pre-pilot -> adjudicate
  -> ledger prepend. (Not spawned now: the pre-pilot is gated on mining
  completion ~15:50; spawning now would just wait.)

## 2026-10-11 17:28 CEST — TERMINAL ADJUDICATION (incarnation XIX): BATCH-49 CLOSED, COST-DOOMED
- S0 spot-check on t6_q4S4a (min-z keep, z=2.61): crit=29.0 → **28.0u vs 19.3u bar — FAILS decisively** (7.0u/stage vs <4.83u/stage budget; XCHECK clean, ref mul64 103.5; log s0_t6_q4S4a.log). Per-stage cost is schedule-independent → no rotation schedule can close the 2.2u/stage gap → pilot FOREGONE per the pre-registered rule (b48 precedent).
- VERDICT: **batch-49 axis CLOSED — VALID scoped kill (quality-alive, cost-doomed).** q4bS4 triage 4/6 KEEP (mechanism alive) but S0 kills it on cost; q4bS3 triage-killed 0/6 (min z=18273.5, b48-class). Scope: 4st/3st repeated-Q4 replacement cascade (2-rot tree, pre-whiten, rotl(k,13)) + class claim "mined-DU-optimal bijective-quadratic 4-bit S-box repeated stage". NOT a claim about cost-optimized quadratic S-boxes (deferred lead).
- Ledger prepended (17:28 entry, most-recent-first): batch-49 → resolved terminal; new deferred lead added (cost-driven quadratic-S-box mining); track-6 active leads = 0. Frontier unchanged: hyb28_mu5_324 19.3u.
- Evidence retained in batch49/: DESIGN.md (9 cuts + launch log), prepilot.log, prepilot_calibrate.log, prepilot_keeps.jsonl, s0_t6_q4S4a.log, run_s0spot_b49.log, gen_b49_bundle.py, bundle fast_battery/candidates/t6_q4S4a/ (rtl.v, model.py, impl.c, meta.json, bit-exact 2000/2000, screener 500/500).
- VERDICT_SCOPE.md: batch-49 kill entry to be appended by this run (below).
- Next lead for track-6: none owned — the 30m reporter / coordinator picks the next axis per the widen directive. XIX stands down (heartbeat final touch 15:28:25Z).

## 2026-10-11 17:31 CEST — PRE-PILOT ADJUDICATED (incarnation XIX)
- PRE-PILOT COMPLETE 15:18:14Z (~5 min after backoff cleared; total 12 draws).
  Calibration: and1/b33c z=3.3 EXACT — harness healthy, non-vacuous.
- **q4bS4 (prize, 4-stage): 4/6 KEEP, min z=2.6** — draws 3.4/3.1/30.2(kill)/3.2/11.3(kill)/2.6.
  The mechanism is ALIVE: 4-stage repeated Q4 cascade reaches triage quality
  comparable to the b33c calibration point. Pre-registered escalation fires:
  bundle gen → synthesis spot-check → PILOT.
- **q4bS3 (wall probe): 0/6 KEEP, min z=18273.5** — all kills z=18k–183k,
  killkey-0x0 dominance on 2/6 (the b48-class kill signature ≥1e4).
  KILL LOUDLY, scoped: 3-stage Q4 repeated cascade is DEAD (mechanism
  prediction confirmed: weaker diffusion at 3st fails; b47's 3st-dense-dead
  precedent). No pilot for q4bS3. Verdict scoped to (3-stage Q4 replacement
  cascade, 2-rot tree, pre-whiten, rotl(k,13)).
- Keeps → prepilot_keeps.jsonl (4 entries, z=2.61/3.07/3.18/3.38).
  Bundle gen (gen_b49_bundle.py, new): Q4 ANF derived and verified bit-exact
  vs the mined LUT on all 16 inputs; t6_q4S4a = min-z keep (z=2.61,
  stages [(Q4,21,37),(Q4,55,60),(Q4,12,19),(Q4,41,15)]): bit-exact C-vs-Python
  2000/2000 OK, screener-vs-bundle (ANF vs LUT) 500/500 OK. Bundle at
  fast_battery/candidates/t6_q4S4a/.
- SYNTHESIS SPOT-CHECK LAUNCHED: run_b49_s0spot.sh via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b49-s0spot`
  (backoff-poll ≤12h → run_synth.py on t6_q4S4a/rtl.v; bar <4.83u/stage).
  On pass → PILOT (2×40 draws, seeds 0xB493/0xB494) → S0 stratified on
  pilot keeps → S1 fail-fast. On fail → cost-doomed: retained as evidence,
  axis closed.
- PENDING: S0 spot-check result → pilot launch → adjudication → LEADS_LEDGER
  prepend. Watchers in place.

## 2026-10-11 17:12 CEST — INCARNATION XIX ACTIVE: LUT filled, DESIGN.md written, pre-pilot launched (awaiting adjudication)
- Mining verdict (12/12 checkpointed starts): BEST energy=9.0 coll=0 DU=8 LATbias=8 compdeg=[1,2], seed 0xB492. LUT verified independently (bijective, S(0)=3, DU=8 exact, max|LAT|=16 at (a,b)=(5,2) = LATbias 8 in miner units — miner scale is |agree-8|, my early "16" was the 2x scale; no miner bug). DU=4 unreachable in pure-quadratic family per 12-start evidence (6x DU=8 / 6x DU=16).
- LUT filled into t6_b49_screen.py (fail-loud asserts bijective/no-zero-corner PASS at import). batch49/DESIGN.md WRITTEN (pre-registered: calibration b33c z=3.3 fail-loud, ~6 draws/arm seeds 0xB491/0xB492, bar max|z|<10, escalation: any KEEP → bundle gen 2000/2000 → S0 stratified <19.3u → S1 fail-fast → staged battery; cuts #1-9 recorded). De-dup vs batches 19–48 + fz24_g/h confirmed: g/h are chi_4 (non-bijective, never-run, bijectivity caveat in b45 DESIGN.md:82-96) — Q4 is a different primitive.
- PRE-PILOT LAUNCHED: run_b49_prepilot.sh via `setsid agentwork-launch.sh --nice 19 --tag track6/b49-prepilot` (own session SID, teardown-safe; wrapper polls backoff ≤12h → calibrate → q4bS4 6 draws → q4bS3 6 draws → keeps to prepilot_keeps.jsonl). At launch load=12.47 → waiting on backoff (self-match pgrep lesson: verify process identity, not just pgrep hits). Heartbeat touched 15:07:48Z.
- PENDING: pre-pilot completion → adjudicate per DESIGN.md verdict rules → CHECKPOINT + LEADS_LEDGER prepend → memory log. A log-watcher (proc session) waits for "PRE-PILOT COMPLETE" and reports automatically.

## 2026-10-11 15:56 CEST (mix-search-status-30m): mining DIED A SECOND TIME — RELAUNCHED WITH CHECKPOINTING
- The 15:20 relaunch (setsid, tag track6/b49-mine-resume) DIED SILENTLY ~13:42 UTC after start 10 (11/12 starts; log -> mine_q4_fast.log.dead2). No process, no traceback, no OOM in dmesg, not frozen — second silent death of this miner (first was 13:04 session-teardown). Root cause still unknown; VM reboot was 13:09, before the run.
- ROOT-CAUSE-CLASS FIX (not just relaunch): anneal_q4_fast.py now checkpoints EVERY completed start to mine_q4_fast.starts.jsonl immediately (load_ckpt/save_ckpt) and skips checkpointed starts on resume — same seeds (0xB492+k), deterministic, identical aggregate. A third silent death can no longer lose completed starts. Round-trip smoke-tested + py_compile clean.
- Relaunch: new backoff-gated wrapper run_b49_mine.sh (polls load-shed.sh backoff, then execs `python3 anneal_q4_fast.py 12`), via `setsid agentwork-launch.sh --nice 19 --tag track6/b49-mine-resume2`, log mine_q4_fast.log. At launch load=26 → wrapper correctly waiting on backoff (starts when clear). NOTE: the 11 completed starts from the dead run are LOST (no per-start persistence existed then) — this relaunch redoes all 12 deterministically (~25-30 min once backoff clears).
- Track-6 still has NO live supervisor (XVIII stopped). Next report run: collect BEST_LUT from the mining log and spawn incarnation XIX (fill Q4 LUT -> DESIGN.md -> calibrate + pre-pilot -> adjudicate -> ledger prepend).
