#!/bin/bash
# S3: PractRand incremental with early kill (fast staged battery).
# Usage: s3_practrand.sh <candidate> <gen_binary> <outdir> [key_hex] [stride]
# Stages 16MB -> 64MB -> 256MB -> 1GB, each piped DIRECTLY to RNG_test stdin64
# (no intermediate files). Parses stdout for FAIL after each stage; STOPS at
# the first FAIL. Exit 0 = all stages pass, 2 = killed at some stage.
set -u
CAND="$1"; GEN="$2"; OUTDIR="$3"; KEY="${4:-123456789abcdef0}"; STRIDE="${5:-1}"
RNG=/home/hatch/tools/practrand/PractRand/RNG_test
mkdir -p "$OUTDIR"
STAGES="16777216 67108864 268435456 1073741824"
NAMES="16MB 64MB 256MB 1GB"
i=0
for NB in $STAGES; do
  i=$((i+1)); NM=$(echo $NAMES | cut -d' ' -f$i)
  LOG="$OUTDIR/s3_practrand_${NM}.log"
  echo "[S3 $CAND] stage $NM (key=$KEY stride=$STRIDE) ..."
  # 2026-10-10 FIX (track-2): RNG_test's stdin reader treats EOF as a fatal
  # read error ("error reading from file", exit 0) INSTEAD of finalizing the
  # stage -- feeding exactly NB bytes makes the gate silently vacuous (zero
  # tests run, no FAIL possible, script reports PASS). Feed an effectively-
  # infinite non-repeating stream (4GB single invocation) and bound the test
  # with -tlmax (clean stop at the stage length via TL_MAX); -tlmin 10 keeps
  # the progressive 1KB->NM checkpoints visible. The generator dies on
  # SIGPIPE when RNG_test exits.
  "$GEN" "$KEY" 4294967296 "$STRIDE" 2>"$OUTDIR/s3_gen_${NM}.err" \
    | "$RNG" stdin64 -tlmax "$NM" -tlmin 10 > "$LOG" 2>&1
  rc=$?
  # Fail-LOUD guard (positive control): a gate that ran zero tests is
  # decoration, not evidence. Never report PASS on an empty test run.
  if ! grep -q "length=" "$LOG"; then
    echo "[S3 $CAND] LOUD INFRA FAILURE at $NM: RNG_test ran zero tests (see $LOG)"
    exit 3
  fi
  if grep -q "FAIL" "$LOG"; then
    echo "[S3 $CAND] KILL at $NM:"
    grep "FAIL" "$LOG" | head -8
    echo "[S3 $CAND] verdict: KILL@$NM"
    exit 2
  fi
  echo "[S3 $CAND] $NM: no FAIL (rng_test rc=$rc)"
done
echo "[S3 $CAND] verdict: PASS (all 4 stages, no FAIL)"
exit 0
