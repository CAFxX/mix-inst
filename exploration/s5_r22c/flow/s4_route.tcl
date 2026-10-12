# S5 stage 4: global + detailed route. Checkpoints: $WORK/routed.def, $WORK/final.v
# Env: TOP, WORK, FLOWDIR. DEF-only session (re-linking after read_def
# confuses instance placement state).
source $::env(FLOWDIR)/common.tcl
read_def $::env(WORK)/placed.def
read_sdc $::env(FLOWDIR)/constraints.sdc
set_thread_count 4
global_route
detailed_route -output_drc $::env(WORK)/reports/route_drc.rpt
write_def $::env(WORK)/routed.def
write_verilog $::env(WORK)/final.v
puts "S5-S4-ROUTE-DONE"
