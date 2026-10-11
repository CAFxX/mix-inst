#!/bin/bash
# Round 23 P6/P8/P9 pipeline: xcheck -> rtlcheck -> s0 -> s1 -> s2 for 7 new candidates.
# Usage: setsid nohup bash p689_pipeline.sh > p689_pipeline.log 2>&1 < /dev/null &
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R23=$EXP/round23
LOCK=$R23/p689_pipeline.lock
exec 9>"$LOCK"
flock -n 9 || { echo "[p689] another instance holds the lock, exiting"; exit 0; }

HEAVY_RE="yosys|RNG_test|diffprof_|s1_screen|iverilog|vvp|openroad"
foreign_heavies() { ps -eo args | grep -E "$HEAVY_RE" | grep -v grep | grep -v "round23" | grep -v "r23_spn" | grep -v "p689_pipeline" | wc -l; }
log() { echo "$(date -u +%FT%TZ) $1" >> $R23/progress.log; echo "$(date -u +%FT%TZ) $1"; }
done_mark() { grep -q " $1 $2 " $R23/progress.log 2>/dev/null; }
polite_wait() {
  while [ "$(foreign_heavies)" -ge 2 ]; do
    log "[p689-polite] $(foreign_heavies) foreign heavies, sleeping 60s"
    sleep 60
  done
}

CANDS="r23_spn_mix4r_hs_alt_nw r23_spn_mix4r_hs_aff_nw r23_spn_mix4r_hs_rh_nw r23_spn_mix4r_mols8a_nw r23_spn_mix4r_mols8b_nw r23_spn_mix4r_mols8c_nw r23_spn_mix4r_ks0_nw"

# ---- xcheck: build diffprof binary + 10k C vs model ----
for c in $CANDS; do
  done_mark XCHECK_DONE $c && { log "XCHECK_SKIP $c"; continue; }
  gcc -O2 -o $FB/build/diffprof_$c $FB/src/s2_diffprof.c $FB/candidates/$c/impl.c -lm 2>$R23/xcheck/$c.build.err \
    || { log "XCHECK_BUILD_FAIL $c"; continue; }
  python3 $R23/xcheck_fast.py $c $FB/build/diffprof_$c 10000 $R23/xcheck/$c.vecs > $R23/xcheck/$c.log 2>&1
  rc=$?
  log "XCHECK_DONE $c rc=$rc $(tail -1 $R23/xcheck/$c.log | head -c 60)"
  [ $rc -ne 0 ] && log "XCHECK_FAIL $c -- stopping pipeline for this candidate"
done

# ---- rtlcheck + s0 + s1 + s2 (heavy, polite, max 2 own jobs) ----
for c in $CANDS; do
  done_mark XCHECK_DONE $c || continue
  grep -q "XCHECK_FAIL $c" $R23/progress.log && continue

  # rtlcheck
  if ! done_mark RTLCHECK_DONE $c; then
    polite_wait
    python3 $EXP/check_rtl.py round23.models.r23.$c $FB/candidates/$c/rtl.v $c $R23/rtlcheck/$c 300 > $R23/rtlcheck/$c.log 2>&1
    log "RTLCHECK_DONE $c $(tail -1 $R23/rtlcheck/$c.log | head -c 80)"
  fi

  # s0
  if ! done_mark S0_DONE $c; then
    polite_wait
    while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 10; done
    python3 $EXP/run_synth.py $FB/candidates/$c/rtl.v $c $R23/s0/$c > $R23/s0/$c.log 2>&1 &
    log "S0_LAUNCH $c"
  fi
done
wait
for c in $CANDS; do
  v=$(grep -h RESULT $R23/s0/$c.log 2>/dev/null | tail -1 | head -c 120)
  log "S0_DONE $c $v"
done

# ---- s1 ----
for c in $CANDS; do
  done_mark XCHECK_DONE $c || continue
  grep -q "XCHECK_FAIL $c" $R23/progress.log && continue
  if ! done_mark S1_DONE $c; then
    polite_wait
    while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 10; done
    python3 $FB/src/s1_screen.py $c $R23/s1/$c > $R23/s1_$c.log 2>&1 &
    log "S1_LAUNCH $c"
  fi
done
wait
for c in $CANDS; do
  v=$(grep -E 'CAL_PASS|CAL_FLAG|KILL' $R23/s1_$c.log 2>/dev/null | tail -1 | head -c 100)
  log "S1_DONE $c $v"
done

# ---- s2 (only S1 survivors; determine from logs) ----
for c in $CANDS; do
  if grep -qE 'CAL_PASS' $R23/s1_$c.log 2>/dev/null; then
    if ! grep -qE '^KILL|^PASS' $R23/s2_$c.log 2>/dev/null; then
      polite_wait
      while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 10; done
      KILL_REP=$(cat $FB/ref/s2_kill_repeats.txt)
      KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
      $FB/build/diffprof_$c $KEY 22 $KILL_REP > $R23/s2_$c.log 2>&1 &
      log "S2_LAUNCH $c"
    else
      log "S2_SKIP $c (verdict exists)"
    fi
  else
    log "S2_SKIP $c (no S1 CAL_PASS)"
  fi
done
wait
for c in $CANDS; do
  v=$(grep -E '^KILL|^PASS' $R23/s2_$c.log 2>/dev/null | tail -1 | head -c 120)
  [ -n "$v" ] && log "S2_DONE $c $v"
done
log "=== p689 pipeline complete ==="
