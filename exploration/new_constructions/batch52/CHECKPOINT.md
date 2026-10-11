# Batch-52 checkpoint (track-6 supervisor incarnation XXII)

## 2026-10-11 ~20:00 CEST — co-design complete, pre-pilot launched

- **Batch-51 adjudication VERIFIED from raw artifacts** (not trusted from
  the 19:45 ledger entry): `batch51/prepilot.log` has 12 try-lines,
  CALIBRATION exit=0, CALIB-1 and1/b33c z=3.3 EXACT, CALIB-2 MU5-324
  z=3.24 KEEP, no keeps file (0 keeps confirmed), muxS4 0/6 minz=3823.6
  (seed 0xb511), muxS3 0/6 minz=54054.4 (seed 0xb512), both arms exit=0,
  "PRE-PILOT COMPLETE" 2026-10-11T17:40:48Z. Adjudication STANDS.
  Nuances vs the ledger summary: (a) DESIGN.md's Falsifier line says
  "0/40" but the pre-registered PRE-PILOT verdict rules (the operative
  rules for the 6/arm pre-pilot) trigger KILL at "0 keeps both arms
  with min z >= 1e3" — triggered cleanly; no pilot/S0 per rules.
  (b) muxS3's killkeys are mixed (not 0x0-dominated) — the wall is
  key-independent, which strengthens the kill.
- **VERDICT_SCOPE.md updated**: O88 (batch-50 QLOW: quality-confirmed,
  cost-closed 24.6/25.7u; QLOW = AND-minimal floor), O89 (batch-51
  MUX-4st/3st: mechanism (b) CONFIRMED, VALID kill); O87's re-test
  trigger fixed (quadratic mining now COMPLETE — trigger retired).
- **Closed-axis audit (b37–b51)**: wall map — <=4st every sparse
  mechanism dead, dense-4st quality-alive but cost-doomed (22.9–28u);
  5st sparse-AND dead, MUX-5st IS the 19.3u frontier; 3st dead x4
  mechanisms.
- **Cubic-mining fallback: CUT ON STRUCTURAL COST ARGUMENT** (DESIGN.md
  cut #1): cubic => >=2 AND levels (definitional) vs QLOW's 1 level at
  ~5u proper; 3st budget needs proper <~5.1u < QLOW's ~5u — the miner's
  target set is empty by structure. Re-test trigger: a MEASURED
  sub-5.1u-proper cubic S-box. No fabricated queue.
- **Batch-52 axis: MUX-5st linear-term ablation (muxS5nl)** — the ONLY
  open frontier attack with a measured cost thesis. Mechanism question:
  is the linear d load-bearing for MUX-5st quality? First-principles
  asymmetry: MUX fires exactly 1 bit on single-bit input WITHOUT d
  (no-zero-corner survives); AND degrades to identity without rc.
  Prize arm muxS5nl (5x no-d) + control arm muxS5d (5x full form,
  fresh draws). De-dup grep-verified: never screened.
- **Pre-pilot LAUNCHED** 2026-10-11T18:00:07Z: `run_b52_prepilot.sh`
  under `setsid agentwork-launch.sh --nice 19 --tag track6/b52-prepilot`
  (PID 99767 alive); backoff-gated (poll 1, waiting — 3 frozen procs,
  shedder active; deadline 12h). Harness unit-verified (no-zero-corner
  firing bit-exact, draws distinct/deterministic).
- **Heartbeat**: `batch52/heartbeat.txt` touched at launch; re-touch
  every 30 min while live.
- **Next**: adjudicate pre-pilot per DESIGN.md's pre-registered rules
  when "PRE-PILOT COMPLETE" lands in `batch52/prepilot.log`.
