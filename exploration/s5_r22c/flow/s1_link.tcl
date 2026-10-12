# S5 stage 1: link the yosys-produced structural netlist (parser-safe).
# Env: TOP, WORK, FLOWDIR. Checkpoint: $WORK/linked.ok
source $::env(FLOWDIR)/common.tcl
read_verilog $::env(WORK)/ysynth.v
link_design $::env(TOP)
read_sdc $::env(FLOWDIR)/constraints.sdc
set ncells [llength [get_cells *]]
if {$ncells < 100} { error "suspiciously few cells after link: $ncells" }
set fh [open $::env(WORK)/linked.ok w]
puts $fh "cells=$ncells top=$::env(TOP)"
close $fh
puts "S5-S1-LINK-DONE cells=$ncells"
