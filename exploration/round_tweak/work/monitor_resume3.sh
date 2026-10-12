#!/bin/bash
# Fresh bounded auto-relaunch monitor for mix-tweak-sweep (registry id: mix-tweak-sweep).
# Installed by the vm-boot-recovery resume agent after the 582d6dea reboot,
# REPLACING the pre-reboot monitor_sweep.sh whose MAX_RELAUNCH=3 budget was
# consumed by the sweep.py:459 arity crash (fresh budget: relaunches=0).
# Job: hourly registry heartbeat while sweep.py is alive; on death, classify
# from log lines appended AFTER this monitor started:
#   (a) "SWEEP COMPLETE"            -> mark done, exit 0
#   (b) traceback in the new lines  -> crash-loop guard: mark done with a
#       "needs attention in RISC-V mix chat" note, NO relaunch, exit 1
#   (c) otherwise (env/reboot class)-> relaunch, bounded by a FRESH
#       MAX_RELAUNCH=3 budget; on exhaustion mark done with attention note.
# The pre-reboot arity crash (ValueError: too many values to unpack in the
# boosts loop) is now guarded inside sweep.py itself (BOOST-ERROR path), so
# it can no longer kill the driver; the guard here covers the S2
# TimeoutExpired and any other escaping traceback.
# A VM reboot kills this monitor too; the 30-min vm-boot-recovery cron then
# re-dispatches a resume agent from the registry entry, which reinstalls it.
set -u

RT=~/workspace/mix/exploration/round_tweak
cd "$RT" || exit 1
WORK="$RT/work"
PIDFILE="$WORK/sweep.pid"
MLOG="$WORK/monitor_resume3.log"
REG=~/workspace/system/bin/workreg.py
ID=mix-tweak-sweep
MAX_RELAUNCH=3
relaunches=0

say() { echo "[monitor3 $(date -u +%FT%TZ)] $*" >> "$MLOG"; }
note_done() { "$REG" done --id "$ID" --note "$1" >> "$MLOG" 2>&1; }
note_rs()   { "$REG" resuming --id "$ID" --note "$1" >> "$MLOG" 2>&1; }

# PIDs of the real sweep.py driver: exact argv "python3 sweep.py"
# (excludes shells whose cmdline merely contains that string) and cwd == RT.
sweep_pids() {
    local p d cl
    for p in $(pgrep -f "[p]ython3 sweep.py" 2>/dev/null); do
        cl=$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null) || continue
        [ "$cl" = "python3 sweep.py " ] || continue
        d=$(readlink "/proc/$p/cwd" 2>/dev/null) || continue
        [ "$d" = "$RT" ] && echo "$p"
    done
}
sweep_alive() { [ -n "$(sweep_pids)" ]; }

launch() {
    setsid nohup python3 sweep.py >> "$WORK/sweep_resume.log" 2>&1 < /dev/null &
    disown
    sleep 30
    local pids
    pids=$(sweep_pids)
    if [ -n "$pids" ]; then
        echo "$pids" | head -1 > "$PIDFILE"
        say "launched sweep.py pid(s): $pids"
        return 0
    fi
    say "ERROR: launch did not produce a live sweep.py"
    return 1
}

# Only classify log lines appended after this monitor started, so the
# pre-reboot tracebacks already in the log can't false-trigger the guard.
LOG_START_LINE=$(wc -l < "$WORK/sweep_resume.log" 2>/dev/null || echo 0)
newlog() { tail -n +"$((LOG_START_LINE + 1))" "$WORK/sweep_resume.log" 2>/dev/null; }

sweep_pids | head -1 > "$PIDFILE"
say "monitor3 started (fresh relaunch budget $MAX_RELAUNCH); live sweep pid(s): $(sweep_pids | tr '\n' ' '); log starts at line $LOG_START_LINE"
"$REG" heartbeat --id "$ID" >> "$MLOG" 2>&1

while true; do
    sleep 3600
    if sweep_alive; then
        # light wedged-process check: no log progress in 3h while alive
        if [ -n "$(find "$WORK/sweep_resume.log" -mmin +180 2>/dev/null)" ]; then
            say "WARN: sweep alive but no log progress in 3h (pid $(sweep_pids | tr '\n' ' '))"
            note_rs "sweep alive (pid $(sweep_pids | tr '\n' ' ')) but no log progress in 3h — possibly wedged; needs a look"
        else
            "$REG" heartbeat --id "$ID" >> "$MLOG" 2>&1
            say "alive (pid $(sweep_pids | tr '\n' ' ')); heartbeat sent"
        fi
        continue
    fi

    # sweep is dead: classify from post-install log lines only
    say "sweep.py not alive; classifying from log lines after $LOG_START_LINE"
    if newlog | grep -q "SWEEP COMPLETE"; then
        line=$(newlog | grep "SWEEP COMPLETE" | tail -1)
        say "terminal completion detected: $line"
        note_done "sweep terminally complete: $line"
        say "marked done; monitor exiting"
        exit 0
    fi
    if newlog | grep -qi "traceback"; then
        tbline=$(newlog | grep -i -A3 "traceback" | tail -4 | tr '\n' ' ' | cut -c1-200)
        say "sweep died with a traceback; NOT auto-relaunching (crash-loop guard)"
        note_done "sweep.py died with traceback at $(date -u +%FT%TZ) ($tbline); not relaunched (crash-loop guard; pre-reboot arity crash consumed old budget); needs attention in RISC-V mix chat"
        say "marked done with attention note; monitor exiting"
        exit 1
    fi
    relaunches=$((relaunches + 1))
    if [ "$relaunches" -gt "$MAX_RELAUNCH" ]; then
        say "relaunch budget ($MAX_RELAUNCH) exhausted; flagging and exiting"
        note_done "sweep.py dead; relaunch budget ($MAX_RELAUNCH) exhausted; needs attention in RISC-V mix chat"
        exit 1
    fi
    say "sweep dead (reboot/environment class); relaunch attempt $relaunches/$MAX_RELAUNCH"
    if launch; then
        note_rs "sweep.py died (env/reboot class); relaunched pid $(cat "$PIDFILE") at $(date -u +%FT%TZ) (attempt $relaunches/$MAX_RELAUNCH fresh budget)"
    else
        note_done "sweep.py died; relaunch attempt $relaunches FAILED to produce a live process — needs attention in RISC-V mix chat"
        exit 1
    fi
done
