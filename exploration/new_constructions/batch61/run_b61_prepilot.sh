#!/bin/bash
# Batch-61 pre-pilot: 12 draws, seed 0xB611. Cleared-flag backoff pattern.
cd ~/workspace/mix/exploration/new_constructions/batch61 || exit 1
cleared=0
for i in $(seq 1 144); do
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1)
  echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> backoff_poll_prepilot.out
  if ! echo "$out" | grep -qi "back off\|BACKOFF"; then cleared=1; break; fi
  sleep 300
done
if [ "$cleared" = "0" ]; then echo "BACKOFF-FAIL: load never cleared in 12h"; exit 1; fi
echo "[$(date -u +%FT%TZ)] backoff CLEAR -- starting batch-61 pre-pilot" | tee -a prepilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b61-prepilot alive" > heartbeat.txt
nice -n 19 python3 t6_b61_screen.py muxD5flocal2 12 0xB611 prepilot_keeps.jsonl >> prepilot.log 2>&1
rc=$?
echo "[$(date -u +%FT%TZ)] PRE-PILOT COMPLETE rc=$rc" | tee -a prepilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b61-prepilot done rc=$rc" > heartbeat.txt
exit $rc
