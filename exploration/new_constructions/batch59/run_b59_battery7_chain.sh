#!/bin/bash
# Batch-59 min-crit escalation chain (adjudicated by the 30m report run
# 2026-10-12 ~05:05 CEST; track-6 supervisor XXXIV AWOL: heartbeat stale
# 02:35Z, no live procs, S0 sweep + t6_b59_0 battery/Q1 all COMPLETE).
# t6_b59_0 (19.1u, best-z) took the Frontier S+Q speed point. This chain
# batteries the 13 cost-eligible keeps STRICTLY under the new 19.1u
# frontier, in crit order: 18.5 -> 18.6x3 -> 18.8 -> 18.9 -> 19.0x7.
# First keep to clear S1->S2->S3->S4->Q1(sac_z5=0) = FRONTIER CHALLENGER.
# Pre-registered escalation rule (b57-style): kill/doom -> next in order.
#
# Launch: setsid agentwork-launch.sh --nice 19 --tag track6/b59-battery7chain -- bash run_b59_battery7_chain.sh
set -u
cd ~/workspace/mix/exploration/new_constructions/batch59
HB=heartbeat.txt
LOG=run_b59_battery7_chain.log
FB=../../fast_battery
log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

# Backoff-poll <=12h with CLEARED-FLAG single gate (AGENTS.md lesson).
deadline=$(( $(date +%s) + 43200 ))
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  log "backoff not clear, waiting (load-gated)"; sleep 60
done
if [ "$cleared" != 1 ]; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-59 min-crit escalation chain"
touch "$HB"

for CAND in t6_b59_7 t6_b59_47 t6_b59_48 t6_b59_54 t6_b59_8 t6_b59_14 \
            t6_b59_15 t6_b59_17 t6_b59_1 t6_b59_41 t6_b59_50 t6_b59_61 t6_b59_9; do
  log "=== BATTERY $CAND (start_stage=1) ==="
  rc=0
  nice -n 19 bash "$FB/run_fast_battery.sh" "$CAND" 1 \
      > "battery_$CAND.log" 2>&1 || rc=$?
  log "BATTERY $CAND rc=$rc"
  grep -E "^S[1-4]|CAL_PASS|KILL|FAIL" "battery_$CAND.log" | tail -8 | tee -a "$LOG"
  touch "$HB"
  if [ "$rc" = "0" ]; then
    log "Q1 $CAND"
    if nice -n 19 python3 ../../round13/q1_sacbic.py "$CAND" "q1_$CAND" \
        > "q1_$CAND.log" 2>&1; then
      tail -5 "q1_$CAND.log" | tee -a "$LOG"
      sac=$(python3 -c "import json;print(json.load(open('q1_$CAND/q1_$CAND.json'))['sac_z5'])" 2>/dev/null || echo "?")
      log "Q1 $CAND sac_z5=$sac"
      if [ "$sac" = "0" ]; then
        log "FRONTIER CHALLENGER: $CAND (S1-S4 PASS + sac_z5=0) -- chain STOPS"
        echo "$CAND" > FRONTIER_CHALLENGER.txt
        touch "$HB"
        exit 0
      else
        log "Q1-KILLED $CAND (sac_z5=$sac) -> next in chain"
      fi
    else
      log "Q1 $CAND FAILED rc=$? -- see q1_$CAND.log -> next in chain"
    fi
  else
    log "KILLED $CAND at battery rc=$rc -> next in chain"
  fi
done
log "chain EXHAUSTED: no cost-eligible keep under 19.1u cleared the full battery -- batch-59 TERMINAL"
touch "$HB"
exit 2
