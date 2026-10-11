#!/bin/bash
# Tweaking track driver: emit all specs, then run the staged sweep.
# Detached: setsid nohup bash run_all.sh &
export PATH="$HOME/tools/micromamba-root/envs/sky130/bin:$HOME/tools/micromamba-root/bin:$PATH"
EXP=/home/hatch/workspace/mix/exploration
RTW=$EXP/round_tweak
cd $RTW
echo "=== EMIT $(date -u +%FT%TZ)" | tee work/driver.log
python3 gen_tweak.py --emit >> work/driver.log 2>&1
echo "=== SWEEP $(date -u +%FT%TZ)" | tee -a work/driver.log
python3 sweep.py >> work/sweep.log 2>&1
echo "=== DONE $(date -u +%FT%TZ) rc=$?" | tee -a work/driver.log
