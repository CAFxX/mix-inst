#!/bin/bash
# Round 10 battery queue: 2 parallel lanes over the candidate list.
# Usage: run_queue10.sh
# Skips candidates flagged S0-FAIL in round10/s0_table.txt.
set -u
EXP=/home/hatch/workspace/mix/exploration
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
CANDS="r10_feist6_rot0211_nw r10_feist6_rot0313_nw r10_feist6_rot0317_nw r10_feist6_rot0411_nw r10_feist6_rot0307_nw r10_feist6_rot0511_nw r10_feist6_rot311 r10_feist5_s1_lin2_nw r10_feist5_s1_2sbox_nw r10_feist5_rot311 r10_feist6_rot311_ksalt_nw r10_feist6_rot311_ksrot_nw r10_feist6_altrot311_713_nw"
PROG="$EXP/round10/progress.log"
: > "$PROG"
run_one() {
  CAND="$1"
  if grep -q "^S0-FAIL $CAND" "$EXP/round10/s0_table.txt" 2>/dev/null; then
    echo "=== [R10] $CAND SKIPPED (S0-FAIL)" >> "$PROG"
    return 0
  fi
  t0=$(date +%s)
  echo "=== [R10] $CAND started $(date -u +%FT%TZ)" >> "$PROG"
  bash "$EXP/fast_battery/run_fast_battery.sh" "$CAND" > "$EXP/round10/battery_${CAND}.log" 2>&1
  rc=$?
  dt=$(( $(date +%s) - t0 ))
  echo "=== [R10] $CAND rc=$rc wall=${dt}s" >> "$PROG"
}
export -f run_one
export EXP PROG
echo "$CANDS" | tr ' ' '\n' | xargs -P 2 -I{} bash -c 'run_one {}'
echo "=== [R10] QUEUE DONE" >> "$PROG"
