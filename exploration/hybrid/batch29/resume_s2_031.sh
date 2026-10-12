#!/bin/bash
# Resume after BOTH battery launchers died ~12:37-12:39Z 2026-10-12 (no log
# trace, no shedder kill record, dmesg unreadable; cause unknown — memory
# pressure plausible). hyb29_mu5_031 had S0a+S1 CAL_PASS verified
# (s1_result.json, battery_hyb29_mu5_031.log); its S2 was 8/72 deltas in when
# the worker died. Resume 031 from stage 2, then chain 032-035 through the
# pre-registered escalation (per-candidate backoff gate, escalate.log).
set -u
B29=/home/hatch/workspace/mix/exploration/hybrid/batch29
FB=/home/hatch/workspace/mix/exploration/fast_battery
cd "$B29"
REG=/home/hatch/workspace/system/bin/workreg.py

cleared=0
for i in $(seq 1 720); do
  if /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    cleared=1; break
  fi
  sleep 60
done
if [ "$cleared" -eq 0 ]; then echo "BACKOFF-FAIL resume hyb29_mu5_031" | tee -a escalate.log; exit 1; fi

cp escalate.log escalate.log.resume4 2>/dev/null || true
echo "=== RESUME hyb29_mu5_031 from S2 $(date -u +%FT%TZ) (launcher died mid-S2) ===" | tee -a escalate.log
nice -n 19 bash "$FB/run_fast_battery.sh" hyb29_mu5_031 2 >> battery_hyb29_mu5_031.log 2>&1
rc=$?
echo "=== hyb29_mu5_031 battery rc=$rc (resumed from S2) $(date -u +%FT%TZ) ===" | tee -a escalate.log
"$REG" heartbeat --id mix-track5-batch29 >/dev/null 2>&1 || true
printf '%s\n' hyb29_mu5_032 hyb29_mu5_033 hyb29_mu5_034 hyb29_mu5_035 > escalate_queue_resume4.txt
exec bash run_escalate.sh escalate_queue_resume4.txt
