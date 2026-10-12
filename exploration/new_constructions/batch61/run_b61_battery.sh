#!/bin/bash
# Batch-61 staged battery escalation (track-6, post-reboot resume):
# S0 sweep COMPLETE 2026-10-12T04:46:51Z (s0_all.log, ranks 0..56,
# XCHECK clean, ref mul64 103.5u stable). Three keeps STRICTLY <18.6u:
#   t6_b61_56  18.3u / 5262 / 17260  (z=2.499, first in z-order)
#   t6_b61_24  18.5u / 6948 / 22904  (z=2.794)
#   t6_b61_38  18.5u / 6344 / 20544  (z=3.090)
# Per DESIGN.md pre-registered rule: escalate cost-eligible keeps in
# z-order -> staged battery S1->S2->S3->S4 (run_fast_battery.sh stops at
# the first kill) -> Q1 SAC/BIC (sac_z5=0 MANDATORY for Frontier-S
# claims). A Q1-clearing keep at <18.6u -> FRONTIER CHALLENGER
# (O124+, PARETO/RETAINED/RTL update). Escalation runs 56 FIRST; 24/38
# are escalated only if 56 is killed (56 dominates both in delay AND
# cells AND area, so a 56 pass leaves nothing for them to challenge).
#
# Usage: run_b61_battery.sh <cand> [<cand> ...]
# Backoff-poll <=12h with CLEARED-FLAG single gate (AGENTS.md lesson).
# Launch: setsid ~/workspace/system/bin/agentwork-launch.sh --nice 19 \
#         --tag track6/b61-battery -- bash run_b61_battery.sh t6_b61_56
set -u
cd /home/hatch/workspace/mix/exploration/new_constructions/batch61 || exit 1
HB=heartbeat.txt
LOG=run_b61_battery.log
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
log "backoff CLEAR -- starting batch-61 staged battery for: $*"
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
    log "Q1 $CAND FAILED rc=$? -- see q1_$CAND.log"
  else
    tail -5 "q1_$CAND.log" | tee -a "$LOG"
  fi
  touch "$HB"
done
log "batch-61 staged battery COMPLETE; survivors:$s4_survivors"
touch "$HB"
