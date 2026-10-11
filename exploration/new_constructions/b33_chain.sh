#!/bin/bash
# Track-6 batch-33: full battery S0->S4 for 7 proxy-KEPT 6-stage AND schedules.
FB=/home/hatch/workspace/mix/exploration/fast_battery
LOG=$FB/results/b33_chain.log
: > "$LOG"
for c in t6_b33a t6_b33b t6_b33c t6_b33d t6_b33e t6_b33f t6_b33g; do
  echo "=== CHAIN $c $(date -u +%FT%TZ) ===" | tee -a "$LOG"
  "$FB/run_fast_battery.sh" "$c" 0 >> "$LOG" 2>&1
  echo "=== $c rc=$? $(date -u +%FT%TZ) ===" | tee -a "$LOG"
done
echo "=== B33 CHAIN DONE $(date -u +%FT%TZ) ===" | tee -a "$LOG"
