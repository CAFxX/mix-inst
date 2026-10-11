#!/bin/bash
# Batch-49 synthesis SPOT-CHECK (track 6): t6_q4S4a (min-z keep, z=2.61).
# Bar: <4.83u/stage at 4st (i.e. <19.3u), XCHECK clean.
# Polls load backoff (cap 12h), then runs run_synth.py once.
# LAUNCH UNDER setsid (agentwork-launch.sh execs -- b43 lesson, AGENTS.md).
set -u
set -o pipefail
cd ~/workspace/mix/exploration/new_constructions/batch49
HB=../track6_heartbeat.txt
CAND=../../fast_battery/candidates
log() { echo "[$(date -Is)] $*" | tee -a run_s0spot_b49.log; }

for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then break; fi
  sleep 60
done
if ! ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-49 S0 spot-check"
touch "$HB"

log "S0 t6_q4S4a"
if ! nice -n 19 python3 ../../run_synth.py "$CAND/t6_q4S4a/rtl.v" t6_q4S4a s0_t6_q4S4a \
    > s0_t6_q4S4a.log 2>&1; then
  log "S0 t6_q4S4a FAILED rc=$? -- see s0_t6_q4S4a.log"
fi
tail -5 s0_t6_q4S4a.log | tee -a run_s0spot_b49.log
touch "$HB"
log "batch-49 S0 spot-check COMPLETE"
