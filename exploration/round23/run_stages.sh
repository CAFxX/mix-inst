#!/bin/bash
# Round 23 staged battery driver with polite concurrency.
# Usage: run_stages.sh <stage> [stage...]   (stages: rtlcheck s0 s1 s2 q1)
# Heavy binaries: yosys, RNG_test, diffprof_, s1_screen, iverilog, vvp.
# Rule: <=2 heavy pipelines system-wide; back off when >=2 FOREIGN heavies.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R23=$EXP/round23
HEAVY_RE="yosys|RNG_test|diffprof_|s1_screen|iverilog|vvp"

foreign_heavies() {
  # count heavy processes NOT belonging to round23 (exclude self by cwd marker)
  ps -eo pid,args | grep -E "$HEAVY_RE" | grep -v grep | grep -v "round23" | wc -l
}

polite_wait() {
  # wait until foreign heavies < 2; also cap own concurrency at 2
  while [ "$(foreign_heavies)" -ge 2 ]; do
    echo "[polite] $(foreign_heavies) foreign heavies, sleeping 60s"
    sleep 60
  done
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 10; done
}

log() { echo "$1" >> $R23/progress.log; echo "$1"; }
done_mark() { grep -q "^$1 $2 " $R23/progress.log 2>/dev/null; }

stage_rtlcheck() {
  c=$1; done_mark RTLCHECK_DONE $c && { log "RTLCHECK_SKIP $c"; return; }
  polite_wait
  python3 $EXP/check_rtl.py round23.models.r23.$c $FB/candidates/$c/rtl.v $c $R23/rtlcheck/$c 300 > $R23/rtlcheck/$c.log 2>&1 &
  log "RTLCHECK_LAUNCH $c"
}

stage_s0() {
  c=$1; done_mark S0_DONE $c && { log "S0_SKIP $c"; return; }
  polite_wait
  python3 $EXP/run_synth.py $FB/candidates/$c/rtl.v $c $R23/s0/$c > $R23/s0/$c.log 2>&1 &
  log "S0_LAUNCH $c"
}

stage_s1() {
  c=$1; done_mark S1_DONE $c && { log "S1_SKIP $c"; return; }
  polite_wait
  python3 $FB/src/s1_screen.py $c $R23/s1/$c > $R23/s1_$c.log 2>&1 &
  log "S1_LAUNCH $c"
}

stage_s2() {
  c=$1; done_mark S2_DONE $c && { log "S2_SKIP $c"; return; }
  polite_wait
  KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  $FB/build/diffprof_$c $KEY 22 $KILL_REP > $R23/s2_$c.log 2>&1 &
  log "S2_LAUNCH $c"
}

stage_q1() {
  c=$1; done_mark Q1_DONE $c && { log "Q1_SKIP $c"; return; }
  polite_wait
  python3 $EXP/round13/q1_sacbic.py $c $R23/q1 > $R23/q1_$c.log 2>&1 &
  log "Q1_LAUNCH $c"
}

# collect finished background jobs and record their verdicts
reap() {
  wait
  for c in $CANDS; do :; done
}

CANDS=$(cat ${R23_CANDS:-$R23/CANDS.txt})
[ $# -ge 1 ] || { echo "usage: $0 <rtlcheck|s0|s1|s2|q1>..."; exit 1; }
for st in "$@"; do
  log "=== STAGE $st ==="
  for c in $CANDS; do
    stage_$st $c
  done
  log "--- waiting for stage $st jobs ---"
  wait
  # record verdicts
  for c in $CANDS; do
    case $st in
      rtlcheck) v=$(grep -E 'RTLCHECK|PASS|FAIL' $R23/rtlcheck/$c.log 2>/dev/null | tail -1 | head -c 80);;
      s0) v=$(grep -h RESULT $R23/s0/$c.log 2>/dev/null | tail -1 | head -c 120);;
      s1) v=$(grep -E 'CAL_PASS|CAL_FLAG|KILL' $R23/s1_$c.log 2>/dev/null | tail -1 | head -c 100);;
      s2) v=$(grep -E 'max\|z\||KILL|PASS' $R23/s2_$c.log 2>/dev/null | tail -2 | tr '\n' ' ' | head -c 160);;
      q1) v=$(python3 -c "
import json
d=json.load(open('$R23/q1/q1_$c.json'))
print('sac_z5=%d bic_maxcorr=%.5f'%(d['sac_z5'],d['bic_maxcorr']))" 2>/dev/null);;
    esac
    log "${st^^}_DONE $c $v"
  done
done
log "ALL_STAGES_DONE $@"
