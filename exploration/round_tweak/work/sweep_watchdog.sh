#!/bin/bash
# Watchdog for the mix tweaking sweep.
# Checks if sweep.py is alive; restarts it if dead; logs LOUDLY.
# Run from cron every 5 minutes, or manually.
# NEVER STOP SILENTLY — a dead sweep gets restarted and reported.

set -u
WORKDIR="/home/hatch/workspace/mix/exploration/round_tweak"
LOG="$WORKDIR/work/sweep_resume.log"
WATCHLOG="$WORKDIR/work/watchdog.log"

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

if pgrep -f "sweep\.py" > /dev/null 2>&1; then
    # Alive — nothing to do, just touch a heartbeat
    echo "$(timestamp) WATCHDOG: sweep.py alive" >> "$WATCHLOG"
    exit 0
fi

# DEAD — restart loudly
echo "$(timestamp) WATCHDOG: *** sweep.py DEAD — restarting ***" | tee -a "$WATCHLOG" >> "$LOG"
echo "$(timestamp) WATCHDOG: *** sweep.py DEAD — restarting ***" >&2

cd "$WORKDIR" || exit 1
nohup python3 sweep.py >> "$LOG" 2>&1 &
NEWPID=$!

sleep 3
if pgrep -f "sweep\.py" > /dev/null 2>&1; then
    echo "$(timestamp) WATCHDOG: restarted sweep.py (PID $NEWPID)" | tee -a "$WATCHLOG" >> "$LOG"
else
    # An exhausted sweep exits immediately with SWEEP COMPLETE (2026-10-09:
    # 1182/1182 specs probed, space empty). That is a clean completion, not a
    # failed restart — do not log RESTART FAILED.
    if tail -3 "$LOG" | grep -q "SWEEP COMPLETE"; then
        echo "$(timestamp) WATCHDOG: sweep.py finished (SWEEP COMPLETE) — spec space exhausted, awaiting new specs" | tee -a "$WATCHLOG" >> "$LOG"
        exit 0
    fi
    echo "$(timestamp) WATCHDOG: *** RESTART FAILED ***" | tee -a "$WATCHLOG" >> "$LOG" >&2
    exit 1
fi
