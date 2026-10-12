#!/bin/bash
# Hourly heartbeat + liveness monitor for the resumed mix tweak sweep
# (mix-tweak-sweep, driver pid captured at launch). Launched detached via
# setsid; logs to work/monitor_heartbeat.log.
ID="mix-tweak-sweep"
DRIVER_PID=20928
WORK="$HOME/workspace/mix/exploration/round_tweak/work"
LOG="$WORK/monitor_heartbeat.log"
SWEEPLOG="$WORK/sweep_resume.log"
WORKREG="$HOME/workspace/system/bin/workreg.py"

stamp() { date -u +%FT%TZ; }

while true; do
  sleep 3600
  if kill -0 "$DRIVER_PID" 2>/dev/null; then
    "$WORKREG" heartbeat --id "$ID" >>"$LOG" 2>&1
    echo "$(stamp) heartbeat ok (driver $DRIVER_PID alive)" >>"$LOG"
  else
    if tail -50 "$SWEEPLOG" | grep -q "SWEEP COMPLETE"; then
      SUM=$(grep "SWEEP COMPLETE" "$SWEEPLOG" | tail -1 | cut -c1-160)
      "$WORKREG" done --id "$ID" --note "sweep finished: $SUM" >>"$LOG" 2>&1
      echo "$(stamp) sweep complete; entry marked done" >>"$LOG"
    else
      echo "$(stamp) ALERT: driver $DRIVER_PID exited WITHOUT 'SWEEP COMPLETE' (abnormal); heartbeats stopped so the entry will go stale and the recovery cron will flag it" >>"$LOG"
    fi
    exit 0
  fi
done
