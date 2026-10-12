#!/bin/bash
# run_fast_battery.sh <candidate> [start_stage]
# Fast staged screening pipeline for the RV64 `mix` design-space search.
# Runs S0 -> S4 in order, STOPS at the first kill/FAIL. Prints per-stage
# verdict + wall-clock time. Everything lands in results/<candidate>/.
#
# Stage order (cheap kills first):
#   S0  unit-delay synthesis probe, ratio bar <= 0.9x multiplier (sec-min;
#       includes mapped-netlist equivalence check vs the Python model)
#   S1  amended 4-family screen: PB+RD (468 cells) + LIN + DIFF   (~minutes)
#   S2  differential early-kill in C, N=2^22, 72 deltas           (seconds-min)
#   S3  PractRand incremental 16MB->64MB->256MB->1GB, early kill (sec-min)
#   S4  TestU01 SmallCrush                                       (~minutes)
#   S5  P&R + peer review: NOT automated; manual gate for survivors (see README).
#
# Exit codes: 0 = all run stages PASS; 2 = killed at some stage (see log);
#             1 = infrastructure error / bad usage.
set -u
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"

FB="$(cd "$(dirname "$0")" && pwd)"
CAND="${1:?usage: run_fast_battery.sh <candidate> [start_stage]}"
START="${2:-0}"
# TMPDIR: /tmp is a shared 512M tmpfs that fills up across projects; gcc
# temp files fail with "No space left on device" (2026-10-12 batch-29).
# Keep compiler temps on workspace disk instead. Root fix, not a workaround.
export TMPDIR="$FB/build/.gcc-tmp"
mkdir -p "$TMPDIR"
OUT="$FB/results/$CAND"
mkdir -p "$OUT" "$FB/build"
LOG="$OUT/battery.log"
: > "$LOG"

stage() { # name ; command...  -> runs, logs full output, prints tail+timing
  local name="$1"; shift
  local t0=$(date +%s)
  echo "=== S$name [$CAND] started $(date -u +%FT%TZ)" | tee -a "$LOG"
  "$@" > "$OUT/s${name}.out" 2>&1
  local rc=$?
  cat "$OUT/s${name}.out" >> "$LOG"
  local dt=$(( $(date +%s) - t0 ))
  echo "$dt" > "$OUT/s${name}_wall_s.txt"
  echo "--- S$name tail:" | tee -a "$LOG"
  tail -6 "$OUT/s${name}.out" | tee -a "$LOG"
  echo "=== S$name [$CAND] rc=$rc wall=${dt}s" | tee -a "$LOG"
  return $rc
}

fail() { echo "BATTERY-FAIL stage=$1 [$CAND] (see $LOG)"; exit 2; }

# ---- per-stage build products (idempotent) ----
BLD="$FB/build"
gcc -O2 -o "$BLD/diffprof_$CAND" "$FB/src/s2_diffprof.c" "$FB/candidates/$CAND/impl.c" -lm \
  || { echo "build diffprof failed"; exit 1; }
gcc -O2 -o "$BLD/gen_$CAND" "$FB/src/s3_gen.c" "$FB/candidates/$CAND/impl.c" \
  || { echo "build gen failed"; exit 1; }
TU=$HOME/tools/testu01/install
GOLDEN_OUT=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['goldens'][0]['out'])")
gcc -O2 -o "$BLD/sc_$CAND" "$FB/src/s4_smallcrush.c" "$FB/candidates/$CAND/impl.c" \
  -DGOLDEN_OUT="$GOLDEN_OUT" -I"$TU/include" -L"$TU/lib" \
  -ltestu01 -lprobdist -lmylib -lm \
  || { echo "build smallcrush failed"; exit 1; }

# ---- xcheck: C impl bit-exact vs Python model (gates all C stages) ----
if [ "$START" -le 1 ]; then
  stage 0a python3 "$FB/src/xcheck.py" "$CAND" "$BLD/diffprof_$CAND" 10000 "$OUT/xcheck_vecs.txt" \
    || fail "xcheck(C-vs-Python)"
fi

# ---- S0 delay ----
if [ "$START" -le 0 ]; then
  stage 0 python3 "$FB/src/s0_delay.py" "$CAND" "$OUT" || fail "S0-delay"
fi

# ---- S1 amended screen ----
if [ "$START" -le 1 ]; then
  stage 1 python3 "$FB/src/s1_screen.py" "$CAND" "$OUT" || fail "S1-screen"
fi

# ---- S2 differential early-kill ----
if [ "$START" -le 2 ]; then
  KILL_REP=$(cat "$FB/ref/s2_kill_repeats.txt")
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][0])")
  stage 2 "$BLD/diffprof_$CAND" "$KEY" 22 "$KILL_REP" || fail "S2-differential"
fi

# ---- S3 PractRand incremental ----
if [ "$START" -le 3 ]; then
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][0])")
  stage 3 bash "$FB/src/s3_practrand.sh" "$CAND" "$BLD/gen_$CAND" "$OUT" "$KEY" 1 \
    || fail "S3-practrand"
  # one strided class (cheap extra): golden-ratio stride, 2nd key
  KEY2=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][1])")
  stage 3b bash "$FB/src/s3_practrand.sh" "${CAND}_strided" "$BLD/gen_$CAND" "$OUT/strided" "$KEY2" 0x9E3779B97F4A7C15 \
    || fail "S3-practrand-strided"
fi

# ---- S4 TestU01 SmallCrush ----
if [ "$START" -le 4 ]; then
  KEY=$(python3 -c "import json;print(json.load(open('$FB/candidates/$CAND/meta.json'))['practrand_keys'][0])")
  export LD_LIBRARY_PATH="$TU/lib:${LD_LIBRARY_PATH:-}"
  stage 4 "$BLD/sc_$CAND" "$KEY" || fail "S4-smallcrush"
fi

echo "BATTERY-PASS [$CAND] all stages survived (S5 P&R+review is a manual gate)"
exit 0
