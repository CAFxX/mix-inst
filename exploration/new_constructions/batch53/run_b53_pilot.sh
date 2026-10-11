#!/bin/bash
# Batch-53 pilot: backoff-gated calibration + 2x40-draw triage.
# Pre-registered in DESIGN.md "Pilot wiring": pre-pilot fired the
# near-miss rule (hetMA5 0/6, min z=14.5 < 100) -> PILOT (2x40 draws):
# hetMA5 seed 0xB533, muxS5d seed 0xB534.
# Standing orders: heavy compute waits for load-shed.sh backoff exit 0;
# launched under setsid (agentwork-launch execs -> session teardown would
# SIGTERM the worker otherwise; batch-43/batch-49-mining precedent).
cd /home/hatch/workspace/mix/exploration/new_constructions/batch53 || exit 1
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
# NOTE 2026-10-11: no second backoff re-check after the loop. The earlier
# double-gate (re-check after a successful break) spuriously BACKOFF-FAILed
# twice (b50 pre-pilot, b53 pilot) on a load transient between the break and
# the re-check; the cleared flag is the single source of truth and the 12h
# deadline still fails loudly via the cleared==0 branch.
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running calibration" >> "$LOG"
python3 t6_b53_screen.py calibrate > pilot_calibrate.log 2>&1
rc=$?
echo "CALIBRATION exit=$rc" >> "$LOG"
cat pilot_calibrate.log >> "$LOG"
if [ $rc -ne 0 ]; then echo "CALIB-FAIL" >> "$LOG"; exit 5; fi
rm -f pilot_keeps.jsonl
python3 t6_b53_screen.py hetMA5 40 0xB533 pilot_keeps.jsonl >> "$LOG" 2>&1
echo "hetMA5 exit=$?" >> "$LOG"
python3 t6_b53_screen.py muxS5d 40 0xB534 pilot_keeps.jsonl >> "$LOG" 2>&1
echo "muxS5d exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) PILOT COMPLETE" >> "$LOG"
