#!/bin/bash
# Track 6 batch-32 S0 retry loop (incarnation I, 2026-10-10).
# Polls the load-backoff gate every 120s; when clear, runs 4x S0 (nice-19,
# sequential) and writes s0_b32/DONE. Light poller only -- heavy work runs
# only after the gate clears.
NC=/home/hatch/workspace/mix/exploration/new_constructions
FB=/home/hatch/workspace/mix/exploration/fast_battery/candidates
RS=/home/hatch/workspace/mix/exploration/run_synth.py
mkdir -p "$NC/s0_b32"
while true; do
  if "$HOME/workspace/system/bin/load-shed.sh" backoff >/dev/null 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear -- running batch-32 S0" >> "$NC/s0_b32/retry.log"
    for n in t6_lane3b t6_lane4a t6_sand5a t6_sand5b t6_sand4a t6_skip4a t6_skip5a; do
      if [ ! -f "$NC/s0_b32/$n/s0_result.json" ]; then
        echo "$(date -u +%FT%TZ) S0 start $n" >> "$NC/s0_b32/retry.log"
        nice -n 19 python3 "$RS" "$FB/$n/rtl.v" "$n" "$NC/s0_b32/$n" >> "$NC/s0_b32/retry.log" 2>&1
        echo "$(date -u +%FT%TZ) S0 done $n rc=$?" >> "$NC/s0_b32/retry.log"
      fi
    done
    echo "$(date -u +%FT%TZ) ALL S0 DONE" > "$NC/s0_b32/DONE"
    echo "$(date -u +%FT%TZ) ALL S0 DONE" >> "$NC/s0_b32/retry.log"
    exit 0
  fi
  sleep 120
done
