#!/bin/bash
# Monitor the resumed round_tweak sweep driver (PID detached via setsid).
# - heartbeat the work-registry entry hourly while the driver is alive
# - mark done when the log shows SWEEP COMPLETE (one-line summary note)
# - mark done as error if the driver exits without completing (user attention needed)
# Killed by a VM reboot; the vm-boot-recovery cron re-dispatches a fresh resume
# because the entry stays 'active' until marked done here.
set -u
WORK=/home/hatch/workspace/mix/exploration/round_tweak/work
LOG=$WORK/sweep_resume.log
ID=mix-tweak-sweep
WORKREG=/home/hatch/workspace/system/bin/workreg.py

drvpid() { pgrep -f '^python3 sweep\.py$' 2>/dev/null | head -1; }

LASTHB=$(date +%s)
while true; do
    sleep 600
    now=$(date +%s)
    if [ $((now - LASTHB)) -ge 3600 ]; then
        $WORKREG heartbeat --id "$ID" >/dev/null 2>&1
        LASTHB=$now
    fi
    if tail -20 "$LOG" 2>/dev/null | grep -q "SWEEP COMPLETE"; then
        summary=$(grep "SWEEP COMPLETE" "$LOG" | tail -1 | cut -c1-300)
        $WORKREG done --id "$ID" --note "$summary"
        exit 0
    fi
    if [ -z "$(drvpid)" ]; then
        taillog=$(tail -3 "$LOG" 2>/dev/null | tr '\n' ' ' | cut -c1-240)
        $WORKREG done --id "$ID" --note "sweep driver exited without SWEEP COMPLETE; last log: $taillog"
        exit 0
    fi
done
