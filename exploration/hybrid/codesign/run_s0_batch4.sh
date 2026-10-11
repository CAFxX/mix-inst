#!/bin/bash
# Batch-4 S0 driver: sequential s0_delay.py runs, checkpointed.
export TMPDIR=~/workspace/tmp
mkdir -p ~/workspace/tmp
EXP=~/workspace/mix/exploration
S0=$EXP/hybrid/codesign/s0_results
CANDS="cd2_p_a43b1_l513_nw cd2_p_a43b7_l513_nw cd2_p_a53b1_l513_nw cd2_p_a53b7_l513_nw cd2_p_a21b1_l513_nw cd2_p_a21b5_l513_nw cd2_p_a29b1_l513_nw cd2_p_a35b7_l513_nw cd2_p_a3b7_l513_nw cd2_p_a61b1_l513_nw cd2_p_a11b7_l311_nw cd2_p_a11b3_l311_nw cd2_p_a3b1_l311_nw cd2_p_a3b5_l311_nw cd2_p_a53b1_l311_nw cd2_p_a53b2_l311_nw cd2_p_a61b1_l311_nw cd2_p_a9b1_l311_nw cd2_p_a29b2_l311_nw cd2_p_a21b1_l311_nw"
for c in $CANDS; do
  if [ -f "$S0/$c/s0_result.json" ]; then echo "SKIP $c (already done)"; continue; fi
  echo "=== S0 $c ==="
  nice -n 19 python3 $EXP/fast_battery/src/s0_delay.py "$c" "$S0/$c" 2>&1 | tail -3
done
echo ALLDONE
