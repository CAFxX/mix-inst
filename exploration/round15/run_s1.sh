#!/bin/bash
# Round 15 S1 screen for all 13 (absolute outdir required), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r15_feist6_alt_s713_c311_nw r15_feist6_alt_s311_c713_nw r15_feist6_alt_2rot_nw r15_feist6_alt_wh_nw r15_feist5_db3_nw r15_feist6_db4_nw r15_feist5_db24_nw r15_feist6_db34_nw r15_feist6_parsplit_nw r15_feist6_alt_rkdiff_nw r15_feist6_alt_rksbox_nw r15_feist6_alt_chioff023_nw"
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round15/s1/$c > $EXP/round15/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round15/s1_$c.log | tail -1 | head -c 100)" >> $EXP/round15/s1_progress.log
}
mkdir -p $EXP/round15/s1
: > $EXP/round15/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round15/s1_progress.log
