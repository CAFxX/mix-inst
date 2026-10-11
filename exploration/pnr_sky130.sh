#!/bin/bash
# Sky130 synth + full P&R + post-route STA for a combinational design.
# Usage: ./pnr_sky130.sh <top> <rtl.v> <workdir> [die_um]
# Reports: routed wirelength, post-route critical input->output delay (ps), DRC.
#
# Peer-review corrections (2026-10-01):
#  - li1 make_tracks added: omitting it caused GRT-0701 (NOT a tool/PDK bug).
#  - place_pins added so the delivered DEF is routable as-is.
#  - full route + estimate_parasitics -detailed_routing + report_drc.
#  - STA uses a 10us VIRTUAL clock purely as a delay-measurement setup
#    (zero IO delays); the reported number is the measured critical-path
#    arrival, NOT a timing-closure claim. "0 violations" at 10us is vacuous.
set -e
TOP=$1; RTL=$2; WD=$3; DIE=${4:-300}
mkdir -p "$WD"
PDK=/home/hatch/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A
LIB=$PDK/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_100C_1v80.lib
TLEF=$PDK/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef
LEF=$PDK/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
YOSYS=/home/hatch/tools/micromamba-root/envs/sky130/bin/yosys
M=$((DIE-15)); CORE=15

echo "=== Yosys synth ==="
$YOSYS -p "
  read_verilog $RTL;
  hierarchy -check -top $TOP;
  proc; opt; fsm; opt; memory; opt;
  techmap; opt;
  dfflibmap -liberty $LIB;
  abc -liberty $LIB -constr /dev/null;
  clean;
  write_verilog -noattr -noexpr -nodec $WD/synth.v;
" 2>&1 | grep -E "Number of|Liberty" | head -5

echo "=== OpenROAD P&R (die ${DIE}um) ==="
cat > $WD/pnr.tcl <<EOF
read_liberty $LIB
read_lef $TLEF
read_lef $LEF
read_verilog $WD/synth.v
link_design $TOP
# virtual clock for delay MEASUREMENT on a combinational design (not a constraint)
create_clock -name vclk -period 10000
set_input_delay 0 -clock vclk [all_inputs]
set_output_delay 0 -clock vclk [all_outputs]
initialize_floorplan -die_area "0 0 $DIE $DIE" -core_area "$CORE $CORE $M $M" -site unithd
# routing tracks AFTER floorplan (tech LEF ships no TRACKS; li1 included - GRT-0701 fix)
make_tracks li1  -x_offset 0.17 -x_pitch 0.34 -y_offset 0.17 -y_pitch 0.34
make_tracks met1 -x_offset 0.17 -x_pitch 0.34 -y_offset 0.17 -y_pitch 0.34
make_tracks met2 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.23 -y_pitch 0.46
make_tracks met3 -x_offset 0.34 -x_pitch 0.68 -y_offset 0.34 -y_pitch 0.68
make_tracks met4 -x_offset 0.46 -x_pitch 0.92 -y_offset 0.46 -y_pitch 0.92
make_tracks met5 -x_offset 1.70 -x_pitch 3.40 -y_offset 1.70 -y_pitch 3.40
place_pins -hor_layers met3 -ver_layers met4
global_placement
repair_design
detailed_placement
estimate_parasitics -placement
global_route -allow_overflow
detailed_route -bottom_routing_layer met1 -top_routing_layer met5 -droute_end_iter 64 -verbose 10
write_def $WD/pnr.def
report_drc > $WD/drc.rpt
estimate_parasitics -detailed_routing
report_checks -path_delay max -fields {capacitance slew input_pins} -digits 4 -format full_clock_expanded > $WD/timing.rpt
report_tns >> $WD/timing.rpt
report_wns >> $WD/timing.rpt
report_area >> $WD/timing.rpt
EOF
~/tools/sky130bin/openroad -no_splash -exit $WD/pnr.tcl 2>&1 | grep -iE "error|DRT-.*[Ff]ail|finished" | head -10
echo "=== results ==="
grep -E "arrival|required" $WD/timing.rpt | head -4
grep -iE "violation|VIOLATION" $WD/drc.rpt | tail -2
grep -iE "design area|utilization" $WD/timing.rpt | head -4
echo "(10us virtual clock: '0 violations' is vacuous; the arrival time above is the measurement)"
