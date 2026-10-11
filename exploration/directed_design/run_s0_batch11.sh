#!/bin/bash
# S0 for batch-11 (D8) candidates: authorized run_synth.py, Yosys 0.69 pinned.
# Run under nice -19; sequential. Appends RESULT lines to results/s0_batch11.log
EXP=/home/hatch/workspace/mix/exploration
DD=$EXP/directed_design
LOG=$DD/results/s0_batch11.log
mkdir -p $DD/results
echo "=== S0 batch11 start $(date -u +%H:%M:%SZ) ===" >> $LOG
for c in dd11_ccs_a dd11_css_a dd11_csc_a dd11_ccs_wa; do
    v=$DD/candidates/$c.v
    out=/tmp/s0_$c
    echo "--- $c $(date -u +%H:%M:%SZ) ---" >> $LOG
    nice -n 19 python3 $EXP/run_synth.py $v $c $out >> $LOG 2>&1
    echo "exit=$? for $c" >> $LOG
done
echo "=== S0 batch11 done $(date -u +%H:%M:%SZ) ===" >> $LOG
