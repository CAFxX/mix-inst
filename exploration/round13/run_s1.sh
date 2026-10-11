#!/bin/bash
# Round 13 S1 screen for all 13 (absolute outdir required), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r13_feist4_s1x2_311_nw r13_feist4_s1x2_713_nw r13_feist5_chi311_nw r13_feist6_chi311_nw r13_feist8_chi311_nw r13_feist6_chis1_311_nw r13_feist6_alt_s1chi_nw r13_feist6_s1x3_chix3_nw r13_lm4_s1_311_nw r13_lm6_s1_311_nw r13_feist6_s1_midk311_nw r13_feist6_s1_rkhi311_nw r13_feist6_sandw311_nw"
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round13/s1/$c > $EXP/round13/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round13/s1_$c.log | tail -1 | head -c 100)" >> $EXP/round13/s1_progress.log
}
mkdir -p $EXP/round13/s1
: > $EXP/round13/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round13/s1_progress.log
