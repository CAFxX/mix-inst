#!/bin/bash
# One-shot adoption check for mix-tweak-sweep (pid adopted: see STATE file).
# Exits: 0 = healthy/running, 10 = DRIVER GONE, 11 = SWEEP COMPLETE.
set -u
RT="$HOME/workspace/mix/exploration/round_tweak"
LOG="$RT/work/sweep_resume.log"
RES="$RT/work/sweep_results.json"
STATE="$RT/work/monitor_state"
WORKREG="$HOME/workspace/system/bin/workreg.py"

touch "$STATE"
LAST_HB=$(grep -oP '^last_hb=\K[0-9]+' "$STATE" 2>/dev/null || echo 0)
NOW=$(date +%s)

# 1) sweep complete?
if tail -n 20 "$LOG" 2>/dev/null | grep -q 'SWEEP COMPLETE'; then
  echo "SWEEP_COMPLETE detected in log tail"
  exit 11
fi

# 2) driver alive? (the setsid launcher shell also carries 'sweep.py' in its
#    cmdline, so anchor to the python process itself)
NPIDS=$(pgrep -f '^python3 sweep\.py' | tr '\n' ' ')
if [ -z "$NPIDS" ]; then
  echo "DRIVER_GONE: no 'python3 sweep.py' process alive"
  echo "--- log tail ---"
  tail -n 30 "$LOG" 2>/dev/null
  echo "--- log mtime ---"
  stat -c '%y %n' "$LOG" "$RES" 2>/dev/null
  exit 10
fi
N=$(echo "$NPIDS" | wc -w)
if [ "$N" -gt 1 ]; then
  echo "WARNING: $N sweep.py instances alive: $NPIDS (expected 1)"
fi

# 3) progress signals
RES_MTIME=$(stat -c '%y' "$RES" 2>/dev/null || echo unknown)
LAST_LOG=$(tail -n 1 "$LOG" 2>/dev/null)
NPROBED=$(python3 -c "import json;print(len(json.load(open('$RES'))))" 2>/dev/null || echo ?)
echo "alive=$NPIDS probed=$NPROBED res_mtime='$RES_MTIME' last_log='$LAST_LOG'"

# 4) hourly heartbeat
if [ $(( NOW - LAST_HB )) -ge 3600 ]; then
  "$WORKREG" heartbeat --id mix-tweak-sweep && \
    sed -i '/^last_hb=/d' "$STATE" && echo "last_hb=$NOW" >> "$STATE" && \
    echo "heartbeat sent"
fi
exit 0
