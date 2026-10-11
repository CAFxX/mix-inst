#!/bin/bash
# Round 12 xcheck: C impl bit-exact vs Python model (10k vectors each).
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r12_feist5_lin3711_nw r12_feist5_lin31119_nw r12_feist5_lin71319_nw r12_feist5_lin31125_nw r12_feist6_s1half311_nw r12_feist7_s1half311_nw r12_feist8_s1half311_nw r12_feist6_lin3711_nw r12_feist6_lin71319_nw r12_feist6_s1_16rot_nw"
run_one() {
  c=$1
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$EXP/round12/xcheck/$c.build.err || { echo "XCHECK_BUILD_FAIL $c"; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $EXP/round12/xcheck/$c.vecs > $EXP/round12/xcheck/$c.log 2>&1
  echo "XCHECK_DONE $c rc=$? $(tail -1 $EXP/round12/xcheck/$c.log | head -c 100)" >> $EXP/round12/xcheck_progress.log
}
: > $EXP/round12/xcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_XCHECK_DONE" >> $EXP/round12/xcheck_progress.log
