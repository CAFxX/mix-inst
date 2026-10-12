#!/bin/bash
# Synthesize one composite inversion core per lam candidate (pinned flow).
# Usage: synth_cores.sh <lam-list-file>
# lam-list-file: lines "lam_hex beta_idx"
set -u
HD=~/workspace/mix/exploration/sbox_screen/handopt
WD=$HD/work
mkdir -p $WD/cores
while read -r lam beta; do
  [ -z "$lam" ] && continue
  case "$lam" in \#*) continue;; esac
  v=$WD/cores/core_lam${lam}_b${beta}.v
  nice -n 19 python3 $HD/comp8.py emit-core --lam "$lam" --beta "$beta" --out "$v" || continue
  out=$WD/cores/synth_lam${lam}_b${beta}.log
  (cd $WD/cores && nice -n 19 python3 ~/workspace/mix/exploration/run_synth.py "$v" comp8_core "synth_lam${lam}_b${beta}") > "$out" 2>&1
  echo "lam=$lam beta=$beta: $(grep -h RESULT "$out" | tail -1)"
done < "$1"
