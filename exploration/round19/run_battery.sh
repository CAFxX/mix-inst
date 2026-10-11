#!/bin/bash
# Round 19: full S2->S4 battery for one frontier-relevant candidate, detached.
# Usage: run_battery.sh <candidate>
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CAND="${1:?usage: run_battery.sh <candidate>}"
bash $EXP/fast_battery/run_fast_battery.sh $CAND 2 > $EXP/round19/battery_$CAND.log 2>&1
rc=$?
echo "BATTERY_DONE $CAND rc=$rc $(date -u +%FT%TZ)" >> $EXP/round19/battery_progress.log
