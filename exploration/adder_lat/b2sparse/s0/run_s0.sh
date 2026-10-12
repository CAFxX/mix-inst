#!/bin/bash
# (b2) sparse-GF harvest S0 — sequential via run_synth.py's global yosys flock.
# Bar: STRICT <30u (vs W3' 48.3u; the sparse-GF cost thesis needs >=38% cheaper).
cd ~/workspace/mix/exploration
LOG=adder_lat/b2sparse/s0/s0.log
mkdir -p adder_lat/b2sparse/s0

# backoff gate (cleared-flag single-gate pattern; fail loud after 2h)
cleared=0
deadline=$(( $(date +%s) + 7200 ))
while [ $(date +%s) -lt $deadline ]; do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  echo "$(date -u +%H:%M:%S) S0: backoff engaged, waiting" >> $LOG
  sleep 120
done
if [ $cleared -eq 0 ]; then
  echo "BACKOFF-FAIL: load never cleared in 2h" >> $LOG
  exit 1
fi

for n in al_b2s_a al_b2s_b al_b2s_c al_b2s_d; do
  echo "=== S0 $n $(date -u +%H:%M:%S) ===" >> $LOG
  nice -n 19 python3 run_synth.py fast_battery/candidates/$n/rtl.v $n adder_lat/b2sparse/s0/work_$n >> $LOG 2>&1
  echo "rc=$? ===" >> $LOG
done
echo "S0-ALLDONE $(date -u +%H:%M:%S)" >> $LOG
