#!/bin/bash
# Batch-43 pilot runner (track 6): complemented-gate 5-stage rotation
# cascades (nandM-5 / norM-5 / ornM-5).
# Polls load backoff (cap 12h), then runs calibration FAIL-LOUD, then the
# three pilot arms sequentially at nice 19.
#   nandM5: 40 draws, seed 0xB431 -> pilot_nandM5.log / keeps_nandM5.jsonl
#   norM5:  40 draws, seed 0xB432 -> pilot_norM5.log / keeps_norM5.jsonl
#   ornM5:  40 draws, seed 0xB433 -> pilot_ornM5.log / keeps_ornM5.jsonl
# KEEPs are dumped per-try to JSONL by the screen script (b39 lesson).
# Resume after a VM reboot: relaunch this script; the seed is deterministic
# so a fresh run reproduces identical try lines -- verify the new log's
# prefix matches the dead run's log up to the kill point (b40 precedent),
# then let it run to completion (a resumed run must first rm the partial
# keeps_*.jsonl to avoid duplicate rows).
set -u
set -o pipefail
cd ~/workspace/mix/exploration/new_constructions/batch43
HB=../supervisor_heartbeat.txt
log() { echo "[$(date -Is)] $*" | tee -a run_b43.log; }

for i in $(seq 1 720); do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then break; fi
  sleep 60
done
if ! ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
  log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1
fi
log "backoff CLEAR -- starting batch-43 pilot"
touch "$HB"

log "calibration: and1/b33c must reproduce z=3.3"
if ! nice -n 19 python3 t6_b43_screen.py calibrate 2>&1 | tee -a run_b43.log; then
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
  if ! nice -n 19 python3 t6_b43_screen.py "$1" "$2" "$3" "keeps_$1.jsonl" \
      > "pilot_$1.log" 2>&1; then
    log "arm $1 exited rc=$? (rc=2 with 0 kills = vacuous-harness GATE-FAIL)"
  fi
  tail -2 "pilot_$1.log" | tee -a run_b43.log
  touch "$HB"
}

run_arm nandM5 40 0xB431
run_arm norM5 40 0xB432
run_arm ornM5 40 0xB433
log "batch-43 pilot COMPLETE"
