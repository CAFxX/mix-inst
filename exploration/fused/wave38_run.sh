#!/bin/bash
# Wave-38 queue runner: wait for load backoff to clear, then calibrate
# (fail-loud) and run the 120-draw exact-DIFF screen. Detached; survives
# supervisor death. Checkpoint: keeps JSONL is appended per-try by the
# screen script itself, so a mid-run death loses nothing.
set -u
cd /home/hatch/workspace/mix/exploration/fused || exit 1
LOG=wave38_screen.log
echo "[wave38-run] started $(date -u +%FT%TZ) pid=$$" >> "$LOG"
for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "[wave38-run] backoff CLEAR after ${i} polls $(date -u +%FT%TZ)" >> "$LOG"
    break
  fi
  if [ "$i" = 720 ]; then
    echo "[wave38-run] LOUD: backoff never cleared in 12h; exiting" >> "$LOG"
    exit 1
  fi
  sleep 60
done
python3 -u wave38_screen.py calibrate >> "$LOG" 2>&1 || {
  echo "[wave38-run] LOUD: calibration FAILED; screen NOT launched" >> "$LOG"
  exit 1
}
python3 -u wave38_screen.py screen 120 0x3838 wave38_keeps.jsonl >> "$LOG" 2>&1
rc=$?
echo "[wave38-run] screen rc=$rc done $(date -u +%FT%TZ)" >> "$LOG"
touch wave38_SCREEN_DONE.txt
exit $rc
