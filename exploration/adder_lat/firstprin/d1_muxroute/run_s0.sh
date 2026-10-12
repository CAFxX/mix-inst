#!/bin/bash
# S0-measure every D1 ladder variant + 2-stage. Synth under nice -n 19 per task.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
RS=~/workspace/mix/exploration/run_synth.py
declare -A TOPS=( [A]=d1_A [B]=d1_B [C]=d1_C [D]=d1_D [E]=d1_E [F]=d1_F [G]=d1_G [H]=d1_H [2stage]=d1_2stage [2stage_H]=d1_2stage_H )
: > "$HERE/s0_results.txt"
for v in A B C D E F G H 2stage 2stage_H; do
  top=${TOPS[$v]}
  echo "=== $v ($top) ==="
  nice -n 19 python3 "$RS" "$HERE/d1_$v.v" "$top" "$HERE/s0_$v" 2>&1 | tail -3 | tee -a "$HERE/s0_results.txt"
done
echo "=== ALL DONE ===" >> "$HERE/s0_results.txt"
