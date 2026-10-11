#!/bin/bash
# Round 19 full staged battery. Cheap -> expensive, per-candidate progress
# logs, resumable after VM reboot (round-13 lesson). 2 parallel max.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v gcc >/dev/null || { echo "gcc NOT FOUND"; exit 1; }
command -v iverilog >/dev/null || { echo "iverilog NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R19=$EXP/round19
CANDS=$(cat $R19/CANDS.txt)
mkdir -p $R19/xcheck $R19/rtlcheck $R19/s0 $R19/s1
touch $R19/progress.log

log() { echo "$1" >> $R19/progress.log; echo "$1"; }
done_mark() { grep -q "^$1 $2 " $R19/progress.log 2>/dev/null; }

stage_xcheck() {
  c=$1; done_mark XCHECK_DONE $c && { log "XCHECK_SKIP $c"; return; }
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$R19/xcheck/$c.build.err \
    || { log "XCHECK_BUILD_FAIL $c"; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $R19/xcheck/$c.vecs > $R19/xcheck/$c.log 2>&1
  log "XCHECK_DONE $c rc=$? $(tail -1 $R19/xcheck/$c.log | head -c 90)"
}
stage_rtlcheck() {
  c=$1; done_mark RTLCHECK_DONE $c && { log "RTLCHECK_SKIP $c"; return; }
  python3 $EXP/check_rtl.py round19.models.r19.$c $FB/candidates/$c/rtl.v $c $R19/rtlcheck/$c 300 > $R19/rtlcheck/$c.log 2>&1
  log "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $R19/rtlcheck/$c.log | tail -1 | head -c 80)"
}
stage_s0() {
  c=$1; done_mark S0_DONE $c && { log "S0_SKIP $c"; return; }
  python3 $EXP/run_synth.py $FB/candidates/$c/rtl.v $c $R19/s0/$c > $R19/s0/$c.log 2>&1
  log "S0_DONE $c rc=$? $(grep -h RESULT $R19/s0/$c.log | tail -1 | head -c 120)"
}
stage_s1() {
  c=$1; done_mark S1_DONE $c && { log "S1_SKIP $c"; return; }
  python3 $FB/src/s1_screen.py $c $R19/s1/$c > $R19/s1_$c.log 2>&1
  log "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $R19/s1_$c.log | tail -1 | head -c 100)"
}

run_stage() {
  stage=$1
  for c in $CANDS; do
    while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
    stage_$stage $c &
  done
  wait
  log "ALL_${stage^^}_DONE"
}

run_stage xcheck
run_stage rtlcheck
run_stage s0
run_stage s1
log "BATTERY_STAGES_1_DONE"
