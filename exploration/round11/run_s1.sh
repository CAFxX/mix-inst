#!/bin/bash
# Round 11 S1 screen for all 10 (cheap statistical characterization).
# NOTE: absolute outdir required (s1_screen.py chdir's internally).
EXP=/home/hatch/workspace/mix/exploration
CANDS="r11_feist6_present311_nw r11_feist6_present713_nw r11_feist6_gift311_nw r11_feist6_gift713_nw r11_feist6_sk4311_nw r11_feist6_sk4713_nw r11_feist6_piccolo311_nw r11_feist6_piccolo713_nw r11_feist6_sk8311_nw r11_feist6_s1mix311_nw"
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round11/s1/$c > $EXP/round11/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round11/s1_$c.log | tail -1)" >> $EXP/round11/s1_progress.log
}
mkdir -p $EXP/round11/s1
: > $EXP/round11/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round11/s1_progress.log
