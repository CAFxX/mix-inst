#!/bin/bash
# S5 equivalence: validated r22c RTL vs yosys sky130-mapped netlist (20k random vectors).
# Idempotent: skips if $WORK/equiv_pass.ok exists.
set -u
source ~/tools/sky130-env.sh
W=~/workspace/mix/exploration/s5_r22c/r22c
PDKV=/home/hatch/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A/libs.ref/sky130_fd_sc_hd/verilog
[ -f "$W/equiv_pass.ok" ] && { echo "equiv r22c: SKIP (pass on record)"; exit 0; }
cd "$W"
sed 's/^module r22c_spn_mix4r_lp_nw(/module r22c_synth(/' ysynth.v > ysynth_tb.v
iverilog -o equiv_sim -g2012 tb_equiv.v \
  ~/workspace/your_files/mix_rtl_pareto/mix_r22c_spn_mix4r_lp_nw.v \
  ysynth_tb.v "$PDKV/primitives.v" "$PDKV/sky130_fd_sc_hd.v" 2>/dev/null
./equiv_sim | tee equiv_result.txt | grep -q "EQUIV-PASS" \
  && { date -u +%FT%TZ > equiv_pass.ok; echo "equiv r22c: PASS"; exit 0; } \
  || { echo "equiv r22c: FAIL"; exit 1; }
