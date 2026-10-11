#!/bin/bash
# Round 13 S0: official delay via run_synth.py (authorized path), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r13_feist4_s1x2_311_nw r13_feist4_s1x2_713_nw r13_feist5_chi311_nw r13_feist6_chi311_nw r13_feist8_chi311_nw r13_feist6_chis1_311_nw r13_feist6_alt_s1chi_nw r13_feist6_s1x3_chix3_nw r13_lm4_s1_311_nw r13_lm6_s1_311_nw r13_feist6_s1_midk311_nw r13_feist6_s1_rkhi311_nw r13_feist6_sandw311_nw"
run_one() {
  c=$1
  python3 $EXP/run_synth.py $EXP/fast_battery/candidates/$c/rtl.v $c $EXP/round13/s0/$c > $EXP/round13/s0/$c.log 2>&1
  echo "S0_DONE $c rc=$? $(grep -h RESULT $EXP/round13/s0/$c.log | tail -1 | head -c 120)" >> $EXP/round13/s0_progress.log
}
mkdir -p $EXP/round13/s0
: > $EXP/round13/s0_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S0_DONE" >> $EXP/round13/s0_progress.log
