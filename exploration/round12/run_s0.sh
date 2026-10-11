#!/bin/bash
# Round 12 S0: official delay via run_synth.py (authorized path), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r12_feist5_lin3711_nw r12_feist5_lin31119_nw r12_feist5_lin71319_nw r12_feist5_lin31125_nw r12_feist6_s1half311_nw r12_feist7_s1half311_nw r12_feist8_s1half311_nw r12_feist6_lin3711_nw r12_feist6_lin71319_nw r12_feist6_s1_16rot_nw"
run_one() {
  c=$1
  python3 $EXP/run_synth.py $EXP/fast_battery/candidates/$c/rtl.v $c $EXP/round12/s0/$c > $EXP/round12/s0/$c.log 2>&1
  echo "S0_DONE $c rc=$? $(grep -h RESULT $EXP/round12/s0/$c.log | tail -1 | head -c 120)" >> $EXP/round12/s0_progress.log
}
mkdir -p $EXP/round12/s0
: > $EXP/round12/s0_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S0_DONE" >> $EXP/round12/s0_progress.log
