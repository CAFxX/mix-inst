#!/bin/bash
# Launch S0 for queued directed-design candidates when load < 4.
# Usage: ./launch_s0_queue.sh
# Polite-mode: checks 1-min load, aborts if >= 4.

LOAD=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | xargs)
LOAD_INT=${LOAD%.*}
if [ "$LOAD_INT" -ge 4 ]; then
    echo "ABORT: load $LOAD >= 4, polite gate not met"
    exit 1
fi

EXP=/home/hatch/workspace/mix/exploration
DD=$EXP/directed_design
YOSYS=/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys

# Verify yosys version
$YOSYS -V 2>&1 | grep -q "0.69" || { echo "ABORT: yosys not 0.69"; exit 1; }

CANDS=(
    # batch-3 heterogeneous (4)
    dd3_hetero_RMRM_nw dd3_hetero_MRMR_nw dd3_hetero_RRMM_nw dd3_hetero_URUR_nw
    # batch-5 round-count (3)
    dd5_r3_513_nw dd5_r5_513_nw dd5_r6_513_nw
    # batch-6 ks x lin (6)
    dd6_ksnorc_lin5_9_nw dd6_kssmallrc_lin5_9_nw dd6_ksrot1_lin5_9_nw
    dd6_ksnorc_lin8_15_nw dd6_kssmallrc_lin8_15_nw dd6_ksrot1_lin8_15_nw
)

for c in "${CANDS[@]}"; do
    v=$DD/candidates/$c.v
    [ -f "$v" ] || { echo "SKIP $c: no .v"; continue; }
    out=/tmp/s0_$c
    echo "=== S0 $c ==="
    nice -19 python3 $EXP/run_synth.py $v $c $out 2>&1 | tail -3
done
echo "DONE"
