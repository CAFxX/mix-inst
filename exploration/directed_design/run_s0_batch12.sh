#!/bin/bash
# S0 for batch-12 (D9) candidates: authorized run_synth.py, Yosys 0.69 pinned.
# Run under nice -19; sequential. Appends RESULT lines to results/s0_batch12.log
EXP=/home/hatch/workspace/mix/exploration
DD=$EXP/directed_design
LOG=$DD/results/s0_batch12.log
mkdir -p $DD/results
echo "=== S0 batch12 start $(date -u +%H:%M:%SZ) ===" >> $LOG
for c in dd12_scsc_midori_513_a dd12_scsc_midori_12_a dd12_scsc_midori_719_a dd12_scsc_midori_1327_a dd12_scsc_midori_513_wa dd12_cscs_midori_513_a; do
    v=$DD/candidates/$c.v
    out=/tmp/s0_$c
    echo "--- $c $(date -u +%H:%M:%SZ) ---" >> $LOG
    nice -n 19 python3 $EXP/run_synth.py $v $c $out >> $LOG 2>&1
    echo "exit=$? for $c" >> $LOG
done
echo "=== S0 batch12 done $(date -u +%H:%M:%SZ) ===" >> $LOG
