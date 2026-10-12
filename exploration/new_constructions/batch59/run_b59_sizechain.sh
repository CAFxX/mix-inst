#!/bin/bash
# Batch-59 deferred-keeps SIZE chain (track-6 supervisor, 2026-10-12).
# The min-crit chain stopped at the first speed challenger (t6_b59_47,
# FRONTIER_CHALLENGER.txt). These 10 keeps cannot take the speed point
# (strict <18.6u bar) but carry size claims vs the frontier:
#   54 (18.6u tie, 6045/19800): ties 47's delay, beats it on cells+area;
#       dominates t6_b59_0 (19.1u, 6358/20580) on all axes.
#   15 (19.0u, 6028/19606): dominates t6_b59_0 on all axes.
#   1  (19.0u, 6191/20354): dominates t6_b59_0 on all axes.
#   61 (19.0u, 6252/20354): dominates t6_b59_0 on all axes.
#   8  (18.8u, 6493/21896): cells slot vs 47 (6493<6656).
#   14 (18.9u, 6414/21812): cells slot vs 47 (6414<6656).
#   17 (19.0u, 6523/20885): cells+area slot vs 47.
#   41 (19.0u, 6393/20812): cells+area slot vs 47.
#   9  (19.0u, 6501/20818): cells+area slot vs 47.
#   50 (19.0u, 6816/21676): area-only slot vs 47 (21676<21830).
# t6_b59_48 (18.6u tie, 6748/22221) EXCLUDED: strictly dominated by
# t6_b59_47 (same 18.6u, more cells, more area) from measured S0 --
# cannot enter the Pareto set in any slot; verdict SUPERSEDED.
# (Dedup note: run_b59_battery7_chain.sh is the TERMINAL speed chain;
# this is a different wrapper for the size axis.)
#
# Size slots STACK: the chain does NOT stop at the first full pass.
# Each S1->S4+Q1(sac_z5=0) pass is logged as SIZE-CHALLENGER; the
# supervisor adjudicates Pareto slots from raw artifacts afterwards.
#
# Launch: setsid agentwork-launch.sh --nice 19 --tag track6/b59-sizechain -- bash run_b59_sizechain.sh
set -u
cd ~/workspace/mix/exploration/new_constructions/batch59
HB=heartbeat.txt
LOG=run_b59_sizechain.log
FB=../../fast_battery
log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

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
log "backoff CLEAR -- starting batch-59 deferred-keeps SIZE chain"
touch "$HB"

for CAND in t6_b59_54 t6_b59_15 t6_b59_1 t6_b59_61 t6_b59_8 t6_b59_14 \
            t6_b59_17 t6_b59_41 t6_b59_9 t6_b59_50; do
  log "=== SIZE-BATTERY $CAND (start_stage=1) ==="
  rc=0
  nice -n 19 bash "$FB/run_fast_battery.sh" "$CAND" 1 \
      > "sizebattery_$CAND.log" 2>&1 || rc=$?
  log "SIZE-BATTERY $CAND rc=$rc"
  grep -E "^S[1-4]|CAL_PASS|KILL|FAIL" "sizebattery_$CAND.log" | tail -8 | tee -a "$LOG"
  touch "$HB"
  if [ "$rc" = "0" ]; then
    log "Q1 $CAND"
    if nice -n 19 python3 ../../round13/q1_sacbic.py "$CAND" "sizeq1_$CAND" \
        > "sizeq1_$CAND.log" 2>&1; then
      tail -5 "sizeq1_$CAND.log" | tee -a "$LOG"
      sac=$(python3 -c "import json;print(json.load(open('sizeq1_$CAND/q1_$CAND.json'))['sac_z5'])" 2>/dev/null || echo "?")
      log "Q1 $CAND sac_z5=$sac"
      if [ "$sac" = "0" ]; then
        log "SIZE-CHALLENGER: $CAND (S1-S4 PASS + sac_z5=0) -- chain CONTINUES"
        echo "$CAND" >> SIZE_CHALLENGERS.txt
      else
        log "Q1-KILLED $CAND (sac_z5=$sac) -> next in chain"
      fi
    else
      log "Q1 $CAND FAILED rc=$? -- see sizeq1_$CAND.log -> next in chain"
    fi
  else
    log "KILLED $CAND at battery rc=$rc -> next in chain"
  fi
done
log "size chain EXHAUSTED -- all 10 deferred keeps adjudicated"
touch "$HB"
exit 0
