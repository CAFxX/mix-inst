#!/bin/bash
# Track-2: saar11 DEEPER validation — staged S3 (64MB -> 256MB -> 1GB) then
# S4 SmallCrush for S3-1GB survivors. Resumable: skips candidates already
# verdicted in deep_summary.txt. Backoff-gated: waits for load-shed clear
# before starting (and re-checks between candidates).
# Method = validated fixed pipe (2026-10-10): effectively-infinite 4GB
# stream + RNG_test stdin64 -tlmax <stage> -tlmin 10 + fail-loud guard
# (a stage log with zero "length=" checkpoints is INFRA_FAIL, never PASS).
# Canary FIRST: identity generator (mix_hash(val,key)=val) MUST FAIL at
# 16MB, else the pipe is vacuous and the whole run aborts LOUD.
set -u
D=~/workspace/mix/exploration/gha/s3_saar11
DEEP="$D/deep"
mkdir -p "$DEEP"
RNG=/home/hatch/tools/practrand/PractRand/RNG_test
S3GEN_SRC=~/workspace/mix/exploration/fast_battery/src/s3_gen.c
KEY=123456789abcdef0
SUM="$DEEP/deep_summary.txt"
touch "$SUM"
log(){ echo "[$(date -u +%FT%TZ)] $*" | tee -a "$DEEP/deep_runner.log"; }

# ---------- backoff gate ----------
wait_clear(){
  local n=0
  while ! ~/workspace/system/bin/load-shed.sh backoff >/dev/null 2>&1; do
    n=$((n+1)); [ $((n % 10)) -eq 1 ] && log "backoff blocked (try $n), waiting 60s"
    sleep 60
  done
}

# ---------- canary: identity must FAIL ----------
if [ ! -f "$DEEP/canary_identity_16MB.log" ]; then
  wait_clear
  cat > "$DEEP/identity_impl.c" <<'EOF'
#include <stdint.h>
uint64_t mix_hash(uint64_t val, uint64_t key){ (void)key; return val; }
EOF
  gcc -O2 -o "$DEEP/gen_identity" "$S3GEN_SRC" "$DEEP/identity_impl.c" || { log "CANARY BUILD FAIL"; exit 1; }
  "$DEEP/gen_identity" "$KEY" 4294967296 2>/dev/null | "$RNG" stdin64 -tlmax 16M -tlmin 10 > "$DEEP/canary_identity_16MB.log" 2>&1
  if grep -q "FAIL" "$DEEP/canary_identity_16MB.log" && grep -q "length=" "$DEEP/canary_identity_16MB.log"; then
    log "CANARY OK: identity FAILs as required: $(grep -m1 'FAIL' "$DEEP/canary_identity_16MB.log")"
  else
    log "CANARY LOUD FAIL: identity did NOT fail — pipe vacuous, ABORTING"
    echo "CANARY_FAIL pipe-vacuous" >> "$SUM"; exit 3
  fi
fi

# ---------- staged S3 per candidate ----------
SHORTS="saar11_g0 saar11_g1 saar11_g2 saar11_g3 saar11_g4 saar11_g5 saar11_g6 saar11_g7 saar11_g8 saar11_g9 saar11_g11 saar11_g12 saar11_g14 saar11_g15 rasd3c1_100"
for short in $SHORTS; do
  if grep -q "^$short " "$SUM"; then log "$short already verdicted, skip"; continue; fi
  gen="$D/gen_$short"
  [ -x "$gen" ] || { echo "$short INFRA_FAIL gen-missing" >> "$SUM"; log "$short INFRA_FAIL gen missing"; continue; }
  verdict=""; failstage=""; failsig=""
  for stage in 64M 256M 1G; do
    wait_clear
    L="$DEEP/s3_${short}_${stage}.log"
    log "$short S3 stage $stage ..."
    "$gen" "$KEY" 4294967296 2>/dev/null | "$RNG" stdin64 -tlmax "$stage" -tlmin 10 > "$L" 2>&1
    if ! grep -q "length=" "$L"; then verdict="INFRA_FAIL"; failstage="$stage"; failsig="zero-tests"; break; fi
    if grep -q "FAIL" "$L"; then verdict="S3_KILL"; failstage="$stage"; failsig="$(grep -m2 'FAIL' "$L" | tr '\n' ' ')"; break; fi
    log "$short $stage clean ($(grep -c 'length=' "$L") checkpoints)"
  done
  if [ -z "$verdict" ]; then
    echo "$short S3_PASS_1GB" >> "$SUM"; log "$short S3 PASS all stages to 1GB"
  else
    echo "$short $verdict @$failstage $failsig" >> "$SUM"; log "$short $verdict @$failstage $failsig"
  fi
done

# ---------- S4 SmallCrush for S3-1GB survivors ----------
TU=$HOME/tools/testu01/install
for short in $SHORTS; do
  grep -q "^$short S3_PASS_1GB" "$SUM" || continue
  grep -q "^$short S4_" "$SUM" && continue
  impl=$(ls "$D"/r25_spn_pba19_sb_${short}_513_nw.impl.c 2>/dev/null || ls "$D"/*_${short}_*.impl.c 2>/dev/null | head -1)
  [ -n "$impl" ] || { echo "$short S4_INFRA_FAIL impl-missing" >> "$SUM"; continue; }
  wait_clear
  # golden probe: mix_hash(0, KEY) from the C impl itself (g0 cross-checked
  # against its meta.json golden 0x1aef715c1b5c3b19 by the supervisor).
  cat > "$DEEP/probe_$short.c" <<EOF
#include <stdio.h>
#include <stdint.h>
uint64_t mix_hash(uint64_t val, uint64_t key);
int main(void){ printf("0x%llx\n", (unsigned long long)mix_hash(0, 0x123456789abcdef0ULL)); return 0; }
EOF
  gcc -O2 -o "$DEEP/probe_$short" "$DEEP/probe_$short.c" "$impl" || { echo "$short S4_INFRA_FAIL probe-build" >> "$SUM"; continue; }
  GOLDEN=$("$DEEP/probe_$short")
  gcc -O2 -o "$DEEP/sc_$short" ~/workspace/mix/exploration/fast_battery/src/s4_smallcrush.c "$impl" \
    -DGOLDEN_OUT="$GOLDEN" -I"$TU/include" -L"$TU/lib" -ltestu01 -lprobdist -lmylib -lm \
    || { echo "$short S4_INFRA_FAIL sc-build" >> "$SUM"; continue; }
  log "$short S4 SmallCrush (golden $GOLDEN) ..."
  LD_LIBRARY_PATH="$TU/lib" "$DEEP/sc_$short" "$KEY" > "$DEEP/s4_${short}.log" 2>&1
  if grep -q "All tests were passed" "$DEEP/s4_${short}.log"; then
    echo "$short S4_PASS golden=$GOLDEN" >> "$SUM"; log "$short S4 PASS"
  else
    sig=$(grep -A2 "FAILED TESTS\|p-value" "$DEEP/s4_${short}.log" | head -4 | tr '\n' ' ')
    echo "$short S4_FAIL $sig" >> "$SUM"; log "$short S4 FAIL: $sig"
  fi
done
log "DEEP RUN COMPLETE"; echo "DEEP_COMPLETE $(date -u +%FT%TZ)" >> "$SUM"
