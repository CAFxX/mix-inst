#!/bin/bash
# Batch-58 PILOT: muxD4f (4-stage pure-MUXD, MU5 frame) with
# fisher-matched triage. 80 draws, seed 0xB582.
# Pre-registered rules (DESIGN.md):
#   - pre-pilot 0/12 -> WEAK-SIGNAL (2026-10-12T02:11Z, minz=3045.9);
#     pilot runs regardless to confirm at 80 draws;
#   - >=1 keep -> bit-exact bundle (gen_b58_bundle.py, output to disk)
#     -> S0 (run_synth.py, strict <19.2u) -> z-order escalation ->
#     staged battery -> Q1;
#   - 0/80 -> FAMILY-KILL verdict (4 MUXD stages insufficient for the
#     fisher bar) -> escalate to deferred muxD5f-local axis;
#   - GATE-FAIL (keeps==n_try, kills==0) -> KILL LOUDLY, diagnose.
# Cleared-flag backoff pattern (AGENTS.md lesson). Launched under setsid.
cd /home/hatch/workspace/mix/exploration/new_constructions/batch58 || exit 1
LOG=pilot.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > backoff_poll_pilot.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter): $(head -c 200 backoff_poll_pilot.out)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: pilot 80 draws seed 0xB582" >> "$LOG"
rm -f pilot_keeps.jsonl
python3 t6_b58_screen.py muxD4f 80 0xB582 pilot_keeps.jsonl >> "$LOG" 2>&1
rc=$?
nkeeps=0
[ -f pilot_keeps.jsonl ] && nkeeps=$(wc -l < pilot_keeps.jsonl)
echo "pilot exit=$rc keeps=$nkeeps" >> "$LOG"
echo "$(date -u +%FT%TZ) PILOT COMPLETE" >> "$LOG"
