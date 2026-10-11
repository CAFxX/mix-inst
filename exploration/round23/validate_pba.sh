#!/bin/bash
# Full-battery validation driver for round-23 P-box challengers:
#   r23_spn_mix4r_pba19b01_nw (27.8u) and r23_spn_mix4r_pba27b01_nw (28.2u)
# Stages: xcheck(10k) -> battery S3(strided)+S4 -> Q1 (SAC/BIC) -> bijectivity (2M x 2 keys).
# Detached, lockfile-guarded, polite-gated on foreign heavies (<=2 total).
set -u
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"

EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R23=$EXP/round23
LOG=$R23/validate_pba.log
LOCK=/tmp/validate_pba.lock

exec 9>"$LOCK"
flock -n 9 || { echo "another validate_pba instance holds the lock; exiting"; exit 0; }

log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }

wait_for_slot() {
  while :; do
    n=$(ps aux | grep -E "yosys|RNG_test|diffprof_|s1_screen" | grep -v grep | wc -l)
    [ "$n" -lt 2 ] && break
    log "[polite] $n heavies, sleeping 60s"
    sleep 60
  done
}

CANDS="r23_spn_mix4r_pba19b01_nw r23_spn_mix4r_pba27b01_nw"

for CAND in $CANDS; do
  log "===== $CAND ====="
  wait_for_slot
  log "battery S3+S4 start $CAND"
  bash "$FB/run_fast_battery.sh" "$CAND" 3 >> "$LOG" 2>&1
  rc=$?
  log "battery $CAND rc=$rc"
  if [ $rc -ne 0 ]; then
    log "KILL: $CAND died in S3/S4 (see $FB/results/$CAND/battery.log)"
    continue
  fi

  # xcheck: 10k C-vs-Python (gates all C stages)
  log "xcheck 10k $CAND"
  python3 "$FB/src/xcheck.py" "$CAND" "$FB/build/diffprof_$CAND" 10000 \
    "$FB/results/$CAND/xcheck_vecs.txt" >> "$LOG" 2>&1 || {
    log "KILL: xcheck failed $CAND"; continue; }
  log "xcheck PASS $CAND"

  # Q1: SAC/BIC
  log "Q1 start $CAND"
  python3 "$EXP/round13/q1_sacbic.py" "$CAND" "$R23/q1" >> "$LOG" 2>&1
  q1v=$(python3 -c "
import json
d=json.load(open('$R23/q1/q1_$CAND.json'))
print('sac_z5=%d bic_maxcorr=%.6f sac_maxdev=%.4f avalanche_mean=%.2f'%(d['sac_z5'],d['bic_maxcorr'],d['sac_maxdev'],d['avalanche_mean']))" 2>/dev/null)
  log "Q1 done $CAND: $q1v"

  # bijectivity: 2M random inputs x 2 keys, collision-free
  log "bijectivity start $CAND"
  gcc -O2 -o "$FB/build/bij_$CAND" /tmp/bij_check.c "$FB/candidates/$CAND/impl.c" >> "$LOG" 2>&1 \
    || { log "build bij failed $CAND"; continue; }
  KEY1=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][0])")
  KEY2=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][1])")
  "$FB/build/bij_$CAND" "$KEY1" 2000000 0x123456789abcdef0 >> "$LOG" 2>&1; r1=$?
  "$FB/build/bij_$CAND" "$KEY2" 2000000 0xfedcba9876543210 >> "$LOG" 2>&1; r2=$?
  log "bijectivity $CAND key1_rc=$r1 key2_rc=$r2 (0=clean)"
  log "===== $CAND DONE ====="
done

log "ALL VALIDATION DONE"
