#!/bin/bash
# Supervisor for the post-reboot (9de86157) mix-tweak-sweep resume.
# Launched detached by the vm-boot-recovery resume subagent.
# Every hour: if sweep.py is alive -> heartbeat the work-registry entry.
# If sweep.py is gone:
#   - log shows SWEEP COMPLETE -> mark the entry done (with outcome note) and exit 0.
#   - otherwise (crash) -> log loudly and exit 3 WITHOUT heartbeating, so the
#     registry entry goes stale and the vm-boot-recovery cron flags it.
# Dies with the VM on reboot; recovery re-dispatches.
RTW=/home/hatch/workspace/mix/exploration/round_tweak
WORK=$RTW/work
LOG=$WORK/sweep_resume.log
HBLOG=$WORK/heartbeat_resume.log
WR=/home/hatch/workspace/system/bin/workreg.py

note() { date -u +"[%Y-%m-%dT%H:%M:%SZ] $*" >> "$HBLOG"; }

while :; do
  sleep 3600
  # bracket trick: this script's own cmdline must not match the pattern
  if pgrep -f 'python3 [s]weep\.py' >/dev/null; then
    $WR heartbeat --id mix-tweak-sweep >> "$HBLOG" 2>&1
    note "heartbeat sent (sweep alive)"
  else
    if grep -q 'SWEEP COMPLETE' "$LOG" 2>/dev/null; then
      summary=$(grep 'SWEEP COMPLETE' "$LOG" | tail -1)
      winners=$(tr '\n' ' ' < "$WORK/winners.txt" 2>/dev/null)
      $WR done --id mix-tweak-sweep \
        --note "sweep complete: $summary winners: ${winners:-none}" \
        >> "$HBLOG" 2>&1
      note "sweep complete; entry marked done"
      exit 0
    else
      note "ALERT: sweep.py process gone and no SWEEP COMPLETE in log; NOT heartbeating (entry will go stale)"
      tail -20 "$LOG" >> "$HBLOG" 2>&1
      exit 3
    fi
  fi
done
