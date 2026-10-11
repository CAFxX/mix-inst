#!/bin/bash
# Round 11 battery queue: run_fast_battery.sh for each S0 survivor, 2 parallel, detached.
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
# survivors filled in after S0
CANDS="$CANDS_R11"
run_one() {
  c=$1
  bash $FB/run_fast_battery.sh $c > $EXP/round11/battery_$c.log 2>&1
  echo "BATTERY_DONE $c rc=$? $(grep -E 'BATTERY-(PASS|FAIL)' $EXP/round11/battery_$c.log | tail -1)" >> $EXP/round11/battery_progress.log
}
: > $EXP/round11/battery_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_BATTERY_DONE" >> $EXP/round11/battery_progress.log
