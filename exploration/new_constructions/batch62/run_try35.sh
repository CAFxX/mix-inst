#!/bin/bash
# Backoff-gated single-draw re-run of try 35 (cleared-flag pattern, AGENTS.md).
cleared=0
for i in $(seq 1 144); do
  out=$(~/workspace/system/bin/load-shed.sh backoff 2>&1); rc=$?
  echo "[$(date -u +%FT%TZ)] backoff poll $i: $out" >> try35_backoff.log
  if [ $rc -eq 0 ]; then cleared=1; break; fi
  sleep 300
done
if [ $cleared -eq 0 ]; then echo "BACKOFF-FAIL: load never cleared in 12h" >> try35_backoff.log; exit 3; fi
setsid nice -n 19 python3 rerun_try35.py >> try35_rerun.log 2>&1 < /dev/null
