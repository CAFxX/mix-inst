#!/bin/bash
# Batch-53 S0 escalation (track-6 supervisor incarnation XXV): synth delay
# probe on the 5 hetMA5 keep bundles (t6_b53_h0..h4). Bar: STRICTLY <19.3u
# measured, XCHECK clean (ref mul64 103.5u).
# Backoff-poll <=12h with CLEARED-FLAG single gate (AGENTS.md lesson --
# no post-loop re-check). Launch: setsid agentwork-launch.sh --nice 19
# --tag track6/b53-escal -- bash run_b53_s0.sh
set -u
cd ~/workspace/mix/exploration/new_constructions/batch53
HB=heartbeat.txt
LOG=run_s0_b53.log
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
log "backoff CLEAR -- starting batch-53 S0 escalation"
touch "$HB"

for n in 0 1 2 3 4; do
  CAND=t6_b53_h$n
  log "S0 $CAND"
  if ! python3 ../../run_synth.py \
      "../../fast_battery/candidates/$CAND/rtl.v" "$CAND" "s0_$CAND" \
      > "s0_$CAND.log" 2>&1; then
    log "S0 $CAND FAILED rc=$? -- see s0_$CAND.log"
  fi
  grep -E "RESULT|xcheck|XCHECK" "s0_$CAND.log" | tail -3 | tee -a "$LOG"
  touch "$HB"
done
log "batch-53 S0 escalation COMPLETE"
touch "$HB"
