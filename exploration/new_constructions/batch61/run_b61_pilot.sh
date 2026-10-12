#!/bin/bash
# Batch-61 pilot: 80 draws, seed 0xB612. Cleared-flag backoff pattern.
cd ~/workspace/mix/exploration/new_constructions/batch61 || exit 1
cleared=0
for i in $(seq 1 144); do
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1)
  echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> backoff_poll_pilot.out
  if ! echo "$out" | grep -qi "back off\|BACKOFF"; then cleared=1; break; fi
  sleep 300
done
if [ "$cleared" = "0" ]; then echo "BACKOFF-FAIL: load never cleared in 12h"; exit 1; fi
echo "[$(date -u +%FT%TZ)] backoff CLEAR -- starting batch-61 pilot" | tee -a pilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b61-pilot alive" > heartbeat.txt
nice -n 19 python3 t6_b61_screen.py muxD5flocal2 80 0xB612 pilot_keeps.jsonl >> pilot.log 2>&1
rc=$?
echo "[$(date -u +%FT%TZ)] PILOT COMPLETE rc=$rc" | tee -a pilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b61-pilot done rc=$rc" > heartbeat.txt
exit $rc
