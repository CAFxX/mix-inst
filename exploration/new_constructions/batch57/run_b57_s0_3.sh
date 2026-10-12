#!/bin/bash
# Batch-57 t6_b57_3 S0: 4th min-z keep (fisher triage z=2.83, n_reject=0,
# pure muxD5f), strict <19.3u cost bar. Escalated per pre-registered rule
# after t6_b57_2 S1-killed (marginal PB rej=2 FLAG).
# Adjudicate on "RESULT" in s0_t6_b57_3.log:
#   crit strictly < 19.3 -> cost-ELIGIBLE -> staged battery S1->S4
#       (run_b57_battery3.sh) -> Q1 on S4 survivor (sac_z5=0 mandatory);
#   cost-DOOMED -> escalate rank 4 (z=2.88) per the pre-registered rule.
# Cleared-flag backoff pattern (AGENTS.md lesson). Launched under setsid.
cd /home/hatch/workspace/mix/exploration || exit 1
LOG=new_constructions/batch57/s0_t6_b57_3.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > new_constructions/batch57/backoff_poll_s0_b57_1.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter): $(head -c 200 new_constructions/batch57/backoff_poll_s0_b57_1.out)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running S0 for t6_b57_3" >> "$LOG"
python3 run_synth.py fast_battery/candidates/t6_b57_3/rtl.v t6_b57_3 \
    new_constructions/batch57/s0_t6_b57_3 >> "$LOG" 2>&1
echo "run_synth exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) S0 COMPLETE" >> "$LOG"
