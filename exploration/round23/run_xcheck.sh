#!/bin/bash
# Round 23 xcheck: C vs Python model, 10k vectors. Cheap (gcc+python).
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R23=$EXP/round23
for c in $(cat $R23/CANDS.txt); do
  if grep -q "^XCHECK_DONE $c " $R23/progress.log 2>/dev/null; then echo "SKIP $c"; continue; fi
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$R23/xcheck/$c.build.err \
    || { echo "XCHECK_BUILD_FAIL $c"; echo "XCHECK_BUILD_FAIL $c" >> $R23/progress.log; continue; }
  python3 $R23/xcheck_fast.py $c $FB/build/diffprof_$c 10000 $R23/xcheck/$c.vecs > $R23/xcheck/$c.log 2>&1
  rc=$?
  echo "XCHECK_DONE $c rc=$rc $(tail -1 $R23/xcheck/$c.log | head -c 60)" | tee -a $R23/progress.log
done
echo ALL_XCHECK_DONE
