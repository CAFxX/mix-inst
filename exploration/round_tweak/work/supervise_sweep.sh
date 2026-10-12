#!/bin/bash
# Adopting supervisor for mix-tweak-sweep (registry id: mix-tweak-sweep).
# Installed by the adoption worker (subagent 98416de3) after the first resume
# worker died on a runtime infra error (exec completion never delivered).
# Role: OBSERVE-ONLY supervisor. Never launches the driver (flock -n on
# sweep.lock guarantees a duplicate exits 1 anyway), never fights
# monitor_sweep.sh, which owns bounded relaunch (env/reboot class) and
# traceback crash-guarding.
#
# Does: every 15 min verify the single sweep.py instance (exact argv
# "python3 sweep.py" + cwd == round_tweak); hourly registry heartbeat ONLY
# while the driver is verified alive (liveness-gated); on "SWEEP COMPLETE"
# mark done; on a confirmed traceback death (two consecutive checks, to
# allow for manual intervention) mark lost with the reason and exit so we
# never loop forever on a crash-loop class. Crash-audit 2026-10-07: the old
# sweep.py:459 arity crash (boosts unpack) is now guarded in-code
# (diagnose/apply_boosts wrapped in try/except); the remaining known
# unguarded path is s2_run's TimeoutExpired (2400s) killing the whole driver.
# Dies with the VM; the 30-min vm-boot-recovery cron re-dispatches a resume
# agent from the registry entry if it is still active.
set -u

RT=~/workspace/mix/exploration/round_tweak
cd "$RT" || exit 1
WORK="$RT/work"
SLOG="$WORK/supervise.log"
REG=~/workspace/system/bin/workreg.py
ID=mix-tweak-sweep
LAST_HB=0
WEDGE_NOTED=0
CRASH_SEEN=0

say() { echo "[supervise $(date -u +%FT%TZ)] $*" >> "$SLOG"; }

sweep_pids() {
    local p d cl
    for p in $(pgrep -f "[p]ython3 sweep.py" 2>/dev/null); do
        cl=$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null) || continue
        [ "$cl" = "python3 sweep.py " ] || continue
        d=$(readlink "/proc/$p/cwd" 2>/dev/null) || continue
        [ "$d" = "$RT" ] && echo "$p"
    done
}

reg_status() { "$REG" get --id "$ID" 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])' 2>/dev/null; }

# Crash classification must scan only post-install log lines: sweep_resume.log
# is appended across reboots and already contains pre-reboot tracebacks.
wc -l < "$WORK/sweep_resume.log" > "$WORK/supervise_line0"
LINE0=$(cat "$WORK/supervise_line0")
say "supervisor started; live sweep pid(s): $(sweep_pids | tr '\n' ' '); log line0=$LINE0"

while true; do
    sleep 900
    case "$(reg_status)" in
        done|lost) say "registry entry already terminal; supervisor exiting"; exit 0 ;;
    esac

    pids=$(sweep_pids)
    now=$(date +%s)
    if [ -n "$pids" ]; then
        CRASH_SEEN=0
        if [ $((now - LAST_HB)) -ge 3600 ]; then
            if "$REG" heartbeat --id "$ID" >> "$SLOG" 2>&1; then
                say "heartbeat sent (alive: $(echo "$pids" | tr '\n' ' '))"
                LAST_HB=$now
                WEDGE_NOTED=0
            else
                say "WARN: heartbeat failed"
            fi
        fi
        if [ -n "$(find "$WORK/sweep_resume.log" -mmin +180 2>/dev/null)" ] && [ "$WEDGE_NOTED" = 0 ]; then
            say "WARN: sweep alive (pid $(echo "$pids" | tr '\n' ' ')) but no log progress in 3h — possibly wedged; noting once"
            "$REG" resuming --id "$ID" --note "sweep alive (pid $(echo "$pids" | tr '\n' ' ')) but no log progress in 3h — possibly wedged; needs a look" >> "$SLOG" 2>&1
            WEDGE_NOTED=1
        fi
        continue
    fi

    # sweep is dead: classify from post-install log lines only
    newlog=$(tail -n +"$((LINE0 + 1))" "$WORK/sweep_resume.log" 2>/dev/null)
    if echo "$newlog" | grep -q "SWEEP COMPLETE"; then
        line=$(echo "$newlog" | grep "SWEEP COMPLETE" | tail -1)
        say "terminal completion detected: $line"
        "$REG" done --id "$ID" --note "sweep terminally complete: $line" >> "$SLOG" 2>&1
        say "marked done; supervisor exiting"
        exit 0
    fi
    if echo "$newlog" | tail -80 | grep -qi "traceback"; then
        CRASH_SEEN=$((CRASH_SEEN + 1))
        say "traceback death detected (consecutive count $CRASH_SEEN); monitor_sweep.sh will not auto-relaunch (crash-loop guard)"
        if [ "$CRASH_SEEN" -ge 2 ]; then
            err=$(echo "$newlog" | grep -i "Error" | tail -1)
            say "traceback confirmed twice; marking lost: $err"
            "$REG" lost --id "$ID" --note "sweep.py died with traceback (crash-loop class; 2026-10-07 audit: the old sweep.py:459 arity crash is now guarded in-code; remaining known unguarded path is s2_run TimeoutExpired killing the driver); not auto-relaunched; needs the RISC-V mix chat. Last error: $err" >> "$SLOG" 2>&1
            say "marked lost; supervisor exiting"
            exit 0
        fi
        continue
    fi
    say "sweep dead, no traceback in post-install log (env/reboot class); monitor_sweep.sh owns bounded relaunch; observing"
done
