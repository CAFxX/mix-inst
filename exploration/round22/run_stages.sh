#!/bin/bash
# Round 22 staged battery. Cheap -> expensive, per-candidate progress logs,
# resumable after VM reboot. Max 2 concurrent heavy pipelines.
# Falsification order per sota_analytical_designs.md: S2 DIFF first (minutes),
# then S1 screen, then S3/S4. S0 (synthesis) runs before S2 to get delay.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v gcc >/dev/null || { echo "gcc NOT FOUND"; exit 1; }
command -v iverilog >/dev/null || { echo "iverilog NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R22=$EXP/round22
CANDS=$(cat $R22/CANDS.txt)
mkdir -p $R22/xcheck $R22/rtlcheck $R22/s0 $R22/s1 $R22/q1
touch $R22/progress.log

log() { echo "$1" >> $R22/progress.log; echo "$1"; }
done_mark() { grep -q "^$1 $2 " $R22/progress.log 2>/dev/null; }

stage_xcheck() {
  c=$1; done_mark XCHECK_DONE $c && { log "XCHECK_SKIP $c"; return; }
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$R22/xcheck/$c.build.err \
    || { log "XCHECK_BUILD_FAIL $c"; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $R22/xcheck/$c.vecs > $R22/xcheck/$c.log 2>&1
  log "XCHECK_DONE $c rc=$? $(tail -1 $R22/xcheck/$c.log | head -c 90)"
}
stage_rtlcheck() {
  c=$1; done_mark RTLCHECK_DONE $c && { log "RTLCHECK_SKIP $c"; return; }
  python3 $EXP/check_rtl.py round22.models.r22.$c $FB/candidates/$c/rtl.v $c $R22/rtlcheck/$c 300 > $R22/rtlcheck/$c.log 2>&1
  log "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $R22/rtlcheck/$c.log | tail -1 | head -c 80)"
}
stage_s0() {
  c=$1; done_mark S0_DONE $c && { log "S0_SKIP $c"; return; }
  python3 $EXP/run_synth.py $FB/candidates/$c/rtl.v $c $R22/s0/$c > $R22/s0/$c.log 2>&1
  log "S0_DONE $c rc=$? $(grep -h RESULT $R22/s0/$c.log | tail -1 | head -c 120)"
}
stage_s2() {
  c=$1; done_mark S2_DONE $c && { log "S2_SKIP $c"; return; }
  KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  $FB/build/diffprof_$c $KEY 22 $KILL_REP > $R22/s2_$c.log 2>&1
  log "S2_DONE $c rc=$? $(grep -E 'max\|z\||KILL|PASS' $R22/s2_$c.log | tail -2 | head -c 160)"
}
stage_s1() {
  c=$1; done_mark S1_DONE $c && { log "S1_DONE_SKIP $c"; return; }
  python3 $FB/src/s1_screen.py $c $R22/s1/$c > $R22/s1_$c.log 2>&1
  log "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $R22/s1_$c.log | tail -1 | head -c 100)"
}
stage_q1() {
  c=$1; done_mark Q1_DONE $c && { log "Q1_SKIP $c"; return; }
  python3 $EXP/round13/q1_sacbic.py $c $R22/q1 > $R22/q1_$c.log 2>&1
  rc=$?
  log "Q1_DONE $c rc=$rc $(python3 -c "
import json
d=json.load(open('$R22/q1/q1_$c.json'))
print('sac_z5=%d bic_maxcorr=%.5f sac_maxdev=%.5f'%(d['sac_z5'],d['bic_maxcorr'],d['sac_maxcorr'] if 'sac_maxcorr' in d else d['sac_maxdev']))
" 2>/dev/null)"
}

run_stage() {
  stage=$1
  for c in $CANDS; do
    while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
    stage_$stage $c &
  done
  wait
}

[ $# -ge 1 ] || { echo "usage: $0 <xcheck|rtlcheck|s0|s2|s1|q1> [more stages...]"; exit 1; }
for st in "$@"; do
  log "=== STAGE $st ==="
  run_stage $st
done
log "ALL_STAGES_DONE $@"
