#!/bin/bash
# Round 15 xcheck: C impl bit-exact vs Python model (10k vectors each), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r15_feist6_alt_s713_c311_nw r15_feist6_alt_s311_c713_nw r15_feist6_alt_2rot_nw r15_feist6_alt_wh_nw r15_feist5_db3_nw r15_feist6_db4_nw r15_feist5_db24_nw r15_feist6_db34_nw r15_feist6_parsplit_nw r15_feist6_alt_rkdiff_nw r15_feist6_alt_rksbox_nw r15_feist6_alt_chioff023_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round15/xcheck
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$EXP/round15/xcheck/$c.build.err || { echo "XCHECK_BUILD_FAIL $c" >> $EXP/round15/xcheck_progress.log; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $EXP/round15/xcheck/$c.vecs > $EXP/round15/xcheck/$c.log 2>&1
  echo "XCHECK_DONE $c rc=$? $(tail -1 $EXP/round15/xcheck/$c.log | head -c 100)" >> $EXP/round15/xcheck_progress.log
}
: > $EXP/round15/xcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_XCHECK_DONE" >> $EXP/round15/xcheck_progress.log
