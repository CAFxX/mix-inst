#!/bin/bash
# Round 15 S0: official delay via run_synth.py (authorized path), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r15_feist6_alt_s713_c311_nw r15_feist6_alt_s311_c713_nw r15_feist6_alt_2rot_nw r15_feist6_alt_wh_nw r15_feist5_db3_nw r15_feist6_db4_nw r15_feist5_db24_nw r15_feist6_db34_nw r15_feist6_parsplit_nw r15_feist6_alt_rkdiff_nw r15_feist6_alt_rksbox_nw r15_feist6_alt_chioff023_nw"
run_one() {
  c=$1
  python3 $EXP/run_synth.py $EXP/fast_battery/candidates/$c/rtl.v $c $EXP/round15/s0/$c > $EXP/round15/s0/$c.log 2>&1
  echo "S0_DONE $c rc=$? $(grep -h RESULT $EXP/round15/s0/$c.log | tail -1 | head -c 120)" >> $EXP/round15/s0_progress.log
}
mkdir -p $EXP/round15/s0
: > $EXP/round15/s0_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S0_DONE" >> $EXP/round15/s0_progress.log
