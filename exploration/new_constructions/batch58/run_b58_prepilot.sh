#!/bin/bash
# Batch-58 PRE-PILOT: muxD4f (4-stage pure-MUXD, MU5 frame) with
# fisher-matched triage. 12 draws, seed 0xB581. HARNESS CHECK ONLY.
# Pre-registered rules (DESIGN.md):
#   - calibration (3 gates) must PASS fail-loud or the pilot is BLOCKED;
#   - 0/12 keeps -> WEAK-SIGNAL flag, PILOT (80 draws, 0xB582) runs
#     regardless to confirm (pilot script: run_b58_pilot.sh, written
#     after pre-pilot adjudication);
#   - GATE-FAIL (keeps==n_try, kills==0) -> KILL LOUDLY, diagnose.
# Cleared-flag backoff pattern (AGENTS.md lesson). Launched under setsid.
cd /home/hatch/workspace/mix/exploration/new_constructions/batch58 || exit 1
LOG=prepilot.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > backoff_poll_prepilot.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter): $(head -c 200 backoff_poll_prepilot.out)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: calibrate (fail-loud)" >> "$LOG"
python3 t6_b58_screen.py calibrate >> "$LOG" 2>&1
rc=$?
echo "calibrate exit=$rc" >> "$LOG"
if [ "$rc" -ne 0 ]; then
  echo "CALIB-FAIL: pilot BLOCKED, diagnose" >> "$LOG"; exit 5
fi
echo "$(date -u +%FT%TZ) calibrate PASS: pre-pilot 12 draws seed 0xB581" >> "$LOG"
rm -f prepilot_keeps.jsonl
python3 t6_b58_screen.py muxD4f 12 0xB581 prepilot_keeps.jsonl >> "$LOG" 2>&1
rc=$?
echo "pre-pilot exit=$rc keeps=$(wc -l < prepilot_keeps.jsonl 2>/dev/null || echo 0)" >> "$LOG"
echo "$(date -u +%FT%TZ) PRE-PILOT COMPLETE" >> "$LOG"
