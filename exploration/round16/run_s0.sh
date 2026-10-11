#!/bin/bash
# Round 15 S0: official delay via run_synth.py (authorized path), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r16_feist6_gift_het_nw r16_feist6_present_het_nw r16_feist6_sk4_het_nw r16_feist6_alt_lin3711_nw r16_feist6_alt_lin71319_nw r16_feist6_parsplit_rev_nw r16_feist6_parsplit_713_nw r16_feist6_parsplit_chioff23_nw r16_feist6_parsplit_w24_nw r16_feist6_giftsplit_nw r16_feist6_alt_s1ps_nw r16_feist6_alt_midk_nw"
run_one() {
  c=$1
  python3 $EXP/run_synth.py $EXP/fast_battery/candidates/$c/rtl.v $c $EXP/round16/s0/$c > $EXP/round16/s0/$c.log 2>&1
  echo "S0_DONE $c rc=$? $(grep -h RESULT $EXP/round16/s0/$c.log | tail -1 | head -c 120)" >> $EXP/round16/s0_progress.log
}
mkdir -p $EXP/round16/s0
: > $EXP/round16/s0_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S0_DONE" >> $EXP/round16/s0_progress.log
