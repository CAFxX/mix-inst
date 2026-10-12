# W4T checkpoint (track-3 supervisor)

## Design
- [DESIGN.md](DESIGN.md) — 4-term rotl-xor linear, cost thesis ~30u (borderline),
  quality thesis 8x denser diffusion than 2-term (addresses O127 DIFF kill).

## Screen
- Script: [screen_w4t.py](screen_w4t.py) (N=300, seed 0x6E34)
- Log: `screen.log` — terminal line is `DONE keeps=N`
- JSONL: `w4t_screen.jsonl` — one row per candidate, resumable
- Liveness: `adder_lat/supervisor_heartbeat.txt` gets `w4t-screen:` lines
  every 25 candidates; process tag `track3/w4t-screen`

## Gates (in order)
1. Canary gate (`check_canaries()`) — abort if FAIL
2. Fisher calibration (al_w3p_a -> KEEP) — abort if FAIL
3. Per candidate: affinity -> rank>=62 -> Fisher triage (KEEP iff LIN+DIFF PASS)

## Pre-registered escalation
- keeps >= 1 -> bundle bit-exact -> S0 (bar <30u strict)
- <30u: full battery + Q1
- 30-35u: COST-MARGINAL, record, do not escalate
- >35u or 0 keeps: arm closed per the gate that fired
- If DIFF-killed like 2-term: next arm is middle-GF + 4-term

## Resume
The script regenerates the candidate stream from seed and skips `done`
rows in the JSONL. To resume: re-run the same launch command.

## Verdicts
- O-numbers go in `../../VERDICT_SCOPE.md`
- Ledger updates in `../../LEADS_LEDGER.md`
