#!/bin/bash
# Full-battery validation for wf2d_aff_a17_b17 (wire-friendly 2D track's first S2 survivor).
# Stages: copy -> S0 -> S1 -> xcheck(10k) -> battery S3/S4 (from stage 3) -> Q1 -> bijectivity (2M x 2 keys).
# S2 already PASS (validation/logs/s2_wf2d_aff_a17_b17.log) — not re-run.
# Detached, lockfile-guarded, polite-gated on foreign heavies (<=2 total).
set -u
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"

EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
WF=$EXP/round_wf/validation
LOG=$WF/validate_a17b17.log
LOCK=/tmp/validate_a17b17.lock

exec 9>"$LOCK"
flock -n 9 || { echo "another validate_a17b17 instance holds the lock; exiting" >> "$LOG"; exit 0; }

log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }

wait_for_slot() {
  while :; do
    n=$(ps aux | grep -E "yosys|RNG_test|diffprof_|s1_screen" | grep -v grep | wc -l)
    [ "$n" -lt 2 ] && break
    log "[polite] $n heavies, sleeping 60s"
    sleep 60
  done
}

CAND=wf2d_aff_a17_b17
log "===== $CAND full battery start ====="

# 0. install candidate into fast_battery tree
if [ ! -d "$FB/candidates/$CAND" ]; then
  log "copying candidate into fast_battery/candidates"
  cp -r "$WF/candidates/$CAND" "$FB/candidates/$CAND" || { log "FATAL: copy failed"; exit 1; }
fi

OUT="$FB/results/$CAND"
mkdir -p "$OUT"

# S0: unit-delay synthesis (pinned Yosys)
wait_for_slot
log "S0 start"
python3 "$FB/src/s0_delay.py" "$CAND" "$OUT" >> "$LOG" 2>&1
rc=$?
log "S0 rc=$rc"
[ $rc -ne 0 ] && { log "KILL at S0"; exit 2; }

# S1: calibrated screen (absolute outdir)
wait_for_slot
log "S1 start"
python3 "$FB/src/s1_screen.py" "$CAND" "$OUT" >> "$LOG" 2>&1
rc=$?
log "S1 rc=$rc"
[ $rc -ne 0 ] && { log "KILL at S1"; exit 2; }

# xcheck: 10k C-vs-Python (gates C stages)
log "xcheck 10k start"
python3 "$FB/src/xcheck.py" "$CAND" "$FB/build/diffprof_$CAND" 10000 \
  "$OUT/xcheck_vecs.txt" >> "$LOG" 2>&1 || { log "KILL: xcheck failed"; exit 2; }
log "xcheck PASS"

# S3+S4: PractRand (std+strided, incremental) + SmallCrush
wait_for_slot
log "battery S3+S4 start"
bash "$FB/run_fast_battery.sh" "$CAND" 3 >> "$LOG" 2>&1
rc=$?
log "battery S3+S4 rc=$rc"
[ $rc -ne 0 ] && { log "KILL at S3/S4 (see $OUT/battery.log)"; exit 2; }

# Q1: SAC/BIC
log "Q1 start"
mkdir -p "$WF/q1"
python3 "$EXP/round13/q1_sacbic.py" "$CAND" "$WF/q1" >> "$LOG" 2>&1
q1v=$(python3 -c "
import json
d=json.load(open('$WF/q1/q1_$CAND.json'))
print('sac_z5=%d bic_maxcorr=%.6f avalanche_mean=%.2f'%(d['sac_z5'],d['bic_maxcorr'],d['avalanche_mean']))")
log "Q1 done: $q1v"

# bijectivity: 2M random inputs x 2 keys, collision-free (persistent tool)
log "bijectivity start"
gcc -O2 -o "$FB/build/bij_$CAND" "$FB/src/s5_bijcheck.c" "$FB/candidates/$CAND/impl.c" \
  >> "$LOG" 2>&1 || { log "FATAL: bij build failed"; exit 1; }
KEY1=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][0])")
KEY2=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][1])")
"$FB/build/bij_$CAND" "$KEY1" 2000000 0x123456789abcdef0 >> "$LOG" 2>&1; r1=$?
"$FB/build/bij_$CAND" "$KEY2" 2000000 0xfedcba9876543210 >> "$LOG" 2>&1; r2=$?
log "bijectivity key1_rc=$r1 key2_rc=$r2 (0=clean)"
[ $r1 -ne 0 ] || [ $r2 -ne 0 ] && { log "KILL at bijectivity"; exit 2; }

log "===== $CAND ALL VALIDATION DONE ====="
