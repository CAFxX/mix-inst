#!/bin/bash
# Round 13: Q1 SAC/BIC + full S2->S4 battery for one frontier-relevant candidate.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CAND="${1:?usage: run_q1_battery.sh <candidate> [start_stage]}"
START="${2:-2}"
echo "=== Q1 [$CAND] $(date -u +%FT%TZ)"
python3 $EXP/round13/q1_sacbic.py $CAND $EXP/round13/q1 || { echo "Q1_FAIL $CAND"; exit 2; }
echo "=== battery S$START-S4 [$CAND] $(date -u +%FT%TZ)"
bash $FB/run_fast_battery.sh $CAND $START > $EXP/round13/battery_$CAND.log 2>&1
rc=$?
echo "BATTERY_DONE $CAND rc=$rc"
exit $rc
