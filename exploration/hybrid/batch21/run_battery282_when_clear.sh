#!/bin/bash
# Queue-runner: wait for load backoff to clear, then run 282 battery (S2->S4).
LOG=~/workspace/mix/exploration/hybrid/batch21/battery_b28_282.log
echo "queue-runner started $(date -u +%FT%TZ) polling backoff every 60s" >> "$LOG"
for i in $(seq 1 120); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "backoff CLEAR at $(date -u +%FT%TZ) after $i polls; launching battery" >> "$LOG"
    cd ~/workspace/mix/exploration/fast_battery && ~/workspace/system/bin/agentwork-launch.sh --nice 10 --tag track5/b28-battery282 -- bash run_fast_battery.sh hyb28_mu5_282 2 >> "$LOG" 2>&1
    echo "battery exited rc=$? at $(date -u +%FT%TZ)" >> "$LOG"
    exit 0
  fi
  sleep 60
done
echo "queue-runner TIMEOUT after 120 polls at $(date -u +%FT%TZ); battery still queued" >> "$LOG"
exit 1
