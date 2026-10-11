#!/bin/bash
# Hourly heartbeat keeper for the mix-tweak-sweep work-registry entry.
# Run this hourly (e.g. from cron) while the sweep driver is expected to run.
# Heartbeats the registry iff a live sweep.py driver exists; exits 1 if the
# driver is dead (so the scheduler can notice and relaunch).
set -u
if pgrep -f "sweep\.py" >/dev/null 2>&1; then
    exec ~/workspace/system/bin/workreg.py heartbeat --id mix-tweak-sweep
else
    echo "supervise_resume: no sweep.py process alive; NOT heartbeating mix-tweak-sweep" >&2
    exit 1
fi
