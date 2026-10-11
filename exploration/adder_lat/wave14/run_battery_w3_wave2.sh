#!/bin/bash
# Wave-14 W3 battery wave 2: al_w3d (S0 27.7u) then al_w3a (S0 41.8u).
# Waits for wave-1 runner completion marker, then backoff-gates each run.
set -u
W=~/workspace/mix/exploration/adder_lat/wave14/work
for i in $(seq 1 360); do
  grep -q BATTERY_W3_DONE $W/battery_w3.log 2>/dev/null && break
  sleep 60
done
grep -q BATTERY_W3_DONE $W/battery_w3.log || { echo "wave1 never finished; aborting wave2"; exit 1; }
cd /home/hatch/workspace/mix/exploration/fast_battery
for cand in al_w3d al_w3a; do
  for i in $(seq 1 180); do
    if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then echo "[gate] CLEAR $cand $(date -u +%FT%TZ)"; break; fi
    sleep 60
  done
  echo "=== BATTERY $cand (start stage 1) $(date -u +%FT%TZ) ==="
  bash run_fast_battery.sh "$cand" 1
  echo "=== BATTERY $cand rc=$? $(date -u +%FT%TZ) ==="
done
echo BATTERY_W3_WAVE2_DONE
