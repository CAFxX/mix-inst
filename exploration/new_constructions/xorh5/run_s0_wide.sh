#!/bin/bash
# track-6 xorh5 widening: S0 sweep (authorized run_synth.py path) for ranks 4-19.
# Sequential under the global yosys flock (run_synth.py serializes itself).
set -u
XH=/home/hatch/workspace/mix/exploration/new_constructions/xorh5
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
LOG=$XH/s0_wide.log
RES=$XH/s0_wide_results.txt
: > "$LOG"; : > "$RES"
for r in 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19; do
  c=t6_xorh5_$r
  echo "=== S0 $c START $(date -u +%FT%TZ)" >> "$LOG"
  nice -n 10 python3 $EXP/run_synth.py $FB/candidates/$c/rtl.v $c $XH/s0_$c >> "$LOG" 2>&1
  rc=$?
  echo "=== S0 $c rc=$rc END $(date -u +%FT%TZ)" >> "$LOG"
  grep -h "^RESULT name=$c " "$LOG" | tail -1 >> "$RES" || true
  echo "[$(date -u +%FT%TZ)] S0 $c rc=$rc" >> "$XH/heartbeat.txt"
done
echo "=== S0 WIDE SWEEP DONE $(date -u +%FT%TZ)" >> "$LOG"
