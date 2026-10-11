#!/bin/bash
# Round 9 resume queue (7 remaining). Fully detached via setsid.
set -u
EXP=/home/hatch/workspace/mix/exploration
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
CANDS="r9_feist6_rot0719_nw r9_feist6_ksalt_nw r9_feist6_ksrot_nw r9_feist6_nork r9_feist6_altrot_nw r9_feist7_rot517_nw r9_feist7_s1_lin2_nw"
PROG="$EXP/round9/progress.log"
run_one() {
  CAND="$1"
  t0=$(date +%s)
  echo "=== [R9b] $CAND started $(date -u +%FT%TZ)" >> "$PROG"
  bash "$EXP/fast_battery/run_fast_battery.sh" "$CAND" > "$EXP/round9/battery_${CAND}.log" 2>&1
  rc=$?
  dt=$(( $(date +%s) - t0 ))
  echo "=== [R9b] $CAND rc=$rc wall=${dt}s" >> "$PROG"
}
export -f run_one
export EXP PROG
echo "$CANDS" | tr ' ' '\n' | xargs -P 2 -I{} bash -c 'run_one {}'
echo "=== [R9b] QUEUE DONE" >> "$PROG"
