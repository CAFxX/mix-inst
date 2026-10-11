#!/bin/bash
# Batch-54 pilot: backoff-gated calibration + 80-draw hetMA5p1 schedule search.
# Pre-registered in DESIGN.md "Falsifier": pre-pilot fired the >=1-KEEP rule
# (1/12 KEEP, z=2.6, seed 0xB541) -> PILOT (80 draws, seed 0xB542).
# Cleared-flag backoff pattern (AGENTS.md lesson; the double-gate killed
# the b50 pre-pilot and b53 pilot wrappers spuriously -- never re-add a
# post-loop re-check).
# Standing orders: heavy compute waits for load-shed.sh backoff exit 0;
# launched under setsid (agentwork-launch execs -> session teardown would
# SIGTERM the worker otherwise; batch-43/batch-49-mining precedent).
cd /home/hatch/workspace/mix/exploration/new_constructions/batch54 || exit 1
LOG=pilot.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > backoff_poll.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter, now=$(date +%s)): $(head -c 200 backoff_poll.out)" >> "$LOG"
  sleep 300
done
# No second backoff re-check after the loop: the cleared flag is the
# single source of truth (b50/b53 double-gate deaths). The 12h deadline
# still fails loudly via the cleared==0 branch below.
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running calibration" >> "$LOG"
python3 t6_b54_screen.py calibrate > pilot_calibrate.log 2>&1
rc=$?
echo "CALIBRATION exit=$rc" >> "$LOG"
cat pilot_calibrate.log >> "$LOG"
if [ $rc -ne 0 ]; then echo "CALIB-FAIL" >> "$LOG"; exit 5; fi
rm -f pilot_keeps.jsonl
python3 t6_b54_screen.py hetMA5p1 80 0xB542 pilot_keeps.jsonl >> "$LOG" 2>&1
echo "hetMA5p1 exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) PILOT COMPLETE" >> "$LOG"
