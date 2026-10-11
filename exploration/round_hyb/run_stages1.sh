#!/bin/bash
# Hybridization round: cheap -> expensive stages (xcheck, rtlcheck, S0, S1),
# per-candidate progress logs, resumable after VM reboot. 2 parallel max.
# Before launching heavy (S0/synth) stages, gate on system-wide load:
#   ps aux | grep -E "run_synth|run_fast_battery|yosys|RNG_test" | grep -v grep | wc -l
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
command -v gcc >/dev/null || { echo "gcc NOT FOUND"; exit 1; }
command -v iverilog >/dev/null || { echo "iverilog NOT FOUND"; exit 1; }
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
RH=$EXP/round_hyb
CANDS=$(cat $RH/CANDS.txt)
mkdir -p $RH/xcheck $RH/rtlcheck $RH/s0 $RH/s1
touch $RH/progress.log

log() { echo "$1" >> $RH/progress.log; echo "$1"; }
done_mark() { grep -q "^$1 $2 " $RH/progress.log 2>/dev/null; }

stage_xcheck() {
  c=$1; done_mark XCHECK_DONE $c && { log "XCHECK_SKIP $c"; return; }
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$RH/xcheck/$c.build.err \
    || { log "XCHECK_BUILD_FAIL $c"; return; }
  python3 $FB/src/xcheck.py $c $FB/build/diffprof_$c 10000 $RH/xcheck/$c.vecs > $RH/xcheck/$c.log 2>&1
  log "XCHECK_DONE $c rc=$? $(tail -1 $RH/xcheck/$c.log | head -c 90)"
}
stage_rtlcheck() {
  c=$1; done_mark RTLCHECK_DONE $c && { log "RTLCHECK_SKIP $c"; return; }
  python3 $EXP/check_rtl.py round_hyb.models.rhyb.$c $FB/candidates/$c/rtl.v $c $RH/rtlcheck/$c 300 > $RH/rtlcheck/$c.log 2>&1
  log "RTLCHECK_DONE $c rc=$? $(grep -E 'RTLCHECK|PASS|FAIL' $RH/rtlcheck/$c.log | tail -1 | head -c 80)"
}
heavy_gate() {
  # never exceed 2 concurrent heavy pipelines system-wide
  # (counts processes incl. S2 diffprof_; 2026-10-03: name-based counting
  # silently missed rh_*/r22c_* pipelines and violated the cap)
  while [ $(ps aux | grep -E "run_synth|run_fast_battery|yosys|RNG_test|diffprof_" | grep -v grep | wc -l) -ge 2 ]; do
    sleep 300
  done
}
stage_s0() {
  c=$1; done_mark S0_DONE $c && { log "S0_SKIP $c"; return; }
  heavy_gate
  python3 $EXP/run_synth.py $FB/candidates/$c/rtl.v $c $RH/s0/$c > $RH/s0/$c.log 2>&1
  log "S0_DONE $c rc=$? $(grep -h RESULT $RH/s0/$c.log | tail -1 | head -c 120)"
}
stage_s1() {
  # ABSOLUTE outdir required (round-7 lesson: s1_screen.py chdirs internally)
  c=$1; done_mark S1_DONE $c && { log "S1_SKIP $c"; return; }
  python3 $FB/src/s1_screen.py $c $RH/s1/$c > $RH/s1_$c.log 2>&1
  log "S1_DONE $c rc=$? $(grep -E 'CAL_PASS|CAL_FLAG|KILL' $RH/s1_$c.log | tail -1 | head -c 100)"
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
