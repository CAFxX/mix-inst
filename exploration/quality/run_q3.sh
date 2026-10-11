#!/bin/bash
# Q3 runner: PractRand endurance, full 64-bit output, 32GB cap, max 2 concurrent.
# Generator emits exactly 32GB then closes stdout; RNG_test finalizes.
# Parse: first FAIL test name, or "32GB clean".
cd ~/workspace/mix/exploration/quality
PR=~/tools/practrand/PractRand/RNG_test
KEY=123456789ABCDEF0
NBYTES=34359738368
CANDS="r7_feist8_s1_1sbox r7_feist8_r311 r7_feist8_spn_nw r7_feist8_r517 r6_feist8_spn r7_feist8_rksimple r7_feist8_rkcheap r7_feist8_gift"

# build per-candidate full-output generators from s3_gen.c
S3=~/workspace/mix/exploration/fast_battery/src/s3_gen.c
C=~/workspace/mix/exploration/fast_battery/candidates
for n in $CANDS; do
  if [ ! -x "q3gen_$n" ]; then
    gcc -O2 -o "q3gen_$n" $S3 $C/$n/impl.c || echo "BUILD FAIL $n"
  fi
done

run_one() {
    local c=$1
    local log="q3_${c}.log"
    if [ -f "$log" ] && grep -q "length= 32 gigabytes" "$log" && grep -q "no anomalies" "$log"; then
        echo "SKIP $c (already 32GB clean)"
        return 0
    fi
    # remove partial log so we don't confuse parsers
    rm -f "$log"
    echo "START $c $(date +%H:%M:%S)"
    ./q3gen_$c $KEY $NBYTES 2>"$log.generr" | $PR stdin64 > "$log" 2>&1
    local rc=$?
    echo "DONE $c rc=$rc $(date +%H:%M:%S)"
}

for c in $CANDS; do
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 10; done
  run_one $c &
done
wait
echo ALL_Q3_DONE
