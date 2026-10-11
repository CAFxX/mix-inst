#!/bin/bash
# S0 for batch-13 (D10) candidates: authorized run_synth.py, Yosys 0.69 pinned.
# Run under nice -19; sequential. Appends RESULT lines to results/s0_batch13.log
# Launch only when `load-shed.sh backoff` reports CLEAR (exit 0 + "CLEAR" line).
EXP=/home/hatch/workspace/mix/exploration
DD=$EXP/directed_design
LOG=$DD/results/s0_batch13.log
mkdir -p $DD/results
echo "=== S0 batch13 start $(date -u +%H:%M:%SZ) ===" >> $LOG
for c in dd13_ax1_r5_shl6 dd13_ax1_r13_shr6 dd13_ax1_r5_shl3 dd13_ax1_r7_shr5 dd13_ax2_ssss_midori_513 dd13_ax2_ssss_midori_1327; do
    v=$DD/candidates/$c.v
    out=$DD/work_batch13/s0_$c
    echo "--- $c $(date -u +%H:%M:%SZ) ---" >> $LOG
    nice -n 19 python3 $EXP/run_synth.py $v $c $out >> $LOG 2>&1
    echo "exit=$? for $c" >> $LOG
done
echo "=== S0 batch13 done $(date -u +%H:%M:%SZ) ===" >> $LOG
