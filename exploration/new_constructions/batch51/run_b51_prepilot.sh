#!/bin/bash
# Batch-51 pre-pilot: backoff-gated calibration + 2x6-draw triage.
# Standing orders: heavy compute waits for load-shed.sh backoff exit 0;
# launched under setsid (agentwork-launch execs -> session teardown would
# SIGTERM the worker otherwise; batch-43/batch-49-mining precedent).
cd /home/hatch/workspace/mix/exploration/new_constructions/batch51 || exit 1
LOG=prepilot.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter, now=$(date +%s))" >> "$LOG"
  sleep 300
done
if ! /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running calibration" >> "$LOG"
python3 t6_b51_screen.py calibrate > prepilot_calibrate.log 2>&1
rc=$?
echo "CALIBRATION exit=$rc" >> "$LOG"
cat prepilot_calibrate.log >> "$LOG"
if [ $rc -ne 0 ]; then echo "CALIB-FAIL" >> "$LOG"; exit 5; fi
rm -f prepilot_keeps.jsonl
python3 t6_b51_screen.py muxS4 6 0xB511 prepilot_keeps.jsonl >> "$LOG" 2>&1
echo "muxS4 exit=$?" >> "$LOG"
python3 t6_b51_screen.py muxS3 6 0xB512 prepilot_keeps.jsonl >> "$LOG" 2>&1
echo "muxS3 exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) PRE-PILOT COMPLETE" >> "$LOG"
