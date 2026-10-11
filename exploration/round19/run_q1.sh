#!/bin/bash
# Round 19 Q1: SAC/BIC spot check. Args: candidate list.
# Same procedure as round 13/18 (q1_sacbic.py, N=2^18, fixed key) — numbers
# are comparable across rounds. Writes round19/q1/q1_<cand>.json.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
R19=$EXP/round19
CANDS="$@"
run_one() {
  c=$1
  if grep -q "^Q1_DONE $c " $R19/progress.log 2>/dev/null; then
    echo "Q1_SKIP $c (already done)"; return
  fi
  python3 $EXP/round13/q1_sacbic.py $c $R19/q1 > $R19/q1_$c.log 2>&1
  rc=$?
  echo "Q1_DONE $c rc=$rc $(python3 -c "
import json
d=json.load(open('$R19/q1/q1_$c.json'))
print('sac_z5=%d bic_maxcorr=%.5f sac_maxdev=%.5f'%(d['sac_z5'],d['bic_maxcorr'],d['sac_maxcorr'] if 'sac_maxcorr' in d else d['sac_maxdev']))
" 2>/dev/null)" >> $R19/progress.log
}
for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo "ALL_Q1_DONE" >> $R19/progress.log
