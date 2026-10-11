#!/bin/bash
# Round 18 S0: official delay via run_synth.py (authorized path), 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
CANDS=$(cat $EXP/round18/CANDS.txt)
run_one() {
  c=$1
  python3 $EXP/run_synth.py $EXP/fast_battery/candidates/$c/rtl.v $c $EXP/round18/s0/$c > $EXP/round18/s0/$c.log 2>&1
  echo "S0_DONE $c rc=$? $(grep -h RESULT $EXP/round18/s0/$c.log | tail -1 | head -c 120)" >> $EXP/round18/s0_progress.log
}
mkdir -p $EXP/round18/s0
: > $EXP/round18/s0_progress.log
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S0_DONE" >> $EXP/round18/s0_progress.log
