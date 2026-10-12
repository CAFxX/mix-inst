# (b2) sparse-GF screen — checkpoint / resume instructions

## What
(b2) sparse-GF: d-constrained 3-stage word-AND, cheap rotl-xor linear between
stages ((p,q) drawn per candidate, rank-gated >=62), ONE GF(2^64) mult
(0x94D049BB133111EB) at END, pre-whiten + rotl(k,13).
N=300 candidates (seed 0xB200), Fisher triage (S1 gate's own rule) + rank>=62 probe.

## Files
- `adder_lat/b2sparse/screen_b2sparse.py` — the screen
- `adder_lat/b2sparse/b2sparse_screen.jsonl` — checkpoint (one JSONL row per
  completed candidate; resume by regenerating the seeded stream and skipping
  `done` rows)
- `adder_lat/b2sparse/DESIGN.md` — co-design with pre-registered escalation
- `adder_lat/b2sparse/run_b2sparse_screen.sh` — backoff-gated launcher
- `adder_lat/w3prime2/` — the closed cheap-linear arm (O127)
- `adder_lat/w3prime/COST_AUTOPSY.md` — why W3' is 48u; arm (a) rejected

## Launch
```bash
setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 \
  --tag track3/b2sparse-screen -- adder_lat/b2sparse/run_b2sparse_screen.sh \
  >> adder_lat/b2sparse/screen.log 2>&1 < /dev/null &
```
(Only when `~/workspace/system/bin/load-shed.sh backoff` exits 0 — the
launcher re-polls with the cleared-flag pattern; do NOT force a start.)

## Resume
The screen is resumable: it counts rows in `b2sparse_screen.jsonl` and skips
that many candidates from the seeded stream. Just re-run the launcher.

## Liveness signals (for status checks — do NOT judge by subagent.list)
- Heartbeat: `adder_lat/supervisor_heartbeat.txt` (touched every 25 candidates, tag b2sparse)
- Work-registry: `~/workspace/system/work-registry/track3-b2sparse.json`
- Process: `pgrep -f screen_b2sparse`
- Progress: `wc -l adder_lat/b2sparse/b2sparse_screen.jsonl` (target 300)

## When "DONE keeps=N" lands
Apply DESIGN.md pre-registered escalation: >=1 KEEP → bundle top keep →
S0 (bar <30u) → staged battery S1→S2→S3→S4→Q1. 0/300 → close with kill
signature (O-form entry), record next re-test trigger.

## Escalation paths (bundle/S0/battery) — same as w3prime lane
- Bundle: fast_battery/candidates/b2_<name>/ via an adapted gen script
  (bit-exact C-vs-Python 2000 vec × 3 keys + screener-vs-bundle 500/500)
- S0: authorized run_synth.py path (see adder_lat/w3prime/s0/)
- Battery: run_fast_battery.sh staged (see adder_lat/w3prime/battery/)
