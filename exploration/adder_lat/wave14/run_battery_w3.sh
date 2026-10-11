#!/bin/bash
# Wave-14 W3 staged battery escalation (b33 playbook), backoff-gated.
# S0 already adjudicated via run_synth.py against the wave-14 adder-like
# bar (<123.4u): al_w3c 31.9u, al_w3b 34.6u -- both cost-eligible.
# Battery therefore starts at stage 1 (run_fast_battery.sh <cand> 1);
# its internal S0 frontier bar (<=0.9x mul) is NOT the wave-14 gate.
# Order: best S0 first (w3c 31.9u), then w3b. w3d/w3a appended by the
# supervisor once their S0 lands and if eligible.
set -u
cd /home/hatch/workspace/mix/exploration/fast_battery
for cand in al_w3c al_w3b; do
  # backoff gate: poll until CLEAR (max ~3h), per standing orders
  for i in $(seq 1 180); do
    if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
      echo "[gate] backoff CLEAR for $cand $(date -u +%FT%TZ)"
      break
    fi
    sleep 60
  done
  echo "=== BATTERY $cand (start stage 1) $(date -u +%FT%TZ) ==="
  bash run_fast_battery.sh "$cand" 1
  echo "=== BATTERY $cand rc=$? $(date -u +%FT%TZ) ==="
done
echo BATTERY_W3_DONE
