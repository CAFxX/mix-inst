#!/bin/bash
# Round 15 xcheck: C impl bit-exact vs Python model (10k vectors each), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r16_feist6_gift_het_nw r16_feist6_present_het_nw r16_feist6_sk4_het_nw r16_feist6_alt_lin3711_nw r16_feist6_alt_lin71319_nw r16_feist6_parsplit_rev_nw r16_feist6_parsplit_713_nw r16_feist6_parsplit_chioff23_nw r16_feist6_parsplit_w24_nw r16_feist6_giftsplit_nw r16_feist6_alt_s1ps_nw r16_feist6_alt_midk_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round16/xcheck
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$EXP/round16/xcheck/$c.build.err || { echo "XCHECK_BUILD_FAIL $c" >> $EXP/round16/xcheck_progress.log; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $EXP/round16/xcheck/$c.vecs > $EXP/round16/xcheck/$c.log 2>&1
  echo "XCHECK_DONE $c rc=$? $(tail -1 $EXP/round16/xcheck/$c.log | head -c 100)" >> $EXP/round16/xcheck_progress.log
}
: > $EXP/round16/xcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_XCHECK_DONE" >> $EXP/round16/xcheck_progress.log
