#!/bin/bash
# track-6 xorh5 escalation: chained staged battery for cost-eligible candidates.
# Sequential (2-vCPU box): xcheck(S0a) -> S1 -> S2 -> S3 -> S4 per candidate.
# run_fast_battery.sh stops at first kill (rc=2); chain continues to next cand.
set -u
XH=/home/hatch/workspace/mix/exploration/new_constructions/xorh5
FB=/home/hatch/workspace/mix/exploration/fast_battery
CHAIN=$XH/battery_chain.log
: > "$CHAIN"
for c in t6_xorh5_0 t6_xorh5_1 t6_xorh5_2; do
  echo "=== CHAIN battery $c START $(date -u +%FT%TZ)" >> "$CHAIN"
  nice -n 10 bash "$FB/run_fast_battery.sh" "$c" 1 >> "$CHAIN" 2>&1
  rc=$?
  echo "=== CHAIN battery $c rc=$rc END $(date -u +%FT%TZ)" >> "$CHAIN"
  echo "[$(date -u +%FT%TZ)] battery $c rc=$rc (0=pass,2=killed,1=infra)" >> "$XH/heartbeat.txt"
done
echo "=== CHAIN ALL DONE $(date -u +%FT%TZ)" >> "$CHAIN"
