#!/bin/bash
# Backoff-aware S0 runner for boolfunc_c.
# Waits for load-shed backoff to clear, then runs run_synth.py under nice -n 19.
EXP=/home/hatch/workspace/mix/exploration
AL=$EXP/adder_lat
BF=$AL/boolfunc
WORK=$BF/s0_work/boolfunc_c
LOG=$BF/s0_boolfunc_c.log
SHED=/home/hatch/workspace/system/bin/load-shed.sh

mkdir -p "$WORK"
echo "[$(date -u +%FT%TZ)] S0 runner started (backoff-gated)" >> "$LOG"

# cleared-flag pattern: fail-loud only if never cleared
cleared=0
for i in $(seq 1 180); do
    if "$SHED" backoff >/dev/null 2>&1; then
        cleared=1
        echo "[$(date -u +%FT%TZ)] backoff clear after $i polls" >> "$LOG"
        break
    fi
    echo "[$(date -u +%FT%TZ)] backoff active (poll $i), sleeping 120s" >> "$LOG"
    sleep 120
done
if [ "$cleared" = "0" ]; then
    echo "[$(date -u +%FT%TZ)] BACKOFF-FAIL: load never cleared in 6h" >> "$LOG"
    exit 3
fi

t0=$(date +%s)
/usr/bin/nice -n 19 /usr/bin/python3 "$EXP/run_synth.py" "$BF/boolfunc_c.v" boolfunc_c "$WORK" >> "$LOG" 2>&1
rc=$?
t1=$(date +%s)
echo "[$(date -u +%FT%TZ)] synth done rc=$rc wall_s=$((t1-t0))" >> "$LOG"
grep -h "^RESULT" "$LOG" | tail -2
exit $rc
