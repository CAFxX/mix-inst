#!/bin/bash
# Round 18 S1 screen for all 9 (absolute outdir required), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS=$(cat $EXP/round18/CANDS.txt)
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round18/s1/$c > $EXP/round18/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round18/s1_$c.log | tail -1 | head -c 100)" >> $EXP/round18/s1_progress.log
}
mkdir -p $EXP/round18/s1
: > $EXP/round18/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round18/s1_progress.log
