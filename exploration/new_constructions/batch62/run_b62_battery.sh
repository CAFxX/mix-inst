#!/bin/bash
# Batch-62 staged battery escalation (track-6):
# FRONTIER-ELIGIBLE keeps (Pareto-nondominated vs Frontier S, adjudicated
# raw from s0_all.log vs PARETO.md 2026-10-12; speed axis honestly closed --
# ZERO sub-18.6u, so this run is the SIZE axis) in z-order (delay, cells) ->
# staged battery S1->S2->S3->S4 (run_fast_battery.sh stops at the first
# kill) -> Q1 SAC/BIC (sac_z5=0 MANDATORY for Frontier-S claims).
# A Q1-clearing keep -> FRONTIER CHALLENGER (O142+,
# PARETO/RETAINED/RTL update per chain rules).
# Usage: run_b62_battery.sh <cand> [<cand> ...]
# Backoff-poll <=12h with CLEARED-FLAG single gate (AGENTS.md lesson).
# Launch: setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 \
#         --tag track6/b62-battery -- bash run_b62_battery.sh t6_b62_0
set -u
cd /home/hatch/workspace/mix/exploration/new_constructions/batch62 || exit 1
HB=heartbeat.txt
LOG=run_b62_battery.log
FB=../../fast_battery
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
log "backoff CLEAR -- starting batch-62 staged battery for: $*"
touch "$HB"

s4_survivors=""
for CAND in "$@"; do
  log "BATTERY $CAND (start_stage=1)"
  rc=0
  nice -n 19 bash "$FB/run_fast_battery.sh" "$CAND" 1 \
      > "battery_$CAND.log" 2>&1 || rc=$?
  log "BATTERY $CAND rc=$rc"
  grep -E "^S[1-4]|CAL_PASS|KILL|FAIL" "battery_$CAND.log" | tail -12 | tee -a "$LOG"
  if [ "$rc" = "0" ]; then
    s4_survivors="$s4_survivors $CAND"
  fi
  touch "$HB"
done
log "S4 survivors:$s4_survivors"
for CAND in $s4_survivors; do
  log "Q1 $CAND"
  if ! nice -n 19 python3 ../../round13/q1_sacbic.py "$CAND" "q1_$CAND" \
      > "q1_$CAND.log" 2>&1; then
    log "Q1-RUNNER-FAIL $CAND (see q1_$CAND.log)"
    continue
  fi
  sacz=$(python3 -c "import json;print(json.load(open('q1_$CAND/q1_$CAND.json'))['sac_z5'])" 2>/dev/null || sacz="?"
  log "Q1 $CAND sac_z5=$sacz"
  touch "$HB"
done
log "batch-62 battery/Q1 escalation done"
