#!/bin/bash
# Batch-46 pilot runner (track 6): hetero chi+AND interleave
# (hetCA4a: C-A-C-A / hetCA4b: A-C-A-C).
# Polls load backoff (cap 12h), then runs calibration FAIL-LOUD, then the
# two pilot arms sequentially at nice 19.
#   hetCA4a: 40 draws, seed 0xB461 -> pilot_hetCA4a.log / keeps_hetCA4a.jsonl
#   hetCA4b: 40 draws, seed 0xB462 -> pilot_hetCA4b.log / keeps_hetCA4b.jsonl
# KEEPs are dumped per-try to JSONL by the screen script (b39 lesson).
# Resume after a VM reboot: relaunch this script; the seed is deterministic
# so a fresh run reproduces identical try lines -- verify the new log's
# prefix matches the dead run's log up to the kill point (b40 precedent),
# then let it run to completion (a resumed run must first rm the partial
# keeps_*.jsonl to avoid duplicate rows).
# LAUNCH UNDER setsid (agentwork-launch.sh execs; a launcher-session
# teardown SIGTERMs the worker -- b43 lesson, AGENTS.md).
set -u
set -o pipefail
cd ~/workspace/mix/exploration/new_constructions/batch46
HB=../supervisor_heartbeat.txt
log() { echo "[$(date -Is)] $*" | tee -a run_b46.log; }

for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then break; fi
  sleep 60
done
if ! ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-46 pilot"
touch "$HB"

log "calibration: and1/b33c must reproduce z=3.3"
if ! nice -n 19 python3 t6_b46_screen.py calibrate 2>&1 | tee -a run_b46.log; then
  log "CALIBRATION FAILED -- harness untrusted, aborting LOUD"; exit 1
fi
log "calibration PASS"
touch "$HB"

run_arm() { # form n_try seed
  log "arm $1: $2 draws seed $3"
  if [ -f "pilot_$1.log" ]; then
    n=1; while [ -f "pilot_$1.log.dead$n" ]; do n=$((n+1)); done
    cp "pilot_$1.log" "pilot_$1.log.dead$n"
    log "preserved pre-existing pilot_$1.log -> .dead$n"
  fi
  if ! nice -n 19 python3 t6_b46_screen.py "$1" "$2" "$3" "keeps_$1.jsonl" \
      > "pilot_$1.log" 2>&1; then
    log "arm $1 exited rc=$? (rc=2 with 0 kills = vacuous-harness GATE-FAIL)"
  fi
  tail -2 "pilot_$1.log" | tee -a run_b46.log
  touch "$HB"
}

run_arm hetCA4a 40 0xB461
run_arm hetCA4b 40 0xB462
log "batch-46 pilot COMPLETE"
