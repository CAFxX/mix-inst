#!/bin/bash
# Batch-56 pilot: backoff-gated calibration + 80 ANDN + 80 OAAND + 24
# AND3-control draws (fisher-matched KEEP bar), pre-registered by
# DESIGN.md. Adjudicate on "PILOT COMPLETE" per the pre-registered rules:
# >=1 prize-arm fisher-KEEP -> bundle -> S0 (<19.3u strict) -> S1
# fail-fast -> staged battery -> Q1; control keeps -> bundle + S0 only
# (no battery on the O97-closed AND3 axis); 0/160 prize-arm keeps with
# calibration clean -> CLOSE the AND-form-variant axis at the triage
# level (O-entry).
# Cleared-flag backoff pattern (AGENTS.md lesson -- never re-add a
# post-loop re-check). Launched under setsid (batch-43 precedent).
cd /home/hatch/workspace/mix/exploration/new_constructions/batch56 || exit 1
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
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running calibration" >> "$LOG"
python3 t6_b56_screen.py calibrate > pilot_calibrate.log 2>&1
rc=$?
echo "CALIBRATION exit=$rc" >> "$LOG"
cat pilot_calibrate.log >> "$LOG"
if [ $rc -ne 0 ]; then echo "CALIB-FAIL" >> "$LOG"; exit 5; fi
rm -f pilot_keeps.jsonl
python3 t6_b56_screen.py hetMA5N 80 0xB564 pilot_keeps.jsonl >> "$LOG" 2>&1
echo "hetMA5N exit=$?" >> "$LOG"
python3 t6_b56_screen.py hetMOA5 80 0xB565 pilot_keeps.jsonl >> "$LOG" 2>&1
echo "hetMOA5 exit=$?" >> "$LOG"
python3 t6_b56_screen.py hetMA5p1f 24 0xB566 pilot_keeps.jsonl >> "$LOG" 2>&1
echo "hetMA5p1f exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) PILOT COMPLETE" >> "$LOG"
