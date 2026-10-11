#!/bin/bash
# Round 11 S0: official delay via run_synth.py (authorized path), 2 parallel.
EXP=/home/hatch/workspace/mix/exploration
CANDS="r11_feist6_present311_nw r11_feist6_present713_nw r11_feist6_gift311_nw r11_feist6_gift713_nw r11_feist6_sk4311_nw r11_feist6_sk4713_nw r11_feist6_piccolo311_nw r11_feist6_piccolo713_nw r11_feist6_sk8311_nw r11_feist6_s1mix311_nw"
run_one() {
  c=$1
  python3 $EXP/run_synth.py $EXP/fast_battery/candidates/$c/rtl.v $c $EXP/round11/s0/$c > $EXP/round11/s0/$c.log 2>&1
  echo "S0_DONE $c rc=$? $(grep -h RESULT $EXP/round11/s0/$c.log | tail -1)" >> $EXP/round11/s0_progress.log
}
mkdir -p $EXP/round11/s0
: > $EXP/round11/s0_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S0_DONE" >> $EXP/round11/s0_progress.log
