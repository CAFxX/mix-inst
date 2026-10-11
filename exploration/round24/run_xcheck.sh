#!/bin/bash
# Round 24 xcheck: C vs Python model, 10k vectors. Cheap (gcc+python).
# Resume-safe: skips candidates with XCHECK_DONE in progress.log.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R24=$EXP/round24
mkdir -p $R24/xcheck
for c in $(cat $R24/CANDS.txt); do
  if grep -q "XCHECK_DONE $c " $R24/progress.log 2>/dev/null; then echo "SKIP $c"; continue; fi
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$R24/xcheck/$c.build.err \
    || { echo "XCHECK_BUILD_FAIL $c"; echo "$(date -u +%FT%TZ) XCHECK_BUILD_FAIL $c" >> $R24/progress.log; continue; }
  python3 $R24/xcheck_fast.py $c $FB/build/diffprof_$c 10000 $R24/xcheck/$c.vecs > $R24/xcheck/$c.log 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) XCHECK_DONE $c rc=$rc $(tail -1 $R24/xcheck/$c.log | head -c 60)" | tee -a $R24/progress.log
done
echo ALL_XCHECK_DONE
