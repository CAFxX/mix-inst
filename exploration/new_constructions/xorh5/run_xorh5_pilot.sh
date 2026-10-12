#!/bin/bash
# xorh5 pilot: 80 draws, seed 0xB6A2 (queued-lead adjudication, track-6).
# Pre-registered rule: pre-pilot (3/12 KEEP, minz=2.1, harness checks
# PASS) -> PILOT runs regardless. >=1 fisher-KEEP -> bundle -> S0
# (strict <18.6u) -> staged battery -> Q1. 0/80 -> FORM-KILL (O-entry).
#
# Launch: setsid agentwork-launch.sh --nice 19 --tag track6/xorh5-pilot -- bash run_xorh5_pilot.sh
set -u
cd ~/workspace/mix/exploration/new_constructions/xorh5
HB=heartbeat.txt
LOG=pilot.log

deadline=$(( $(date +%s) + 43200 ))
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  echo "[$(date -Is)] backoff not clear, waiting" | tee -a "$LOG"; sleep 60
done
if [ "$cleared" != 1 ]; then
  echo "[$(date -Is)] BACKOFF never cleared in 12h -- aborting LOUD" | tee -a "$LOG"; exit 1
fi
echo "[$(date -Is)] backoff clear: xorh5 pilot 80 draws seed 0xB6A2" | tee -a "$LOG"
touch "$HB"
rm -f pilot_keeps.jsonl
nice -n 19 python3 t6_xorh5_screen.py xorh5 80 0xB6A2 pilot_keeps.jsonl 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
echo "[$(date -Is)] PILOT COMPLETE rc=$rc" | tee -a "$LOG"
touch "$HB"
exit $rc
