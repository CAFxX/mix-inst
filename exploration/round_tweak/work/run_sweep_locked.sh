#!/bin/bash
# Launch the sweep driver holding a non-blocking flock on sweep.lock for the
# WHOLE driver lifetime (flock forks/execs python3 and waits, so the lock is
# released only when sweep.py exits or the VM dies). A duplicate invocation of
# this script exits 1 instead of racing the work dir.
set -u
RT=/home/hatch/workspace/mix/exploration/round_tweak
WORK="$RT/work"
LOG="$WORK/sweep_resume.log"
cd "$RT" || exit 1
# non-blocking: exit 1 if another driver holds the lock
exec flock -n "$WORK/sweep.lock" --command "python3 sweep.py" >> "$LOG" 2>&1
