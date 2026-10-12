#!/bin/bash
# Batch-29 pre-pilot (12 draws, 0xB291) -> pilot (80 draws, 0xB292) chain.
# Pre-registered rule: pilot runs regardless of the pre-pilot outcome.
# Backoff gate uses the cleared-flag pattern (single gate, no re-check).
set -u
cd /home/hatch/workspace/mix/exploration/hybrid/batch29
cleared=0
for i in $(seq 1 720); do
  if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1
    break
  fi
  sleep 60
done
if [ "$cleared" -eq 0 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >&2
  exit 9
fi
echo "PRE-PILOT start $(date -u +%FT%TZ)"
nice -n 19 python3 hyb_b29_screen.py b29local 12 0xB291 pre_pilot_keeps.jsonl > pre_pilot.log 2>&1
rc1=$?
echo "PRE-PILOT done rc=$rc1 $(date -u +%FT%TZ)"
tail -3 pre_pilot.log
echo "PILOT start $(date -u +%FT%TZ)"
nice -n 19 python3 hyb_b29_screen.py b29local 80 0xB292 pilot_keeps.jsonl > pilot.log 2>&1
rc2=$?
echo "PILOT done rc=$rc2 $(date -u +%FT%TZ)"
tail -3 pilot.log
echo "b29 screen chain complete: pre-pilot rc=$rc1 pilot rc=$rc2"
