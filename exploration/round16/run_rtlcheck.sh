#!/bin/bash
# Round 15 RTL<->model: 300 vectors each via check_rtl.py, 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v iverilog >/dev/null || { echo "iverilog NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r16_feist6_gift_het_nw r16_feist6_present_het_nw r16_feist6_sk4_het_nw r16_feist6_alt_lin3711_nw r16_feist6_alt_lin71319_nw r16_feist6_parsplit_rev_nw r16_feist6_parsplit_713_nw r16_feist6_parsplit_chioff23_nw r16_feist6_parsplit_w24_nw r16_feist6_giftsplit_nw r16_feist6_alt_s1ps_nw r16_feist6_alt_midk_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round16/rtlcheck
  python3 $EXP/check_rtl.py round16.models.r16.$c $FB/candidates/$c/rtl.v $c $EXP/round16/rtlcheck/$c 300 > $EXP/round16/rtlcheck/$c.log 2>&1
  echo "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $EXP/round16/rtlcheck/$c.log | tail -1 | head -c 80)" >> $EXP/round16/rtlcheck_progress.log
}
: > $EXP/round16/rtlcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_RTLCHECK_DONE" >> $EXP/round16/rtlcheck_progress.log
