#!/bin/bash
# Batch-62 pilot RESUME: tries 21..79 after VM reboot (seed 0xB622).
# Cleared-flag backoff pattern (same as run_b62_pilot.sh).
cd ~/workspace/mix/exploration/new_constructions/batch62 || exit 1
cleared=0
for i in $(seq 1 144); do
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1)
  echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> backoff_poll_pilot_resume.out
  if ! echo "$out" | grep -qi "back off\|BACKOFF"; then cleared=1; break; fi
  sleep 300
done
if [ "$cleared" = "0" ]; then echo "BACKOFF-FAIL: load never cleared in 12h"; exit 1; fi
echo "[$(date -u +%FT%TZ)] backoff CLEAR -- resuming batch-62 pilot (tries 21-79)" | tee -a pilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-pilot-resume alive" > heartbeat.txt
nice -n 19 python3 resume_pilot.py >> pilot.log 2>&1
rc=$?
echo "[$(date -u +%FT%TZ)] PILOT RESUME COMPLETE rc=$rc" | tee -a pilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-pilot-resume done rc=$rc" > heartbeat.txt
exit $rc
