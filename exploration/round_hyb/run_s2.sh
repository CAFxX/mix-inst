#!/bin/bash
# Hybridization round S2 differential profiler. Args: candidate list (default: all).
# Per-candidate progress log -> resumable after VM reboot.
# Inspect the |z| column, not just repeats (notr5/drop4 lesson: |z|>~100 on
# single-bit deltas is a structural kill even at 0 repeats).
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
RH=$EXP/round_hyb
CANDS="$@"
[ -z "$CANDS" ] && CANDS=$(cat $RH/CANDS.txt)
KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
echo "S2 kill threshold = $KILL_REP (from ref file)"
run_one() {
  c=$1
  if grep -q "^S2_DONE $c " $RH/progress.log 2>/dev/null; then
    echo "S2_SKIP $c (already done)"; return
  fi
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  $FB/build/diffprof_$c $KEY 22 $KILL_REP > $RH/s2_$c.log 2>&1
  rc=$?
  echo "S2_DONE $c rc=$rc $(grep -E 'max\|z\||KILL|PASS' $RH/s2_$c.log | tail -2 | head -c 160)" >> $RH/progress.log
}
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_S2_DONE" >> $RH/progress.log
