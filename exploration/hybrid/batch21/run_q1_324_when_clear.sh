#!/bin/bash
# Q1 for hyb28_mu5_324 (queued by mix-search-status-30m 09:31 run, 2026-10-11).
# 324: S1 CAL_PASS, S0 19.3u XCHECK-clean (<19.8u bar), S2/S3/S3b/S4 PASS.
# Q1 (sac_z5=0 mandatory for Frontier S claim; bic reported) is the last gate.
# Idempotent: skip if q1 output already exists.
EXP=/home/hatch/workspace/mix/exploration
OUT=$EXP/fast_battery/results/hyb28_mu5_324
CAND=hyb28_mu5_324
LOG=$EXP/hybrid/batch21/q1_324.log
if [ -f "$OUT/q1_$CAND.json" ]; then
  echo "[q1-324] already done, skipping" >> $LOG
  exit 0
fi
i=0
while [ $i -lt 360 ]; do
  if $HOME/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; then
    echo "[q1-324] backoff CLEAR after $i polls $(date -u +%FT%TZ)" >> $LOG
    nice -n 10 python3 $EXP/round13/q1_sacbic.py $CAND $OUT >> $LOG 2>&1
    rc=$?
    echo "[q1-324] rc=$rc $(date -u +%FT%TZ)" >> $LOG
    if [ -f "$OUT/q1_$CAND.json" ]; then
      python3 -c "
import json
d=json.load(open('$OUT/q1_${CAND}.json'))
print('Q1', '$CAND', 'sac_z5=', d.get('sac_z5'), 'sac_maxdev=', round(d.get('sac_maxdev',0),5), 'bic_maxcorr=', round(d.get('bic_maxcorr',0),5), 'avalanche_mean=', round(d.get('avalanche_mean',0),2))
" >> $LOG
    fi
    exit $rc
  fi
  i=$((i+1)); sleep 60
done
echo "[q1-324] backoff never cleared in 6h, giving up LOUD" >> $LOG
exit 1
