#!/bin/bash
# Batch-59 staged battery escalation for t6_b59_0 (track-6 supervisor
# incarnation XXXIV): S1 FAIL-FAST, then staged battery S1->S2->S3->S4
# on the best-z fisher-keep (run_fast_battery.sh STOPS at the first
# kill), then Q1 SAC/BIC (sac_z5=0 MANDATORY for Frontier-S claims).
# Cost-eligible: t6_b59_0 (19.1u STRICTLY <19.2u, XCHECK clean) --
# rank-0 muxD5f-local keep (z=2.17, n_reject=0, m=1 perturbation of
# the t6_b57_8 winner): first in the z-order escalation queue
# (pre-pilot + pilot keeps combined, 65 unique).
# If killed -> escalate next cost-eligible keep in z-order
# (t6_b59_1 z=2.34 19.0u -> t6_b59_2 z=2.37 19.1u -> ... per s0_all.log).

# Backoff-poll <=12h with CLEARED-FLAG single gate (AGENTS.md lesson).
# Launch: setsid agentwork-launch.sh --nice 19 --tag track6/b59-battery0 --
# bash run_b59_battery0.sh
set -u
cd ~/workspace/mix/exploration/new_constructions/batch59
HB=heartbeat.txt
LOG=run_b59_battery0.log
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
log "backoff CLEAR -- starting batch-59 staged battery for t6_b59_0"
touch "$HB"

CAND=t6_b59_0
log "BATTERY $CAND (start_stage=1)"
rc=0
nice -n 19 bash "$FB/run_fast_battery.sh" "$CAND" 1 \
    > "battery_$CAND.log" 2>&1 || rc=$?
log "BATTERY $CAND rc=$rc"
grep -E "^S[1-4]|CAL_PASS|KILL|FAIL" "battery_$CAND.log" | tail -12 | tee -a "$LOG"
touch "$HB"
if [ "$rc" = "0" ]; then
  log "Q1 $CAND"
  if ! nice -n 19 python3 ../../round13/q1_sacbic.py "$CAND" "q1_$CAND" \
      > "q1_$CAND.log" 2>&1; then
    log "Q1 $CAND FAILED rc=$? -- see q1_$CAND.log"
  else
    tail -5 "q1_$CAND.log" | tee -a "$LOG"
  fi
fi
log "batch-59 battery t6_b59_0 COMPLETE rc=$rc"
touch "$HB"
