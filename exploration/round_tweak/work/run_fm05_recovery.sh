#!/bin/bash
# Recovery for the 2026-10-11 07:46Z died-at-PROMOTE: sweep.py died right after
# logging "PROMOTE rtw_ab48_fm05 -> full battery", so the Q1 + battery stages
# never ran, and the restart's probe_terminal treats fm05 as terminal
# (pareto_win_any is global vs 19.8u; the N8 nb rule pareto_win_delay is local
# to the 38.3u bar). This script replays exactly what the sweep would have done:
# Q1 (bic<=0.02 gate) -> full battery S1..S4.
# Resume: deterministic — Q1/battery write their own logs; re-running is idempotent.
# Idempotent: skips stages whose verdict artifacts already exist.
set -u
EXP=/home/hatch/workspace/mix/exploration
WORK=$EXP/round_tweak/work
NAME=rtw_ab48_fm05
LOG=$WORK/fm05_recovery.log
Q1J=$WORK/q1/q1_${NAME}.json
BATT=$EXP/fast_battery/results/${NAME}/battery.log
exec >>"$LOG" 2>&1
echo "[fm05-recovery $(date -u +%H:%M:%S)] start"

# backoff gate (poll <= 6h)
deadline=$(( $(date +%s) + 21600 ))
while ! /home/hatch/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; do
  if [ $(date +%s) -gt $deadline ]; then
    echo "[fm05-recovery $(date -u +%H:%M:%S)] BACKOFF TIMEOUT 6h, exiting LOUD"; exit 3
  fi
  sleep 60
done

# Q1 gate (skip if already done)
if [ -f "$Q1J" ]; then
  echo "[fm05-recovery] Q1 already done: $(cat "$Q1J")"
else
  echo "[fm05-recovery $(date -u +%H:%M:%S)] running Q1"
  python3 $EXP/round13/q1_sacbic.py $NAME $WORK/q1
fi
BIC=$(python3 -c "import json;d=json.load(open('$Q1J'));print(d.get('bic_maxcorr'))" 2>/dev/null)
echo "[fm05-recovery] Q1 bic_maxcorr=$BIC"
if [ -f "$Q1J" ]; then
  OK=$(python3 -c "
import json
d=json.load(open('$Q1J'))
b=d.get('bic_maxcorr')
print('yes' if (b is not None and b<=0.02) else 'no')")
else
  echo "[fm05-recovery] Q1 FAILED to produce $Q1J, exiting LOUD"; exit 2
fi
if [ "$OK" != "yes" ]; then
  echo "[fm05-recovery] Q1 bic gate FAILED ($BIC > 0.02) -> battery SKIPPED (per N8 rule), done"; exit 0
fi

# full battery (skip if already done)
if [ -f "$BATT" ] && grep -qE "BATTERY-(PASS|FAIL)" "$BATT"; then
  echo "[fm05-recovery] battery already complete:"; tail -3 "$BATT"; exit 0
fi
echo "[fm05-recovery $(date -u +%H:%M:%S)] running full battery"
bash $EXP/fast_battery/run_fast_battery.sh $NAME
echo "[fm05-recovery $(date -u +%H:%M:%S)] battery rc=$?"
tail -5 "$BATT" 2>/dev/null
