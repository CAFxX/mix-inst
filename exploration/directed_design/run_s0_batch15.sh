#!/bin/bash
# S0 for batch-15 (D13) candidates: authorized run_synth.py, Yosys 0.69 pinned.
# Run under nice -19; sequential. Appends RESULT lines to results/s0_batch15.log
# Launch only when `load-shed.sh backoff` reports CLEAR (exit 0 + "CLEAR" line).
# QUEUED 2026-10-10 ~17:55 CEST: backoff said BACKOFF (load 12.06 >= 12).
EXP=/home/hatch/workspace/mix/exploration
DD=$EXP/directed_design
LOG=$DD/results/s0_batch15.log
mkdir -p $DD/results
echo "=== S0 batch15 start $(date -u +%H:%M:%SZ) ===" >> $LOG
for c in dd15_cscc_r5_shl6 dd15_cscc_shr2_shr5 dd15_cscc_shl2_shr6; do
    v=$DD/candidates/$c.v
    out=$DD/work_batch15/s0_$c
    echo "--- $c $(date -u +%H:%M:%SZ) ---" >> $LOG
    nice -n 19 python3 $EXP/run_synth.py $v $c $out >> $LOG 2>&1
    echo "exit=$? for $c" >> $LOG
done
echo "=== S0 batch15 done $(date -u +%H:%M:%SZ) ===" >> $LOG
