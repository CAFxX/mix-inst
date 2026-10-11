#!/bin/bash
# Round 14 xcheck: C impl bit-exact vs Python model (10k vectors each), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r14_feist6_chi_s1alt_nw r14_feist6_alt713_nw r14_feist6_alt_chinolin_nw r14_feist6_alt_chioff_nw r14_feist6_alt_rkhi_nw r14_feist4_chis1l_nw r14_feist4_pars1chi_nw r14_feist5_s1x2_311_nw r14_feist6_chi25_nw r14_feist6_chi16_nw r14_feist6_r9_outdiff_nw r14_feist6_r9_outdiff2_nw r14_feist6_s1chi_311_nw"
run_one() {
  c=$1
  mkdir -p $EXP/round14/xcheck
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$EXP/round14/xcheck/$c.build.err || { echo "XCHECK_BUILD_FAIL $c" >> $EXP/round14/xcheck_progress.log; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $EXP/round14/xcheck/$c.vecs > $EXP/round14/xcheck/$c.log 2>&1
  echo "XCHECK_DONE $c rc=$? $(tail -1 $EXP/round14/xcheck/$c.log | head -c 100)" >> $EXP/round14/xcheck_progress.log
}
: > $EXP/round14/xcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_XCHECK_DONE" >> $EXP/round14/xcheck_progress.log
