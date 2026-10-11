#!/bin/bash
# Round 13 S2: differential early-kill for all 11 S1 survivors, 2 parallel.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r13_feist4_s1x2_311_nw r13_feist4_s1x2_713_nw r13_feist6_chi311_nw r13_feist8_chi311_nw r13_feist6_chis1_311_nw r13_feist6_alt_s1chi_nw r13_feist6_s1x3_chix3_nw r13_lm6_s1_311_nw r13_feist6_s1_midk311_nw r13_feist6_s1_rkhi311_nw r13_feist6_sandw311_nw"
KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
echo "S2 kill threshold at call site: $KILL_REP" | tee $EXP/round13/s2_progress.log
run_one() {
  c=$1
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  $FB/build/diffprof_$c "$KEY" 22 "$KILL_REP" > $EXP/round13/s2_$c.log 2>&1
  rc=$?
  echo "S2_DONE $c rc=$rc $(grep -E 'REPEATS|repeats|max' $EXP/round13/s2_$c.log | tail -2 | head -c 160)" >> $EXP/round13/s2_progress.log
}
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S2_DONE" >> $EXP/round13/s2_progress.log
