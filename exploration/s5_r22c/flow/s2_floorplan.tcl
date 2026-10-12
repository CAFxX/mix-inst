# S5 stage 2: floorplan + tapcell + PDN. Checkpoint: $WORK/floorplan.def
# Env: TOP, WORK, FLOWDIR.
source $::env(FLOWDIR)/common.tcl
read_verilog $::env(WORK)/ysynth.v
link_design $::env(TOP)
read_sdc $::env(FLOWDIR)/constraints.sdc
initialize_floorplan -site unithd -utilization 40 -aspect_ratio 1 -core_space 2
make_tracks
place_pins -hor_layers met3 -ver_layers met2
tapcell -tapcell_master sky130_fd_sc_hd__tapvpwrvgnd_1 \
        -endcap_master sky130_fd_sc_hd__decap_3 \
        -distance 14
add_global_connection -net {VPWR} -inst_pattern {.*} -pin_pattern {VPWR} -power
add_global_connection -net {VGND} -inst_pattern {.*} -pin_pattern {VGND} -ground
source $::env(FLOWDIR)/pdn.cfg
pdngen
write_def $::env(WORK)/floorplan.def
puts "S5-S2-FLOORPLAN-DONE"
