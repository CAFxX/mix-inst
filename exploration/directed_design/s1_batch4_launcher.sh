#!/bin/bash
# PART-2 S1 (fast_battery s1_screen incl. screen_calibrated) for the 4 ks qualifiers.
# Gates: (1) PART-1 S2 chain complete (ALLDONE_5_9 in run.log) so we never exceed
# 2 heavy pipelines; (2) 1-min load average < 8.0 (round_tweak sweep has priority).
DD=~/workspace/mix/exploration/directed_design
FB=~/workspace/mix/exploration/fast_battery
while ! grep -q ALLDONE_5_9 "$DD/results/s2/run.log" 2>/dev/null; do sleep 600; done
for c in dd4_ks_norc_nw dd4_ks_smallrc_nw dd4_ks_rot1_nw dd4_ks_norot_nw; do
  while true; do
    load=$(awk '{print $1}' /proc/loadavg)
    if awk "BEGIN{exit !($load < 8.0)}"; then break; fi
    sleep 600
  done
  mkdir -p "$DD/results/s1/$c"
  echo "=== S1 $c $(date -u +%FT%TZ) ===" >> "$DD/results/s1/$c/s1_screen.log"
  python3 "$FB/src/s1_screen.py" "$c" "$DD/results/s1/$c" >> "$DD/results/s1/$c/s1_screen.log" 2>&1
  echo "rc=$? $(date -u +%FT%TZ)" >> "$DD/results/s1/$c/s1_screen.log"
done
echo "BATCH4_S1_DONE $(date -u +%FT%TZ)" >> "$DD/results/s1/run.log"
