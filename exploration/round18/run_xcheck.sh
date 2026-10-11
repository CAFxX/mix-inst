#!/bin/bash
# Round 18 xcheck: C impl bit-exact vs Python model (10k vectors each), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v gcc >/dev/null || { echo "gcc NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS=$(cat $EXP/round18/CANDS.txt)
run_one() {
  c=$1
  mkdir -p $EXP/round18/xcheck
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$EXP/round18/xcheck/$c.build.err || { echo "XCHECK_BUILD_FAIL $c" >> $EXP/round18/xcheck_progress.log; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $EXP/round18/xcheck/$c.vecs > $EXP/round18/xcheck/$c.log 2>&1
  echo "XCHECK_DONE $c rc=$? $(tail -1 $EXP/round18/xcheck/$c.log | head -c 100)" >> $EXP/round18/xcheck_progress.log
}
: > $EXP/round18/xcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_XCHECK_DONE" >> $EXP/round18/xcheck_progress.log
