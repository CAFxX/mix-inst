#!/bin/bash
# Wave-38 battery escalation (track 8, queued by the 09:15 status report):
# wait for load backoff to clear, then run the b33 playbook battery
# (S1->S2->S3->S4 via run_fast_battery.sh start_stage=1; S0 already done)
# sequentially on the 3 cost-eligible survivors (crit strictly < 19.8u).
# Detached; survives supervisor death. Idempotent: skips candidates with an
# existing battery verdict. Q1 (sac/bic) is NOT in run_fast_battery — the
# track-8 supervisor runs it for any candidate with rc=0.
set -u
cd /home/hatch/workspace/mix/exploration/fused || exit 1
LOG=wave38_battery.log
mkdir -p wave38_battery
echo "[wave38-batt] started $(date -u +%FT%TZ) pid=$$ (queued by status report)" >> "$LOG"
for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "[wave38-batt] backoff CLEAR after ${i} polls $(date -u +%FT%TZ)" >> "$LOG"
    break
  fi
  if [ "$i" = 720 ]; then
    echo "[wave38-batt] LOUD: backoff never cleared in 12h; exiting" >> "$LOG"
    exit 1
  fi
  sleep 60
done
FB=/home/hatch/workspace/mix/exploration/fast_battery
for name in w38_t004 w38_t116 w38_t090; do
  if grep -q "^=== BATTERY ${name} rc=" "$FB/results/${name}/battery.log" 2>/dev/null; then
    echo "[wave38-batt] skip ${name} (verdict already recorded)" >> "$LOG"
    continue
  fi
  echo "[wave38-batt] battery ${name} start $(date -u +%FT%TZ)" >> "$LOG"
  nice -n 10 bash "$FB/run_fast_battery.sh" "$name" 1 \
    > "wave38_battery/battery_${name}.log" 2>&1
  rc=$?
  echo "[wave38-batt] battery ${name} rc=${rc} $(date -u +%FT%TZ)" >> "$LOG"
done
echo "[wave38-batt] ALL DONE $(date -u +%FT%TZ)" >> "$LOG"
touch wave38_BATTERY_DONE.txt
