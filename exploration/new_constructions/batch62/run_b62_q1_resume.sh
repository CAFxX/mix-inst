#!/bin/bash
# Batch-62 Q1 resume (track-6): post-reboot continuation for the S4 survivors
# t6_b62_26 t6_b62_9 t6_b62_3 (battery S0a->S4 all PASS pre-reboot; the
# launcher was killed 2026-10-12T18:13Z right after printing
# "S4 survivors:", before its Q1 loop started).
# Usage: run_b62_q1_resume.sh <cand> [<cand> ...]
# Skips candidates with an existing q1_<cand>/q1_<cand>.json (already
# triaged on disk -- never re-run triaged candidates).
# Gate: cleared-flag backoff single gate (AGENTS.md lesson), nice -n 19.
# Launch: setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 \
#         --tag track6/b62-q1 -- bash run_b62_q1_resume.sh t6_b62_26 t6_b62_9 t6_b62_3
set -u
cd /home/hatch/workspace/mix/exploration/new_constructions/batch62 || exit 1
HB=heartbeat.txt
LOG=run_b62_q1.log
WORKREG=/home/hatch/workspace/system/bin/workreg.py
log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

if [ "$#" -lt 1 ]; then echo "usage: $0 <cand> [cand ...]"; exit 1; fi

deadline=$(( $(date +%s) + 43200 ))
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  sleep 60
done
if [ "$cleared" != 1 ]; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-62 Q1 resume for: $*"
touch "$HB"

sacz_of() {
  python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["sac_z5"])' "$1" 2>/dev/null
}

for CAND in "$@"; do
  if [ -f "q1_$CAND/q1_$CAND.json" ]; then
    sacz=$(sacz_of "q1_$CAND/q1_$CAND.json") || sacz="?"
    log "Q1 $CAND already on disk (sac_z5=$sacz) -- skipping, do not re-run triaged candidates"
    continue
  fi
  log "Q1 $CAND"
  if ! nice -n 19 python3 ../../round13/q1_sacbic.py "$CAND" "q1_$CAND" >"q1_$CAND.log" 2>&1; then
    log "Q1-RUNNER-FAIL $CAND (see q1_$CAND.log)"
    continue
  fi
  sacz=$(sacz_of "q1_$CAND/q1_$CAND.json") || sacz="?"
  log "Q1 $CAND sac_z5=$sacz"
  touch "$HB"
done
log "batch-62 Q1 resume done -- heartbeat workreg track6-batch62"
"$WORKREG" heartbeat --id track6-batch62 >>"$LOG" 2>&1 || true
