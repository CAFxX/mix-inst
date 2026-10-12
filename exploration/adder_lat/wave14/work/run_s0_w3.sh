#!/bin/bash
cd ~/workspace/mix/exploration
for n in al_w3b al_w3c al_w3d al_w3a; do
  echo "=== S0 $n ==="
  python3 run_synth.py fast_battery/candidates/$n/rtl.v $n adder_lat/wave14/work/s0_$n 2>&1 | tail -n 3
done
echo S0_ALL_DONE
