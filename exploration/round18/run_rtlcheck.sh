#!/bin/bash
# Round 18 RTL<->model: 300 vectors each via check_rtl.py, 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v iverilog >/dev/null || { echo "iverilog NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS=$(cat $EXP/round18/CANDS.txt)
run_one() {
  c=$1
  mkdir -p $EXP/round18/rtlcheck
  python3 $EXP/check_rtl.py round18.models.r18.$c $FB/candidates/$c/rtl.v $c $EXP/round18/rtlcheck/$c 300 > $EXP/round18/rtlcheck/$c.log 2>&1
  echo "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $EXP/round18/rtlcheck/$c.log | tail -1 | head -c 80)" >> $EXP/round18/rtlcheck_progress.log
}
: > $EXP/round18/rtlcheck_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_RTLCHECK_DONE" >> $EXP/round18/rtlcheck_progress.log
