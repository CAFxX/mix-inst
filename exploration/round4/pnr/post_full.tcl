# Post-route reporting for OpenROAD v2.0 (no report_area / report_drc commands).
# Args (via env): TOP, SYNTH (unused, for symmetry), DEF (final.def), WD, LIB/LEF env as usual.
# For sequential: set SEQ=1 and CLK_PERIOD.
read_liberty $env(PDK_LIB)
read_lef $env(PDK_TLEF)
read_lef $env(PDK_LEF_SC_HD)
read_def $env(DEF)
read_verilog $env(SYNTH)
link_design $env(TOP)
estimate_parasitics -detailed_routing
if {[info exists env(SEQ)]} {
  if {[info exists env(CLK_PERIOD)]} { set CP $env(CLK_PERIOD) } else { set CP 10 }
  create_clock -name clk -period $CP [get_ports clk]
  set_input_delay 0 -clock clk [get_ports {val[*] key[*] valid_in}]
  set_output_delay 0 -clock clk [get_ports {out[*] valid_out}]
} else {
  create_clock -name vclk -period 10000
  set_input_delay 0 -clock vclk [all_inputs]
  set_output_delay 0 -clock vclk [all_outputs]
}
# design area from DB masters (um^2)
set block [ord::get_db_block]
set area 0.0
set ninst 0
foreach inst [$block getInsts] {
  set master [$inst getMaster]
  set area [expr {$area + [$master getArea]}]
  incr ninst
}
set dbunits [$block getDbUnitsPerMicron]
set areport [open $env(WD)/area.rpt w]
puts $areport "instances: $ninst"
puts $areport "design_area_um2: [format %.3f [expr {$area / ($dbunits * $dbunits)}]]"
close $areport
# critical path + slack
report_checks -path_delay max -digits 4 > $env(WD)/timing.rpt
report_tns >> $env(WD)/timing.rpt
report_wns >> $env(WD)/timing.rpt
report_checks -path_delay min -digits 4 > $env(WD)/timing_min.rpt
# power with default activity (documented assumption: no SAIF/VCD)
report_power > $env(WD)/power.rpt
