#!/bin/bash
# S0 for batch-10 (D7) candidates: authorized run_synth.py, Yosys 0.69 pinned.
# Run under nice -19; sequential. Appends RESULT lines to results/s0_batch10.log
EXP=/home/hatch/workspace/mix/exploration
DD=$EXP/directed_design
LOG=$DD/results/s0_batch10.log
mkdir -p $DD/results
echo "=== S0 batch10 start $(date -u +%H:%M:%SZ) ===" >> $LOG
for c in dd10_scsc_linsbox_a dd10_scsc_linchi_a dd10_sccs_linsbox_a \
         dd10_scsc_singlerot_a dd10_scsc_singlerot_linsbox_a dd10_scsc_linsbox_rm; do
    v=$DD/candidates/$c.v
    out=/tmp/s0_$c
    echo "--- $c $(date -u +%H:%M:%SZ) ---" >> $LOG
    nice -n 19 python3 $EXP/run_synth.py $v $c $out >> $LOG 2>&1
    echo "exit=$? for $c" >> $LOG
done
echo "=== S0 batch10 done $(date -u +%H:%M:%SZ) ===" >> $LOG
