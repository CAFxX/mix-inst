#!/bin/bash
# Round 20: S3+S4 backfill for the r19 fm candidates (Frontier Q provisional
# points). Their S0/S1/S2/Q1 evidence already exists in round19/.
# Usage: run_fm_backfill.sh <candidate>   (runs S3 PractRand + S4 SmallCrush)
# Max 2 concurrent heavy pipelines.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CAND="${1:?usage: run_fm_backfill.sh <candidate>}"
bash $EXP/fast_battery/run_fast_battery.sh $CAND 3 > $EXP/round20/battery_$CAND.log 2>&1
rc=$?
echo "BATTERY_DONE $CAND rc=$rc $(date -u +%FT%TZ)" >> $EXP/round20/battery_progress.log
echo "BATTERY_DONE $CAND rc=$rc"
