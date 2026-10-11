#!/bin/bash
DD=~/workspace/mix/exploration/directed_design
FB=~/workspace/mix/exploration/fast_battery
c=dd1_lin_5_9_nw
while ! grep -q ALLDONE "$DD/results/s2/run.log" 2>/dev/null; do sleep 120; done
echo "=== S2 $c $(date -u +%FT%TZ) ===" >> "$DD/results/s2/$c/s2_diffprof.log"
$FB/build/diffprof_$c 0x123456789abcdef0 22 10 >> "$DD/results/s2/$c/s2_diffprof.log" 2>&1
echo "rc=$? $(date -u +%FT%TZ)"
echo "ALLDONE_5_9" >> "$DD/results/s2/run.log"
