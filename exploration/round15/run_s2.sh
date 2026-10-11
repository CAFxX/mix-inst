#!/bin/bash
# Round 15 S2: differential early-kill for the 7 S1-passing 6r alt-structure
# designs (2 parallel). Per-candidate progress lines for reboot-resume.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
CANDS="r15_feist6_alt_s713_c311_nw r15_feist6_alt_s311_c713_nw r15_feist6_alt_2rot_nw r15_feist6_parsplit_nw r15_feist6_alt_rkdiff_nw r15_feist6_alt_rksbox_nw r15_feist6_alt_chioff023_nw"
KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
echo "S2 kill threshold at call site: $KILL_REP" | tee $EXP/round15/s2_progress.log
run_one() {
  c=$1
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  $FB/build/diffprof_$c "$KEY" 22 "$KILL_REP" > $EXP/round15/s2_$c.log 2>&1
  rc=$?
  echo "S2_DONE $c rc=$rc $(grep -E 'REPEATS|repeats|max' $EXP/round15/s2_$c.log | tail -2 | head -c 160)" >> $EXP/round15/s2_progress.log
}
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
  run_one $c &
done
wait
echo "ALL_S2_DONE" >> $EXP/round15/s2_progress.log
