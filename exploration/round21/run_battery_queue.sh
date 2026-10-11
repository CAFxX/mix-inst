#!/bin/bash
# Round 21: full S3->S4 battery queue for frontier-relevant candidates.
# S0/S1/S2/Q1 already recorded; start at S3. Detached, 2 concurrent,
# per-candidate checkpointing in battery_progress.log (reboot-resumable).
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
R21=$EXP/round21
CANDS="r21_feist6_alt_notr_chioff31_fm07_nw r21_feist6_alt_notr_chioff13all_fm07_nw r21_feist6_alt_notr_chioff13all_fm311_nw r21_feist6_alt_notr_3rot_ns_nw"
run_one() {
  c=$1
  if grep -q "^BATTERY_DONE $c " $R21/battery_progress.log 2>/dev/null; then
    echo "BATTERY_SKIP $c (already done)"; return
  fi
  bash $EXP/fast_battery/run_fast_battery.sh $c 3 > $R21/battery_$c.log 2>&1
  rc=$?
  echo "BATTERY_DONE $c rc=$rc $(date -u +%FT%TZ)" >> $R21/battery_progress.log
}
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 30; done
  run_one $c &
done
wait
echo "ALL_BATTERIES_DONE $(date -u +%FT%TZ)" >> $R21/battery_progress.log
