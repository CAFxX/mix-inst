#!/bin/bash
# Batch-59 size-chain RESUME (track-6 supervisor, 2026-10-12).
# The original run_b59_sizechain.sh wrapper was killed mid-flight by VM/daemon
# instability at ~04:11:56Z, right after t6_b59_41's battery PASSED (rc=0,
# BATTERY-PASS in sizebattery_t6_b59_41.log) — its Q1 never completed
# (sizeq1_t6_b59_41/ empty). This resume does NOT rerun 41's battery:
#   1. Q1 for t6_b59_41 (sac_z5=0 mandatory) — battery artifacts already pass.
#   2. SIZE-BATTERY -> Q1 for t6_b59_9 (cells+area slot vs 47: 6501/20818).
#   3. SIZE-BATTERY -> Q1 for t6_b59_50 (area-only slot vs 47: 21676<21830).
# Size slots STACK: the resume does NOT stop at the first full pass.
# Each S1->S4+Q1(sac_z5=0) pass is logged as SIZE-CHALLENGER; the supervisor
# adjudicates Pareto slots from raw artifacts afterwards.
# Cleared-flag backoff pattern (AGENTS.md lesson). Launched under setsid.
set -u
cd ~/workspace/mix/exploration/new_constructions/batch59
HB=heartbeat.txt
LOG=run_b59_sizechain_resume.log
FB=../../fast_battery
log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

deadline=$(( $(date +%s) + 43200 ))
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if ~/workspace/system/bin/load-shed.sh backoff > backoff_poll_resume.out 2>&1; then
    cleared=1; break
  fi
  log "backoff not clear, waiting (load-gated)"; sleep 60
done
if [ "$cleared" != 1 ]; then
  log "BACKOFF-FAIL: load never cleared in 12h -- aborting LOUD"; exit 4
fi
log "backoff CLEAR -- batch-59 size-chain RESUME starting"
touch "$HB"

run_q1() { # $1 = candidate; runs Q1, logs verdict, appends SIZE_CHALLENGERS.txt on full pass
  local CAND=$1
  log "Q1 $CAND"
  if nice -n 19 python3 ../../round13/q1_sacbic.py "$CAND" "sizeq1_$CAND" \
      > "sizeq1_$CAND.log" 2>&1; then
    tail -5 "sizeq1_$CAND.log" | tee -a "$LOG"
    sac=$(python3 -c "import json,glob;f=glob.glob('sizeq1_$CAND/q1_$CAND.json')[0];print(json.load(open(f))['sac_z5'])" 2>/dev/null || sac="?"
    log "Q1 $CAND sac_z5=$sac"
    if [ "$sac" = "0" ]; then
      log "SIZE-CHALLENGER: $CAND (S1-S4 PASS + sac_z5=0) -- resume CONTINUES"
      echo "$CAND" >> SIZE_CHALLENGERS.txt
    else
      log "Q1-KILLED $CAND (sac_z5=$sac) -> next"
    fi
  else
    log "Q1 $CAND FAILED rc=$? -- see sizeq1_$CAND.log -> next"
  fi
  touch "$HB"
}

run_battery_then_q1() { # $1 = candidate
  local CAND=$1
  log "=== SIZE-BATTERY $CAND (start_stage=1) ==="
  rc=0
  nice -n 19 bash "$FB/run_fast_battery.sh" "$CAND" 1 \
      > "sizebattery_$CAND.log" 2>&1 || rc=$?
  log "SIZE-BATTERY $CAND rc=$rc"
  grep -E "^S[1-4]|CAL_PASS|KILL|FAIL" "sizebattery_$CAND.log" | tail -8 | tee -a "$LOG"
  touch "$HB"
  if [ "$rc" = "0" ]; then
    run_q1 "$CAND"
  else
    log "KILLED $CAND at battery rc=$rc -> next"
  fi
}

# 1. t6_b59_41: battery already PASS (BATTERY-PASS in sizebattery_t6_b59_41.log);
#    run ONLY the Q1 step.
if grep -q "BATTERY-PASS" sizebattery_t6_b59_41.log 2>/dev/null; then
  log "t6_b59_41 battery PASS verified on disk -- running Q1 only"
  run_q1 "t6_b59_41"
else
  log "BATTERY-PASS missing for t6_b59_41 -- escalating: full battery first"
  run_battery_then_q1 "t6_b59_41"
fi

# 2+3. The never-run keeps through the full battery->Q1 path.
run_battery_then_q1 "t6_b59_9"
run_battery_then_q1 "t6_b59_50"

log "size-chain RESUME EXHAUSTED"
touch "$HB"
exit 0
