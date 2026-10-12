#!/bin/bash
# Batch-62 pilot: 80 draws, seed 0xB622. Cleared-flag backoff pattern.
# Prereq: pre-pilot draws complete (prepilot.log shows PRE-PILOT COMPLETE).
cd ~/workspace/mix/exploration/new_constructions/batch62 || exit 1
cleared=0
for i in $(seq 1 144); do
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1)
  echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> backoff_poll_pilot.out
  if ! echo "$out" | grep -qi "back off\|BACKOFF"; then cleared=1; break; fi
  sleep 300
done
if [ "$cleared" = "0" ]; then echo "BACKOFF-FAIL: load never cleared in 12h"; exit 1; fi
if ! grep -q "PRE-PILOT COMPLETE" prepilot.log 2>/dev/null; then
  echo "PILOT-ABORT: pre-pilot not complete" | tee -a pilot.log
  exit 2
fi
echo "[$(date -u +%FT%TZ)] backoff CLEAR -- starting batch-62 pilot" | tee -a pilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-pilot alive" > heartbeat.txt
nice -n 19 python3 t6_b62_screen.py muxD5fweakgated 80 0xB622 pilot_keeps.jsonl >> pilot.log 2>&1
rc=$?
echo "[$(date -u +%FT%TZ)] PILOT COMPLETE rc=$rc" | tee -a pilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-pilot done rc=$rc" > heartbeat.txt
exit $rc
