#!/bin/bash
# Durable monitor for mix-tweak-sweep (registry id: mix-tweak-sweep).
# Installed by the vm-boot-recovery resume agent after the 818a0543 reboot.
# Job: hourly registry heartbeat while sweep.py is alive; on death, classify
# the failure from work/sweep_resume.log and either (a) mark done on
# "SWEEP COMPLETE", (b) relaunch (bounded) on reboot/environment death,
# or (c) flag for attention on a crash/traceback death. Never sits dead silently.
# A VM reboot kills this monitor too; the 30-min vm-boot-recovery cron then
# re-dispatches a resume agent from the registry entry, which reinstalls it.
set -u

RT=~/workspace/mix/exploration/round_tweak
cd "$RT" || exit 1
WORK="$RT/work"
PIDFILE="$WORK/sweep.pid"
MLOG="$WORK/monitor.log"
REG=~/workspace/system/bin/workreg.py
ID=mix-tweak-sweep
MAX_RELAUNCH=3
relaunches=0

say() { echo "[monitor $(date -u +%FT%TZ)] $*" >> "$MLOG"; }
note() { "$REG" resuming --id "$ID" --note "$1" >> "$MLOG" 2>&1; }

# Print PIDs of the real sweep.py driver: exact argv "python3 sweep.py"
# (excludes the bash wrapper whose cmdline merely contains that string)
# and cwd == this round_tweak dir.
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
    # Locked wrapper: holds flock on sweep.lock for the whole driver lifetime,
    # so a duplicate invocation exits 1 instead of racing the work dir.
    setsid nohup "$WORK/run_sweep_locked.sh" >> "$WORK/sweep_resume.log" 2>&1 < /dev/null &
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

# Record the currently-live PID(s) at install time, plus the log line count:
# sweep_resume.log is appended across reboots and already contains pre-reboot
# tracebacks, so crash classification must scan only post-install lines.
sweep_pids | head -1 > "$PIDFILE"
wc -l < "$WORK/sweep_resume.log" > "$WORK/monitor_line0"
say "monitor started; live sweep pid(s): $(sweep_pids | tr '\n' ' '); log line0=$(cat "$WORK/monitor_line0")"
"$REG" heartbeat --id "$ID" >> "$MLOG" 2>&1

while true; do
    sleep 3600
    if sweep_alive; then
        # light wedged-process check: no log progress in 3h while alive
        if [ -n "$(find "$WORK/sweep_resume.log" -mmin +180 2>/dev/null)" ]; then
            say "WARN: sweep alive but no log progress in 3h (pid $(sweep_pids | tr '\n' ' '))"
            note "sweep alive (pid $(sweep_pids | tr '\n' ' ')) but no log progress in 3h — possibly wedged; needs a look"
        else
            "$REG" heartbeat --id "$ID" >> "$MLOG" 2>&1
            say "alive (pid $(sweep_pids | tr '\n' ' ')); heartbeat sent"
        fi
        continue
    fi

    # sweep is dead: classify from the log tail
    say "sweep.py not alive; classifying from log"
    if tail -30 "$WORK/sweep_resume.log" | grep -q "SWEEP COMPLETE"; then
        line=$(grep "SWEEP COMPLETE" "$WORK/sweep_resume.log" | tail -1)
        say "terminal completion detected: $line"
        "$REG" done --id "$ID" --note "sweep terminally complete: $line" >> "$MLOG" 2>&1
        say "marked done; monitor exiting"
        exit 0
    fi
    if tail -n +"$(($(cat "$WORK/monitor_line0") + 1))" "$WORK/sweep_resume.log" | tail -40 | grep -qi "traceback"; then
        say "sweep died with a traceback; NOT auto-relaunching (crash-loop guard)"
        note "sweep.py died with traceback at $(date -u +%FT%TZ); not relaunched — needs attention in RISC-V mix chat"
        continue
    fi
    relaunches=$((relaunches + 1))
    if [ "$relaunches" -gt "$MAX_RELAUNCH" ]; then
        say "relaunch budget ($MAX_RELAUNCH) exhausted; flagging and exiting"
        note "sweep.py dead $MAX_RELAUNCH relaunches failed/exhausted; needs attention"
        exit 1
    fi
    say "sweep dead (reboot/environment class); relaunch attempt $relaunches/$MAX_RELAUNCH"
    if launch; then
        note "sweep.py died (env/reboot class); relaunched pid $(cat "$PIDFILE") at $(date -u +%FT%TZ) (attempt $relaunches)"
    else
        note "sweep.py died; relaunch attempt $relaunches FAILED to produce a live process — needs attention"
    fi
done
