#!/bin/bash
# Batch-29 escalation: staged battery (S0a XCHECK 10000 -> S1 -> S2 ->
# S3 -> S3b -> S4) for size-eligible keeps in z-order. Stops at first
# kill per candidate (run_fast_battery.sh exit 2). Q1 + frontier
# adjudication handled separately after each BATTERY-PASS.
set -u
B29=/home/hatch/workspace/mix/exploration/hybrid/batch29
FB=/home/hatch/workspace/mix/exploration/fast_battery
cd "$B29"
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"

QUEUE="$1"  # file with candidate names in z-order, one per line
: > escalate.log
while read -r cand; do
  [ -z "$cand" ] && continue
  echo "=== ESCALATE $cand $(date -u +%FT%TZ) ===" | tee -a escalate.log
  # Backoff gate per candidate (cleared-flag pattern).
  cleared=0
  for i in $(seq 1 720); do
    if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
      cleared=1; break
    fi
    sleep 60
  done
  if [ "$cleared" -eq 0 ]; then echo "BACKOFF-FAIL for $cand" | tee -a escalate.log; continue; fi
  nice -n 19 bash "$FB/run_fast_battery.sh" "$cand" 1 > "battery_$cand.log" 2>&1
  rc=$?
  tail -3 "battery_$cand.log" | tee -a escalate.log
  echo "=== $cand battery rc=$rc $(date -u +%FT%TZ) ===" | tee -a escalate.log
  /home/hatch/workspace/system/bin/workreg.py heartbeat --id mix-track5-batch29 >/dev/null 2>&1 || true
done < "$QUEUE"
echo "ESCALATION QUEUE COMPLETE $(date -u +%FT%TZ)" | tee -a escalate.log
