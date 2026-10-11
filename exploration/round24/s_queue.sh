#!/bin/bash
# Round 24 detached stage queue: rtlcheck -> s0 -> s1 -> s2 (S1 survivors only).
# Usage: setsid nohup bash s_queue.sh > s_queue.log 2>&1 < /dev/null &
# Lockfile guard: only one instance. Resume-safe via progress.log done-marks.
# Each stage script is also independently resume-safe.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
R24=$EXP/round24
LOCK=$R24/s_queue.lock
exec 9>"$LOCK"
flock -n 9 || { echo "[s_queue] another instance holds the lock, exiting"; exit 0; }

log() { echo "$(date -u +%FT%TZ) $1" >> $R24/progress.log; echo "$(date -u +%FT%TZ) $1"; }

log "=== S_QUEUE start: rtlcheck -> s0 -> s1 -> s2 ==="

bash $R24/run_stages.sh rtlcheck || log "QUEUE_WARN rtlcheck stage exited nonzero"
bash $R24/run_stages.sh s0 || log "QUEUE_WARN s0 stage exited nonzero"
bash $R24/run_stages.sh s1 || log "QUEUE_WARN s1 stage exited nonzero"

# S2 only on S1 CAL_PASS survivors (verdict read from s1_result.json at record time)
grep "S1_DONE" $R24/progress.log | grep "verdict=CAL_PASS" | awk '{print $3}' > $R24/CANDS_S2.txt
NS2=$(wc -l < $R24/CANDS_S2.txt)
log "S2 shortlist: $NS2 survivors"
if [ "$NS2" -gt 0 ]; then
  R24_CANDS=$R24/CANDS_S2.txt bash $R24/run_stages.sh s2 || log "QUEUE_WARN s2 stage exited nonzero"
fi

log "=== S_QUEUE complete ==="
