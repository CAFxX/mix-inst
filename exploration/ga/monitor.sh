#!/bin/bash
# Monitor for the mix GA evolution driver (PID-free: re-discovers by pattern).
# Hourly: heartbeat workreg, log driver liveness.
# If driver dead: check run.log tail for failure class; if terminal
#   ("48h wall budget exhausted" / STOP file) -> mark done + exit;
#   otherwise relaunch with --resume and heartbeat.
# Runs until the 48h budget from checkpoint t0 (2026-10-03T16:11Z) plus margin.

LOG=$HOME/workspace/mix/exploration/ga/monitor.log
WORKDIR=$HOME/workspace/mix/exploration
DEADLINE_S=2007686400   # ~2026-10-05T22:00Z, margin past 48h budget end 2026-10-05T16:11Z

mkdir -p "$WORKDIR/ga"
touch "$LOG"
echo "$(date -u +%FT%TZ) monitor starting" >> "$LOG"

while [ "$(date +%s)" -lt "$DEADLINE_S" ]; do
  PID=$(pgrep -f "^python3 ga/ga.py --resume" | head -1)
  if [ -z "$PID" ]; then
    TAIL=$(tail -5 "$WORKDIR/ga/run.log")
    echo "$(date -u +%FT%TZ) driver DEAD; run.log tail:" >> "$LOG"
    echo "$TAIL" >> "$LOG"
    if echo "$TAIL" | grep -q "48h wall budget exhausted"; then
      OUTCOME=$(echo "$TAIL" | tr '\n' ' ' | cut -c1-200)
      $HOME/workspace/system/bin/workreg.py done --id mix-ga-evolution --note "48h budget exhausted. $OUTCOME"
      echo "$(date -u +%FT%TZ) terminal exit (budget); marked done; monitor exiting" >> "$LOG"
      exit 0
    fi
    cd "$WORKDIR" && setsid nohup python3 ga/ga.py --resume >> ga/run.log 2>&1 < /dev/null &
    sleep 45
    PID2=$(pgrep -f "^python3 ga/ga.py --resume" | head -1)
    echo "$(date -u +%FT%TZ) relaunched, PID=${PID2:-FAILED}" >> "$LOG"
    $HOME/workspace/system/bin/workreg.py resuming --id mix-ga-evolution --note "driver died, relaunched PID ${PID2:-?} by monitor" >> "$LOG" 2>&1
  else
    ELAPSED=$(ps -o etime= -p "$PID" | tr -d ' ')
    echo "$(date -u +%FT%TZ) alive pid=$PID etime=$ELAPSED" >> "$LOG"
    $HOME/workspace/system/bin/workreg.py heartbeat --id mix-ga-evolution >> "$LOG" 2>&1
  fi
  sleep 3600
done
echo "$(date -u +%FT%TZ) monitor deadline reached; exiting" >> "$LOG"
