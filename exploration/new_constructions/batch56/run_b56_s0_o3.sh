#!/bin/bash
# Batch-56 o2 S0: 4th min-z keep (fisher triage z=3.56, n_reject=0,
# OAAND(53,61,9,28)@pos1 + 4x MUXD), strict <19.3u cost bar.
# Adjudicate on "RESULT" in s0_t6_b56_o3.log:
#   crit strictly < 19.3 -> cost-ELIGIBLE -> S1 fail-fast
#       (fast_battery/run_fast_battery.sh start_stage=1) -> staged battery
#       -> Q1 on any S4 survivor (sac_z5=0 mandatory, bic reported);
#   cost-DOOMED -> escalate o3 (z=3.56, 4th min-z) per the pre-registered
#       rule; 3+ doomed keeps -> form-level cost verdict in VERDICT_SCOPE.md.
# Cleared-flag backoff pattern (AGENTS.md lesson -- NO double-gate
# post-loop re-check). Launched under setsid (batch-43 precedent).
cd /home/hatch/workspace/mix/exploration || exit 1
LOG=new_constructions/batch56/s0_t6_b56_o3.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > new_constructions/batch56/backoff_poll_o2.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter): $(head -c 200 new_constructions/batch56/backoff_poll_o2.out)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running S0 for t6_b56_o3" >> "$LOG"
python3 run_synth.py fast_battery/candidates/t6_b56_o3/rtl.v t6_b56_o3 \
    new_constructions/batch56/s0_t6_b56_o3 >> "$LOG" 2>&1
echo "run_synth exit=$?" >> "$LOG"
echo "$(date -u +%FT%TZ) S0 COMPLETE" >> "$LOG"
