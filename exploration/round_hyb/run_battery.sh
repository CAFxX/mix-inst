#!/bin/bash
# Hybridization round: full battery (S3/S4) for one frontier-relevant candidate.
# Checks the system-wide heavy-pipeline gate first, then runs detached.
# Usage: run_battery.sh <candidate>
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CAND="${1:?usage: run_battery.sh <candidate>}"
while [ $(ps aux | grep -E "run_synth|run_fast_battery|yosys|RNG_test" | grep -v grep | wc -l) -ge 2 ]; do
  sleep 300
done
echo "BATTERY_START $CAND $(date -u +%FT%TZ)" >> $EXP/round_hyb/battery_progress.log
bash $EXP/fast_battery/run_fast_battery.sh $CAND 2 > $EXP/round_hyb/battery_$CAND.log 2>&1
rc=$?
echo "BATTERY_DONE $CAND rc=$rc $(date -u +%FT%TZ)" >> $EXP/round_hyb/battery_progress.log
