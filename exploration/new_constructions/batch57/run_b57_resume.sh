#!/bin/bash
# XXXIII resume: t6_b57_8 from S3b (S1/S2/S3 verified PASS, checkpointed in
# battery_s1s2s3_PASS.log). Runs S3+S3b+S4 (START=3; S3 re-run is deterministic
# ~5min), then Q1 (sac_z5=0 mandatory). Launch:
#   setsid agentwork-launch.sh --nice 19 --tag track6/b57-battery-resume -- \
#     bash run_b57_resume.sh >> resume_b57_8.log 2>&1 < /dev/null &
set -u
cd ~/workspace/mix/exploration/new_constructions/batch57
HB=heartbeat.txt
LOG=resume_b57_8.log
FB=../../fast_battery
CAND=t6_b57_8
log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; touch "$HB"; }

log "RESUME $CAND from S3 (START=3): S3+S3b+S4"
nice -n 19 bash "$FB/run_fast_battery.sh" "$CAND" 3 >> "$LOG" 2>&1
rc=$?
log "battery rc=$rc"
if [ "$rc" != "0" ]; then
  log "BATTERY-FAIL $CAND -- see $FB/results/$CAND/battery.log"
  exit 2
fi
log "S4 PASS -- running Q1 sac/bic"
if ! nice -n 19 python3 ../../round13/q1_sacbic.py "$CAND" "q1_$CAND" >> "q1_$CAND.log" 2>&1; then
  log "Q1 $CAND FAILED rc=$? -- see q1_$CAND.log"
  exit 2
fi
log "Q1 $CAND done:"
tail -5 "q1_$CAND.log" | tee -a "$LOG"
log "RESUME COMPLETE $CAND"
