#!/bin/bash
# Track-6 sup XI: wait for load backoff to clear, then run S0 for t6_nandM6a
# and t6_norM6a sequentially. Launched 2026-10-11 ~05:22 UTC.
cd ~/workspace/mix/exploration || exit 1
mkdir -p new_constructions/batch41/s0_t6_nandM6a new_constructions/batch41/s0_t6_norM6a
for i in $(seq 1 60); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "backoff CLEAR after ${i} checks $(date -u)"
    break
  fi
  sleep 60
done
~/workspace/system/bin/load-shed.sh backoff || { echo "STILL BACKED OFF after 60 min -- S0s remain queued"; exit 3; }
~/workspace/system/bin/agentwork-launch.sh --nice 19 --tag track6/b41-s0-nandM6a -- \
  python3 run_synth.py fast_battery/candidates/t6_nandM6a/rtl.v t6_nandM6a \
  new_constructions/batch41/s0_t6_nandM6a > new_constructions/batch41/s0_t6_nandM6a/s0.log 2>&1
echo "S0 nandM6a done rc=$? $(date -u)"; grep RESULT new_constructions/batch41/s0_t6_nandM6a/s0.log
~/workspace/system/bin/agentwork-launch.sh --nice 19 --tag track6/b41-s0-norM6a -- \
  python3 run_synth.py fast_battery/candidates/t6_norM6a/rtl.v t6_norM6a \
  new_constructions/batch41/s0_t6_norM6a > new_constructions/batch41/s0_t6_norM6a/s0.log 2>&1
echo "S0 norM6a done rc=$? $(date -u)"; grep RESULT new_constructions/batch41/s0_t6_norM6a/s0.log
echo ALL_S0_DONE
