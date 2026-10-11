#!/bin/bash
# Batch-45 pilot runner (track 6): true chi S-box as the repeated STAGE
# (chiS-4 / chiS-5: stage(x,a,b) = chi3(x) ^ rotl(chi3(x),a) ^ rotl(chi3(x),b)).
# Polls load backoff (cap 12h), then runs calibration FAIL-LOUD, then the
# two pilot arms sequentially at nice 19.
#   chiS4: 40 draws, seed 0xB451 -> pilot_chiS4.log / keeps_chiS4.jsonl
#   chiS5: 40 draws, seed 0xB452 -> pilot_chiS5.log / keeps_chiS5.jsonl
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
cd ~/workspace/mix/exploration/new_constructions/batch45
HB=../supervisor_heartbeat.txt
log() { echo "[$(date -Is)] $*" | tee -a run_b45.log; }

for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then break; fi
  sleep 60
done
if ! ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-45 pilot"
touch "$HB"

log "calibration: and1/b33c must reproduce z=3.3"
if ! nice -n 19 python3 t6_b45_screen.py calibrate 2>&1 | tee -a run_b45.log; then
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
  if ! nice -n 19 python3 t6_b45_screen.py "$1" "$2" "$3" "keeps_$1.jsonl" \
      > "pilot_$1.log" 2>&1; then
    log "arm $1 exited rc=$? (rc=2 with 0 kills = vacuous-harness GATE-FAIL)"
  fi
  tail -2 "pilot_$1.log" | tee -a run_b45.log
  touch "$HB"
}

run_arm chiS4 40 0xB451
run_arm chiS5 40 0xB452
log "batch-45 pilot COMPLETE"
