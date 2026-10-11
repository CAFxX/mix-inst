#!/bin/bash
# Round 12 S1 screen for all 10 (absolute outdir required).
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r12_feist5_lin3711_nw r12_feist5_lin31119_nw r12_feist5_lin71319_nw r12_feist5_lin31125_nw r12_feist6_s1half311_nw r12_feist7_s1half311_nw r12_feist8_s1half311_nw r12_feist6_lin3711_nw r12_feist6_lin71319_nw r12_feist6_s1_16rot_nw"
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round12/s1/$c > $EXP/round12/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round12/s1_$c.log | tail -1 | head -c 100)" >> $EXP/round12/s1_progress.log
}
mkdir -p $EXP/round12/s1
: > $EXP/round12/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round12/s1_progress.log
