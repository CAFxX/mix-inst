#!/bin/bash
# Batch-57 pilot: 80 MUXD draws under the gate-matched fisher bar.
# Adjudicate on "PILOT COMPLETE" in batch57/pilot.log per DESIGN.md.
# Cleared-flag backoff pattern (AGENTS.md lesson).
cd /home/hatch/workspace/mix/exploration/new_constructions/batch57 || exit 1
LOG=pilot.log
deadline=$(( $(date +%s) + 24*3600 ))
echo "$(date -u +%FT%TZ) pilot wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > backoff_poll_pilot.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 24h" >> "$LOG"; exit 4
fi
rm -f pilot_keeps.jsonl
echo "$(date -u +%FT%TZ) pilot: 80 draws seed 0xB572" >> "$LOG"
python3 t6_b57_screen.py muxD5f 80 0xB572 pilot_keeps.jsonl >> "$LOG" 2>&1
echo "muxD5f pilot exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) PILOT COMPLETE" >> "$LOG"
