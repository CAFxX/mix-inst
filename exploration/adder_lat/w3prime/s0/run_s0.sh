#!/bin/bash
# W3' harvest S0 — sequential, run_synth.py holds the global yosys flock
cd ~/workspace/mix/exploration
LOG=adder_lat/w3prime/s0/s0.log
for n in al_w3p_a al_w3p_b al_w3p_c al_w3p_d; do
  echo "=== S0 $n $(date -u +%H:%M:%S) ===" >> $LOG
  nice -n 10 python3 run_synth.py fast_battery/candidates/$n/rtl.v $n adder_lat/w3prime/s0/work_$n >> $LOG 2>&1
  echo "rc=$? ===" >> $LOG
done
echo "S0-ALLDONE $(date -u +%H:%M:%S)" >> $LOG
