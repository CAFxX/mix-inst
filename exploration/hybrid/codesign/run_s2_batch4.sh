#!/bin/bash
# Batch-4 S2 driver (resume design-layer): differential profile for S1 qualifiers.
# Idempotent: skips candidates with a finished s2.out (contains PASS or KILL).
# Waits for the S1 rest-batch (s1_batch4_rest.log S1_REST_ALLDONE) before starting,
# preserving polite-mode concurrency-1. Detached launch expected.
set -u
# Exclusive lock: prevent duplicate driver instances (two incidents 2026-10-07/08:
# overlapping S1/S2 drivers writing the same outdirs). Second instance exits.
LOCKF=$CD/s2_batch4.lock
exec 9>"$LOCKF"
flock -n 9 || { echo "$(date -u): S2 batch-4 driver already running (lock held), exiting." >> "$LOG"; exit 2; }
export TMPDIR=~/workspace/tmp
mkdir -p ~/workspace/tmp
EXP=~/workspace/mix/exploration
FB=$EXP/fast_battery
CD=$EXP/hybrid/codesign
S2BIN=$CD/s2_bin
S2RES=$CD/s2_results
S1RES=$CD/s1_results
LOG=$CD/s2_batch4.log
KEY=0x123456789abcdef0
LOGBASE=$EXP/hybrid/NEXT_ITER_STATUS.md
mkdir -p "$S2BIN" "$S2RES"

hb() { echo "$(date '+%Y-%m-%d %H:%M %Z'): $1" >> "$LOGBASE"; }

{
echo "=== S2 batch-4 driver start $(date -u) ==="

# Wait for the S1 rest-batch to drain (max 8h)
WAITED=0
while ! grep -q S1_REST_ALLDONE "$CD/s1_batch4_rest.log" 2>/dev/null; do
  if [ "$WAITED" -ge 480 ]; then echo "WAIT TIMEOUT 8h, proceeding anyway"; break; fi
  sleep 60; WAITED=$((WAITED+1))
done
echo "S1 batch marker seen after ${WAITED}min wait"

for c in cd2_p_a43b7_l513_nw cd2_p_a53b1_l513_nw cd2_p_a3b7_l513_nw cd2_p_a61b1_l513_nw \
         cd2_p_a11b7_l311_nw cd2_p_a11b3_l311_nw cd2_p_a3b1_l311_nw cd2_p_a53b1_l311_nw \
         cd2_p_a53b2_l311_nw cd2_p_a61b1_l311_nw cd2_p_a9b1_l311_nw; do
  OUT=$S2RES/$c/s2.out
  if [ -f "$OUT" ] && grep -qE "^(PASS|KILL)" "$OUT"; then
    echo "SKIP $c (s2 done: $(grep -E '^(PASS|KILL)' "$OUT" | tail -1))"
    continue
  fi
  SJ=$S1RES/$c/s1_result.json
  if [ ! -f "$SJ" ]; then echo "SKIP $c (no s1_result.json)"; continue; fi
  V=$(python3 -c "import json;print(json.load(open('$SJ')).get('verdict'))" 2>/dev/null)
  if [ "$c" = "cd2_p_a53b1_l513_nw" ]; then
    case "$V" in FLAG) ;; *) echo "SKIP $c (S1=$V, not FLAG)"; continue;; esac
  else
    [ "$V" = "CAL_PASS" ] || { echo "SKIP $c (S1=$V)"; continue; }
  fi
  echo "=== S2 $c (S1=$V) ==="
  mkdir -p "$S2RES/$c"
  gcc -O2 -o "$S2BIN/dp_$c" "$FB/src/s2_diffprof.c" "$FB/candidates/$c/impl.c" -lm \
    || { echo "BUILD FAIL $c"; continue; }
  # 2400s timeout: S2 binaries can hang (see rtw_fm23_31, cd2_p_a9b1_l311_nw).
  # Fail closed on timeout: record a TIMEOUT marker, keep partial output, move on.
  timeout 2400 nice -n 19 "$S2BIN/dp_$c" "$KEY" 22 10 > "$OUT" 2>&1
  RC=$?
  if [ $RC -eq 124 ]; then
    echo "TIMEOUT: S2 binary hung >2400s, skipped fail-closed, no promotion; re-probe eligible" >> "$OUT"
  fi
  echo "--- $c: $(grep -E '^(PASS|KILL)' "$OUT" | tail -1)"
  hb "(batch4 S2) $c = $(grep -E '^(PASS|KILL)' "$OUT" | tail -1)"
done
echo S2_BATCH4_ALLDONE
} >> "$LOG" 2>&1
