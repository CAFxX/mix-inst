#!/bin/bash
# Batch-60 pilot: 80 draws, seed 0xB602 (track-6 supervisor).
# Pre-registered rule: pre-pilot (9/12 KEEP, minz=2.3, harness checks
# PASS -- basin-depth axis HOT) -> PILOT runs regardless. >=1
# fisher-KEEP -> bit-exact bundle -> S0 (strict <18.6u) -> staged
# battery -> Q1. 0/80 -> AXIS-KILL (O-entry) -> deferred mux3f/xorh5.
#
# Launch: setsid agentwork-launch.sh --nice 19 --tag track6/b60-pilot -- bash run_b60_pilot.sh
set -u
cd ~/workspace/mix/exploration/new_constructions/batch60
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
echo "[$(date -Is)] backoff clear: batch-60 pilot 80 draws seed 0xB602" | tee -a "$LOG"
touch "$HB"
rm -f pilot_keeps.jsonl
nice -n 19 python3 t6_b60_screen.py muxD5fbasindepth 80 0xB602 pilot_keeps.jsonl 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
echo "[$(date -Is)] PILOT COMPLETE rc=$rc" | tee -a "$LOG"
touch "$HB"
exit $rc
