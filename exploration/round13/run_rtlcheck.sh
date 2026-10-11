#!/bin/bash
# Round 13 RTL<->model: 300 vectors each via check_rtl.py, 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r13_feist4_s1x2_311_nw r13_feist4_s1x2_713_nw r13_feist5_chi311_nw r13_feist6_chi311_nw r13_feist8_chi311_nw r13_feist6_chis1_311_nw r13_feist6_alt_s1chi_nw r13_feist6_s1x3_chix3_nw r13_lm4_s1_311_nw r13_lm6_s1_311_nw r13_feist6_s1_midk311_nw r13_feist6_s1_rkhi311_nw r13_feist6_sandw311_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round13/rtlcheck
  python3 $EXP/check_rtl.py round13.models.r13.$c $FB/candidates/$c/rtl.v $c $EXP/round13/rtlcheck/$c 300 > $EXP/round13/rtlcheck/$c.log 2>&1
  echo "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $EXP/round13/rtlcheck/$c.log | tail -1 | head -c 80)" >> $EXP/round13/rtlcheck_progress.log
}
: > $EXP/round13/rtlcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_RTLCHECK_DONE" >> $EXP/round13/rtlcheck_progress.log
