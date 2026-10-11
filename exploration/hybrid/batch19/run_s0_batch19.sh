#!/bin/bash
# Batch-19 S0 driver: sequential s0_delay.py runs (no-dretime flow), checkpointed.
# Usage: run_s0_batch19.sh <cand> [<cand> ...]
export TMPDIR=~/workspace/tmp
mkdir -p ~/workspace/tmp
EXP=~/workspace/mix/exploration
S0=$EXP/hybrid/batch19/s0_results
mkdir -p "$S0"
for c in "$@"; do
  if [ -f "$S0/$c/s0_result.json" ]; then echo "SKIP $c (already done)"; continue; fi
  echo "=== S0 $c ==="
  nice -n 19 python3 $EXP/fast_battery/src/s0_delay.py "$c" "$S0/$c" 2>&1 | tail -3
done
echo ALLDONE
