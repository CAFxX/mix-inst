#!/bin/bash
# Round 24 survivor pipeline: S3 (PractRand x2 configs) -> S4 (SmallCrush) ->
# 2M x 2-key bijectivity -> Q1 (SAC/BIC). One candidate at a time (inherently
# polite); polite_wait before each heavy-binary step.
# Usage: R24_CANDS=<listfile> bash run_survivors.sh   (default: CANDS_S3.txt)
# Resume-safe: skips candidates with SURV_DONE in progress.log.
# Lockfile guard: only one instance.
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
FB=$EXP/fast_battery
R24=$EXP/round24
TU=$HOME/tools/testu01/install
LOCK=$R24/survivors.lock
exec 9>"$LOCK"
flock -n 9 || { echo "[survivors] another instance holds the lock, exiting"; exit 0; }

HEAVY_RE="yosys|RNG_test|diffprof_|s1_screen|iverilog|vvp"
foreign_heavies() { ps -eo args | grep -E "$HEAVY_RE" | grep -v grep | grep -v "round24" | grep -v "r24_spn" | wc -l; }
polite_wait() { while [ "$(foreign_heavies)" -ge 2 ]; do echo "[polite] $(foreign_heavies) foreign heavies, sleeping 60s"; sleep 60; done; }
log() { echo "$(date -u +%FT%TZ) $1" >> $R24/progress.log; echo "$(date -u +%FT%TZ) $1"; }
done_mark() { grep -q "$1 $2 " $R24/progress.log 2>/dev/null; }

CANDS=$(cat ${R24_CANDS:-$R24/CANDS_S3.txt})
[ -n "$CANDS" ] || { log "SURVIVORS: empty candidate list, nothing to do"; exit 0; }

run_one() {
  c=$1
  done_mark SURV_DONE $c && { log "SURV_SKIP $c"; return; }
  OUT=$R24/survivors/$c
  mkdir -p $OUT
  log "SURV_LAUNCH $c"

  # builds (cheap)
  gcc -O2 -o $FB/build/gen_$c $FB/src/s3_gen.c $FB/candidates/$c/impl.c \
    || { log "SURV_FAIL $c build gen"; return; }
  GOLDEN_OUT=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['goldens'][0]['out'])")
  gcc -O2 -o $FB/build/sc_$c $FB/src/s4_smallcrush.c $FB/candidates/$c/impl.c \
    -DGOLDEN_OUT="$GOLDEN_OUT" -I"$TU/include" -L"$TU/lib" \
    -ltestu01 -lprobdist -lmylib -lm \
    || { log "SURV_FAIL $c build smallcrush"; return; }
  gcc -O2 -o $FB/build/bij_$c $FB/src/s5_bijcheck.c $FB/candidates/$c/impl.c \
    || { log "SURV_FAIL $c build bij"; return; }

  KEY1=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][0])")
  KEY2=$(python3 -c "import json;print(json.load(open('$FB/candidates/$c/meta.json'))['practrand_keys'][1])")

  # S3: PractRand 16M->64M->256M->1G, early kill; then strided 2nd key
  polite_wait
  bash $FB/src/s3_practrand.sh "$c" "$FB/build/gen_$c" "$OUT" "$KEY1" 1 > $OUT/s3.log 2>&1 \
    || { log "SURV_FAIL $c S3-practrand (see $OUT/s3.log)"; return; }
  log "SURV_S3_PASS $c"
  polite_wait
  bash $FB/src/s3_practrand.sh "${c}_strided" "$FB/build/gen_$c" "$OUT/strided" "$KEY2" 0x9E3779B97F4A7C15 > $OUT/s3b.log 2>&1 \
    || { log "SURV_FAIL $c S3-strided (see $OUT/s3b.log)"; return; }
  log "SURV_S3B_PASS $c"

  # S4: TestU01 SmallCrush
  # (verdict parse: TestU01 prints "All tests were passed" on success and
  # "gave a p-value outside [0.001, 0.999]:" + table on failure; the word
  # "FAIL" never appears, so a grep -q FAIL check would silently pass a
  # failing candidate — the p-value-list check is the real verdict)
  polite_wait
  export LD_LIBRARY_PATH="$TU/lib:${LD_LIBRARY_PATH:-}"
  $FB/build/sc_$c "$KEY1" > $OUT/s4.log 2>&1 \
    || { log "SURV_FAIL $c S4-smallcrush (see $OUT/s4.log)"; return; }
  if grep -q "gave a p-value outside" $OUT/s4.log; then
    log "SURV_FAIL $c S4-smallcrush p-value outside [0.001,0.999] (see $OUT/s4.log)"; return
  fi
  grep -q "All tests were passed" $OUT/s4.log \
    || { log "SURV_FAIL $c S4-smallcrush no pass confirmation (see $OUT/s4.log)"; return; }
  log "SURV_S4_PASS $c"

  # bijectivity: 2M x 2 keys, zero collisions tolerated
  $FB/build/bij_$c "$KEY1" 2000000 0x1234 > $OUT/bij1.log 2>&1 \
    || { log "SURV_FAIL $c bij key1 (see $OUT/bij1.log)"; return; }
  $FB/build/bij_$c "$KEY2" 2000000 0x5678 > $OUT/bij2.log 2>&1 \
    || { log "SURV_FAIL $c bij key2 (see $OUT/bij2.log)"; return; }
  log "SURV_BIJ_PASS $c (2M x 2 keys collision-free)"

  # Q1: SAC/BIC
  mkdir -p $R24/q1
  python3 $EXP/round13/q1_sacbic.py $c $R24/q1 > $OUT/q1.log 2>&1 \
    || { log "SURV_FAIL $c Q1 (see $OUT/q1.log)"; return; }
  q=$(python3 -c "
import json
d=json.load(open('$R24/q1/q1_$c.json'))
print('sac_z5=%d bic_maxcorr=%.5f'%(d['sac_z5'],d['bic_maxcorr']))" 2>/dev/null)
  log "SURV_Q1 $c $q"

  log "SURV_DONE $c ALL_PASS q1=[$q]"
}

log "=== SURVIVORS start ==="
for c in $CANDS; do run_one $c; done
log "=== SURVIVORS complete ==="
