#!/bin/bash
# Round 23 P689 S0+S1+S2 for 7 new candidates (rtlcheck already PASS).
# Usage: setsid nohup bash p689_s0s1s2.sh > p689_s0s1s2.log 2>&1 < /dev/null &
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R23=$EXP/round23
LOCK=$R23/p689_s0s1s2.lock
exec 9>"$LOCK"
flock -n 9 || { echo "[p689s0] another instance holds the lock, exiting"; exit 0; }

HEAVY_RE="yosys|RNG_test|diffprof_|s1_screen|iverilog|vvp|openroad"
foreign_heavies() { ps -eo args | grep -E "$HEAVY_RE" | grep -v grep | grep -v "round23" | grep -v "r23_spn" | grep -v "p689" | wc -l; }
log() { echo "$(date -u +%FT%TZ) $1" >> $R23/progress.log; echo "$(date -u +%FT%TZ) $1"; }
polite_wait() {
  while [ "$(foreign_heavies)" -ge 2 ]; do
    log "[p689s0-polite] $(foreign_heavies) foreign heavies, sleeping 60s"
    sleep 60
  done
}

CANDS="r23_spn_mix4r_hs_alt_nw r23_spn_mix4r_hs_aff_nw r23_spn_mix4r_hs_rh_nw r23_spn_mix4r_mols8a_nw r23_spn_mix4r_mols8b_nw r23_spn_mix4r_mols8c_nw r23_spn_mix4r_ks0_nw"

s0_done() { grep -q "RESULT" $R23/s0/$1.log 2>/dev/null; }
s1_done() { grep -qE 'CAL_PASS|CAL_FLAG' $R23/s1_$1.log 2>/dev/null; }

log "=== p689 S0 stage ==="
for c in $CANDS; do
  if s0_done $c; then log "S0_SKIP $c"; continue; fi
  polite_wait
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 10; done
  python3 $EXP/run_synth.py $FB/candidates/$c/rtl.v $c $R23/s0/$c > $R23/s0/$c.log 2>&1 &
  log "S0_LAUNCH $c"
done
wait
for c in $CANDS; do
  v=$(grep -h RESULT $R23/s0/$c.log 2>/dev/null | tail -1 | head -c 120)
  log "S0_DONE $c $v"
done

log "=== p689 S1 stage ==="
for c in $CANDS; do
  if s1_done $c; then log "S1_SKIP $c"; continue; fi
  polite_wait
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 10; done
  python3 $FB/src/s1_screen.py $c $R23/s1/$c > $R23/s1_$c.log 2>&1 &
  log "S1_LAUNCH $c"
done
wait
for c in $CANDS; do
  v=$(grep -E 'CAL_PASS|CAL_FLAG|KILL' $R23/s1_$c.log 2>/dev/null | tail -1 | head -c 100)
  log "S1_DONE $c $v"
done

log "=== p689 S2 stage (S1 survivors only) ==="
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
log "=== p689 S0/S1/S2 complete ==="
