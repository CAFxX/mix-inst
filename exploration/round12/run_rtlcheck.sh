#!/bin/bash
# Round 12 RTL<->model: 300 vectors each via check_rtl.py, 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r12_feist5_lin3711_nw r12_feist5_lin31119_nw r12_feist5_lin71319_nw r12_feist5_lin31125_nw r12_feist6_s1half311_nw r12_feist7_s1half311_nw r12_feist8_s1half311_nw r12_feist6_lin3711_nw r12_feist6_lin71319_nw r12_feist6_s1_16rot_nw"
run_one() {
  c=$1
  python3 $EXP/check_rtl.py round12.models.r12.$c $FB/candidates/$c/rtl.v $c $EXP/round12/rtlcheck/$c 300 > $EXP/round12/rtlcheck/$c.log 2>&1
  echo "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $EXP/round12/rtlcheck/$c.log | tail -1 | head -c 80)" >> $EXP/round12/rtlcheck_progress.log
}
: > $EXP/round12/rtlcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_RTLCHECK_DONE" >> $EXP/round12/rtlcheck_progress.log
