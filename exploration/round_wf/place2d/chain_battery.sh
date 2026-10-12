#!/bin/bash
# Chain: wait for screen_batch_resume.sh (PID from arg or autodetect) to finish,
# then run full battery S0->S4 + Q1 for every S2-PASS aff candidate.
# Designed to run detached. Respects the polite gate by starting only after the batch.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
WF=$EXP/round_wf
FB=$EXP/fast_battery
BATCH_PID=${1:-1885}
echo "[chain] waiting for batch driver $BATCH_PID"
while kill -0 $BATCH_PID 2>/dev/null; do sleep 60; done
echo "[chain] batch driver gone, starting batteries"
mkdir -p $WF/validation/q1
for c in wf2d_aff_a17_b17 wf2d_aff_a49_b49 wf2d_aff_a09_b25; do
  LOG=$WF/validation/logs/s2_$c.log
  if ! grep -q "VERDICT: S2-PASS" $LOG 2>/dev/null; then
    echo "[chain] $c: no S2-PASS, skipping"; continue
  fi
  echo "[chain] === battery $c ==="
  rm -rf $FB/candidates/$c
  cp -r $WF/validation/candidates/$c $FB/candidates/$c
  bash $FB/run_fast_battery.sh $c > $WF/validation/logs/battery_$c.log 2>&1
  echo "[chain] battery rc=$? for $c (tail: $(tail -1 $WF/validation/logs/battery_$c.log | cut -c1-100))"
  echo "[chain] === Q1 $c ==="
  python3 $EXP/round13/q1_sacbic.py $c $WF/validation/q1 > $WF/validation/logs/q1_$c.log 2>&1
  echo "[chain] Q1 rc=$? : $(python3 -c "
import json;d=json.load(open('$WF/validation/q1/q1_$c.json'))
print('sac_z5=%d bic_maxcorr=%.5f'%(d['sac_z5'],d['bic_maxcorr']))" 2>/dev/null)"
done
echo "[chain] ALL DONE"
