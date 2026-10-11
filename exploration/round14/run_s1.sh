#!/bin/bash
# Round 14 S1 screen for all 13 (absolute outdir required), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r14_feist6_chi_s1alt_nw r14_feist6_alt713_nw r14_feist6_alt_chinolin_nw r14_feist6_alt_chioff_nw r14_feist6_alt_rkhi_nw r14_feist4_chis1l_nw r14_feist4_pars1chi_nw r14_feist5_s1x2_311_nw r14_feist6_chi25_nw r14_feist6_chi16_nw r14_feist6_r9_outdiff_nw r14_feist6_r9_outdiff2_nw r14_feist6_s1chi_311_nw"
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round14/s1/$c > $EXP/round14/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round14/s1_$c.log | tail -1 | head -c 100)" >> $EXP/round14/s1_progress.log
}
mkdir -p $EXP/round14/s1
: > $EXP/round14/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round14/s1_progress.log
