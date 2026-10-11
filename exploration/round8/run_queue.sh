#!/bin/bash
# Round 8 battery queue runner. Usage: run_queue.sh <tag> <cand1> <cand2> ...
# Runs run_fast_battery.sh sequentially over the candidates, appending a
# one-line summary per candidate to round8/progress_<tag>.log
set -u
EXP=/home/hatch/workspace/mix/exploration
TAG="$1"; shift
PROG="$EXP/round8/progress_${TAG}.log"
: > "$PROG"
for CAND in "$@"; do
  t0=$(date +%s)
  echo "=== [$TAG] $CAND started $(date -u +%FT%TZ)" | tee -a "$PROG"
  bash "$EXP/fast_battery/run_fast_battery.sh" "$CAND" > "$EXP/round8/battery_${CAND}.log" 2>&1
  rc=$?
  dt=$(( $(date +%s) - t0 ))
  s0=$(python3 -c "import json;print(json.load(open('$EXP/fast_battery/results/$CAND/s0_result.json'))['delay_u'])" 2>/dev/null || s0="?")
  echo "=== [$TAG] $CAND rc=$rc wall=${dt}s s0_delay=${s0}u" | tee -a "$PROG"
done
echo "=== [$TAG] QUEUE DONE" | tee -a "$PROG"
