read_lef /tmp/test_tracks.tlef
read_lef $env(PDK_LEF_SC_HD)
read_verilog synth_add64.v
link_design add64
initialize_floorplan -die_area "0 0 200 200" -core_area "15 15 185 185" -site unithd
set block [ord::get_db_block]
foreach tg [$block getTrackGrids] {
  set layer [[$tg getTechLayer] getName]
  if {$layer == "met1" || $layer == "met2"} {
    puts "TRACKGRID layer=$layer"
    puts "   X: [$tg getGridPatternX 0]"
    puts "   Y: [$tg getGridPatternY 0]"
  }
}
