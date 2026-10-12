#!/bin/bash
# w4t battery: S1->S4 via run_fast_battery.sh START=1 (S0 already done, all <30u)
cd ~/workspace/mix/exploration/fast_battery
LOG=../adder_lat/w4term/battery.log
for n in w4t_0 w4t_108 w4t_112 w4t_131 w4t_150 w4t_153 w4t_154 w4t_181 w4t_182 w4t_191 w4t_201 w4t_208 w4t_218 w4t_241 w4t_244 w4t_246 w4t_248 w4t_250 w4t_255 w4t_268 w4t_271 w4t_275 w4t_279 w4t_289 w4t_50 w4t_74 w4t_88 w4t_95; do
  echo "=== BATTERY $n $(date -u +%H:%M:%S) ===" >> $LOG
  nice -n 19 ./run_fast_battery.sh $n 1 >> $LOG 2>&1
  echo "battery $n rc=$? ===" >> $LOG
done
echo "BATTERY-ALLDONE $(date -u +%H:%M:%S)" >> $LOG
