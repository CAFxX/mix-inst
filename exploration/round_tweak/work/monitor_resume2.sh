#!/bin/bash
# monitor for mix-tweak-sweep resume after 2026-10-06 aef153be reboot.
# Installed by vm-boot-recovery run (the resume worker errored on a runtime
# transient after relaunching the driver). Heartbeats hourly; marks done when
# the sweep driver exits.
DRIVER_PID=15280
ID=mix-tweak-sweep
LOG=/home/hatch/workspace/mix/exploration/round_tweak/work/monitor_resume2.log
while kill -0 "$DRIVER_PID" 2>/dev/null; do
  sleep 3600
  /home/hatch/workspace/system/bin/workreg.py heartbeat --id "$ID" >>"$LOG" 2>&1
done
echo "$(date -u +%FT%TZ) driver $DRIVER_PID exited; see work/sweep_resume.log tail for verdict" >>"$LOG"
/home/hatch/workspace/system/bin/workreg.py done --id "$ID" --note "sweep driver exited $(date -u +%FT%TZ); verdict in work/sweep_resume.log tail" >>"$LOG" 2>&1
