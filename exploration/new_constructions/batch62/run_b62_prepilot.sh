#!/bin/bash
# Batch-62 pre-pilot: 12 draws, seed 0xB621. HARNESS CHECK ONLY.
# Fail-loud prerequisites: calib.log must show CALIBRATION PASS (the
# instrument validation gate); selftest must pass. Then the draws.
# Cleared-flag backoff pattern (AGENTS.md lesson).
cd ~/workspace/mix/exploration/new_constructions/batch62 || exit 1
cleared=0
for i in $(seq 1 144); do
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1)
  echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> backoff_poll_prepilot.out
  if ! echo "$out" | grep -qi "back off\|BACKOFF"; then cleared=1; break; fi
  sleep 300
done
if [ "$cleared" = "0" ]; then echo "BACKOFF-FAIL: load never cleared in 12h"; exit 1; fi
echo "[$(date -u +%FT%TZ)] backoff CLEAR -- batch-62 pre-pilot prereqs" | tee -a prepilot.log
if ! grep -q "CALIBRATION PASS" calib.log 2>/dev/null; then
  echo "PREPILOT-ABORT: calib.log does not show CALIBRATION PASS (instrument not validated)" | tee -a prepilot.log
  exit 2
fi
echo "[$(date -u +%FT%TZ)] calibration PASS confirmed -- running selftest + 12 draws" | tee -a prepilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-prepilot alive" > heartbeat.txt
nice -n 19 python3 t6_b62_screen.py selftest >> prepilot.log 2>&1 || { echo "SELFTEST-FAIL" | tee -a prepilot.log; exit 3; }
nice -n 19 python3 t6_b62_screen.py muxD5fweakgated 12 0xB621 prepilot_keeps.jsonl >> prepilot.log 2>&1
rc=$?
echo "[$(date -u +%FT%TZ)] PRE-PILOT COMPLETE rc=$rc" | tee -a prepilot.log
date '+%Y-%m-%d %H:%M:%S' | xargs -I{} echo "{} b62-prepilot done rc=$rc" > heartbeat.txt
exit $rc
