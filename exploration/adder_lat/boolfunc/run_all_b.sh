#!/bin/bash
# Design B runner: backoff-gated synth (3 offsets) + full Fisher triage.
# Cleared-flag single-gate pattern (AGENTS.md lesson 2026-10-11): the cleared
# flag is the single source of truth; no post-loop re-check.
set -u
HERE=/home/hatch/workspace/mix/exploration/adder_lat/boolfunc
LOG=$HERE/run_all.log
cleared=0
while [ $cleared -eq 0 ]; do
  if $HOME/workspace/system/bin/load-shed.sh backoff >>"$LOG" 2>&1; then
    cleared=1
  else
    sleep 60
  fi
done
echo "BACKOFF CLEAR $(date -u +%FT%TZ)" >>"$LOG"
V=$HERE/boolfunc_b.v
for t in boolfunc_b_13 boolfunc_b_17 boolfunc_b_311; do
  echo "== synth $t" >>"$LOG"
  nice -n 19 python3 /home/hatch/workspace/mix/exploration/run_synth.py "$V" "$t" "$HERE/synth_$t" >>"$LOG" 2>&1
  echo "synth_$t exit=$?" >>"$LOG"
done
echo "== fisher triage ==" >>"$LOG"
nice -n 19 python3 "$HERE/screen_b.py" >>"$LOG" 2>&1
echo "fisher exit=$?" >>"$LOG"
echo "RUNNER DONE $(date -u +%FT%TZ)" >>"$LOG"
