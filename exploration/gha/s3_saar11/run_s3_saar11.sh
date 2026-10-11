#!/bin/bash
# Track-2: S3-16MB screen for the 15 saar11 S2-clean candidates.
# FIXED METHODOLOGY (2026-10-10): RNG_test stdin64 with FINITE piped input is
# silently vacuous in this environment (reads all input, runs zero tests,
# exits 0 with "error reading from file"). Use an effectively-infinite
# non-repeating stream (1GB single invocation) + -tlmax 16M (clean stop at
# 16MB via TL_MAX) + -tlmin 10 (show progressive 1KB->16MB checkpoints).
# Usage: run_s3_saar11.sh  (runs all 15 sequentially, ~16s each)
set -u
D=~/workspace/mix/exploration/gha/s3_saar11
RNG=/home/hatch/tools/practrand/PractRand/RNG_test
S3GEN_SRC=~/workspace/mix/exploration/fast_battery/src/s3_gen.c
KEY=123456789abcdef0
cd "$D"
: > s3_saar11_16MB_summary.txt
for f in r25_spn_pba19_sb_saar11_g*.impl.c r25_spn_pba19_sb_rasd3c1_100_513_nw.impl.c; do
  [ -f "$f" ] || continue
  name="${f%.impl.c}"
  short="$(echo "$name" | sed 's/r25_spn_pba19_sb_//;s/_513_nw//')"
  if [ ! -x "gen_$short" ]; then
    gcc -O2 -o "gen_$short" "$S3GEN_SRC" "$f" 2>"compile_$short.err" \
      || { echo "$short COMPILE_FAIL" | tee -a s3_saar11_16MB_summary.txt; continue; }
  fi
  ( "./gen_$short" "$KEY" 1073741824 2>/dev/null \
      | "$RNG" stdin64 -tlmax 16M -tlmin 10 > "s3_${short}_16MB.log" 2>"s3_${short}_16MB.err" )
  if grep -q "FAIL" "s3_${short}_16MB.log"; then
    res="KILL"; grep "FAIL" "s3_${short}_16MB.log" | head -3 >> "s3_${short}_16MB.err"
  elif grep -q "no anomalies" "s3_${short}_16MB.log"; then
    res="PASS"
  else
    res="INCONCLUSIVE"
  fi
  echo "$short $res" | tee -a s3_saar11_16MB_summary.txt
done
echo "DONE $(date -u +%FT%TZ)" | tee -a s3_saar11_16MB_summary.txt
