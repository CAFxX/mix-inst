# Full Sky130 P&R flow with detailed routing.
# Args (via env): TOP, SYNTH (synth.v path), WD (work dir), DIE (die size, default 300)
# Env: PDK_LIB, PDK_TLEF, PDK_LEF_SC_HD must be set (source ~/tools/sky130-env.sh)
read_liberty $env(PDK_LIB)
read_lef $env(PDK_TLEF)
read_lef $env(PDK_LEF_SC_HD)
read_verilog $env(SYNTH)
link_design $env(TOP)
# virtual clock for IO constraints on combinational design
create_clock -name vclk -period 10000
set_input_delay 0 -clock vclk [all_inputs]
set_output_delay 0 -clock vclk [all_outputs]
set DIE $env(DIE)
initialize_floorplan -die_area "0 0 $DIE $DIE" -core_area "15 15 [expr {$DIE-15}] [expr {$DIE-15}]" -site unithd
# Tech LEF has no TRACKS section: create tracks for ALL routing layers
# (li1 included -- missing li1 tracks cause GRT-0701 "Missing track structure").
# Pitches/offsets from sky130_fd_sc_hd__nom.tlef LAYER statements.
make_tracks li1  -x_offset 0.23 -x_pitch 0.46 -y_offset 0.17 -y_pitch 0.34
make_tracks met1 -x_offset 0.17 -x_pitch 0.34 -y_offset 0.17 -y_pitch 0.34
make_tracks met2 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.23 -y_pitch 0.46
make_tracks met3 -x_offset 0.34 -x_pitch 0.68 -y_offset 0.34 -y_pitch 0.68
make_tracks met4 -x_offset 0.46 -x_pitch 0.92 -y_offset 0.46 -y_pitch 0.92
make_tracks met5 -x_offset 1.70 -x_pitch 3.40 -y_offset 1.70 -y_pitch 3.40
place_pins -hor_layers met3 -ver_layers met2
global_placement
repair_design
detailed_placement
# Restrict signal routing to met1-met5 (exclude li1): li1 is the intra-cell
# local-interconnect layer; routing signals on it causes systematic DRC
# violations in TritonRoute. Matches ORFS sky130hd (set_routing_layers -signal met1-met5).
set_routing_layers -signal met1-met5 -clock met1-met5
global_route
detailed_route -droute_end_iter 20
write_def $env(WD)/final.def
# Note: report_area and report_drc do not exist in OpenROAD v2.0.
# Use post.tcl separately for area/power/timing; DRC violations are
# reported by TritonRoute during detailed_route (see log).
report_checks -path_delay max -fields {capacitance slew input_pins} -digits 4 -format full_clock_expanded > $env(WD)/timing.rpt
report_tns >> $env(WD)/timing.rpt
report_wns >> $env(WD)/timing.rpt
report_checks -path_delay min -fields {capacitance slew input_pins} -digits 4 -format full_clock_expanded > $env(WD)/timing_min.rpt
report_power >> $env(WD)/power.rpt
