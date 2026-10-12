# S5 stage 3: global + detailed placement, filler. Checkpoint: $WORK/placed.def
# Env: TOP, WORK, FLOWDIR. DEF-only session (re-linking after read_def
# drops pin geometries and confuses placement state).
source $::env(FLOWDIR)/common.tcl
read_def $::env(WORK)/floorplan.def
read_sdc $::env(FLOWDIR)/constraints.sdc
set_thread_count 4
global_placement
detailed_placement
filler_placement "sky130_fd_sc_hd__fill_1 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_4 sky130_fd_sc_hd__fill_8"
write_def $::env(WORK)/placed.def
puts "S5-S3-PLACE-DONE"
