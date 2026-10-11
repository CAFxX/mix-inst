#!/bin/bash
# Batch-4 S1 driver (resume design-layer): sequential s1_screen.py, checkpointed.
export TMPDIR=~/workspace/tmp
mkdir -p ~/workspace/tmp
EXP=~/workspace/mix/exploration
S1=$EXP/hybrid/codesign/s1_results
LOG=$EXP/hybrid/codesign/s1_batch4_rest.log
# Exclusive lock: prevent duplicate driver instances (incident 2026-10-07).
exec 9>"$EXP/hybrid/codesign/s1_batch4_rest.lock"
flock -n 9 || { echo "$(date -u): S1 rest-batch driver already running, exiting." >> "$LOG"; exit 2; }
CANDS="cd2_p_a43b7_l513_nw cd2_p_a3b7_l513_nw cd2_p_a61b1_l513_nw cd2_p_a11b7_l311_nw cd2_p_a11b3_l311_nw cd2_p_a3b1_l311_nw cd2_p_a53b1_l311_nw cd2_p_a53b2_l311_nw cd2_p_a61b1_l311_nw cd2_p_a9b1_l311_nw"
{
echo "=== S1 rest-batch start $(date -u) ==="
for c in $CANDS; do
  if [ -f "$S1/$c/s1_result.json" ]; then echo "SKIP $c (already done)"; continue; fi
  echo "=== S1 $c ==="
  mkdir -p "$S1/$c"
  nice -n 19 python3 $EXP/fast_battery/src/s1_screen.py "$c" "$S1/$c" 2>&1 | tail -4
  rc=${PIPESTATUS[0]}
  echo "--- $c done rc=$rc $(date -u) ---"
done
echo S1_REST_ALLDONE
} >> "$LOG" 2>&1
