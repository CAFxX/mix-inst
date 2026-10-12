#!/bin/bash
# track-6 xorh5 widening: chained staged battery for the 13 S0-eligible ranks.
# Order: frontier-dominators first (18,16,9,5), then the rest by rank.
set -u
XH=/home/hatch/workspace/mix/exploration/new_constructions/xorh5
FB=/home/hatch/workspace/mix/exploration/fast_battery
CHAIN=$XH/battery_chain_wide.log
: > "$CHAIN"
for c in t6_xorh5_18 t6_xorh5_16 t6_xorh5_9 t6_xorh5_5 t6_xorh5_4 t6_xorh5_7 t6_xorh5_8 t6_xorh5_10 t6_xorh5_11 t6_xorh5_12 t6_xorh5_14 t6_xorh5_15 t6_xorh5_17; do
  echo "=== CHAIN battery $c START $(date -u +%FT%TZ)" >> "$CHAIN"
  nice -n 10 bash "$FB/run_fast_battery.sh" "$c" 1 >> "$CHAIN" 2>&1
  rc=$?
  echo "=== CHAIN battery $c rc=$rc END $(date -u +%FT%TZ)" >> "$CHAIN"
  echo "[$(date -u +%FT%TZ)] battery $c rc=$rc (0=pass,2=killed,1=infra)" >> "$XH/heartbeat.txt"
done
echo "=== CHAIN WIDE ALL DONE $(date -u +%FT%TZ)" >> "$CHAIN"
