#!/bin/bash
# Q2 runner: 8 candidates x 5 reductions, max 2 concurrent PractRand pipelines.
# Each: qgen <key> 1GB <red> | RNG_test stdin64 > q2_<cand>_<red>.log
cd ~/workspace/mix/exploration/quality
PR=~/tools/practrand/PractRand/RNG_test
KEY=123456789ABCDEF0
NBYTES=1073741824
CANDS="r7_feist8_s1_1sbox r7_feist8_r311 r7_feist8_spn_nw r7_feist8_r517 r6_feist8_spn r7_feist8_rksimple r7_feist8_rkcheap r7_feist8_gift"
REDS="low8 low16 low32 high32 xor32"

run_one() {
    local c=$1 r=$2
    local log="q2_${c}_${r}.log"
    if [ -f "$log" ] && grep -q "no anomalies" "$log"; then
        echo "SKIP $c/$r (already PASS)"
        return 0
    fi
    echo "START $c/$r $(date +%H:%M:%S)"
    ./qgen_$c $KEY $NBYTES $r 2>"$log.generr" | $PR stdin64 > "$log" 2>&1
    local rc=$?
    echo "DONE $c/$r rc=$rc $(date +%H:%M:%S)"
}

# simple 2-slot job control
for c in $CANDS; do
  for r in $REDS; do
    while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 5; done
    run_one $c $r &
  done
done
wait
echo ALL_Q2_DONE
