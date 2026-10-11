# Sky130 P&R flow for sequential designs (real clock port).
# Args (via env): TOP, SYNTH, WD, DIE, CLK_PERIOD (ns, default 20), CLK_PORT (default clk)
read_liberty $env(PDK_LIB)
read_lef $env(PDK_TLEF)
read_lef $env(PDK_LEF_SC_HD)
read_verilog $env(SYNTH)
link_design $env(TOP)
if {[info exists env(CLK_PERIOD)]} { set CP $env(CLK_PERIOD) } else { set CP 20 }
if {[info exists env(CLK_PORT)]} { set CKP $env(CLK_PORT) } else { set CKP "clk" }
create_clock -name clk -period $CP [get_ports $CKP]
set_input_delay 0 -clock clk [get_ports {val[*] key[*] valid_in}]
set_output_delay 0 -clock clk [get_ports {out[*] valid_out}]
set DIE $env(DIE)
initialize_floorplan -die_area "0 0 $DIE $DIE" -core_area "15 15 [expr {$DIE-15}] [expr {$DIE-15}]" -site unithd
make_tracks li1  -x_offset 0.23 -x_pitch 0.46 -y_offset 0.17 -y_pitch 0.34
make_tracks met1 -x_offset 0.17 -x_pitch 0.34 -y_offset 0.17 -y_pitch 0.34
make_tracks met2 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.23 -y_pitch 0.46
make_tracks met3 -x_offset 0.34 -x_pitch 0.68 -y_offset 0.34 -y_pitch 0.68
make_tracks met4 -x_offset 0.46 -x_pitch 0.92 -y_offset 0.46 -y_pitch 0.92
make_tracks met5 -x_offset 1.70 -x_pitch 3.40 -y_offset 1.70 -y_pitch 3.40
place_pins -hor_layers met3 -ver_layers met2
global_placement
repair_design
repair_timing
detailed_placement
global_route
detailed_route
write_def $env(WD)/final.def
report_checks -path_delay max -fields {capacitance slew input_pins} -digits 4 -format full_clock_expanded > $env(WD)/timing.rpt
report_tns >> $env(WD)/timing.rpt
report_wns >> $env(WD)/timing.rpt
report_checks -path_delay min -fields {capacitance slew input_pins} -digits 4 -format full_clock_expanded > $env(WD)/timing_min.rpt
report_area >> $env(WD)/timing.rpt
report_power >> $env(WD)/power.rpt
report_drc > $env(WD)/drc.rpt
