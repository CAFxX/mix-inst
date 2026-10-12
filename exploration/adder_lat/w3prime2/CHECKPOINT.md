# W3'' screen — checkpoint / resume instructions

## What
W3'' screen: d-constrained 3-stage word-AND with cheap linear diffusion
(`x ^= rotl(x,p) ^ rotl(x,q)` per stage, replacing GF(2^64) mult).
N=300 candidates, Fisher triage (S1 gate's own rule) + rank≥62 probe.

## Files
- `adder_lat/w3prime2/screen_w3pp.py` — the screen
- `adder_lat/w3prime2/w3pp_screen.jsonl` — checkpoint (one JSONL row per
  completed candidate; resume by regenerating the seeded stream and skipping
  `done` rows)
- `adder_lat/w3prime2/DESIGN.md` — co-design with pre-registered escalation
- `adder_lat/w3prime2/../w3prime/COST_AUTOPSY.md` — why W3' is 48u; arm (a)
  rejected with reasons
- `adder_lat/w3prime2/run_w3pp_screen.sh` — backoff-gated launcher

## Launch
```bash
setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 \
  --tag track3/w3pp-screen -- adder_lat/w3prime2/run_w3pp_screen.sh \
  >> adder_lat/w3prime2/screen.log 2>&1 < /dev/null &
```

## Resume
The screen is resumable: it counts rows in `w3pp_screen.jsonl` and skips that
many candidates from the seeded stream. Just re-run the launcher.

## Liveness signals (for status checks — do NOT judge by subagent.list)
- Heartbeat: `adder_lat/supervisor_heartbeat.txt` (touched every 25 candidates)
- Process: `pgrep -f w3pp_screen`
- Progress: `wc -l adder_lat/w3prime2/w3pp_screen.jsonl` (target 300)

## When "DONE keeps=N" lands
Apply DESIGN.md pre-registered escalation: ≥1 KEEP → bundle top keeps →
S0 (bar <30u) → battery. 0/300 → close cheap-linear variant, (b2) next.
