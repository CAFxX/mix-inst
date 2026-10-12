#!/bin/bash
# Resume after BOTH battery launchers died ~12:37-12:39Z 2026-10-12 (no log
# trace, no shedder kill record, dmesg unreadable; cause unknown — memory
# pressure plausible). t6_b62_33 had S0a+S1 CAL_PASS verified
# (s1_result.json, battery_t6_b62_33.log); its S2 was 4/72 deltas in when the
# worker died. Resume 33 from stage 2 (run_fast_battery.sh <cand> 2 skips
# S0a+S1; S2 re-runs fully), then chain the remaining queue (17/26/9/3/6/21/36)
# through the pre-registered escalation.
set -u
cd /home/hatch/workspace/mix/exploration/new_constructions/batch62 || exit 1
HB=heartbeat.txt; LOG=run_b62_battery.log; FB=../../fast_battery
log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

deadline=$(( $(date +%s) + 43200 ))
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  sleep 60
done
if [ "$cleared" != 1 ]; then log "BACKOFF never cleared in 12h -- aborting LOUD"; exit 1; fi
touch "$HB"
log "RESUME t6_b62_33 from S2 (S0a+S1 CAL_PASS verified; launcher died mid-S2 ~12:37Z)"
echo "=== RESUME t6_b62_33 from S2 $(date -u +%FT%TZ) (launcher died mid-S2) ===" >> battery_t6_b62_33.log
nice -n 19 bash "$FB/run_fast_battery.sh" t6_b62_33 2 >> battery_t6_b62_33.log 2>&1
rc=$?
log "BATTERY t6_b62_33 rc=$rc (resumed from S2)"
touch "$HB"
/home/hatch/workspace/system/bin/workreg.py heartbeat --id track6-batch62 >/dev/null 2>&1 || true
exec bash run_b62_battery.sh t6_b62_17 t6_b62_26 t6_b62_9 t6_b62_3 t6_b62_6 t6_b62_21 t6_b62_36
