#!/bin/bash
# S5 equivalence: mult64 RTL vs yosys sky130-mapped netlist (20k random vectors).
# Idempotent: skips if $WORK/equiv_pass.ok exists.
set -u
source ~/tools/sky130-env.sh
W=~/workspace/mix/exploration/s5_r22c/mult
PDKV=/home/hatch/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A/libs.ref/sky130_fd_sc_hd/verilog
[ -f "$W/equiv_pass.ok" ] && { echo "equiv mult: SKIP (pass on record)"; exit 0; }
cd "$W"
sed 's/^module mul64(/module mul64_synth(/' ysynth.v > ysynth_tb.v
iverilog -o equiv_sim -g2012 tb_equiv_mult.v \
  ~/workspace/mix/synth/mul64.v \
  ysynth_tb.v "$PDKV/primitives.v" "$PDKV/sky130_fd_sc_hd.v" 2>/dev/null
./equiv_sim | tee equiv_result.txt | grep -q "EQUIV-PASS" \
  && { date -u +%FT%TZ > equiv_pass.ok; echo "equiv mult: PASS"; exit 0; } \
  || { echo "equiv mult: FAIL"; exit 1; }
