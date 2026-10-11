#!/bin/bash
# Batch-53 staged battery escalation (track-6 supervisor incarnation XXV):
# S1 FAIL-FAST on the FIRST cost-eligible keep (lesson b), then staged
# battery S1->S2->S3->S4 on each surviving cost-eligible keep in z order
# (run_fast_battery.sh STOPS at the first kill), then Q1 SAC/BIC on any
# S4 survivor (sac_z5=0 MANDATORY for Frontier-S claims).
# Cost-eligible keeps (S0 <19.3u strict, XCHECK clean): h0 (19.1), h1
# (19.2), h3 (18.9), h4 (18.7). h2 (19.7) cost-doomed, excluded.
# Backoff-poll <=12h with CLEARED-FLAG single gate. Launch:
# setsid agentwork-launch.sh --nice 19 --tag track6/b53-escal --
# bash run_b53_battery.sh
set -u
cd ~/workspace/mix/exploration/new_constructions/batch53
HB=heartbeat.txt
LOG=run_b53_battery.log
FB=../../fast_battery
log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

deadline=$(( $(date +%s) + 43200 ))
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  sleep 60
done
if [ "$cleared" != 1 ]; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-53 staged battery"
touch "$HB"

s4_survivors=""
for CAND in t6_b53_h0 t6_b53_h1 t6_b53_h3 t6_b53_h4; do
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
    log "Q1 $CAND FAILED rc=$? -- see q1_$CAND.log"
  else
    tail -5 "q1_$CAND.log" | tee -a "$LOG"
  fi
  touch "$HB"
done
log "batch-53 staged battery COMPLETE; survivors:$s4_survivors"
touch "$HB"
