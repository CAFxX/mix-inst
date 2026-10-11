#!/bin/bash
# Round 19 S2 differential profiler. Args: candidate list (default: all).
# Per-candidate progress log -> resumable after VM reboot.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R19=$EXP/round19
CANDS="$@"
[ -z "$CANDS" ] && CANDS=$(cat $R19/CANDS.txt)
KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
echo "S2 kill threshold = $KILL_REP (from ref file)"
run_one() {
  c=$1
  if grep -q "^S2_DONE $c " $R19/progress.log 2>/dev/null; then
    echo "S2_SKIP $c (already done)"; return
  fi
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  $FB/build/diffprof_$c $KEY 22 $KILL_REP > $R19/s2_$c.log 2>&1
  rc=$?
  echo "S2_DONE $c rc=$rc $(grep -E 'max\|z\||KILL|PASS' $R19/s2_$c.log | tail -2 | head -c 160)" >> $R19/progress.log
}
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S2_DONE" >> $R19/progress.log
