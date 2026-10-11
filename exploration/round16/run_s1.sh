#!/bin/bash
# Round 15 S1 screen for all 13 (absolute outdir required), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r16_feist6_gift_het_nw r16_feist6_present_het_nw r16_feist6_sk4_het_nw r16_feist6_alt_lin3711_nw r16_feist6_alt_lin71319_nw r16_feist6_parsplit_rev_nw r16_feist6_parsplit_713_nw r16_feist6_parsplit_chioff23_nw r16_feist6_parsplit_w24_nw r16_feist6_giftsplit_nw r16_feist6_alt_s1ps_nw r16_feist6_alt_midk_nw"
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round16/s1/$c > $EXP/round16/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round16/s1_$c.log | tail -1 | head -c 100)" >> $EXP/round16/s1_progress.log
}
mkdir -p $EXP/round16/s1
: > $EXP/round16/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round16/s1_progress.log
