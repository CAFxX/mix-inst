#!/bin/bash
# Round 14 RTL<->model: 300 vectors each via check_rtl.py, 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v iverilog >/dev/null || { echo "iverilog NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r14_feist6_chi_s1alt_nw r14_feist6_alt713_nw r14_feist6_alt_chinolin_nw r14_feist6_alt_chioff_nw r14_feist6_alt_rkhi_nw r14_feist4_chis1l_nw r14_feist4_pars1chi_nw r14_feist5_s1x2_311_nw r14_feist6_chi25_nw r14_feist6_chi16_nw r14_feist6_r9_outdiff_nw r14_feist6_r9_outdiff2_nw r14_feist6_s1chi_311_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round14/rtlcheck
  python3 $EXP/check_rtl.py round14.models.r14.$c $FB/candidates/$c/rtl.v $c $EXP/round14/rtlcheck/$c 300 > $EXP/round14/rtlcheck/$c.log 2>&1
  echo "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $EXP/round14/rtlcheck/$c.log | tail -1 | head -c 80)" >> $EXP/round14/rtlcheck_progress.log
}
: > $EXP/round14/rtlcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_RTLCHECK_DONE" >> $EXP/round14/rtlcheck_progress.log
