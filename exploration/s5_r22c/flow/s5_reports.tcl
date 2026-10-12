# S5 stage 5: final reports (timing/power). Reads routed DEF + final netlist.
# Env: TOP, WORK, FLOWDIR. Outputs in $WORK/reports/.
# Achieved combinational delay = 19.0 - worst_slack  (20ns clock, 0.5ns in/out).
# NOTE: read_def BEFORE link (else "Chip already exists").
source $::env(FLOWDIR)/common.tcl
read_def $::env(WORK)/routed.def
read_verilog $::env(WORK)/final.v
link_design $::env(TOP)
read_sdc $::env(FLOWDIR)/constraints.sdc
report_checks -path_delay max -fields {input_pins net} -digits 4 \
    > $::env(WORK)/reports/timing_max.rpt
report_checks -path_delay min -digits 4 \
    > $::env(WORK)/reports/timing_min.rpt
report_power > $::env(WORK)/reports/power.rpt
puts "S5-S5-REPORTS-DONE"
