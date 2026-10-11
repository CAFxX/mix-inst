#!/bin/bash
# S0 for batch-14 (D11) candidates: authorized run_synth.py, Yosys 0.69 pinned.
# Run under nice -19; sequential. Appends RESULT lines to results/s0_batch14.log
# Launch only when `load-shed.sh backoff` reports CLEAR (exit 0 + "CLEAR" line).
EXP=/home/hatch/workspace/mix/exploration
DD=$EXP/directed_design
LOG=$DD/results/s0_batch14.log
mkdir -p $DD/results
echo "=== S0 batch14 start $(date -u +%H:%M:%SZ) ===" >> $LOG
for c in dd14_ax1_shr2_shr5 dd14_ax1_shl2_shr6 dd14_ax2_ssss_midori_1943 dd14_ax2_ssss_midori_r13_shr6; do
    v=$DD/candidates/$c.v
    out=$DD/work_batch14/s0_$c
    echo "--- $c $(date -u +%H:%M:%SZ) ---" >> $LOG
    nice -n 19 python3 $EXP/run_synth.py $v $c $out >> $LOG 2>&1
    echo "exit=$? for $c" >> $LOG
done
echo "=== S0 batch14 done $(date -u +%H:%M:%SZ) ===" >> $LOG
