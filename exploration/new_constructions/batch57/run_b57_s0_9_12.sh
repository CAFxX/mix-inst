#!/bin/bash
# Batch-57 S0 cleanup: ranks 9-12 (fisher triage z=3.81/3.91/3.92/5.38,
# n_reject=0, pure muxD5f), never escalated. Strict bar <19.2u (frontier
# t6_b57_8 at 19.2u). run_synth.py ONLY for S0 measurement.
# Adjudicate on "RESULT" in s0_t6_b57_<k>.log:
#   crit strictly < 19.2 -> cost-ELIGIBLE -> staged battery S1->S4 -> Q1
#   cost-DOOMED (>=19.2u) -> O-entry, ledger prepend, no battery.
# Cleared-flag backoff pattern (AGENTS.md lesson). Launched under setsid.
cd /home/hatch/workspace/mix/exploration || exit 1
LOG=new_constructions/batch57/s0_t6_b57_9_12.log
deadline=$(( $(date +%s) + 12*3600 ))
echo "$(date -u +%FT%TZ) wrapper start: deadline=$deadline now=$(date +%s)" >> "$LOG"
iter=0
cleared=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  iter=$((iter+1))
  if /home/hatch/workspace/system/bin/load-shed.sh backoff > new_constructions/batch57/backoff_poll_s0_b57_9_12.out 2>&1; then
    echo "$(date -u +%FT%TZ) backoff clear after $iter polls" >> "$LOG"
    cleared=1
    break
  fi
  echo "$(date -u +%FT%TZ) waiting on backoff (poll $iter): $(head -c 200 new_constructions/batch57/backoff_poll_s0_b57_9_12.out)" >> "$LOG"
  sleep 300
done
if [ "$cleared" -ne 1 ]; then
  echo "BACKOFF-FAIL: load never cleared in 12h" >> "$LOG"; exit 4
fi
echo "$(date -u +%FT%TZ) backoff clear: running S0 for t6_b57_9..12" >> "$LOG"
for k in 9 10 11 12; do
  echo "$(date -u +%FT%TZ) S0 start t6_b57_$k" >> "$LOG"
  python3 run_synth.py fast_battery/candidates/t6_b57_$k/rtl.v t6_b57_$k \
      new_constructions/batch57/s0_t6_b57_$k >> "$LOG" 2>&1
  echo "t6_b57_$k run_synth exit=$?" >> "$LOG"
  grep "RESULT name=t6_b57_$k " "$LOG" | tail -1 >> "$LOG"
done
echo "$(date -u +%FT%TZ) S0 9-12 COMPLETE" >> "$LOG"
