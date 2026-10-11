#!/bin/bash
# Round 15 RTL<->model: 300 vectors each via check_rtl.py, 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v iverilog >/dev/null || { echo "iverilog NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r17_feist5_parsplit_nw r17_feist5_alt_s1chi_nw r17_feist5_alt_chifirst_nw r17_feist6_parmix_nw r17_feist6_alt_pshalf_nw r17_feist6_dbs1split_nw r17_feist6_parsplit_chioff01_nw r17_feist6_premix_nw r17_feist4_parsplit_nw r17_feist5_parsplit_713_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round17/rtlcheck
  python3 $EXP/check_rtl.py round17.models.r17.$c $FB/candidates/$c/rtl.v $c $EXP/round17/rtlcheck/$c 300 > $EXP/round17/rtlcheck/$c.log 2>&1
  echo "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $EXP/round17/rtlcheck/$c.log | tail -1 | head -c 80)" >> $EXP/round17/rtlcheck_progress.log
}
: > $EXP/round17/rtlcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_RTLCHECK_DONE" >> $EXP/round17/rtlcheck_progress.log
