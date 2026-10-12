#!/bin/bash
# Batch-62 pre-pilot RESUME: original launcher died after try 3 (no procs).
# Runs tries 4-11 (seed 0xB621, RNG advanced past completed tries), then
# chains the 80-draw pilot. Cleared-flag backoff pattern.
cd ~/workspace/mix/exploration/new_constructions/batch62 || exit 1
cleared=0
for i in $(seq 1 144); do
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1)
  echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> backoff_poll_prepilot.out
  if ! echo "$out" | grep -qi "back off\|BACKOFF"; then cleared=1; break; fi
  sleep 300
done
if [ "$cleared" = "0" ]; then echo "BACKOFF-FAIL: load never cleared in 12h" | tee -a prepilot.log; exit 1; fi
echo "[$(date -u +%FT%TZ)] batch-62 pre-pilot RESUME: tries 4-11 (seed 0xB621)" | tee -a prepilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-prepilot resume alive" > heartbeat.txt
nice -n 19 python3 resume_prepilot.py >> prepilot.log 2>&1
rc=$?
echo "[$(date -u +%FT%TZ)] PRE-PILOT COMPLETE rc=$rc" | tee -a prepilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-prepilot done rc=$rc" > heartbeat.txt
[ "$rc" = "0" ] || exit $rc
# Chain the pilot (it re-gates on backoff and checks PRE-PILOT COMPLETE).
exec bash run_b62_pilot.sh
