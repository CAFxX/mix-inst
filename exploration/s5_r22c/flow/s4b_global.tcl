# S5 stage 4b: GLOBAL route + parasitic estimation (fast path for delay gate).
# Detailed routing is infeasible on the loaded VM (35min for 10%).
# This gives wirelength/timing via global routes + Steiner estimation.
# Env: TOP, WORK, FLOWDIR. Checkpoints: $WORK/global_routed.def
source $::env(FLOWDIR)/common.tcl
read_def $::env(WORK)/placed.def
read_sdc $::env(FLOWDIR)/constraints.sdc
set_thread_count 4
global_route
# estimate parasitics from global routes
estimate_parasitics -placement
report_checks -path_delay max -fields {input_pins net} -digits 4 \
    > $::env(WORK)/reports/timing_max_global.rpt
report_checks -path_delay min -digits 4 \
    > $::env(WORK)/reports/timing_min_global.rpt
report_power > $::env(WORK)/reports/power_global.rpt
write_def $::env(WORK)/global_routed.def
puts "S5-S4B-GLOBAL-ROUTE-DONE"
