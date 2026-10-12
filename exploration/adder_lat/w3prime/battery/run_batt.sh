#!/bin/bash
# W3' harvest battery — S1->S4 via run_fast_battery.sh START=1 (S0 already done)
cd ~/workspace/mix/exploration/fast_battery
for n in al_w3p_a al_w3p_b al_w3p_c al_w3p_d; do
  echo "=== BATTERY $n $(date -u +%H:%M:%S) ===" >> ../adder_lat/w3prime/battery/battery.log
  nice -n 10 ./run_fast_battery.sh $n 1 >> ../adder_lat/w3prime/battery/battery.log 2>&1
  echo "battery $n rc=$? ===" >> ../adder_lat/w3prime/battery/battery.log
done
echo "BATTERY-ALLDONE $(date -u +%H:%M:%S)" >> ../adder_lat/w3prime/battery/battery.log
