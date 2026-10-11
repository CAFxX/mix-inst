#!/bin/bash
# Round 13 S2 RESUME (post-reboot 2026-10-03 00:29): remaining 6 candidates.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r13_feist6_chis1_311_nw r13_feist6_s1x3_chix3_nw r13_lm6_s1_311_nw r13_feist6_s1_midk311_nw r13_feist6_s1_rkhi311_nw r13_feist6_sandw311_nw"
KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
run_one() {
  c=$1
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  $FB/build/diffprof_$c "$KEY" 22 "$KILL_REP" > $EXP/round13/s2_$c.log 2>&1
  rc=$?
  echo "S2_DONE $c rc=$rc $(grep -E '^(PASS|KILL)' $EXP/round13/s2_$c.log | tail -1 | head -c 120)" >> $EXP/round13/s2_progress.log
}
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S2_DONE" >> $EXP/round13/s2_progress.log
