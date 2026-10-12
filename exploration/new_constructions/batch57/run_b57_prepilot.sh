#!/bin/bash
# Batch-57 pre-pilot: backoff-gated calibration + 12 MUXD draws (fisher bar).
# HARNESS CHECK ONLY -- the pilot (80 draws) runs regardless; 12 draws
# cannot falsify under the strict bar.
# Cleared-flag backoff pattern (AGENTS.md lesson; the double-gate killed
# the b50 pre-pilot and b53 pilot wrappers spuriously -- never re-add a
# post-loop re-check).
cd /home/hatch/workspace/mix/exploration/new_constructions/batch57 || exit 1
LOG=prepilot.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > backoff_poll.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter, now=$(date +%s)): $(head -c 200 backoff_poll.out)" >> "$LOG"
  sleep 300
done
# No second backoff re-check after the loop: the cleared flag is the
# single source of truth (b50/b53 double-gate deaths). The 12h deadline
# still fails loudly via the cleared==0 branch below.
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running calibration" >> "$LOG"
python3 t6_b57_screen.py calibrate > prepilot_calibrate.log 2>&1
rc=$?
echo "CALIBRATION exit=$rc" >> "$LOG"
cat prepilot_calibrate.log >> "$LOG"
if [ $rc -ne 0 ]; then echo "CALIB-FAIL" >> "$LOG"; exit 5; fi
rm -f prepilot_keeps.jsonl
python3 t6_b57_screen.py muxD5f 12 0xB571 prepilot_keeps.jsonl >> "$LOG" 2>&1
echo "muxD5f pre-pilot exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) PRE-PILOT COMPLETE" >> "$LOG"
exec /home/hatch/workspace/mix/exploration/new_constructions/batch57/run_b57_pilot.sh
