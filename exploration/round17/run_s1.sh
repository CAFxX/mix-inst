#!/bin/bash
# Round 15 S1 screen for all 13 (absolute outdir required), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS="r17_feist5_parsplit_nw r17_feist5_alt_s1chi_nw r17_feist5_alt_chifirst_nw r17_feist6_parmix_nw r17_feist6_alt_pshalf_nw r17_feist6_dbs1split_nw r17_feist6_parsplit_chioff01_nw r17_feist6_premix_nw r17_feist4_parsplit_nw r17_feist5_parsplit_713_nw"
run_one() {
  c=$1
  python3 $EXP/fast_battery/src/s1_screen.py $c $EXP/round17/s1/$c > $EXP/round17/s1_$c.log 2>&1
  echo "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $EXP/round17/s1_$c.log | tail -1 | head -c 100)" >> $EXP/round17/s1_progress.log
}
mkdir -p $EXP/round17/s1
: > $EXP/round17/s1_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S1_DONE" >> $EXP/round17/s1_progress.log
