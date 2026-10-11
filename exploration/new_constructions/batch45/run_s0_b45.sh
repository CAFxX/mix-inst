#!/bin/bash
# Batch-45 S0 runner (track 6): stratified S0 sample of chiS4 keeps.
#   t6_chiS4a (z=2.82, min) / t6_chiS4b (z=5.38, median) / t6_chiS4c (z=7.96, max)
# Bar: strictly <19.3u MEASURED, XCHECK clean (analyze.py == analyze2.py).
# Polls load backoff (cap 12h), then runs run_synth.py sequentially at nice 10.
# LAUNCH UNDER setsid (agentwork-launch.sh execs -- b43 lesson, AGENTS.md).
set -u
set -o pipefail
cd ~/workspace/mix/exploration/new_constructions/batch45
HB=../supervisor_heartbeat.txt
CAND=../../fast_battery/candidates
log() { echo "[$(date -Is)] $*" | tee -a run_s0_b45.log; }

for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then break; fi
  sleep 60
done
if ! ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-45 S0s"
touch "$HB"

run_s0() { # bundle_name
  local b=$1
  log "S0 $b"
  if ! nice -n 10 python3 ../../run_synth.py "$CAND/$b/rtl.v" "$b" "s0_$b" \
      > "s0_$b.log" 2>&1; then
    log "S0 $b FAILED rc=$? -- see s0_$b.log"
  fi
  tail -3 "s0_$b.log" | tee -a run_s0_b45.log
  touch "$HB"
}

run_s0 t6_chiS4a
run_s0 t6_chiS4b
run_s0 t6_chiS4c
log "batch-45 S0s COMPLETE"
