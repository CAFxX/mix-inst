#!/bin/bash
# Track-6 sup X: wait for load backoff to clear, then run S0 for t6_ormM6b and
# t6_ormM6c sequentially. Launched 2026-10-11 ~04:34 UTC.
cd ~/workspace/mix/exploration || exit 1
for i in $(seq 1 60); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "backoff CLEAR after ${i} checks $(date -u)"
    break
  fi
  sleep 60
done
~/workspace/system/bin/load-shed.sh backoff || { echo "STILL BACKED OFF after 60 min -- S0s remain queued (QUEUED.txt markers stand)"; exit 3; }
~/workspace/system/bin/agentwork-launch.sh --nice 19 --tag track6/b40-s0-ormM6b -- \
  python3 run_synth.py fast_battery/candidates/t6_ormM6b/rtl.v t6_ormM6b \
  new_constructions/batch40/s0_ormM6b > new_constructions/batch40/s0_ormM6b/s0.log 2>&1
echo "S0b done rc=$? $(date -u)"; grep RESULT new_constructions/batch40/s0_ormM6b/s0.log
~/workspace/system/bin/agentwork-launch.sh --nice 19 --tag track6/b40-s0-ormM6c -- \
  python3 run_synth.py fast_battery/candidates/t6_ormM6c/rtl.v t6_ormM6c \
  new_constructions/batch40/s0_ormM6c > new_constructions/batch40/s0_ormM6c/s0.log 2>&1
echo "S0c done rc=$? $(date -u)"; grep RESULT new_constructions/batch40/s0_ormM6c/s0.log
echo ALL_S0_DONE
