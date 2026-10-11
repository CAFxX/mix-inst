#!/bin/bash
# Round 13 xcheck: C impl bit-exact vs Python model (10k vectors each), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r13_feist4_s1x2_311_nw r13_feist4_s1x2_713_nw r13_feist5_chi311_nw r13_feist6_chi311_nw r13_feist8_chi311_nw r13_feist6_chis1_311_nw r13_feist6_alt_s1chi_nw r13_feist6_s1x3_chix3_nw r13_lm4_s1_311_nw r13_lm6_s1_311_nw r13_feist6_s1_midk311_nw r13_feist6_s1_rkhi311_nw r13_feist6_sandw311_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round13/xcheck
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$EXP/round13/xcheck/$c.build.err || { echo "XCHECK_BUILD_FAIL $c" >> $EXP/round13/xcheck_progress.log; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $EXP/round13/xcheck/$c.vecs > $EXP/round13/xcheck/$c.log 2>&1
  echo "XCHECK_DONE $c rc=$? $(tail -1 $EXP/round13/xcheck/$c.log | head -c 100)" >> $EXP/round13/xcheck_progress.log
}
: > $EXP/round13/xcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_XCHECK_DONE" >> $EXP/round13/xcheck_progress.log
