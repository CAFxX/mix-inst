#!/bin/bash
# Track-4 quality-reference role: S3-16MB (PractRand stdin64, core test set) on the 5 clean references.
# Generator: fast_battery/src/s3_gen.c (sequential counter v*stride, key=0x123456789abcdef0, stride=1),
# bit-exact vs model.py 100/100 (s3_verify run 2026-10-10T20:03Z). RNG_test: ~/tools/practrand/PractRand/RNG_test.
# Each run feeds 16MB (16777216 bytes); RNG_test stops at EOF ("error reading from file" = normal).
# Continues through anomalies — every candidate gets its full 16MB verdict.
set -u
D=~/workspace/mix/exploration/directed_design/s3_ref
R=~/tools/practrand/PractRand/RNG_test
cd "$D" || exit 1
for n in dd14_ax1_shl2_shr6 dd13_ax2_ssss_midori_513 dd1_lin_5_13_nw dd1_lin_8_15_nw dd1_lin_5_9_nw; do
  echo "[S3 $n] start $(date -u +%FT%TZ)" | tee -a chain.log
  ./s3gen_$n 123456789abcdef0 16777216 1 | "$R" stdin64 > "${n}_16MB.log" 2>&1
  echo "[S3 $n] pipeline_exit=${PIPESTATUS[0]}/${PIPESTATUS[1]} done $(date -u +%FT%TZ)" | tee -a chain.log
done
echo "[S3 chain] ALL DONE $(date -u +%FT%TZ)" | tee -a chain.log
